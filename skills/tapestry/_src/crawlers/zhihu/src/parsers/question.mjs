import { urlInfo, zhihuEntityState } from './common.mjs';

export function parseQuestion(result) {
  const entities = zhihuEntityState(result);
  const info = urlInfo(result?.finalUrl || result?.url || '');
  const question = entities?.questions?.[info.questionId || ''];
  if (!question) {
    return {
      kind: 'question',
      ok: false,
      reason: 'question-not-found-in-initial-state',
      finalUrl: result?.finalUrl,
    };
  }

  const allAnswers = Object.values(entities?.answers || {});
  const relatedAnswers = allAnswers
    .filter((answer) => String(answer?.question?.id || answer?.question?.id) === String(question.id))
    .sort((a, b) => Number(b.voteupCount || 0) - Number(a.voteupCount || 0))
    .slice(0, 3)
    .map((answer) => ({
      id: answer.id,
      author: answer.author?.name || null,
      excerpt: answer.excerpt || null,
      voteupCount: answer.voteupCount ?? null,
      commentCount: answer.commentCount ?? null,
      createdTime: answer.createdTime ?? null,
      updatedTime: answer.updatedTime ?? null,
    }));

  return {
    kind: 'question',
    ok: true,
    id: question.id,
    title: question.title,
    excerpt: question.excerpt || null,
    answerCount: question.answerCount ?? null,
    followerCount: question.followerCount ?? null,
    visitCount: question.visitCount ?? null,
    commentCount: question.commentCount ?? null,
    topAnswers: relatedAnswers,
    comments: result?.comments || null,
    finalUrl: result.finalUrl,
  };
}
