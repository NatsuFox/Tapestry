import fs from 'node:fs/promises';
import path from 'node:path';
import { chromium } from 'playwright-core';
import { resolveChromiumExecutable } from './config.mjs';
import { finalizeCommentCapture, urlInfo } from './parsers/common.mjs';

const DEFAULT_USER_AGENT =
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36';

function onlyZhihuNetworkEvent(url) {
  return url.includes('zhihu.com') || url.includes('static.zhihu.com') || url.startsWith('blob:https://zhuanlan.zhihu.com/');
}

function summarizeCookies(cookies, includeValues = false) {
  return cookies.map((cookie) => ({
    name: cookie.name,
    domain: cookie.domain,
    path: cookie.path,
    sameSite: cookie.sameSite,
    secure: cookie.secure,
    httpOnly: cookie.httpOnly,
    expires: cookie.expires,
    ...(includeValues ? { value: cookie.value } : {}),
  }));
}

async function ensureOutputDir(outputDir) {
  if (!outputDir) return null;
  await fs.mkdir(outputDir, { recursive: true });
  return outputDir;
}

async function maybeWriteFile(filePath, content) {
  if (!filePath) return;
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, content, 'utf8');
}

function detectChallengeReload(network, finalUrl) {
  const targetUrl = finalUrl || '';
  let saw403 = false;
  let sawChallengeScript = false;
  let sawReload200 = false;

  for (const event of network) {
    if (event.type === 'response' && event.url === targetUrl && event.status === 403) saw403 = true;
    if (event.url?.includes('static.zhihu.com/zse-ck/')) sawChallengeScript = true;
    if (event.type === 'response' && event.url === targetUrl && event.status === 200) sawReload200 = true;
  }

  return saw403 && sawChallengeScript && sawReload200;
}

function detectPageSignals(html, bodyText = '') {
  return {
    hasArticle: html.includes('<article'),
    hasPostMain: html.includes('Post-Main'),
    hasQuestionPage: html.includes('QuestionHeader-title') || html.includes('Question-main'),
    hasAnswerPage: html.includes('QuestionAnswer-content') || html.includes('AnswerItem'),
    hasProfilePage: html.includes('ProfileHeader-main') || html.includes('ProfileMain'),
    hasInitialData: html.includes('id="js-initialData"'),
    hasMeaningfulText: bodyText.trim().length > 120,
  };
}

