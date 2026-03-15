import test from 'node:test';
import assert from 'node:assert/strict';
import { parseCliArgs } from '../../src/cli.mjs';

test('parseCliArgs accepts positional URLs and defaults', () => {
  const parsed = parseCliArgs(['https://zhuanlan.zhihu.com/p/2014452522178334926']);
  assert.deepEqual(parsed.urls, ['https://zhuanlan.zhihu.com/p/2014452522178334926']);
  assert.equal(parsed.kind, 'auto');
  assert.equal(parsed.retries, 0);
  assert.equal(parsed.format, 'pretty');
});

test('parseCliArgs parses output and retry flags', () => {
  const parsed = parseCliArgs([
    '--out-dir',
    '/tmp/zhihu-run',
    '--save-html',
    '--save-text',
    '--save-json',
    '--retries',
    '2',
    '--retry-delay-ms',
    '2000',
    '--format',
    'jsonl',
    'https://www.zhihu.com/question/610072126/answer/2013215979509940714',
  ]);

  assert.equal(parsed.outDir, '/tmp/zhihu-run');
  assert.equal(parsed.saveHtml, true);
  assert.equal(parsed.saveText, true);
  assert.equal(parsed.saveJson, true);
  assert.equal(parsed.retries, 2);
  assert.equal(parsed.retryDelayMs, 2000);
  assert.equal(parsed.format, 'jsonl');
});

test('parseCliArgs supports explicit comment toggles', () => {
  const parsed = parseCliArgs([
    '--no-comments',
    'https://www.zhihu.com/question/610072126/answer/2013215979509940714',
  ]);
  assert.equal(parsed.includeComments, false);
});

test('parseCliArgs rejects missing option values', () => {
  assert.throws(() => parseCliArgs(['--out-dir']), /Missing value/);
  assert.throws(() => parseCliArgs(['--format']), /Missing value/);
});
