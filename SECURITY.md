# Security Policy | 安全政策

[中文](#中文) | [English](#english)

---

## 中文

## 支持的版本

我们为以下版本的安全漏洞发布补丁：

| 版本    | 支持状态           |
| ------- | ------------------ |
| main    | :white_check_mark: |
| < 1.0   | :x:                |

## 报告漏洞

我们非常重视 Tapestry 的安全性。如果你认为发现了安全漏洞，请按照以下方式向我们报告。

### 请不要

- **不要**为安全漏洞创建公开的 GitHub issue
- **不要**在漏洞被解决之前公开披露

### 请这样做

1. **直接发送邮件**至 [security@your-domain.com]，包含：
   - 漏洞描述
   - 重现步骤
   - 潜在影响
   - 建议的修复方案（如果有）

2. **使用主题行**：`[SECURITY] 问题简要描述`

3. **包含**：
   - 你的联系信息
   - 受影响的 Tapestry 版本
   - 相关日志或截图

### 预期流程

- **确认**：我们将在 48 小时内确认收到你的漏洞报告
- **更新**：我们会定期向你发送进展更新
- **时间线**：我们力争在 7 天内解决关键漏洞
- **致谢**：经你同意，我们会在安全公告中致谢

### 安全注意事项

使用 Tapestry 时，请注意：

1. **网络爬取合法性**：确保你有权从目标平台爬取内容
2. **速率限制**：尊重平台的速率限制，避免被封禁
3. **身份认证**：永远不要将凭证或 API 密钥提交到仓库
4. **数据隐私**：注意爬取内容中的个人数据
5. **本地存储**：捕获的内容存储在本地 - 适当保护你的文件系统

### 最佳实践

- 保持 Python 环境和依赖项更新
- 使用虚拟环境隔离依赖
- 在分享或发布前审查爬取的内容
- 遵守平台服务条款
- 为知识库实施适当的访问控制

---

## English

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Tapestry seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please Do Not

- **Do not** open a public GitHub issue for security vulnerabilities
- **Do not** disclose the vulnerability publicly until it has been addressed

### Please Do

1. **Email us directly** at [security@your-domain.com] with:
   - A description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact
   - Any suggested fixes (if you have them)

2. **Use the subject line**: `[SECURITY] Brief description of the issue`

3. **Include**:
   - Your contact information
   - The version of Tapestry affected
   - Any relevant logs or screenshots

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
- **Updates**: We will send you regular updates about our progress
- **Timeline**: We aim to address critical vulnerabilities within 7 days
- **Credit**: With your permission, we will credit you in the security advisory

### Security Considerations

When using Tapestry, please be aware:

1. **Web Scraping Legality**: Ensure you have the right to scrape content from target platforms
2. **Rate Limiting**: Respect platform rate limits to avoid being blocked
3. **Authentication**: Never commit credentials or API keys to the repository
4. **Data Privacy**: Be mindful of personal data in scraped content
5. **Local Storage**: Captured content is stored locally - secure your filesystem appropriately

### Best Practices

- Keep your Python environment and dependencies up to date
- Use virtual environments to isolate dependencies
- Review scraped content before sharing or publishing
- Follow platform Terms of Service
- Implement appropriate access controls for your knowledge base