async function captureZhihuComments(page, pageUrl, options = {}) {
  const info = urlInfo(pageUrl || '');
  if (!['question', 'answer'].includes(info.kind)) return null;

  const resourceType = info.kind;
  const resourceId = info.kind === 'question' ? info.questionId : info.answerId;
  if (!resourceId) return null;

  const commentBundle = await page.evaluate(
    async ({ resourceType, resourceId, rootLimit, childLimit, orderBy, childOrderBy, maxRootPages, maxChildPagesPerRoot }) => {
      const toText = (value = '') => {
        const html = String(value || '');
        const prepared = html
          .replace(/<br\s*\/?>/gi, '\n')
          .replace(/<\/(p|div|li|blockquote|h\d)>/gi, '\n');
        const div = document.createElement('div');
        div.innerHTML = prepared;
        return (div.textContent || '')
          .replace(/\u00a0/g, ' ')
          .replace(/\r/g, '')
          .split('\n')
          .map((line) => line.trim())
          .filter(Boolean)
          .join('\n');
      };

      const normalizeAuthor = (author) => {
        if (!author || typeof author !== 'object') return null;
        return {
          id: author.id == null ? null : String(author.id),
          name: author.name || null,
          urlToken: author.url_token || null,
          headline: author.headline || null,
          avatarUrl: author.avatar_url || null,
          isAnonymous: Boolean(author.is_anonymous),
        };
      };

      const normalizeComment = (comment) => ({
        id: comment?.id == null ? null : String(comment.id),
        type: comment?.type || 'comment',
        resourceType: comment?.resource_type || null,
        contentHtml: comment?.content ?? null,
        contentText: toText(comment?.content ?? ''),
        createdTime: typeof comment?.created_time === 'number' ? comment.created_time : null,
        likeCount: typeof comment?.like_count === 'number' ? comment.like_count : null,
        replyCommentId:
          comment?.reply_comment_id && String(comment.reply_comment_id) !== '0'
            ? String(comment.reply_comment_id)
            : null,
        replyRootCommentId:
          comment?.reply_root_comment_id && String(comment.reply_root_comment_id) !== '0'
            ? String(comment.reply_root_comment_id)
            : null,
        childCommentCount: typeof comment?.child_comment_count === 'number' ? comment.child_comment_count : 0,
        isHot: Boolean(comment?.hot),
        isTop: Boolean(comment?.top),
        ipLocation:
          Array.isArray(comment?.comment_tag) && comment.comment_tag.find((tag) => tag?.type === 'ip_info')?.text
            ? comment.comment_tag.find((tag) => tag?.type === 'ip_info')?.text
            : null,
        labels: Array.isArray(comment?.comment_tag)
          ? comment.comment_tag.map((tag) => ({ type: tag?.type || null, text: tag?.text || null }))
          : [],
        author: normalizeAuthor(comment?.author),
      });

      const mergeComments = (comments = []) => {
        const seen = new Set();
        const merged = [];
        for (const comment of comments) {
          const id = comment?.id == null ? null : String(comment.id);
          if (!id || seen.has(id)) continue;
          seen.add(id);
          merged.push(comment);
        }
        merged.sort((a, b) => Number(a?.createdTime || 0) - Number(b?.createdTime || 0));
        return merged;
      };

      const fetchJson = async (targetUrl) => {
        const response = await fetch(targetUrl, {
          credentials: 'include',
          headers: {
            Accept: 'application/json, text/plain, */*',
            'X-Requested-With': 'fetch',
          },
        });
        const text = await response.text();
        let json = null;
        try {
          json = text ? JSON.parse(text) : null;
        } catch {
          json = null;
        }
        if (!response.ok) {
          throw new Error(`HTTP ${response.status} for ${targetUrl}: ${text.slice(0, 240)}`);
        }
        if (!json || typeof json !== 'object') {
          throw new Error(`Invalid JSON for ${targetUrl}`);
        }
        return json;
      };

      const resourcePlural = resourceType === 'question' ? 'questions' : 'answers';
      const rootUrl = (offset = '') => {
        const search = new URLSearchParams();
        search.set('order_by', orderBy);
        search.set('limit', String(rootLimit));
        search.set('offset', offset || '');
        return `https://www.zhihu.com/api/v4/comment_v5/${resourcePlural}/${resourceId}/root_comment?${search.toString()}`;
      };
      const childUrl = (rootCommentId, offset = '') => {
        const search = new URLSearchParams();
        search.set('order_by', childOrderBy);
        search.set('limit', String(childLimit));
        search.set('offset', offset || '');
        return `https://www.zhihu.com/api/v4/comment_v5/comment/${rootCommentId}/child_comment?${search.toString()}`;
      };

      const rootComments = [];
      const errors = [];
      let totalCount = null;
      let rootPagesFetched = 0;
      let childPagesFetched = 0;
      let childThreadsFetched = 0;
      let rootIsEnd = true;
      let nextRootUrl = rootUrl('');

      for (let pageIndex = 0; pageIndex < maxRootPages && nextRootUrl; pageIndex += 1) {
        const requestUrl = nextRootUrl;
        const payload = await fetchJson(requestUrl);
        rootPagesFetched += 1;
        rootIsEnd = Boolean(payload?.paging?.is_end);
        if (typeof payload?.counts?.total_counts === 'number') totalCount = payload.counts.total_counts;
        const pageComments = Array.isArray(payload?.data) ? payload.data : [];

        for (const rawRoot of pageComments) {
          const embeddedChildren = Array.isArray(rawRoot?.child_comments)
            ? rawRoot.child_comments.map(normalizeComment)
            : [];
          let childComments = embeddedChildren;
          const wantedChildCount = typeof rawRoot?.child_comment_count === 'number' ? rawRoot.child_comment_count : 0;

          if (wantedChildCount > embeddedChildren.length) {
            childThreadsFetched += 1;
            try {
              let nextChildUrl = childUrl(rawRoot.id, '');
              const fetchedChildren = [];
              for (let childPageIndex = 0; childPageIndex < maxChildPagesPerRoot && nextChildUrl; childPageIndex += 1) {
                const childRequestUrl = nextChildUrl;
                const childPayload = await fetchJson(childRequestUrl);
                childPagesFetched += 1;
                const childPageComments = Array.isArray(childPayload?.data)
                  ? childPayload.data.map(normalizeComment)
                  : [];
                fetchedChildren.push(...childPageComments);
                if (childPayload?.paging?.is_end) break;
                nextChildUrl = childPayload?.paging?.next || null;
                if (!nextChildUrl || nextChildUrl === childRequestUrl) break;
              }
              childComments = mergeComments([...embeddedChildren, ...fetchedChildren]);
            } catch (error) {
              errors.push({
                stage: 'child-comment-fetch',
                rootCommentId: String(rawRoot.id),
                error: String(error),
              });
            }
          }

          rootComments.push({
            ...normalizeComment(rawRoot),
            childComments: mergeComments(childComments),
          });
        }

        if (payload?.paging?.is_end) break;
        nextRootUrl = payload?.paging?.next || null;
        if (!nextRootUrl || nextRootUrl === requestUrl) break;
      }

      return {
        ok: true,
        resourceType,
        resourceId: String(resourceId),
        orderBy,
        childOrderBy,
        totalCount,
        rootPagesFetched,
        childPagesFetched,
        childThreadsFetched,
        rootPaginationComplete: rootIsEnd,
        rootComments,
        errors,
      };
    },
    {
      resourceType,
      resourceId,
      rootLimit: options.rootLimit ?? 20,
      childLimit: options.childLimit ?? 20,
      orderBy: options.orderBy ?? 'score',
      childOrderBy: options.childOrderBy ?? 'ts',
      maxRootPages: options.maxRootPages ?? 200,
      maxChildPagesPerRoot: options.maxChildPagesPerRoot ?? 200,
    },
  );

  return finalizeCommentCapture(commentBundle);
}

