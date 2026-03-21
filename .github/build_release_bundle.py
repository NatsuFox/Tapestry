#!/usr/bin/env python3
"""Build deterministic GitHub release archives for the Tapestry skill bundle."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tarfile
import tomllib
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_FILES = (
    Path("LICENSE"),
    Path("README.md"),
    Path("docs/installation.md"),
    Path("pyproject.toml"),
    Path(".claude-plugin/plugin.json"),
    Path(".claude-plugin/marketplace.json"),
)
SKILL_PACK_ROOT = Path("skills/tapestry")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build zip and tar.gz release bundles for the Tapestry skill pack."
    )
    parser.add_argument(
        "--version",
        help="Release version without a leading 'v'. Defaults to the tag name or pyproject version.",
    )
    parser.add_argument(
        "--output-dir",
        default="dist/releases",
        help="Directory where the archives and checksum file will be written.",
    )
    return parser.parse_args()


def resolve_version(cli_version: str | None) -> str:
    if cli_version:
        return cli_version.removeprefix("v")

    ref_type = os.environ.get("GITHUB_REF_TYPE", "")
    ref_name = os.environ.get("GITHUB_REF_NAME", "")
    if ref_type == "tag" and ref_name:
        return ref_name.removeprefix("v")

    pyproject = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    return data["project"]["version"]


def tracked_skill_files() -> list[Path]:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "-z", "--cached", "--", str(SKILL_PACK_ROOT)],
        check=True,
        capture_output=True,
        text=False,
    )
    tracked_paths = [Path(item.decode("utf-8")) for item in result.stdout.split(b"\0") if item]
    files: list[Path] = []
    skipped: list[Path] = []
    for relative_path in tracked_paths:
        source = REPO_ROOT / relative_path
        if source.is_symlink() or not source.is_file():
            skipped.append(relative_path)
            continue
        files.append(relative_path)

    if skipped:
        print(
            "Skipping non-portable tracked entries from the release bundle:",
            ", ".join(path.as_posix() for path in skipped),
            file=sys.stderr,
        )

    if not files:
        raise RuntimeError(f"No tracked files found under {SKILL_PACK_ROOT}")
    return sorted(files)


def copy_file(relative_path: Path, destination_root: Path) -> None:
    source = REPO_ROOT / relative_path
    if not source.exists():
        raise FileNotFoundError(f"Missing expected file: {relative_path}")
    destination = destination_root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def create_stage_dir(bundle_name: str, output_dir: Path) -> tuple[Path, list[Path]]:
    stage_dir = output_dir / bundle_name
    if stage_dir.exists():
        shutil.rmtree(stage_dir)

    copied_paths: list[Path] = []
    for relative_path in STATIC_FILES:
        copy_file(relative_path, stage_dir)
        copied_paths.append(relative_path)

    for relative_path in tracked_skill_files():
        copy_file(relative_path, stage_dir)
        copied_paths.append(relative_path)

    manifest_path = stage_dir / "MANIFEST.txt"
    manifest_path.write_text(
        "".join(f"{path.as_posix()}\n" for path in copied_paths),
        encoding="utf-8",
    )
    copied_paths.append(Path("MANIFEST.txt"))
    return stage_dir, copied_paths


def build_zip(stage_dir: Path, bundle_name: str, output_dir: Path) -> Path:
    zip_path = output_dir / f"{bundle_name}.zip"
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(stage_dir.rglob("*")):
            archive.write(path, path.relative_to(output_dir))
    return zip_path


def build_tarball(stage_dir: Path, bundle_name: str, output_dir: Path) -> Path:
    tar_path = output_dir / f"{bundle_name}.tar.gz"
    if tar_path.exists():
        tar_path.unlink()

    with tarfile.open(tar_path, "w:gz") as archive:
        archive.add(stage_dir, arcname=bundle_name)
    return tar_path


def write_checksums(paths: list[Path], output_dir: Path, bundle_name: str) -> Path:
    checksum_path = output_dir / f"{bundle_name}.sha256"
    lines = []
    for path in paths:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.name}")
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return checksum_path


def main() -> None:
    args = parse_args()
    version = resolve_version(args.version)
    output_dir = (REPO_ROOT / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    bundle_name = f"tapestry-skills-v{version}"
    stage_dir, _ = create_stage_dir(bundle_name, output_dir)
    zip_path = build_zip(stage_dir, bundle_name, output_dir)
    tar_path = build_tarball(stage_dir, bundle_name, output_dir)
    checksum_path = write_checksums([zip_path, tar_path], output_dir, bundle_name)

    print(f"Created release bundle: {zip_path}")
    print(f"Created release bundle: {tar_path}")
    print(f"Created checksum file: {checksum_path}")


if __name__ == "__main__":
    main()
