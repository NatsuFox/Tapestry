# zhihu-api

本地可复用的知乎抓取 API 骨架。

目标：
- 用真实浏览器自然跑过知乎前端 challenge
- 把通用浏览器链路与内容类型 parser 分离
- 先支持知乎专栏文章，后续可继续扩展到问题、回答、用户页等

## 启动

```bash
cd /root/Workspace/PROJECTS/powers/Tapestry/skills/tapestry/_src/crawlers/zhihu
npm install
node src/server.mjs

# 或者
zhihu-api
```

默认监听：`http://127.0.0.1:8765`

## CLI 入口

除了本地 HTTP API，现在也提供了一个直接可跑的 CLI：

```bash
zhihu-parse https://zhuanlan.zhihu.com/p/2014452522178334926
```

批量 URL + 输出目录示例：

```bash
zhihu-parse \
  --out-dir /tmp/zhihu-run \
  --save-text \
  --save-html \
  https://zhuanlan.zhihu.com/p/2014452522178334926 \
  https://www.zhihu.com/question/610072126/answer/2013215979509940714 \
  https://www.zhihu.com/people/cfeng2003
```

CLI 特点：
- 不依赖先手工启动 server，直接本地抓取并解析
- 自动根据 URL 判型，也可用 `--kind` 强制指定
- `question` / `answer` 默认抓评论；可用 `--no-comments` 关闭
- 支持 `--out-dir`、`--save-json`、`--save-html`、`--save-text`
- 支持 `--retries` / `--retry-delay-ms`
- 输出格式支持 `pretty` / `json` / `jsonl`

当前已支持的内容类型：
- 专栏文章 `zhuanlan.article`
- 问题页 `question`（默认附带完整评论树与回复关系）
- 单回答页 `answer`（默认附带完整评论树与回复关系）
- 用户主页 `profile`

评论抓取补充说明：
- `question` / `answer` 默认开启 `includeComments`
- 返回里会附带：`rootComments`、`flatComments`、`replyCommentId`、`replyRootCommentId`、`replyToAuthor`
- `complete=true` 代表：根评论分页已走到尾、每个 root 的子回复线程也补齐、且抓取过程中无错误
- 另外保留知乎接口原始计数校验：`totalCount`、`apiTotalMatchesFetched`、`apiTotalDelta`
- 实测某些页面存在“接口 `total_counts` 大于实际可枚举评论数”的现象，因此不要只拿 `totalCount` 判断抓取是否完整

## 健康检查

```bash
curl http://127.0.0.1:8765/health
```

## 通用抓取

```bash
curl -s http://127.0.0.1:8765/v1/fetch \
  -H 'content-type: application/json' \
  -d '{
    "url": "https://zhuanlan.zhihu.com/p/2014452522178334926",
    "includeText": true,
    "includeHtml": false,
    "outputDir": "/tmp/zhihu-run",
    "saveText": true,
    "saveHar": true,
    "saveJson": true
  }'
```

## 自动识别解析

`/v1/parse` 现在会先根据传入 URL 推断类型；如果 URL 是 `question` / `answer`，默认也会自动开启评论抓取（除非显式传 `"includeComments": false`）。

响应顶部会额外带上：
- `requestedKind`：根据请求路由 / 输入 URL 推断出来的目标类型
- `detectedKind`：实际抓取完成后，从最终 URL 判定出的类型
- `includeComments`：本次请求最终采用的评论抓取开关

```bash
curl -s http://127.0.0.1:8765/v1/parse \
  -H 'content-type: application/json' \
  -d '{
    "url": "https://zhuanlan.zhihu.com/p/2014452522178334926",
    "includeText": true,
    "saveText": true
  }'
```

回答页自动判型 + 默认抓评论示例：

```bash
curl -s http://127.0.0.1:8765/v1/parse \
  -H 'content-type: application/json' \
  -d '{
    "url": "https://www.zhihu.com/question/610072126/answer/2013215979509940714"
  }'
```

## 专栏文章解析

```bash
curl -s http://127.0.0.1:8765/v1/column/article \
  -H 'content-type: application/json' \
  -d '{
    "url": "https://zhuanlan.zhihu.com/p/2014452522178334926",
    "includeText": true,
    "outputDir": "/tmp/zhihu-column",
    "saveText": true,
    "saveHar": true
  }'
```

## 问题 / 回答 / 用户页解析

```bash
curl -s http://127.0.0.1:8765/v1/question \
  -H 'content-type: application/json' \
  -d '{"url":"https://www.zhihu.com/question/1986998840415520396"}'

curl -s http://127.0.0.1:8765/v1/answer \
  -H 'content-type: application/json' \
  -d '{"url":"https://www.zhihu.com/question/1986998840415520396/answer/1991952278236729989"}'

# 如需显式关闭评论抓取（question / answer 默认开启）
curl -s http://127.0.0.1:8765/v1/answer \
  -H 'content-type: application/json' \
  -d '{"url":"https://www.zhihu.com/question/1986998840415520396/answer/1991952278236729989","includeComments":false}'

curl -s http://127.0.0.1:8765/v1/profile \
  -H 'content-type: application/json' \
  -d '{"url":"https://www.zhihu.com/people/zhou-yuan"}'
```

## 设计说明

- `src/fetcher.mjs`
  - 负责通用浏览器 challenge 复现
  - 输出网络证据、cookie 名称、sessionStorage 键名、文本/HTML 等
- `src/parsers/common.mjs`
  - 提供 URL 识别与 `js-initialData` 提取
- `src/parsers/column-article.mjs`
  - 负责知乎专栏文章的结构化提取
- `src/parsers/question.mjs`
  - 负责知乎问题页的结构化提取（含完整评论树挂载）
- `src/parsers/answer.mjs`
  - 负责知乎单回答页的结构化提取（含完整评论树挂载）
- `src/parsers/profile.mjs`
  - 负责知乎用户主页的结构化提取
- `src/server.mjs`
  - 暴露 HTTP API，便于 agent 通过本地接口调用

## 快速回归 / smoke test

先启动服务：

```bash
zhihu-api
```

然后一次跑多个 URL：

```bash
cd /root/Workspace/PROJECTS/powers/Tapestry/skills/tapestry/_src/crawlers/zhihu
npm run smoke -- \
  https://zhuanlan.zhihu.com/p/2014452522178334926 \
  https://www.zhihu.com/question/610072126/answer/2013215979509940714 \
  https://www.zhihu.com/people/cfeng2003
```

还可以跑基础测试：

```bash
cd /root/Workspace/PROJECTS/powers/Tapestry/skills/tapestry/_src/crawlers/zhihu
npm test
```

CLI 帮助：

```bash
zhihu-parse --help
```

## 后续扩展建议

- 为 question / answer / profile 补更丰富的字段（例如回答列表、时间线、更多计数）
- 把 column parser 进一步切换到 HTML/JSON 主导而不是文本回退
- 加入更稳的 DOM 选择器解析，减少纯文本启发式依赖
- 如需对外分发，补一个正式 CLI 包装层（参数解析、批量输出目录、失败重试）
