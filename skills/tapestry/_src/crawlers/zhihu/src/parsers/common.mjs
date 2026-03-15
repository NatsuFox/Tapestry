export function extractInitialData(html = '') {
  const match = html.match(/<script id="js-initialData" type="text\/json">([\s\S]*?)<\/script>/);
  if (!match) return null;
  try {
    return JSON.parse(match[1]);
  } catch {
    return null;
  }
}

export function cleanLines(text = '') {
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);
}

export function normalizeTitle(title = '') {
  return typeof title === 'string' ? title.replace(/ - 知乎$/, '') : title;
}

export function zhihuEntityState(result) {
  const html = result?.content?.html || '';
  const parsed = extractInitialData(html);
  return parsed?.initialState?.entities || null;
}

export function urlInfo(url = '') {
  try {
    const u = new URL(url);
    const path = u.pathname || '/';
    let kind = 'unknown';
    let articleId = null;
    let questionId = null;
    let answerId = null;
    let userToken = null;

    let m = path.match(/^\/p\/(\d+)/);
    if (m) {
      kind = 'zhuanlan.article';
      articleId = m[1];
    }

    m = path.match(/^\/question\/(\d+)(?:\/answer\/(\d+))?/);
    if (m) {
      questionId = m[1];
      answerId = m[2] || null;
      kind = answerId ? 'answer' : 'question';
    }

    m = path.match(/^\/people\/([^/?#]+)/);
    if (m) {
      userToken = m[1];
      kind = 'profile';
    }

    return { kind, articleId, questionId, answerId, userToken, pathname: path };
  } catch {
    return { kind: 'unknown', articleId: null, questionId: null, answerId: null, userToken: null, pathname: '' };
  }
}

export function detectResultKind(result) {
  const info = urlInfo(result?.finalUrl || result?.url || '');
  return info.kind;
}

function safeString(value) {
  return value == null ? null : String(value);
}

function safeNumber(value) {
  return typeof value === 'number' ? value : value == null ? null : Number(value);
}

function normalizeCommentAuthor(author) {
  if (!author || typeof author !== 'object') return null;
  return {
    id: safeString(author.id),
    name: author.name || null,
    urlToken: author.urlToken || author.url_token || null,
    headline: author.headline || null,
    avatarUrl: author.avatarUrl || author.avatar_url || null,
    isAnonymous: Boolean(author.isAnonymous || author.is_anonymous),
  };
}

function annotateRelationFields(comment, byId, fallbackRootId = null) {
  const replyToCommentId = safeString(comment.replyCommentId);
  const rootCommentId = safeString(comment.replyRootCommentId) || fallbackRootId || safeString(comment.id);
  const replyToComment = replyToCommentId ? byId.get(replyToCommentId) || null : null;

  return {
    ...comment,
    id: safeString(comment.id),
    replyCommentId: replyToCommentId,
    replyRootCommentId: rootCommentId,
    replyToCommentId,
    rootCommentId,
    replyToAuthor: replyToComment?.author
      ? {
          id: safeString(replyToComment.author.id),
          name: replyToComment.author.name || null,
          urlToken: replyToComment.author.urlToken || null,
        }
      : null,
  };
}

export function finalizeCommentCapture(bundle) {
  if (!bundle || typeof bundle !== 'object') return bundle;
  if (bundle.ok === false) return bundle;

  const inputRoots = Array.isArray(bundle.rootComments) ? bundle.rootComments : [];
  const flatSeed = [];
  const byId = new Map();

  const firstPassRoots = inputRoots.map((root) => {
    const rootComment = {
      ...root,
      id: safeString(root.id),
      isRoot: true,
      author: normalizeCommentAuthor(root.author),
      createdTime: safeNumber(root.createdTime),
      likeCount: safeNumber(root.likeCount),
      childCommentCount: safeNumber(root.childCommentCount) ?? 0,
      childComments: Array.isArray(root.childComments)
        ? root.childComments.map((child) => ({
            ...child,
            id: safeString(child.id),
            isRoot: false,
            author: normalizeCommentAuthor(child.author),
            createdTime: safeNumber(child.createdTime),
            likeCount: safeNumber(child.likeCount),
            childCommentCount: safeNumber(child.childCommentCount) ?? 0,
          }))
        : [],
    };

    flatSeed.push(rootComment);
    byId.set(rootComment.id, rootComment);
    for (const child of rootComment.childComments) {
      flatSeed.push(child);
      byId.set(child.id, child);
    }

    return rootComment;
  });

  const rootComments = firstPassRoots.map((root) => {
    const normalizedRoot = annotateRelationFields(root, byId, root.id);
    const childComments = root.childComments.map((child) => annotateRelationFields(child, byId, root.id));
    return {
      ...normalizedRoot,
      childComments,
      childCommentsFetched: childComments.length,
      childCommentsComplete: (normalizedRoot.childCommentCount ?? 0) <= childComments.length,
    };
  });

  const flatComments = [];
  for (const root of rootComments) {
    flatComments.push({ ...root, childComments: undefined });
    for (const child of root.childComments) {
      flatComments.push({ ...child });
    }
  }

  const childCommentCount = flatComments.filter((comment) => !comment.isRoot).length;
  const rootCommentCount = rootComments.length;
  const fetchedCount = rootCommentCount + childCommentCount;
  const totalCount = safeNumber(bundle.totalCount);
  const allChildThreadsComplete = rootComments.every(
    (root) => (root.childCommentCount ?? 0) <= (root.childCommentsFetched ?? 0),
  );
  const paginationComplete = Boolean(bundle.rootPaginationComplete);
  const fetchErrors = Array.isArray(bundle.errors) ? bundle.errors : [];
  const complete = paginationComplete && allChildThreadsComplete && fetchErrors.length === 0;

  return {
    ...bundle,
    totalCount,
    rootCommentCount,
    childCommentCount,
    fetchedCount,
    complete,
    paginationComplete,
    allChildThreadsComplete,
    apiTotalMatchesFetched: totalCount == null ? null : fetchedCount === totalCount,
    apiTotalDelta: totalCount == null ? null : totalCount - fetchedCount,
    rootComments,
    flatComments,
  };
}
