import test from 'node:test';
import assert from 'node:assert/strict';
import { defaultIncludeComments, inferRequestedKind } from '../../src/request-options.mjs';

test('inferRequestedKind keeps explicit endpoint kinds', () => {
  assert.equal(inferRequestedKind('answer', { url: 'https://zhuanlan.zhihu.com/p/1' }), 'answer');
  assert.equal(inferRequestedKind('profile', { url: 'https://www.zhihu.com/question/1' }), 'profile');
});

test('inferRequestedKind infers auto endpoint kind from URL', () => {
  assert.equal(
    inferRequestedKind('auto', { url: 'https://www.zhihu.com/question/610072126/answer/2013215979509940714' }),
    'answer',
  );
  assert.equal(inferRequestedKind('auto', { url: 'https://www.zhihu.com/question/1986998840415520396' }), 'question');
  assert.equal(inferRequestedKind('auto', { url: 'https://www.zhihu.com/people/cfeng2003' }), 'profile');
});

test('defaultIncludeComments enables comments for auto question/answer URLs', () => {
  assert.equal(
    defaultIncludeComments('auto', { url: 'https://www.zhihu.com/question/610072126/answer/2013215979509940714' }),
    true,
  );
  assert.equal(
    defaultIncludeComments('auto', { url: 'https://www.zhihu.com/question/1986998840415520396' }),
    true,
  );
  assert.equal(defaultIncludeComments('auto', { url: 'https://zhuanlan.zhihu.com/p/2014452522178334926' }), false);
});

test('defaultIncludeComments respects explicit request override', () => {
  assert.equal(
    defaultIncludeComments('auto', {
      url: 'https://www.zhihu.com/question/610072126/answer/2013215979509940714',
      includeComments: false,
    }),
    false,
  );
  assert.equal(defaultIncludeComments('profile', { url: 'https://www.zhihu.com/people/cfeng2003', includeComments: true }), true);
});
