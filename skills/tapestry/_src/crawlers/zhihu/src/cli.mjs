#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { fetchZhihuPage } from './fetcher.mjs';
import { detectResultKind, urlInfo } from './parsers/common.mjs';
import { parseAuto, parseByKind } from './parsers/index.mjs';
import { defaultIncludeComments, inferRequestedKind } from './request-options.mjs';

const HELP = `zhihu-parse - local Zhihu fetch/parse CLI

Usage:
  zhihu-parse [options] <url> [more-urls...]

Options:
  --kind <kind>              Force parser kind (auto|zhuanlan.article|question|answer|profile)
  --out-dir <dir>            Save outputs under this directory (one subdir per URL)
  --save-html                Save fetched page.html
  --save-text                Save fetched page.txt
  --save-json                Save structured result.json
  --include-comments         Force-enable comment capture
  --no-comments              Force-disable comment capture
  --retries <n>              Retry failed fetches this many extra times (default: 0)
  --retry-delay-ms <ms>      Delay between retries in milliseconds (default: 1500)
  --timeout-ms <ms>          Browser fetch timeout override
  --wait-after-load-ms <ms>  Post-load settle delay override
  --format <pretty|json|jsonl>
                             pretty=human summary (default)
                             json=emit one JSON array of full results
                             jsonl=emit one JSON object per line
  --help, -h                 Show this help

Examples:
  zhihu-parse https://zhuanlan.zhihu.com/p/2014452522178334926
  zhihu-parse --out-dir /tmp/zhihu-run --save-json --save-text \
    https://www.zhihu.com/question/610072126/answer/2013215979509940714
  zhihu-parse --format json \
    https://zhuanlan.zhihu.com/p/2014452522178334926 \
    https://www.zhihu.com/people/cfeng2003
`;

function requireValue(optionName, value) {
  if (value == null || value.startsWith('-')) {
    throw new Error(`Missing value for ${optionName}`);
  }
  return value;
}

function parseInteger(name, value) {
  const parsed = Number.parseInt(requireValue(name, value), 10);
  if (!Number.isFinite(parsed)) {
    throw new Error(`Invalid ${name}: ${value}`);
  }
  return parsed;
}

export function parseCliArgs(argv = process.argv.slice(2)) {
  const options = {
    urls: [],
    kind: 'auto',
    outDir: null,
    saveHtml: false,
    saveText: false,
    saveJson: false,
    includeComments: undefined,
    retries: 0,
    retryDelayMs: 1500,
    timeoutMs: undefined,
    waitAfterLoadMs: undefined,
    format: 'pretty',
    help: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    const next = argv[index + 1];

    if (arg === '--help' || arg === '-h') {
      options.help = true;
      continue;
    }
    if (arg === '--kind') {
      options.kind = requireValue('--kind', next);
      index += 1;
      continue;
    }
    if (arg === '--out-dir') {
      options.outDir = requireValue('--out-dir', next);
      index += 1;
      continue;
    }
    if (arg === '--save-html') {
      options.saveHtml = true;
      continue;
    }
    if (arg === '--save-text') {
      options.saveText = true;
      continue;
    }
    if (arg === '--save-json') {
      options.saveJson = true;
      continue;
    }
    if (arg === '--include-comments') {
      options.includeComments = true;
      continue;
    }
    if (arg === '--no-comments') {
      options.includeComments = false;
      continue;
    }
    if (arg === '--retries') {
      options.retries = parseInteger('retries', next);
      index += 1;
      continue;
    }
    if (arg === '--retry-delay-ms') {
      options.retryDelayMs = parseInteger('retry-delay-ms', next);
      index += 1;
      continue;
    }
    if (arg === '--timeout-ms') {
      options.timeoutMs = parseInteger('timeout-ms', next);
      index += 1;
      continue;
    }
    if (arg === '--wait-after-load-ms') {
      options.waitAfterLoadMs = parseInteger('wait-after-load-ms', next);
      index += 1;
      continue;
    }
    if (arg === '--format') {
      options.format = requireValue('--format', next);
      index += 1;
      continue;
    }
    if (arg === '--json') {
      options.format = 'json';
      continue;
    }
    if (arg.startsWith('-')) {
      throw new Error(`Unknown option: ${arg}`);
    }
    options.urls.push(arg);
  }

  if (!['pretty', 'json', 'jsonl'].includes(options.format)) {
    throw new Error(`Unsupported format: ${options.format}`);
  }
  if (!options.help && options.urls.length === 0) {
    throw new Error('At least one Zhihu URL is required');
  }
  return options;
}

function baseNameForUrl(url, requestedKind, index) {
  const info = urlInfo(url);
  switch (requestedKind === 'auto' ? info.kind : requestedKind) {
    case 'zhuanlan.article':
      return `article-${info.articleId || index}`;
    case 'question':
      return `question-${info.questionId || index}`;
    case 'answer':
      return `answer-${info.answerId || info.questionId || index}`;
    case 'profile':
      return `profile-${info.userToken || index}`;
    default:
      return `item-${String(index).padStart(3, '0')}`;
  }
}

