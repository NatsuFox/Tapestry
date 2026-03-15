import { cleanLines, urlInfo, zhihuEntityState } from './common.mjs';

export function parseAnswer(result) {
  const entities = zhihuEntityState(result);
  const info = urlInfo(result?.finalUrl || result?.url || '');
  const answer = entities?.answers?.[info.answerId || ''];
  if (!answer) {
    return {
      kind: 'answer',
      ok: false,
      reason: 'answer-not-found-in-initial-state',
      finalUrl: result?.finalUrl,
    };
  }

  const lines = cleanLines(result?.content?.text || '');
  const publishLine = lines.find((line) => /^发布于 /.test(line)) || null;

  return {
    kind: 'answer',
    ok: true,
    id: answer.id,
    questionId: answer.question?.id || null,
    questionTitle: answer.question?.title || null,
    author: answer.author?.name || null,
    authorHeadline: answer.author?.headline || answer.author?.badgeV2?.title || null,
    excerpt: answer.excerpt || null,
    voteupCount: answer.voteupCount ?? null,
    commentCount: answer.commentCount ?? null,
    createdTime: answer.createdTime ?? null,
    updatedTime: answer.updatedTime ?? null,
    publishLine,
    comments: result?.comments || null,
    finalUrl: result.finalUrl,
  };
}