export async function fetchZhihuPage(options = {}) {
  const {
    url,
    timeoutMs = 45_000,
    waitAfterLoadMs = 4_000,
    locale = 'en-US',
    userAgent = DEFAULT_USER_AGENT,
    viewport = { width: 1280, height: 800 },
    outputDir,
    saveHtml = false,
    saveText = false,
    saveJson = false,
    saveHar = false,
    includeHtml = false,
    includeText = true,
    includeComments = false,
    includeCookieValues = false,
    chromiumExecutable = resolveChromiumExecutable(),
  } = options;

  if (!url || typeof url !== 'string') {
    throw new Error('fetchZhihuPage requires a url string');
  }

  const outDir = await ensureOutputDir(outputDir);
  const recordHarPath = outDir && saveHar ? path.join(outDir, 'network.har') : undefined;

  const browser = await chromium.launch({
    executablePath: chromiumExecutable,
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-blink-features=AutomationControlled',
      `--lang=${locale},${locale.split('-')[0]};q=0.9`,
      `--window-size=${viewport.width},${viewport.height}`,
    ],
  });

  const context = await browser.newContext({
    userAgent,
    locale,
    viewport,
    recordHar: recordHarPath ? { path: recordHarPath, mode: 'minimal' } : undefined,
    extraHTTPHeaders: {
      'Accept-Language': `${locale},${locale.split('-')[0]};q=0.9`,
      'Cache-Control': 'no-cache',
      Pragma: 'no-cache',
    },
  });

  const page = await context.newPage();
  const network = [];

  page.on('request', (request) => {
    const requestUrl = request.url();
    if (!onlyZhihuNetworkEvent(requestUrl)) return;
    network.push({
      type: 'request',
      method: request.method(),
      url: requestUrl,
      resource: request.resourceType(),
    });
  });

  page.on('response', async (response) => {
    const responseUrl = response.url();
    if (!onlyZhihuNetworkEvent(responseUrl)) return;
    network.push({
      type: 'response',
      status: response.status(),
      url: responseUrl,
      contentType: response.headers()['content-type'] || '',
    });
  });

  let gotoError = null;
  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: timeoutMs });
  } catch (error) {
    gotoError = String(error);
  }
  await page.waitForTimeout(waitAfterLoadMs);

  const html = await page.content();
  const bodyText = await page.evaluate(() => (document.body ? document.body.innerText : ''));
  const title = await page.title();
  const finalUrl = page.url();
  const cookies = await context.cookies();
  const browserState = await page.evaluate(() => {
    const session = {};
    try {
      for (let i = 0; i < sessionStorage.length; i += 1) {
        const key = sessionStorage.key(i);
        session[key] = sessionStorage.getItem(key);
      }
    } catch (error) {
      session.__error = String(error);
    }
    return {
      href: location.href,
      title: document.title,
      webdriver: navigator.webdriver,
      userAgent: navigator.userAgent,
      language: navigator.language,
      platform: navigator.platform,
      cookie: document.cookie,
      session,
    };
  });
  const signals = detectPageSignals(html, bodyText);
  const hasZseMeta = html.includes('zh-zse-ck');
  const cookieNames = cookies.map((cookie) => cookie.name);
  const sessionStorageKeys = Object.keys(browserState.session || {});
  const challengeReloadDetected = detectChallengeReload(network, finalUrl);
  const challengeStateDetected =
    cookieNames.includes('__zse_ck') || sessionStorageKeys.includes('zap:zse_ck_referrer');
  const ok =
    !gotoError &&
    signals.hasInitialData &&
    (signals.hasArticle ||
      signals.hasQuestionPage ||
      signals.hasAnswerPage ||
      signals.hasProfilePage ||
      signals.hasMeaningfulText);

  let comments = null;
  if (ok && includeComments) {
    try {
      comments = await captureZhihuComments(page, finalUrl, options.comments || {});
    } catch (error) {
      comments = {
        ok: false,
        error: error instanceof Error ? error.message : String(error),
      };
    }
  }

  if (outDir) {
    if (saveHtml) await maybeWriteFile(path.join(outDir, 'page.html'), html);
    if (saveText) await maybeWriteFile(path.join(outDir, 'page.txt'), bodyText);
  }

  const result = {
    ok,
    url,
    finalUrl,
    title,
    gotoError,
    evidence: {
      network,
      cookieNames,
      sessionStorageKeys,
      webdriver: browserState.webdriver,
      ...signals,
      hasZseMeta,
      challengeReloadDetected,
      challengeStateDetected,
    },
    cookies: summarizeCookies(cookies, includeCookieValues),
    browserState: {
      href: browserState.href,
      title: browserState.title,
      webdriver: browserState.webdriver,
      userAgent: browserState.userAgent,
      language: browserState.language,
      platform: browserState.platform,
      session: browserState.session,
    },
    content: {
      ...(includeHtml ? { html } : {}),
      ...(includeText ? { text: bodyText } : {}),
    },
    ...(includeComments ? { comments } : {}),
    files: outDir
      ? {
          ...(saveHtml ? { html: path.join(outDir, 'page.html') } : {}),
          ...(saveText ? { text: path.join(outDir, 'page.txt') } : {}),
          ...(saveHar ? { har: path.join(outDir, 'network.har') } : {}),
        }
      : {},
  };

  if (outDir && saveJson) {
    await maybeWriteFile(path.join(outDir, 'result.json'), JSON.stringify(result, null, 2));
  }

  await browser.close();
  return result;
}
