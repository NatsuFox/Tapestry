import { detectResultKind, urlInfo } from './common.mjs';
import { parseColumnArticle } from './column-article.mjs';
import { parseQuestion } from './question.mjs';
import { parseAnswer } from './answer.mjs';
import { parseProfile } from './profile.mjs';

export function parseByKind(kind, result) {
  switch (kind) {
    case 'zhuanlan.article':
      return parseColumnArticle(result);
    case 'question':
      return parseQuestion(result);
    case 'answer':
      return parseAnswer(result);
    case 'profile':
      return parseProfile(result);
    default:
      return {
        kind: 'unknown',
        ok: false,
        reason: 'unsupported-kind',
        detectedKind: detectResultKind(result),
        urlInfo: urlInfo(result?.finalUrl || result?.url || ''),
      };
  }
}

export function parseAuto(result) {
  return parseByKind(detectResultKind(result), result);
}
