# GitHub同步脚本 - 优化版本

## 功能特性

### 🚀 核心功能
- **一键同步**: 自动检测网络环境，一键同步代码到GitHub
- **智能检测**: 自动检测Git代理配置和网络连通性
- **错误处理**: 完善的错误处理和用户友好的提示信息
- **配置管理**: 支持配置文件，可自定义各种参数

### 🎨 用户体验
- **彩色输出**: 支持终端颜色，信息更清晰易读
- **进度显示**: 清晰的步骤进度提示
- **详细反馈**: 每个操作都有详细的状态反馈
- **交互式操作**: 支持用户输入和选择

### ⚙️ 技术特性
- **面向对象设计**: 模块化架构，易于维护和扩展
- **类型提示**: 完整的Python类型提示
- **异常处理**: 完善的异常处理机制
- **超时控制**: 支持命令执行超时设置
- **重试机制**: 网络连接失败时自动重试

## 安装要求

- Python 3.6+
- Git已安装并配置
- 网络环境可访问GitHub（或配置代理）

## 使用方法

### 基本使用
```bash
# 直接运行，开始同步流程
python sync_to_github.py
```

### 命令行选项
```bash
# 显示帮助信息
python sync_to_github.py -h

# 显示当前配置
python sync_to_github.py -c

# 设置配置项
python sync_to_github.py -s default_commit_msg="feat: add new feature"
python sync_to_github.py -s timeout=10
python sync_to_github.py -s check_proxy=false

# 重置为默认配置
python sync_to_github.py -r
```

## 配置说明

配置文件位置: `~/.sync_github_config.json`

### 可配置项
- `default_commit_msg`: 默认提交信息
- `auto_push`: 是否自动推送 (true/false)
- `check_proxy`: 是否检查代理 (true/false)
- `timeout`: 命令超时时间(秒)
- `retry_count`: 网络重试次数

### 配置示例
```json
{
  "default_commit_msg": "feat: add new feature",
  "auto_push": true,
  "check_proxy": true,
  "timeout": 5,
  "retry_count": 3
}
```

## 工作流程

1. **环境检查** - 检查Git代理配置和网络连通性
2. **状态检查** - 检查Git仓库状态和分支信息
3. **文件添加** - 添加所有更改到暂存区
4. **提交更改** - 提交更改到本地仓库
5. **推送到远程** - 推送到GitHub远程仓库

## 错误处理

### 常见问题及解决方案

#### 网络连接问题
- 检查网络环境
- 配置可用的代理
- 启动代理软件（如Clash、V2RayN等）

#### Git配置问题
- 检查Git代理配置
- 取消错误的代理配置
- 验证Git仓库状态

#### 权限问题
- 检查GitHub访问权限
- 验证SSH密钥或Token配置

## 与原版本对比

| 特性 | 原版本 | 优化版本 |
|------|--------|----------|
| 代码结构 | 函数式 | 面向对象 |
| 错误处理 | 基础 | 完善 |
| 配置管理 | 硬编码 | 可配置 |
| 用户体验 | 简单 | 友好 |
| 功能扩展 | 固定 | 可扩展 |
| 维护性 | 一般 | 优秀 |

## 开发说明

### 架构设计
- `ConfigManager`: 配置管理
- `GitManager`: Git操作管理
- `NetworkChecker`: 网络检查
- `SyncManager`: 同步流程管理

### 扩展建议
- 支持更多Git操作（如pull、merge等）
- 添加日志记录功能
- 支持多仓库管理
- 集成CI/CD流程

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request来改进这个脚本！

## 更新日志

### v2.0.0 (当前版本)
- 重构为面向对象架构
- 添加配置管理功能
- 改进错误处理和用户体验
- 支持命令行参数
- 添加彩色输出和进度显示
- 完善文档和注释
