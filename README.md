# 魔兽争霸3自定义地图开发项目

基于网易Y3编辑器的War3地图开发项目，提供完整的开发环境、文档体系和协作工具。

## 项目结构

```
war3/
├── docs/                    # 📚 文档体系
│   ├── README.md           # 文档导航
│   ├── 项目管理/           # 项目规划与规范
│   ├── 教学文档/           # Y3编辑器使用教程
│   └── 附录/              # 术语表、FAQ等
├── maps/                   # 🗺️ 地图项目目录
│   └── ProjectName001_1/   # 你的地图项目
├── tools/                  # 🛠️ 工具脚本
│   ├── start_y3_editor.py  # 启动Y3编辑器
│   ├── map_manager.py      # 地图项目管理工具
│   ├── quick_import.py     # 快速导入工具
│   └── sync_to_github.py   # Git同步工具
├── templates/              # 📋 项目模板
└── src/                    # 💻 源代码
```

## 快速开始

### 1. 启动Y3编辑器
```bash
python start_y3_editor.py
```

### 2. 导入地图项目
```bash
python tools/quick_import.py
```

### 3. 管理地图项目
```bash
python tools/map_manager.py
```

### 4. 同步到GitHub
```bash
python sync_to_github.py
```

## 主要功能

- 🎮 **Y3编辑器集成**: 一键启动和管理Y3编辑器
- 📁 **地图项目管理**: 导入、备份、同步、模板化
- 📚 **完整文档体系**: 从入门到进阶的详细教程
- 🤝 **团队协作**: Git版本管理、文档维护规范
- 🛠️ **自动化工具**: 批量处理、快速导入导出

## 文档导航

详细文档请查看 [docs/README.md](docs/README.md)

## 开发环境

- Y3编辑器: `D:\Program Files\y3\games\2.0\game\Editor.exe`
- Python: 3.7+
- Git: 版本管理

## 贡献指南

1. 阅读 [docs/新成员入门指引.md](docs/新成员入门指引.md)
2. 按照 [docs/团队协作与文档维护建议.md](docs/团队协作与文档维护建议.md) 进行协作
3. 遇到问题请查看 [docs/附录/FAQ.md](docs/附录/FAQ.md)

## 许可证

MIT License 