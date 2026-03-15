import test from 'node:test';
import assert from 'node:assert/strict';
import { urlInfo } from '../../src/parsers/common.mjs';

test('urlInfo detects zhuanlan article URLs', () => {
  assert.deepEqual(urlInfo('https://zhuanlan.zhihu.com/p/2014452522178334926'), {
    kind: 'zhuanlan.article',
    articleId: '2014452522178334926',
    questionId: null,
    answerId: null,
    userToken: null,
    pathname: '/p/2014452522178334926',
  });
});

test('urlInfo detects answer URLs', () => {
  assert.deepEqual(urlInfo('https://www.zhihu.com/question/610072126/answer/2013215979509940714'), {
    kind: 'answer',
    articleId: null,
    questionId: '610072126',
    answerId: '2013215979509940714',
    userToken: null,
    pathname: '/question/610072126/answer/2013215979509940714',
  });
});

test('urlInfo detects profile URLs', () => {
  assert.deepEqual(urlInfo('https://www.zhihu.com/people/cfeng2003'), {
    kind: 'profile',
    articleId: null,
    questionId: null,
    answerId: null,
    userToken: 'cfeng2003',
    pathname: '/people/cfeng2003',
  });
});
