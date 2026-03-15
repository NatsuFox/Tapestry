import { cleanLines, normalizeTitle, urlInfo, zhihuEntityState } from './common.mjs';

export function parseColumnArticle(result) {
  const entities = zhihuEntityState(result);
  const info = urlInfo(result?.finalUrl || result?.url || '');
  const article = entities?.articles?.[info.articleId || ''];
  if (article) {
    return {
      kind: 'zhuanlan.article',
      ok: true,
      title: article.title,
      author: article.author?.name || null,
      bio: article.author?.headline || article.author?.description || null,
      excerpt: article.excerpt || null,
      voteupCount: article.voteupCount ?? null,
      commentCount: article.commentCount ?? null,
      created: article.created ?? null,
      updated: article.updated ?? null,
      finalUrl: result.finalUrl,
    };
  }

  const text = result?.content?.text || '';
  const lines = cleanLines(text);
  if (lines.length === 0) {
    return {
      kind: 'zhuanlan.article',
      ok: false,
      reason: 'empty-text',
    };
  }

  const loginIndex = lines.indexOf('登录/注册');
  const title = loginIndex >= 0 && lines[loginIndex + 1] ? lines[loginIndex + 1] : normalizeTitle(result.title);
  const author = loginIndex >= 0 && lines[loginIndex + 4] ? lines[loginIndex + 4] : null;
  const bio = loginIndex >= 0 && lines[loginIndex + 5] ? lines[loginIndex + 5] : null;
  const likesLine = lines.find((line) => /人赞同了该文章/.test(line)) || null;
  const firstParagraphIndex = likesLine ? lines.indexOf(likesLine) + 1 : Math.min(lines.length, 8);
  const excerpt = lines.slice(firstParagraphIndex, firstParagraphIndex + 10).join('\n');

  return {
    kind: 'zhuanlan.article',
    ok: true,
    title,
    author,
    bio,
    likesLine,
    excerpt,
    finalUrl: result.finalUrl,
  };
}
