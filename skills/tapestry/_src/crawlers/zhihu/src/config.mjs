import fs from 'node:fs';
import path from 'node:path';

const DEFAULT_EXECUTABLE_CANDIDATES = [
  process.env.ZHIHU_CHROMIUM_EXECUTABLE,
  '~/.cache/ms-playwright/chromium-1208/chrome-linux/chrome',
  '/usr/bin/chromium-browser',
  '/usr/bin/chromium',
  '/usr/bin/google-chrome',
  '/usr/bin/google-chrome-stable',
  '/usr/bin/chrome',
  '/usr/bin/microsoft-edge',
  '/usr/bin/microsoft-edge-stable',
  '~/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome',
  '~/.cache/ms-playwright/chromium-*/chrome-linux/chrome',
  '~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome',
].filter(Boolean);

function expandGlobLike(candidate) {
  // Expand ~ to home directory
  if (candidate.startsWith('~/')) {
    const home = process.env.HOME || process.env.USERPROFILE;
    candidate = path.join(home, candidate.slice(2));
  }

  if (!candidate.includes('*')) return [candidate];
  const parts = candidate.split('/');
  let prefixes = ['/'];
  for (const part of parts.filter(Boolean)) {
    const next = [];
    for (const prefix of prefixes) {
      if (!part.includes('*')) {
        next.push(path.join(prefix, part));
        continue;
      }
      const dir = prefix;
      if (!fs.existsSync(dir)) continue;
      for (const entry of fs.readdirSync(dir)) {
        const re = new RegExp('^' + part.replace(/[-/\\^$+?.()|[\]{}]/g, '\\$&').replace(/\*/g, '.*') + '$');
        if (re.test(entry)) next.push(path.join(dir, entry));
      }
    }
    prefixes = next;
  }
  return prefixes;
}

export function resolveChromiumExecutable() {
  for (const candidate of DEFAULT_EXECUTABLE_CANDIDATES) {
    for (const expanded of expandGlobLike(candidate)) {
      if (expanded && fs.existsSync(expanded)) return expanded;
    }
  }
  throw new Error(
    'Unable to locate a Chromium executable. Set ZHIHU_CHROMIUM_EXECUTABLE explicitly.',
  );
}

export function defaultServerConfig() {
  return {
    host: process.env.ZHIHU_API_HOST || '127.0.0.1',
    port: Number(process.env.ZHIHU_API_PORT || 8765),
    chromiumExecutable: resolveChromiumExecutable(),
  };
}
