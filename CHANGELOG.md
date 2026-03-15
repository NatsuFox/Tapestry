# Changelog | 更新日志

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of Tapestry skill pack
- Multi-platform crawler support (Zhihu, X/Twitter, Xiaohongshu, Weibo, Hacker News, Reddit, Generic HTML)
- Four-skill workflow: Ingest, Feed, Synthesis, Display
- Book-like hierarchical knowledge base structure
- Visual frontend for browsing knowledge base
- Comprehensive test suite
- Bilingual documentation (Chinese/English)

### Changed

### Deprecated

### Removed

### Fixed

### Security

---

## [0.1.0] - 2026-03-15

### Added
- Initial project structure
- Core crawler registry and routing system
- Zhihu crawler with reverse-engineered API
- X/Twitter public page crawler
- Xiaohongshu content crawler
- Weibo public post crawler
- Hacker News discussion crawler
- Reddit thread crawler
- Generic HTML fallback crawler
- Feed normalization system with source-specific specs
- Knowledge base synthesis workflow
- Display skill with frontend viewer
- Test infrastructure
- Documentation (README, CONTRIBUTING, LICENSE)
- GitHub issue templates and PR template
- Security policy

---

## Release Notes Format

Each release should include:

### Added
- New features
- New crawlers
- New documentation

### Changed
- Changes in existing functionality
- Updated dependencies
- Improved performance

### Deprecated
- Features that will be removed in future releases

### Removed
- Removed features
- Removed dependencies

### Fixed
- Bug fixes
- Security patches

### Security
- Security-related changes
- Vulnerability fixes

---

## Version History

- **0.1.0** (2026-03-15): Initial release with core functionality
- **Unreleased**: Current development version

---

## How to Contribute to Changelog

When submitting a PR, please add your changes to the `[Unreleased]` section under the appropriate category. The maintainers will move entries to versioned sections during releases.

Example:
```markdown
## [Unreleased]

### Added
- feat(crawlers): add Bilibili video crawler (#123)
```
