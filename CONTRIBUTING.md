# 贡献指南 | Contributing Guide

[中文](#中文) | [English](#english)

---

## 中文

感谢你考虑为 Tapestry 做出贡献！我们欢迎所有形式的贡献，包括但不限于：

- 🐛 Bug 报告和修复
- ✨ 新功能和增强
- 📝 文档改进
- 🧪 测试覆盖
- 🌐 新平台爬虫
- 💡 使用反馈和建议

### 开始之前

1. **搜索现有 Issues**：在创建新 issue 之前，请先搜索是否已有相关讨论
2. **阅读文档**：确保你熟悉项目的架构和设计理念
3. **小步快跑**：从小的改进开始，逐步熟悉项目

### 开发流程

#### 1. Fork 和克隆

```bash
# Fork 仓库到你的账号
# 然后克隆你的 fork
git clone https://github.com/your-username/Tapestry.git
cd Tapestry

# 添加上游仓库
git remote add upstream https://github.com/original-owner/Tapestry.git
```

#### 2. 创建分支

```bash
# 从 main 分支创建新的功能分支
git checkout -b feature/your-feature-name

# 或者修复分支
git checkout -b fix/issue-description
```

#### 3. 开发和测试

```bash
# 安装到 Agent 框架进行测试（使用符号链接便于开发）
ln -s "$(pwd)/skills/tapestry" ~/.claude/skills/tapestry

# 或直接复制
cp -r skills/tapestry ~/.claude/skills/

# 运行测试
cd skills/tapestry/_tests
pytest -v

# 运行特定测试
pytest test_ingest.py -v
```

#### 4. 提交变更

遵循约定式提交（Conventional Commits）规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型（type）**：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构（既不是新功能也不是修复）
- `test`: 添加或修改测试
- `chore`: 构建过程或辅助工具的变动

**示例**：
```bash
git commit -m "feat(crawlers): add Bilibili video crawler

- Implement video metadata extraction
- Support comment tree parsing
- Add tests for Bilibili crawler

Closes #123"
```

#### 5. 推送和创建 PR

```bash
# 推送到你的 fork
git push origin feature/your-feature-name

# 在 GitHub 上创建 Pull Request
```

### PR 检查清单

在提交 PR 之前，请确保：

- [ ] 代码遵循项目现有的风格
- [ ] 添加了必要的类型注解和文档字符串
- [ ] 所有测试通过（`pytest`）
- [ ] 更新了相关文档
- [ ] 提交信息清晰且遵循约定式提交规范
- [ ] PR 描述清楚说明了变更的动机和内容

### PR 模板

创建 PR 时，请包含以下信息：

```markdown
## 变更类型
- [ ] 新功能
- [ ] Bug 修复
- [ ] 文档更新
- [ ] 性能优化
- [ ] 代码重构

## 变更描述
<!-- 简要描述这个 PR 做了什么 -->

## 动机和背景
<!-- 为什么需要这个变更？解决了什么问题？ -->

## 测试
<!-- 如何验证这个变更？提供测试步骤 -->
1.
2.
3.

## 相关 Issue
<!-- 关联的 issue 编号，如 Closes #123 -->

## 截图（如适用）
<!-- 如果是 UI 变更，请提供截图 -->

## 检查清单
- [ ] 代码遵循项目风格指南
- [ ] 添加了必要的测试
- [ ] 所有测试通过
- [ ] 更新了相关文档
- [ ] 提交信息清晰明确
```

### 贡献领域

#### 🕷️ 添加新平台爬虫

1. 在 `skills/tapestry/_src/crawlers/` 创建新目录
2. 实现爬虫接口：
   ```python
   from _src.registry import CrawlerDefinition

   CRAWLER = CrawlerDefinition(
       id="platform_name",
       title="Platform Name",
       domains=["platform.com"],
       url_patterns=[r"pattern"],
       handler=crawl_platform
   )
   ```
3. 在 `_src/registry.py` 中注册
4. 添加 Feed 规范到 `skills/tapestry/feed/_specs/`
5. 编写测试

#### 📝 改进订阅源规范

1. 编辑 `skills/tapestry/feed/_specs/` 中的规范文件
2. 确保与 `_shared-standard.md` 保持一致
3. 测试规范在实际内容上的表现

#### 🎨 增强前端界面

1. 修改 `skills/tapestry/display/_ui/` 中的前端资源
2. 确保响应式设计
3. 测试不同浏览器的兼容性

#### 📚 完善知识库治理

1. 优化 `skills/tapestry/_kb_rules/` 中的规则
2. 改进主题分类逻辑
3. 提升知识库的可维护性

### 代码风格

- 使用 Python 3.10+ 特性
- 遵循 PEP 8 风格指南
- 使用类型注解
- 编写清晰的文档字符串
- 保持函数简洁（单一职责）

### 测试指南

```bash
# 运行所有测试
cd skills/tapestry/_tests
pytest

# 运行特定测试文件
pytest test_ingest.py

# 运行特定测试函数
pytest test_ingest.py::test_function_name

# 查看覆盖率
pytest --cov=_src --cov-report=html
```

### 文档规范

- 所有公共函数和类都应有文档字符串
- 使用 Google 风格的文档字符串
- 示例：
  ```python
  def crawl_platform(url: str) -> CrawlerProduct:
      """Crawl content from the platform.

      Args:
          url: The URL to crawl

      Returns:
          CrawlerProduct containing captured data

      Raises:
          ValueError: If URL is invalid
      """
  ```

### 报告 Bug

创建 Bug 报告时，请包含：

1. **环境信息**
   - 操作系统
   - Python 版本
   - Agent 框架版本

2. **重现步骤**
   - 详细的操作步骤
   - 预期行为
   - 实际行为

3. **相关日志**
   - 错误信息
   - 堆栈跟踪

4. **最小可重现示例**
   - 尽可能提供最小的代码示例

### 功能请求

创建功能请求时，请说明：

1. **使用场景**：为什么需要这个功能？
2. **预期行为**：功能应该如何工作？
3. **替代方案**：是否考虑过其他解决方案？
4. **额外上下文**：任何有助于理解需求的信息

### 行为准则

我们致力于提供一个友好、安全和包容的环境。参与本项目即表示你同意：

- 尊重所有贡献者
- 使用友好和包容的语言
- 接受建设性的批评
- 关注对社区最有利的事情
- 对其他社区成员表现出同理心

不可接受的行为包括：

- 使用性化的语言或图像
- 人身攻击或侮辱性评论
- 公开或私下骚扰
- 未经许可发布他人的私人信息
- 其他不道德或不专业的行为

### 获取帮助

- 📖 查看 [README](README.md) 了解项目概况
- 🐛 浏览 [Issues](https://github.com/your-username/Tapestry/issues) 寻找已知问题
- 💬 在 issue 中提问或发起讨论
- 🏷️ 查找标记为 `good first issue` 的问题（适合新贡献者）
- 🆘 查找标记为 `help wanted` 的问题（需要社区帮助）

### 许可证

通过贡献代码，你同意你的贡献将在 [MIT License](LICENSE) 下授权。

---

## English

Thank you for considering contributing to Tapestry! We welcome all forms of contributions, including but not limited to:

- 🐛 Bug reports and fixes
- ✨ New features and enhancements
- 📝 Documentation improvements
- 🧪 Test coverage
- 🌐 New platform crawlers
- 💡 Usage feedback and suggestions

### Before You Start

1. **Search Existing Issues**: Before creating a new issue, please search for related discussions
2. **Read Documentation**: Make sure you're familiar with the project's architecture and design philosophy
3. **Start Small**: Begin with small improvements to gradually familiarize yourself with the project

### Development Workflow

#### 1. Fork and Clone

```bash
# Fork the repository to your account
# Then clone your fork
git clone https://github.com/your-username/Tapestry.git
cd Tapestry

# Add upstream repository
git remote add upstream https://github.com/original-owner/Tapestry.git
```

#### 2. Create a Branch

```bash
# Create a new feature branch from main
git checkout -b feature/your-feature-name

# Or a fix branch
git checkout -b fix/issue-description
```

#### 3. Develop and Test

```bash
# Install to your AI agent framework for testing (use symlink for development)
ln -s "$(pwd)/skills/tapestry" ~/.claude/skills/tapestry

# Or direct copy
cp -r skills/tapestry ~/.claude/skills/

# Run tests
cd skills/tapestry/_tests
pytest -v

# Run specific tests
pytest test_ingest.py -v
```

#### 4. Commit Changes

Follow Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation update
- `style`: Code formatting (no functional changes)
- `refactor`: Refactoring (neither feature nor fix)
- `test`: Adding or modifying tests
- `chore`: Build process or auxiliary tool changes

**Example**:
```bash
git commit -m "feat(crawlers): add Bilibili video crawler

- Implement video metadata extraction
- Support comment tree parsing
- Add tests for Bilibili crawler

Closes #123"
```

#### 5. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

### PR Checklist

Before submitting a PR, ensure:

- [ ] Code follows existing project style
- [ ] Added necessary type annotations and docstrings
- [ ] All tests pass (`pytest`)
- [ ] Updated relevant documentation
- [ ] Commit messages are clear and follow Conventional Commits
- [ ] PR description clearly explains motivation and changes

### PR Template

When creating a PR, please include:

```markdown
## Change Type
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation update
- [ ] Performance optimization
- [ ] Code refactoring

## Description
<!-- Briefly describe what this PR does -->

## Motivation and Context
<!-- Why is this change needed? What problem does it solve? -->

## Testing
<!-- How to verify this change? Provide test steps -->
1.
2.
3.

## Related Issues
<!-- Link related issue numbers, e.g., Closes #123 -->

## Screenshots (if applicable)
<!-- If UI changes, provide screenshots -->

## Checklist
- [ ] Code follows project style guide
- [ ] Added necessary tests
- [ ] All tests pass
- [ ] Updated relevant documentation
- [ ] Commit messages are clear
```

### Contribution Areas

#### 🕷️ Adding New Platform Crawlers

1. Create new directory in `skills/tapestry/_src/crawlers/`
2. Implement crawler interface:
   ```python
   from _src.registry import CrawlerDefinition

   CRAWLER = CrawlerDefinition(
       id="platform_name",
       title="Platform Name",
       domains=["platform.com"],
       url_patterns=[r"pattern"],
       handler=crawl_platform
   )
   ```
3. Register in `_src/registry.py`
4. Add Feed spec to `skills/tapestry/feed/_specs/`
5. Write tests

#### 📝 Improving Feed Specifications

1. Edit spec files in `skills/tapestry/feed/_specs/`
2. Ensure consistency with `_shared-standard.md`
3. Test specs on actual content

#### 🎨 Enhancing Frontend

1. Modify frontend assets in `skills/tapestry/display/_ui/`
2. Ensure responsive design
3. Test browser compatibility

#### 📚 Refining Knowledge Base Governance

1. Optimize rules in `skills/tapestry/_kb_rules/`
2. Improve topic classification logic
3. Enhance knowledge base maintainability

### Code Style

- Use Python 3.10+ features
- Follow PEP 8 style guide
- Use type annotations
- Write clear docstrings
- Keep functions concise (single responsibility)

### Testing Guidelines

```bash
# Run all tests
cd skills/tapestry/_tests
pytest

# Run specific test file
pytest test_ingest.py

# Run specific test function
pytest test_ingest.py::test_function_name

# View coverage
pytest --cov=_src --cov-report=html
```

### Documentation Standards

- All public functions and classes should have docstrings
- Use Google-style docstrings
- Example:
  ```python
  def crawl_platform(url: str) -> CrawlerProduct:
      """Crawl content from the platform.

      Args:
          url: The URL to crawl

      Returns:
          CrawlerProduct containing captured data

      Raises:
          ValueError: If URL is invalid
      """
  ```

### Reporting Bugs

When creating a bug report, include:

1. **Environment Information**
   - Operating system
   - Python version
   - Agent framework version

2. **Reproduction Steps**
   - Detailed operation steps
   - Expected behavior
   - Actual behavior

3. **Relevant Logs**
   - Error messages
   - Stack traces

4. **Minimal Reproducible Example**
   - Provide minimal code example if possible

### Feature Requests

When creating a feature request, explain:

1. **Use Case**: Why is this feature needed?
2. **Expected Behavior**: How should the feature work?
3. **Alternatives**: Have you considered other solutions?
4. **Additional Context**: Any information that helps understand the need

### Code of Conduct

We are committed to providing a friendly, safe, and inclusive environment. By participating in this project, you agree to:

- Respect all contributors
- Use welcoming and inclusive language
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards other community members

Unacceptable behavior includes:

- Use of sexualized language or imagery
- Personal attacks or insulting comments
- Public or private harassment
- Publishing others' private information without permission
- Other unethical or unprofessional conduct

### Getting Help

- 📖 Check [README](README.md) for project overview
- 🐛 Browse [Issues](https://github.com/your-username/Tapestry/issues) for known issues
- 💬 Ask questions or start discussions in issues
- 🏷️ Look for issues tagged `good first issue` (suitable for new contributors)
- 🆘 Look for issues tagged `help wanted` (need community help)

### License

By contributing code, you agree that your contributions will be licensed under the [MIT License](LICENSE).