function summarize(parsed = {}) {
  switch (parsed.kind) {
    case 'zhuanlan.article':
      return {
        title: parsed.title,
        author: parsed.author,
        voteupCount: parsed.voteupCount,
        commentCount: parsed.commentCount,
      };
    case 'question':
      return {
        title: parsed.title,
        answerCount: parsed.answerCount,
        commentCount: parsed.commentCount,
        fetchedComments: parsed.comments?.fetchedCount ?? null,
        commentsComplete: parsed.comments?.complete ?? null,
      };
    case 'answer':
      return {
        questionTitle: parsed.questionTitle,
        author: parsed.author,
        voteupCount: parsed.voteupCount,
        commentCount: parsed.commentCount,
        fetchedComments: parsed.comments?.fetchedCount ?? null,
        commentsComplete: parsed.comments?.complete ?? null,
      };
    case 'profile':
      return {
        name: parsed.name,
        headline: parsed.headline,
        followerCount: parsed.followerCount,
        answerCount: parsed.answerCount,
      };
    default:
      return {};
  }
}

function prettyPrint(result) {
  const lines = [
    `URL: ${result.url}`,
    `ok: ${result.ok}`,
    `requestedKind: ${result.requestedKind}`,
    `detectedKind: ${result.detectedKind}`,
    `includeComments: ${result.includeComments}`,
  ];
  for (const [key, value] of Object.entries(summarize(result.parsed))) {
    lines.push(`${key}: ${value}`);
  }
  if (result.savedResultPath) lines.push(`savedResult: ${result.savedResultPath}`);
  if (result.outputDir) lines.push(`outputDir: ${result.outputDir}`);
  return lines.join('\n');
}

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
}

async function sleep(ms) {
  await new Promise((resolve) => setTimeout(resolve, ms));
}

export async function fetchAndParseUrl(url, options, index = 1) {
  const requestedKind = inferRequestedKind(options.kind, { url });
  const includeComments = defaultIncludeComments(options.kind, {
    url,
    includeComments: options.includeComments,
  });
  const outputDir = options.outDir
    ? path.join(options.outDir, `${String(index).padStart(3, '0')}-${baseNameForUrl(url, requestedKind, index)}`)
    : null;

  if (outputDir) await ensureDir(outputDir);

  let attempt = 0;
  let lastPayload = null;
  let lastError = null;

  while (attempt <= options.retries) {
    try {
      const fetch = await fetchZhihuPage({
        url,
        includeText: true,
        includeHtml: true,
        includeComments,
        outputDir,
        saveHtml: options.saveHtml,
        saveText: options.saveText,
        timeoutMs: options.timeoutMs,
        waitAfterLoadMs: options.waitAfterLoadMs,
      });
      const detectedKind = detectResultKind(fetch);
      const parsed = options.kind === 'auto' ? parseAuto(fetch) : parseByKind(options.kind, fetch);
      const payload = {
        ok: fetch.ok && parsed.ok,
        url,
        requestedKind,
        detectedKind,
        includeComments,
        fetch,
        parsed,
        outputDir,
      };
      if (outputDir && options.saveJson) {
        payload.savedResultPath = path.join(outputDir, 'result.json');
        await fs.writeFile(payload.savedResultPath, JSON.stringify(payload, null, 2));
      }
      if (payload.ok) return payload;
      lastPayload = payload;
    } catch (error) {
      lastError = error;
    }

    if (attempt < options.retries) {
      await sleep(options.retryDelayMs);
    }
    attempt += 1;
  }

  if (lastPayload) return lastPayload;
  return {
    ok: false,
    url,
    requestedKind,
    detectedKind: null,
    includeComments,
    fetch: null,
    parsed: null,
    outputDir,
    error: lastError instanceof Error ? lastError.message : String(lastError),
  };
}

export async function runCli(argv = process.argv.slice(2)) {
  const options = parseCliArgs(argv);
  if (options.help) {
    console.log(HELP);
    return { exitCode: 0, results: [] };
  }

  if (options.outDir) await ensureDir(options.outDir);
  const effectiveOptions = {
    ...options,
    saveJson: options.saveJson || Boolean(options.outDir),
  };

  const results = [];
  for (let index = 0; index < options.urls.length; index += 1) {
    const url = options.urls[index];
    const result = await fetchAndParseUrl(url, effectiveOptions, index + 1);
    results.push(result);
  }

  if (options.format === 'json') {
    console.log(JSON.stringify(results, null, 2));
  } else if (options.format === 'jsonl') {
    for (const result of results) console.log(JSON.stringify(result));
  } else {
    console.log(results.map(prettyPrint).join('\n\n'));
  }

  const exitCode = results.some((result) => !result.ok) ? 1 : 0;
  return { exitCode, results };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  try {
    const { exitCode } = await runCli();
    process.exitCode = exitCode;
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  }
}
