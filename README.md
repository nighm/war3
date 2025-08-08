# 魔兽争霸3自定义地图开发项目

基于网易Y3编辑器的War3地图开发项目，提供完整的开发环境、文档体系和协作工具。

## 🎯 项目状态

✅ **已完成功能**
- Y3编辑器集成与一键启动
- 地图项目导入与管理体系
- 完整文档体系（教学、FAQ、术语表）
- 团队协作工具与规范
- Git版本管理与自动化同步

✅ **最新更新**
- 成功集成Y3地图项目 `ProjectName001_1`
- 建立完整的地图项目管理流程
- 提供地图项目结构详解与开发指南

## 项目结构

```
war3/
├── docs/                    # 📚 文档体系
│   ├── README.md           # 文档导航
│   ├── 项目管理/           # 项目规划与规范
│   ├── 教学文档/           # Y3编辑器使用教程
│   └── 附录/              # 术语表、FAQ等
├── maps/                   # 🗺️ 地图项目目录
│   └── ProjectName001_1/   # Y3地图项目（已集成）
│       ├── maps/EntryMap/  # 主地图文件
│       ├── editor_table/   # 物编数据
│       ├── global_script/  # 全局脚本
│       └── project_info.json # 项目信息
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
- 🗺️ **地图开发**: 完整的地图项目结构与开发流程

## 地图项目详解

### ProjectName001_1 项目结构
- **maps/EntryMap/**: 主地图文件（地形、单位、物品、技能）
- **editor_table/**: 物编数据（单位属性、技能效果、物品配置）
- **global_script/**: 全局Lua脚本
- **plugins/**: Y3编辑器插件
- **配置文件**: 游戏模式、规则、UI等配置

### 开发流程
1. 在Y3编辑器中设计地图
2. 使用工具导入到war3项目
3. 在项目中进行版本管理和协作开发
4. 定期同步到Y3编辑器进行测试

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