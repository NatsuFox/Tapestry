# Tapestry Roadmap | 路线图

[中文](#中文) | [English](#english)

---

## 中文

本路线图概述了 Tapestry 的计划功能和改进。项目可能会根据社区反馈和优先级进行调整。

## 版本 1.0（当前开发中）

### 核心功能
- [x] 多平台爬虫框架
- [x] 知乎爬虫（逆向工程 API）
- [x] X/Twitter 爬虫（公开页面）
- [x] 小红书爬虫
- [x] 微博爬虫
- [x] Hacker News 爬虫
- [x] Reddit 爬虫
- [x] 通用 HTML 后备爬虫
- [x] 订阅源规范化系统
- [x] 知识库综合工作流
- [x] 可视化前端查看器
- [x] 测试基础设施
- [x] 双语文档

### 文档
- [x] 包含架构细节的 README
- [x] 贡献指南
- [x] 行为准则
- [x] 安全政策
- [x] Issue 模板
- [x] PR 模板
- [x] 完整的文档系统 (docs/)
- [x] 安装指南
- [x] 快速参考
- [x] 架构文档
- [x] 用户指南（基础使用、知识库、高级工作流）
- [x] 参考文档（平台、配置、故障排除、API）
- [x] 常见问题和术语表
- [ ] 🔴 包含真实用例的示例目录
- [ ] 🔴 快速入门指南（5分钟内完成首次捕获）
- [ ] 🟡 教程视频或动画 GIF
- [ ] 🟡 与类似工具的对比表
- [ ] 🟡 迁移指南（从其他工具和版本间迁移）
- [ ] 🟢 性能基准测试文档
- [ ] 🟡 集成指南（Obsidian、Notion、Roam Research）
- [ ] 🟢 文档贡献指南 (CONTRIBUTING_DOCS.md)
- [ ] 🟢 每个爬虫的文档（每个爬虫的 README）
- [ ] 🟢 可视化图表和流程图

### 质量与测试
- [x] 核心逻辑单元测试
- [ ] 集成测试
- [ ] 端到端测试
- [ ] 性能基准测试
- [ ] 代码覆盖率报告

---

## 版本 1.1（2026 年第二季度）

### 新爬虫
- [ ] Bilibili（视频平台）
- [ ] 豆瓣（评论和讨论）
- [ ] Medium（文章）
- [ ] Dev.to（开发者内容）
- [ ] Stack Overflow（问答）

### 增强功能
- [ ] 增量更新（重新爬取新评论）
- [ ] 批处理改进
- [ ] 更好的错误处理和重试逻辑
- [ ] 长时间操作的进度指示器
- [ ] 可配置的存储后端

### 知识库
- [ ] 全文搜索
- [ ] 标签系统
- [ ] 交叉引用检测
- [ ] 导出为多种格式（PDF、EPUB、HTML）
- [ ] 备份和恢复功能

### 文档改进
- [ ] 🔴 **示例目录**：包含示例输入/输出的真实用例
  - 研究文献综述工作流
  - 跨平台主题追踪
  - 专家关注和个人资料存档
  - 每周摘要自动化
- [ ] 🔴 **快速入门指南**：5分钟内从零到首次捕获
  - 最小化安装步骤
  - 单命令示例
  - 即时视觉反馈
- [ ] 🟡 **对比表**：与类似工具的详细对比
  - vs. 网页剪藏工具（Evernote、Notion、Pocket）
  - vs. 网页爬虫（Scrapy、BeautifulSoup）
  - vs. 书签管理器（Raindrop、Pinboard）
  - 功能矩阵和使用场景推荐
- [ ] 🟡 **集成指南**：与流行工具的分步集成
  - Obsidian 仓库设置和工作流
  - Notion 数据库导入
  - Roam Research 集成
  - 静态站点生成器（MkDocs、Hugo、Jekyll）
- [ ] 🟡 **迁移指南**：迁移到/从 Tapestry
  - 从浏览器书签导入
  - 从 Pocket/Raindrop 导入
  - 导出到其他格式
  - 版本升级指南
- [ ] 🟡 **教程视频/GIF**：可视化演示
  - 安装演练
  - 首次捕获演示
  - 知识库组织
  - 高级工作流
- [ ] 🟢 **性能基准测试**：记录的性能特征
  - 速度对比（HTTP vs 浏览器）
  - 内存使用概况
  - 批处理基准测试
  - 平台特定性能说明
- [ ] 🟢 **每个爬虫的文档**：每个爬虫实现的 README
  - 平台特定的怪癖
  - 选择器说明
  - 已知限制
  - 测试说明
- [ ] 🟢 **文档风格指南**：CONTRIBUTING_DOCS.md
  - 写作风格指南
  - Markdown 约定
  - 代码示例标准
  - 截图/图表指南

---

## 版本 1.2（2026 年第三季度）

### 高级爬取
- [ ] 认证爬取（经用户同意）
- [ ] 动态内容处理（JavaScript 重度网站）
- [ ] 媒体下载（图片、视频）
- [ ] Archive.org 集成
- [ ] Wayback Machine 后备

### AI 增强
- [ ] 自动主题分类
- [ ] 重复检测
- [ ] 内容摘要
- [ ] 情感分析
- [ ] 实体提取

### 前端改进
- [ ] 高级搜索界面
- [ ] 时间线视图
- [ ] 连接关系图可视化
- [ ] 暗色模式
- [ ] 移动响应式设计

---

## 版本 2.0（2026 年第四季度）

### 协作功能
- [ ] 多用户支持
- [ ] 共享知识库
- [ ] 注释和高亮
- [ ] 评论和讨论
- [ ] 知识库版本控制

### 集成
- [ ] 浏览器扩展
- [ ] 移动应用
- [ ] 第三方工具 API
- [ ] Obsidian 插件
- [ ] Notion 集成

### 性能
- [ ] 分布式爬取
- [ ] 缓存层
- [ ] 数据库后端选项
- [ ] 增量索引
- [ ] 并行处理

---

## 未来考虑

### 研究与探索
- [ ] 内容质量评分的机器学习
- [ ] 自动事实核查
- [ ] 多语言支持
- [ ] 音频/视频转录
- [ ] 知识图谱构建

### 平台扩展
- [ ] 国际平台（非中文）
- [ ] 学术平台（arXiv、ResearchGate）
- [ ] 新闻聚合器
- [ ] 播客平台
- [ ] 新闻通讯存档

### 企业功能
- [ ] 自托管部署
- [ ] SSO 集成
- [ ] 审计日志
- [ ] 合规工具
- [ ] 高级权限

---

## 如何为路线图做贡献

我们欢迎社区对路线图的意见！你可以这样帮助：

1. **为功能投票**：在 Issues 中对现有功能请求发表评论
2. **建议新功能**：创建功能请求 issue
3. **实现功能**：从路线图中选择一项并提交 PR
4. **提供反馈**：分享你的使用场景和痛点

---

## 优先级

- 🔴 **高优先级**：核心功能的关键项
- 🟡 **中优先级**：重要但不阻塞
- 🟢 **低优先级**：锦上添花，社区驱动

---

## 发布计划

- **次要版本**（1.x）：每 2-3 个月
- **补丁版本**（1.x.y）：根据需要修复 bug
- **主要版本**（x.0）：每年或需要破坏性变更时

---

## 更新日志

详细的发布说明请参见 [CHANGELOG.md](CHANGELOG.md)。

---

## English

This roadmap outlines the planned features and improvements for Tapestry. Items are subject to change based on community feedback and priorities.

## Version 1.0 (Current Development)

### Core Features
- [x] Multi-platform crawler framework
- [x] Zhihu crawler (reverse-engineered API)
- [x] X/Twitter crawler (public pages)
- [x] Xiaohongshu crawler
- [x] Weibo crawler
- [x] Hacker News crawler
- [x] Reddit crawler
- [x] Generic HTML fallback crawler
- [x] Feed normalization system
- [x] Knowledge base synthesis workflow
- [x] Visual frontend viewer
- [x] Test infrastructure
- [x] Bilingual documentation

### Documentation
- [x] README with architecture details
- [x] Contributing guide
- [x] Code of conduct
- [x] Security policy
- [x] Issue templates
- [x] PR template
- [x] Comprehensive documentation system (docs/)
- [x] Installation guide
- [x] Quick reference
- [x] Architecture documentation
- [x] User guides (basic usage, knowledge base, advanced workflows)
- [x] Reference documentation (platforms, configuration, troubleshooting, API)
- [x] FAQ and Glossary
- [ ] 🔴 Examples directory with real-world use cases
- [ ] 🔴 Quick Start guide (zero to first capture in 5 minutes)
- [ ] 🟡 Tutorial videos or animated GIFs
- [ ] 🟡 Comparison table with similar tools
- [ ] 🟡 Migration guide (from other tools and between versions)
- [ ] 🟢 Performance benchmarks documentation
- [ ] 🟡 Integration guides (Obsidian, Notion, Roam Research)
- [ ] 🟢 Documentation contribution guide (CONTRIBUTING_DOCS.md)
- [ ] 🟢 Per-crawler documentation (README for each crawler)
- [ ] 🟢 Visual diagrams and flowcharts

### Quality & Testing
- [x] Unit tests for core logic
- [ ] Integration tests
- [ ] End-to-end tests
- [ ] Performance benchmarks
- [ ] Code coverage reports

---

## Version 1.1 (Q2 2026)

### New Crawlers
- [ ] Bilibili (video platform)
- [ ] Douban (reviews and discussions)
- [ ] Medium (articles)
- [ ] Dev.to (developer content)
- [ ] Stack Overflow (Q&A)

### Enhanced Features
- [ ] Incremental updates (re-crawl for new comments)
- [ ] Batch processing improvements
- [ ] Better error handling and retry logic
- [ ] Progress indicators for long operations
- [ ] Configurable storage backends

### Knowledge Base
- [ ] Full-text search
- [ ] Tag system
- [ ] Cross-reference detection
- [ ] Export to various formats (PDF, EPUB, HTML)
- [ ] Backup and restore functionality

### Documentation Improvements
- [ ] 🔴 **Examples Directory**: Real-world use cases with sample inputs/outputs
  - Research literature review workflow
  - Topic tracking across platforms
  - Expert following and profile archival
  - Weekly digest automation
- [ ] 🔴 **Quick Start Guide**: Get from zero to first capture in 5 minutes
  - Minimal installation steps
  - Single command examples
  - Immediate visual feedback
- [ ] 🟡 **Comparison Table**: Detailed comparison with similar tools
  - vs. Web clippers (Evernote, Notion, Pocket)
  - vs. Web scrapers (Scrapy, BeautifulSoup)
  - vs. Bookmark managers (Raindrop, Pinboard)
  - Feature matrix and use case recommendations
- [ ] 🟡 **Integration Guides**: Step-by-step integration with popular tools
  - Obsidian vault setup and workflow
  - Notion database import
  - Roam Research integration
  - Static site generators (MkDocs, Hugo, Jekyll)
- [ ] 🟡 **Migration Guide**: Moving to/from Tapestry
  - Importing from browser bookmarks
  - Importing from Pocket/Raindrop
  - Exporting to other formats
  - Version upgrade guides
- [ ] 🟡 **Tutorial Videos/GIFs**: Visual demonstrations
  - Installation walkthrough
  - First capture demo
  - Knowledge base organization
  - Advanced workflows
- [ ] 🟢 **Performance Benchmarks**: Documented performance characteristics
  - Speed comparisons (HTTP vs browser)
  - Memory usage profiles
  - Batch processing benchmarks
  - Platform-specific performance notes
- [ ] 🟢 **Per-Crawler Documentation**: README for each crawler implementation
  - Platform-specific quirks
  - Selector explanations
  - Known limitations
  - Testing instructions
- [ ] 🟢 **Documentation Style Guide**: CONTRIBUTING_DOCS.md
  - Writing style guidelines
  - Markdown conventions
  - Code example standards
  - Screenshot/diagram guidelines

---

## Version 1.2 (Q3 2026)

### Advanced Crawling
- [ ] Authenticated crawling (with user consent)
- [ ] Dynamic content handling (JavaScript-heavy sites)
- [ ] Media download (images, videos)
- [ ] Archive.org integration
- [ ] Wayback Machine fallback

### AI Enhancements
- [ ] Automatic topic classification
- [ ] Duplicate detection
- [ ] Content summarization
- [ ] Sentiment analysis
- [ ] Entity extraction

### Frontend Improvements
- [ ] Advanced search interface
- [ ] Timeline view
- [ ] Graph visualization of connections
- [ ] Dark mode
- [ ] Mobile-responsive design

---

## Version 2.0 (Q4 2026)

### Collaboration Features
- [ ] Multi-user support
- [ ] Shared knowledge bases
- [ ] Annotation and highlighting
- [ ] Comments and discussions
- [ ] Version control for knowledge base

### Integration
- [ ] Browser extension
- [ ] Mobile app
- [ ] API for third-party tools
- [ ] Obsidian plugin
- [ ] Notion integration

### Performance
- [ ] Distributed crawling
- [ ] Caching layer
- [ ] Database backend option
- [ ] Incremental indexing
- [ ] Parallel processing

---

## Future Considerations

### Research & Exploration
- [ ] Machine learning for content quality scoring
- [ ] Automatic fact-checking
- [ ] Multi-language support
- [ ] Audio/video transcription
- [ ] Knowledge graph construction

### Platform Expansion
- [ ] International platforms (non-Chinese)
- [ ] Academic platforms (arXiv, ResearchGate)
- [ ] News aggregators
- [ ] Podcast platforms
- [ ] Newsletter archives

### Enterprise Features
- [ ] Self-hosted deployment
- [ ] SSO integration
- [ ] Audit logging
- [ ] Compliance tools
- [ ] Advanced permissions

---

## How to Contribute to the Roadmap

We welcome community input on the roadmap! Here's how you can help:

1. **Vote on Features**: Comment on existing feature requests in Issues
2. **Suggest New Features**: Open a feature request issue
3. **Implement Features**: Pick an item from the roadmap and submit a PR
4. **Provide Feedback**: Share your use cases and pain points

---

## Priority Levels

- 🔴 **High Priority**: Critical for core functionality
- 🟡 **Medium Priority**: Important but not blocking
- 🟢 **Low Priority**: Nice to have, community-driven

---

## Release Schedule

- **Minor versions** (1.x): Every 2-3 months
- **Patch versions** (1.x.y): As needed for bug fixes
- **Major versions** (x.0): Annually or when breaking changes are needed

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed release notes.
