import process from 'node:process';
import { urlInfo } from '../src/parsers/common.mjs';

const baseUrl = process.env.ZHIHU_API_BASE_URL || 'http://127.0.0.1:8765';
const urls = process.argv.slice(2);

if (urls.length === 0) {
  console.error('Usage: node scripts/smoke.mjs <zhihu-url> [more-urls...]');
  process.exit(1);
}

function endpointFor(url) {
  const info = urlInfo(url);
  switch (info.kind) {
    case 'zhuanlan.article':
      return '/v1/column/article';
    case 'question':
      return '/v1/question';
    case 'answer':
      return '/v1/answer';
    case 'profile':
      return '/v1/profile';
    default:
      return '/v1/parse';
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

for (const url of urls) {
  const endpoint = endpointFor(url);
  const response = await fetch(`${baseUrl}${endpoint}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ url }),
  });

  const payload = await response.json();
  const parsed = payload.parsed || {};
  console.log(
    JSON.stringify(
      {
        url,
        endpoint,
        ok: payload.ok,
        requestedKind: payload.requestedKind ?? null,
        detectedKind: payload.detectedKind ?? parsed.kind ?? null,
        includeComments: payload.includeComments ?? null,
        summary: summarize(parsed),
      },
      null,
      2,
    ),
  );
}
