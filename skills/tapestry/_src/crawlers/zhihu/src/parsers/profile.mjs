import { urlInfo, zhihuEntityState } from './common.mjs';

export function parseProfile(result) {
  const entities = zhihuEntityState(result);
  const info = urlInfo(result?.finalUrl || result?.url || '');
  const user = entities?.users?.[info.userToken || ''];
  if (!user) {
    return {
      kind: 'profile',
      ok: false,
      reason: 'user-not-found-in-initial-state',
      finalUrl: result?.finalUrl,
    };
  }

  return {
    kind: 'profile',
    ok: true,
    id: user.id,
    name: user.name,
    headline: user.headline || null,
    description: user.description || null,
    urlToken: user.urlToken || null,
    followerCount: user.followerCount ?? null,
    followingCount: user.followingCount ?? null,
    answerCount: user.answerCount ?? null,
    articlesCount: user.articlesCount ?? null,
    pinsCount: user.pinsCount ?? null,
    finalUrl: result.finalUrl,
  };
}
