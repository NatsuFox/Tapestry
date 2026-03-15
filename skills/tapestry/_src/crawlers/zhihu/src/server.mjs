import http from 'node:http';
import { defaultServerConfig } from './config.mjs';
import { fetchZhihuPage } from './fetcher.mjs';
import { parseByKind, parseAuto } from './parsers/index.mjs';
import { detectResultKind } from './parsers/common.mjs';
import { defaultIncludeComments, inferRequestedKind } from './request-options.mjs';

function sendJson(res, status, data) {
  const body = JSON.stringify(data, null, 2);
  res.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'content-length': Buffer.byteLength(body),
  });
  res.end(body);
}

async function readJsonBody(req) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const raw = Buffer.concat(chunks).toString('utf8').trim();
  return raw ? JSON.parse(raw) : {};
}

function routeNotFound(res) {
  sendJson(res, 404, { ok: false, error: 'not-found' });
}

async function handleFetch(req, res) {
  const body = await readJsonBody(req);
  const result = await fetchZhihuPage(body);
  sendJson(res, 200, result);
}

async function handleParse(req, res, kind) {
  const body = await readJsonBody(req);
  const requestedKind = inferRequestedKind(kind, body);
  const shouldIncludeComments = defaultIncludeComments(kind, body);
  const result = await fetchZhihuPage({
    includeText: true,
    includeHtml: true,
    includeComments: shouldIncludeComments,
    ...body,
  });
  const detectedKind = detectResultKind(result);
  const parsed = kind === 'auto' ? parseAuto(result) : parseByKind(kind, result);
  sendJson(res, 200, {
    ok: result.ok && parsed.ok,
    requestedKind,
    detectedKind,
    includeComments: shouldIncludeComments,
    fetch: result,
    parsed,
  });
}

export async function createServer() {
  const config = defaultServerConfig();
  const server = http.createServer(async (req, res) => {
    try {
      const url = new URL(req.url || '/', 'http://127.0.0.1');
      if (req.method === 'GET' && url.pathname === '/health') {
        return sendJson(res, 200, {
          ok: true,
          service: 'zhihu-api',
          chromiumExecutable: config.chromiumExecutable,
        });
      }
      if (req.method === 'POST' && url.pathname === '/v1/fetch') {
        return await handleFetch(req, res);
      }
      if (req.method === 'POST' && url.pathname === '/v1/parse') {
        return await handleParse(req, res, 'auto');
      }
      if (req.method === 'POST' && url.pathname === '/v1/column/article') {
        return await handleParse(req, res, 'zhuanlan.article');
      }
      if (req.method === 'POST' && url.pathname === '/v1/question') {
        return await handleParse(req, res, 'question');
      }
      if (req.method === 'POST' && url.pathname === '/v1/answer') {
        return await handleParse(req, res, 'answer');
      }
      if (req.method === 'POST' && url.pathname === '/v1/profile') {
        return await handleParse(req, res, 'profile');
      }
      return routeNotFound(res);
    } catch (error) {
      return sendJson(res, 500, {
        ok: false,
        error: error instanceof Error ? error.message : String(error),
      });
    }
  });

  return { server, config };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const { server, config } = await createServer();
  server.listen(config.port, config.host, () => {
    console.log(
      JSON.stringify(
        {
          ok: true,
          service: 'zhihu-api',
          listen: `http://${config.host}:${config.port}`,
          chromiumExecutable: config.chromiumExecutable,
          endpoints: [
            '/health',
            '/v1/fetch',
            '/v1/parse',
            '/v1/column/article',
            '/v1/question',
            '/v1/answer',
            '/v1/profile'
          ],
        },
        null,
        2,
      ),
    );
  });
}
