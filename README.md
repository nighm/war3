# War3 Custom Map Studio

## 项目概述

War3 Custom Map Studio 是一个完整的魔兽争霸3自定义地图制作工具链，采用领域驱动设计（DDD）架构，提供从地图设计到最终发布的完整解决方案。202508072051

### 核心功能

- 🗺️ **地图编辑器**: 可视化地图设计工具
- ⚡ **触发器系统**: 图形化触发器编辑器
- 🎨 **资源管理器**: 模型、贴图、音效管理
- 📊 **数据编辑器**: 单位、物品、技能数据编辑
- 🧪 **测试工具**: 地图测试和调试功能
- 📦 **发布系统**: 地图打包和发布管理

### 技术架构

```
src/
├── domain/           # 领域层 - 核心业务逻辑
│   ├── entities/     # 实体（地图、单位、技能等）
│   ├── value_objects/ # 值对象
│   └── services/     # 领域服务
├── application/      # 应用层 - 用例和业务流程
│   ├── use_cases/    # 用例实现
│   └── services/     # 应用服务
├── infrastructure/   # 基础设施层 - 外部依赖
│   ├── persistence/  # 数据持久化
│   ├── external/     # 外部服务
│   └── tools/        # 工具集成
├── interfaces/       # 接口层 - 用户界面
│   ├── cli/          # 命令行接口
│   ├── gui/          # 图形用户界面
│   └── api/          # API接口
└── shared/           # 共享组件
    ├── utils/        # 工具函数
    └── constants/    # 常量定义
```

### 开发环境要求

- Python 3.8+
- PyQt6
- Git
- 魔兽争霸3游戏文件（用于资源提取）

### 快速开始

1. **克隆项目**
```bash
git clone <repository-url>
cd war3-custom-map-studio
```

2. **安装依赖**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **运行应用**
```bash
python src/main.py
```

### 项目结构

```
war3-custom-map-studio/
├── src/                    # 源代码
│   ├── domain/            # 领域层
│   ├── application/       # 应用层
│   ├── infrastructure/    # 基础设施层
│   ├── interfaces/        # 接口层
│   └── shared/           # 共享组件
├── docs/                  # 文档
├── tests/                 # 测试
├── resources/             # 资源文件
├── scripts/              # 脚本工具
├── config/               # 配置文件
└── output/               # 输出文件
```

### 开发规范

- 遵循DDD架构原则
- 使用类型提示
- 编写单元测试
- 代码注释使用中文
- 提交信息使用中文

### 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

### 许可证

MIT License

---

**注意**: 本项目仅用于学习和研究目的，请遵守相关游戏的使用条款。 