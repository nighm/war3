# 魔兽争霸3地图开发工作室 - API文档

## 概述

本文档描述了魔兽争霸3地图开发工作室的完整API接口，包括领域服务、应用服务、基础设施服务等各个层次的接口定义。

## 目录

1. [领域层 (Domain Layer)](#领域层-domain-layer)
2. [应用层 (Application Layer)](#应用层-application-layer)
3. [基础设施层 (Infrastructure Layer)](#基础设施层-infrastructure-layer)
4. [使用示例](#使用示例)
5. [错误处理](#错误处理)
6. [性能优化建议](#性能优化建议)

## 领域层 (Domain Layer)

### 实体 (Entities)

#### MapProject

地图项目实体，代表一个完整的地图项目。

**属性：**
- `id: UUID` - 项目唯一标识符
- `name: str` - 项目名称
- `project_type: str` - 项目类型 (rpg, td, moba, survival, melee)
- `description: str` - 项目描述
- `project_path: Path` - 项目根路径
- `source_path: Path` - 源代码路径
- `output_path: Path` - 输出路径
- `created_at: datetime` - 创建时间
- `updated_at: datetime` - 更新时间
- `version: str` - 版本号
- `config: Dict[str, Any]` - 配置信息
- `resources: Dict[str, List[str]]` - 资源文件列表
- `is_active: bool` - 是否激活
- `is_archived: bool` - 是否归档

**方法：**
- `update_project_info(**kwargs) -> None` - 更新项目信息
- `add_resource(resource_type: str, resource_path: str) -> None` - 添加资源
- `remove_resource(resource_type: str, resource_path: str) -> bool` - 移除资源
- `get_resource_count(resource_type: str) -> int` - 获取资源数量
- `archive_project() -> None` - 归档项目
- `activate_project() -> None` - 激活项目
- `validate_project() -> List[str]` - 验证项目完整性
- `to_dict() -> Dict[str, Any]` - 转换为字典
- `from_dict(data: Dict[str, Any]) -> 'MapProject'` - 从字典创建

### 值对象 (Value Objects)

#### MapConfig

地图配置值对象，包含地图的各种配置参数。

**属性：**
- `map_name: str` - 地图名称
- `map_description: str` - 地图描述
- `map_author: str` - 地图作者
- `map_version: str` - 地图版本
- `max_players: int` - 最大玩家数 (1-12)
- `game_type: str` - 游戏类型 (melee, custom, campaign)
- `difficulty: str` - 难度 (easy, normal, hard)
- `map_size: str` - 地图尺寸 (small, medium, large, extra_large)
- `terrain_type: str` - 地形类型
- `weather_effects: bool` - 天气效果
- `starting_gold: int` - 初始金币
- `starting_lumber: int` - 初始木材
- `starting_food: int` - 初始人口
- `editor_version: str` - 编辑器版本
- `custom_scripts: bool` - 自定义脚本
- `custom_models: bool` - 自定义模型
- `custom_settings: Dict[str, Any]` - 自定义设置

**方法：**
- `get_setting(key: str, default: Any = None) -> Any` - 获取自定义设置
- `has_setting(key: str) -> bool` - 检查是否有指定设置
- `to_dict() -> Dict[str, Any]` - 转换为字典
- `from_dict(data: Dict[str, Any]) -> 'MapConfig'` - 从字典创建

### 仓储接口 (Repository Interfaces)

#### MapRepository

地图项目仓储接口，定义数据持久化操作。

**方法：**
- `save(project: MapProject) -> bool` - 保存项目
- `find_by_id(project_id: UUID) -> Optional[MapProject]` - 根据ID查找
- `find_by_name(name: str) -> Optional[MapProject]` - 根据名称查找
- `find_by_path(path: Path) -> Optional[MapProject]` - 根据路径查找
- `find_all() -> List[MapProject]` - 查找所有项目
- `find_by_type(project_type: str) -> List[MapProject]` - 根据类型查找
- `find_active() -> List[MapProject]` - 查找活跃项目
- `find_archived() -> List[MapProject]` - 查找归档项目
- `delete(project_id: UUID) -> bool` - 删除项目
- `exists(project_id: UUID) -> bool` - 检查项目是否存在
- `count() -> int` - 获取项目总数
- `search(query: str) -> List[MapProject]` - 搜索项目
- `get_project_stats() -> Dict[str, Any]` - 获取项目统计信息

### 领域服务 (Domain Services)

#### MapAnalysisService

地图分析服务接口，提供项目结构、资源和性能分析。

**方法：**
- `analyze_project_structure(project: MapProject) -> Dict[str, Any]` - 分析项目结构
- `analyze_resources(project: MapProject) -> Dict[str, Any]` - 分析资源
- `analyze_performance(project: MapProject) -> Dict[str, Any]` - 分析性能
- `generate_analysis_report(project: MapProject) -> Dict[str, Any]` - 生成分析报告

#### BatchProcessor

批处理服务接口，提供批量操作功能。

**方法：**
- `process_projects(projects: List[MapProject], rule: ProcessingRule) -> ProcessingResult` - 批量处理项目
- `can_process(project: MapProject, rule: ProcessingRule) -> bool` - 检查是否可以处理
- `get_processing_stats() -> Dict[str, Any]` - 获取处理统计
- `clear_history() -> None` - 清除处理历史
- `get_failed_projects() -> List[MapProject]` - 获取失败的项目
- `retry_failed_projects() -> ProcessingResult` - 重试失败的项目

#### ResourceOptimizationService

资源优化服务接口，提供资源压缩、去重、清理等功能。

**方法：**
- `optimize_project(project: MapProject, optimization_type: OptimizationType, level: OptimizationLevel) -> OptimizationResult` - 优化项目
- `get_optimization_suggestions(project: MapProject) -> List[str]` - 获取优化建议
- `can_optimize(project: MapProject, optimization_type: OptimizationType) -> bool` - 检查是否可以优化
- `get_optimization_history(project: MapProject) -> List[OptimizationResult]` - 获取优化历史
- `get_optimization_stats(project: MapProject) -> Dict[str, Any]` - 获取优化统计

#### PerformanceAnalysisService

性能分析服务接口，提供性能监控和分析。

**方法：**
- `analyze_project_performance(project: MapProject) -> PerformanceResult` - 分析项目性能
- `get_performance_metrics(project: MapProject) -> List[PerformanceMetric]` - 获取性能指标
- `monitor_performance(project: MapProject, duration: float) -> PerformanceReport` - 监控性能
- `get_performance_history(project: MapProject) -> List[PerformanceResult]` - 获取性能历史
- `get_performance_stats(project: MapProject) -> Dict[str, Any]` - 获取性能统计
- `clear_performance_history(project: MapProject) -> None` - 清除性能历史

#### CodeQualityService

代码质量服务接口，提供代码质量分析。

**方法：**
- `analyze_code_quality(project: MapProject) -> QualityResult` - 分析代码质量
- `get_quality_metrics(project: MapProject) -> List[QualityMetric]` - 获取质量指标
- `check_specific_file(file_path: str) -> QualityResult` - 检查特定文件
- `get_quality_history(project: MapProject) -> List[QualityResult]` - 获取质量历史
- `get_quality_stats(project: MapProject) -> Dict[str, Any]` - 获取质量统计
- `clear_quality_history(project: MapProject) -> None` - 清除质量历史

## 应用层 (Application Layer)

### 应用服务 (Application Services)

#### ProjectService

项目服务，协调领域和基础设施层，实现业务用例。

**方法：**
- `create_project(name: str, project_type: str, project_path: str, config_data: Dict[str, Any]) -> MapProject` - 创建项目
- `open_project(project_id: str) -> MapProject` - 打开项目
- `save_project(project: MapProject) -> bool` - 保存项目
- `delete_project(project_id: str) -> bool` - 删除项目
- `analyze_project(project_id: str) -> Dict[str, Any]` - 分析项目
- `generate_report(project_id: str) -> Dict[str, Any]` - 生成报告
- `list_projects() -> List[MapProject]` - 列出所有项目
- `search_projects(query: str) -> List[MapProject]` - 搜索项目
- `batch_analyze_projects() -> ProcessingResult` - 批量分析项目
- `batch_archive_projects() -> ProcessingResult` - 批量归档项目
- `batch_activate_projects() -> ProcessingResult` - 批量激活项目
- `batch_cleanup_projects() -> ProcessingResult` - 批量清理项目
- `batch_validate_projects() -> ProcessingResult` - 批量验证项目

### 用例 (Use Cases)

#### BatchProcessMapsUseCase

批量处理地图用例，实现批量操作业务逻辑。

**方法：**
- `batch_analyze_projects() -> ProcessingResult` - 批量分析项目
- `batch_archive_projects() -> ProcessingResult` - 批量归档项目
- `batch_activate_projects() -> ProcessingResult` - 批量激活项目
- `batch_cleanup_projects() -> ProcessingResult` - 批量清理项目
- `batch_export_projects() -> ProcessingResult` - 批量导出项目
- `batch_validate_projects() -> ProcessingResult` - 批量验证项目
- `get_processing_statistics() -> Dict[str, Any]` - 获取处理统计
- `get_failed_processing_results() -> List[ProcessingResult]` - 获取失败的处理结果
- `retry_failed_operations() -> ProcessingResult` - 重试失败的操作

## 基础设施层 (Infrastructure Layer)

### 仓储实现 (Repository Implementations)

#### JsonMapRepository

基于JSON文件的地图项目仓储实现。

**方法：**
- 实现所有MapRepository接口方法
- `backup_projects() -> str` - 备份项目数据
- `restore_projects(backup_file: str) -> bool` - 从备份恢复项目

### 性能监控 (Performance Monitoring)

#### PerformanceMonitor

性能监控器，实时监控系统性能。

**方法：**
- `start_monitoring() -> None` - 开始监控
- `stop_monitoring() -> None` - 停止监控
- `add_alert_callback(callback: Callable) -> None` - 添加告警回调
- `get_performance_summary() -> Dict[str, float]` - 获取性能摘要
- `generate_report(start_time: datetime, end_time: datetime) -> PerformanceReport` - 生成性能报告
- `save_metrics(file_path: str) -> None` - 保存性能指标
- `load_metrics(file_path: str) -> None` - 加载性能指标
- `clear_metrics() -> None` - 清除性能指标

## 使用示例

### 创建新项目

```python
from src.application.services.project_service import ProjectService
from src.infrastructure.repositories.json_map_repository import JsonMapRepository
from src.domain.services.map_analysis_service import DefaultMapAnalysisService

# 初始化服务
repo = JsonMapRepository()
analysis_service = DefaultMapAnalysisService()
project_service = ProjectService(repo, analysis_service)

# 创建项目
project = project_service.create_project(
    name="我的RPG地图",
    project_type="rpg",
    project_path="/path/to/my/project",
    config_data={
        "map_name": "英雄传说",
        "map_description": "一个史诗级的RPG地图",
        "map_author": "地图作者",
        "max_players": 8
    }
)

print(f"项目创建成功: {project.name}")
```

### 批量分析项目

```python
# 批量分析所有项目
result = project_service.batch_analyze_projects()

print(f"批量分析完成:")
print(f"总项目数: {result.total_projects}")
print(f"成功操作: {result.successful_operations}")
print(f"失败操作: {result.failed_operations}")

if result.failed_operations > 0:
    print("失败的项目:")
    for failed in result.failed_projects:
        print(f"  - {failed.name}: {failed.failure_reason}")
```

### 性能监控

```python
from src.domain.services.performance_monitor import PerformanceMonitor

# 创建性能监控器
monitor = PerformanceMonitor()

# 添加告警回调
def alert_handler(alert):
    print(f"性能告警 [{alert.level}]: {alert.message}")
    print(f"建议: {alert.recommendation}")

monitor.add_alert_callback(alert_handler)

# 开始监控
monitor.start_monitoring()

# 执行一些操作...
import time
time.sleep(10)

# 停止监控
monitor.stop_monitoring()

# 生成报告
report = monitor.generate_report()
print("性能报告:")
print(f"CPU平均使用率: {report.summary.get('avg_cpu_percent', 0):.2f}%")
print(f"内存平均使用率: {report.summary.get('avg_memory_percent', 0):.2f}%")

for recommendation in report.recommendations:
    print(f"建议: {recommendation}")
```

### 资源优化

```python
from src.domain.services.resource_optimization_service import DefaultResourceOptimizationService, OptimizationType, OptimizationLevel

# 创建资源优化服务
optimization_service = DefaultResourceOptimizationService()

# 优化项目资源
result = optimization_service.optimize_project(
    project=project,
    optimization_type=OptimizationType.COMPRESSION,
    level=OptimizationLevel.AGGRESSIVE
)

print(f"资源优化完成:")
print(f"原始大小: {result.original_size_mb:.2f} MB")
print(f"优化后大小: {result.optimized_size_mb:.2f} MB")
print(f"节省空间: {result.space_saved_mb:.2f} MB")
print(f"压缩率: {result.compression_ratio:.2f}%")
```

## 错误处理

### 异常类型

- `ValueError`: 参数验证失败
- `FileNotFoundError`: 文件或目录不存在
- `PermissionError`: 权限不足
- `RuntimeError`: 运行时错误

### 错误处理示例

```python
try:
    project = project_service.create_project(
        name="",
        project_type="invalid_type",
        project_path="/nonexistent/path",
        config_data={}
    )
except ValueError as e:
    print(f"参数错误: {e}")
except FileNotFoundError as e:
    print(f"路径不存在: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

## 性能优化建议

### 1. 批量操作

- 使用批量处理方法而不是单个处理
- 合理设置批处理大小，避免内存溢出

### 2. 资源管理

- 及时关闭文件句柄
- 使用上下文管理器管理资源
- 避免在循环中创建大量对象

### 3. 缓存策略

- 缓存频繁访问的数据
- 使用LRU缓存策略
- 定期清理过期缓存

### 4. 异步处理

- 对于IO密集型操作使用异步处理
- 使用线程池处理CPU密集型任务
- 避免阻塞主线程

### 5. 监控和调优

- 启用性能监控
- 定期分析性能报告
- 根据建议调整系统配置

## 版本信息

- **当前版本**: 1.0.0
- **最后更新**: 2024年12月12日
- **兼容性**: Python 3.8+

## 联系方式

如有问题或建议，请联系开发团队。
