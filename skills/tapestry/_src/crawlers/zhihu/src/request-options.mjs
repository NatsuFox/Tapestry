import { urlInfo } from './parsers/common.mjs';

export function inferRequestedKind(kind, body = {}) {
  if (kind !== 'auto') return kind;
  return urlInfo(body?.url || '').kind;
}

export function defaultIncludeComments(kind, body = {}) {
  if (typeof body?.includeComments === 'boolean') return body.includeComments;
  const requestedKind = inferRequestedKind(kind, body);
  return requestedKind === 'question' || requestedKind === 'answer';
}
