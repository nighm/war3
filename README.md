# War3 Map Studio - DDD架构重构版

## 🚀 项目简介

War3 Map Studio 是一个基于领域驱动设计(DDD)架构的魔兽争霸3地图开发工具。项目已完成完整的DDD重构，提供了现代化的架构设计和丰富的功能特性。

## 📁 项目结构

```
war3/
├── src/                    # 核心源代码 (DDD架构)
│   ├── domain/            # 领域层
│   ├── application/       # 应用层
│   └── infrastructure/    # 基础设施层
├── tests/                 # 测试代码
├── docs/                  # 项目文档
│   ├── architecture/      # 架构文档
│   └── guides/           # 使用指南
├── scripts/               # 工具脚本
│   └── utilities/        # 实用工具
├── maps/                  # 地图资源
├── tools/                 # 工具目录
├── templates/             # 模板文件
└── config/                # 配置文件
```

## 🎯 核心特性

- **DDD架构**: 完整的领域驱动设计实现
- **批量处理**: 支持多项目批量操作
- **资源优化**: 地图资源压缩和去重
- **性能监控**: 实时系统性能监控
- **代码质量**: 自动化代码质量分析
- **测试覆盖**: 完整的单元和集成测试

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 依赖包: 见 `requirements.txt`

### 安装和运行
```bash
# 安装依赖
pip install -r requirements.txt

# 运行主程序
python src/main.py

# 运行测试
python -m pytest tests/
```

## 📚 文档导航

- **架构设计**: [DDD重构实施计划](docs/DDD重构实施计划.md)
- **API文档**: [完整API参考](docs/API文档.md)
- **使用示例**: [详细使用指南](docs/使用示例.md)
- **快速启动**: [scripts/utilities/quick_start.py](scripts/utilities/quick_start.py)

## 🛠️ 开发工具

- **测试框架**: pytest + coverage
- **代码质量**: 自动化质量检查
- **性能监控**: 实时性能分析
- **批量处理**: 自动化工作流

## 📊 项目状态

- ✅ **Phase 1**: DDD架构基础 (已完成)
- ✅ **Phase 2**: 核心功能实现 (已完成)
- ✅ **Phase 3**: 功能扩展和完善 (已完成)

**总体完成度: 100%** 🎉

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 创建 Pull Request
- 查看项目文档

---

**最后更新**: 2024年12月12日  
**版本**: v1.3 (DDD重构完成版) 