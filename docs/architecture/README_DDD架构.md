# 🏗️ War3 Map Studio DDD架构使用指南

## 📖 概述

本项目已成功重构为遵循DDD（领域驱动设计）架构的现代化Python项目。重构后的代码具有更好的可维护性、可测试性和可扩展性。

## 🏛️ 架构概览

```
src/
├── domain/                 # 领域层
│   ├── entities/          # 业务实体
│   ├── value_objects/     # 值对象
│   ├── services/          # 领域服务
│   └── repositories/      # 仓储接口
├── application/            # 应用层
│   └── services/          # 应用服务
├── infrastructure/         # 基础设施层
│   └── repositories/      # 仓储实现
└── shared/                 # 共享组件
    └── utils/             # 工具类
```

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 无额外依赖（使用标准库）

### 基本使用

#### 1. 检查环境
```bash
python src/main.py --check-env
```

#### 2. 创建新项目
```bash
python src/main.py --create-project "MyRPGMap" --project-type rpg
```

#### 3. 打开现有项目
```bash
python src/main.py --open-project "path/to/project"
```

#### 4. 使用命令行界面
```bash
python src/main.py --cli
```

## 🎯 核心功能

### 项目管理
- **创建项目**：支持多种地图类型（RPG、TD、MOBA、生存、对战）
- **项目分析**：自动分析项目结构、资源和性能
- **配置管理**：统一的项目配置管理
- **资源跟踪**：自动识别和分类项目资源

### 项目类型支持
1. **RPG** - 角色扮演游戏
2. **TD** - 塔防游戏
3. **MOBA** - 多人在线竞技
4. **Survival** - 生存游戏
5. **Melee** - 对战游戏

## 🏗️ 架构组件详解

### 领域层 (Domain Layer)

#### MapProject 实体
```python
from src.domain.entities.map_project import MapProject

project = MapProject(
    name="我的地图",
    project_type="rpg",
    description="一个有趣的RPG地图"
)

# 验证项目
errors = project.validate_project()
if not errors:
    print("项目验证通过")

# 添加资源
project.add_resource("models", "hero.mdx")
project.add_resource("textures", "hero.blp")
```

#### MapConfig 值对象
```python
from src.domain.value_objects.map_config import MapConfig

config = MapConfig(
    map_name="英雄传说",
    map_description="一个史诗级的冒险故事",
    map_author="地图作者",
    max_players=8,
    game_type="custom"
)
```

#### MapAnalysisService 领域服务
```python
from src.domain.services.map_analysis_service import DefaultMapAnalysisService

service = DefaultMapAnalysisService()

# 分析项目结构
structure = service.analyze_project_structure(project)

# 分析资源
resources = service.analyze_resources(project)

# 分析性能
performance = service.analyze_performance(project)

# 生成完整报告
report = service.generate_analysis_report(project)
```

### 应用层 (Application Layer)

#### ProjectService 应用服务
```python
from src.application.services.project_service import ProjectService

# 创建项目
project = project_service.create_project(
    name="新项目",
    project_type="rpg",
    description="项目描述"
)

# 打开项目
project = project_service.open_project("path/to/project")

# 分析项目
analysis = project_service.analyze_project(project)

# 生成报告
report = project_service.generate_report(project)
```

### 基础设施层 (Infrastructure Layer)

#### JsonMapRepository 仓储实现
```python
from src.infrastructure.repositories.json_map_repository import JsonMapRepository

repo = JsonMapRepository()

# 保存项目
repo.save(project)

# 查找项目
project = repo.find_by_name("项目名称")
project = repo.find_by_id(project_id)

# 列出所有项目
projects = repo.find_all()

# 按类型查找
rpg_projects = repo.find_by_type("rpg")

# 搜索项目
results = repo.search("关键词")
```

## 🔧 扩展开发

### 添加新的项目类型

1. 在 `MapProject` 实体中添加类型支持
2. 在 `MapConfig` 中添加相关配置
3. 在 `ProjectService` 中添加类型特定的逻辑

### 添加新的分析功能

1. 在 `MapAnalysisService` 中添加新的分析方法
2. 在 `ProjectService` 中集成新功能
3. 更新命令行界面

### 添加新的存储后端

1. 实现 `MapRepository` 接口
2. 在 `ProjectService` 中注入新的仓储
3. 更新配置

## 📊 性能特性

- **内存效率**：使用值对象减少内存占用
- **延迟加载**：资源按需加载
- **缓存机制**：分析结果缓存
- **异步支持**：可扩展为异步处理

## 🧪 测试

### 运行测试
```bash
# 环境检查
python src/main.py --check-env

# 功能测试
python src/main.py --cli
```

### 测试覆盖
- 领域实体验证
- 领域服务功能
- 应用服务协调
- 基础设施持久化
- 集成功能

## 📈 监控和日志

### 日志级别
- **INFO**：正常操作信息
- **WARNING**：警告信息
- **ERROR**：错误信息

### 性能监控
- 项目创建时间
- 分析执行时间
- 资源使用情况

## 🔄 版本兼容性

### 向后兼容
- 保持原有CLI接口
- 支持现有项目格式
- 渐进式功能迁移

### 升级路径
1. 备份现有项目
2. 运行新版本
3. 验证功能正常
4. 迁移项目数据

## 🚨 故障排除

### 常见问题

#### 1. 导入错误
```bash
# 确保在项目根目录运行
cd /path/to/war3
python src/main.py --check-env
```

#### 2. 权限错误
```bash
# 检查目录权限
ls -la src/
```

#### 3. Python版本问题
```bash
# 检查Python版本
python --version
# 需要Python 3.8+
```

### 调试模式
```bash
# 启用详细日志
export PYTHONPATH=.
python -u src/main.py --cli
```

## 📚 相关文档

- [DDD重构实施计划](docs/DDD重构实施计划.md)
- [项目架构设计](docs/架构设计.md)
- [API参考文档](docs/API参考.md)

## 🤝 贡献指南

1. 遵循DDD架构原则
2. 保持代码风格一致
3. 添加适当的测试
4. 更新相关文档

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**最后更新**：2024年12月12日  
**版本**：v1.0.0  
**维护者**：War3 Map Studio Team
