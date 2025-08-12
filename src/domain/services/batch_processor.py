#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理领域服务
负责地图项目的批量操作和规则引擎
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import time

from ..entities.map_project import MapProject


class ProcessingStatus(Enum):
    """处理状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ProcessingRule(Enum):
    """处理规则枚举"""
    ALL = "all"
    BY_TYPE = "by_type"
    BY_SIZE = "by_size"
    BY_DATE = "by_date"
    CUSTOM = "custom"


@dataclass
class ProcessingResult:
    """处理结果"""
    project_id: str
    project_name: str
    status: ProcessingStatus
    start_time: float
    end_time: Optional[float] = None
    error_message: Optional[str] = None
    details: Dict[str, Any] = None
    
    @property
    def duration(self) -> float:
        """计算处理时长"""
        if self.end_time and self.start_time:
            return self.end_time - self.start_time
        return 0.0
    
    @property
    def is_success(self) -> bool:
        """是否成功"""
        return self.status == ProcessingStatus.COMPLETED


class BatchProcessor(ABC):
    """批量处理器接口"""
    
    @abstractmethod
    def process_projects(self, projects: List[MapProject], 
                        operation: Callable[[MapProject], Any],
                        rule: ProcessingRule = ProcessingRule.ALL,
                        **kwargs) -> List[ProcessingResult]:
        """批量处理项目"""
        pass
    
    @abstractmethod
    def can_process(self, project: MapProject, rule: ProcessingRule, **kwargs) -> bool:
        """检查项目是否可以处理"""
        pass


class DefaultBatchProcessor(BatchProcessor):
    """默认批量处理器实现"""
    
    def __init__(self):
        """初始化批量处理器"""
        self.processing_history: List[ProcessingResult] = []
    
    def process_projects(self, projects: List[MapProject], 
                        operation: Callable[[MapProject], Any],
                        rule: ProcessingRule = ProcessingRule.ALL,
                        **kwargs) -> List[ProcessingResult]:
        """批量处理项目"""
        results = []
        
        # 过滤项目
        filtered_projects = [
            p for p in projects 
            if self.can_process(p, rule, **kwargs)
        ]
        
        print(f"开始批量处理 {len(filtered_projects)} 个项目...")
        
        for i, project in enumerate(filtered_projects, 1):
            print(f"处理项目 {i}/{len(filtered_projects)}: {project.name}")
            
            result = ProcessingResult(
                project_id=str(project.id),
                project_name=project.name,
                status=ProcessingStatus.PROCESSING,
                start_time=time.time()
            )
            
            try:
                # 执行操作
                operation_result = operation(project)
                
                # 更新结果
                result.status = ProcessingStatus.COMPLETED
                result.end_time = time.time()
                result.details = {
                    "operation_result": operation_result,
                    "rule_applied": rule.value,
                    "kwargs": kwargs
                }
                
                print(f"✅ {project.name} 处理成功")
                
            except Exception as e:
                # 处理失败
                result.status = ProcessingStatus.FAILED
                result.end_time = time.time()
                result.error_message = str(e)
                result.details = {
                    "rule_applied": rule.value,
                    "kwargs": kwargs
                }
                
                print(f"❌ {project.name} 处理失败: {e}")
            
            results.append(result)
            self.processing_history.append(result)
        
        # 生成处理报告
        self._generate_processing_report(results)
        
        return results
    
    def can_process(self, project: MapProject, rule: ProcessingRule, **kwargs) -> bool:
        """检查项目是否可以处理"""
        if rule == ProcessingRule.ALL:
            return True
        
        elif rule == ProcessingRule.BY_TYPE:
            target_type = kwargs.get('project_type')
            return target_type and project.project_type == target_type
        
        elif rule == ProcessingRule.BY_SIZE:
            if not project.project_path.exists():
                return False
            
            size_limit = kwargs.get('size_limit_mb', 100)
            project_size = self._calculate_project_size(project.project_path)
            return project_size <= size_limit
        
        elif rule == ProcessingRule.BY_DATE:
            if not project.project_path.exists():
                return False
            
            date_limit = kwargs.get('date_limit')
            if not date_limit:
                return True
            
            project_date = project.updated_at
            return project_date >= date_limit
        
        elif rule == ProcessingRule.CUSTOM:
            custom_filter = kwargs.get('custom_filter')
            if custom_filter and callable(custom_filter):
                return custom_filter(project)
            return True
        
        return False
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        if not self.processing_history:
            return {
                "total_processed": 0,
                "success_count": 0,
                "failure_count": 0,
                "average_duration": 0.0
            }
        
        total = len(self.processing_history)
        success_count = len([r for r in self.processing_history if r.is_success])
        failure_count = total - success_count
        
        # 计算平均处理时长
        successful_results = [r for r in self.processing_history if r.is_success]
        if successful_results:
            avg_duration = sum(r.duration for r in successful_results) / len(successful_results)
        else:
            avg_duration = 0.0
        
        return {
            "total_processed": total,
            "success_count": success_count,
            "failure_count": failure_count,
            "success_rate": (success_count / total) * 100 if total > 0 else 0,
            "average_duration": round(avg_duration, 2)
        }
    
    def clear_history(self) -> None:
        """清空处理历史"""
        self.processing_history.clear()
    
    def get_failed_projects(self) -> List[ProcessingResult]:
        """获取失败的项目"""
        return [r for r in self.processing_history if r.status == ProcessingStatus.FAILED]
    
    def retry_failed_projects(self, operation: Callable[[MapProject], Any]) -> List[ProcessingResult]:
        """重试失败的项目"""
        failed_results = self.get_failed_projects()
        if not failed_results:
            return []
        
        # 获取失败的项目
        failed_project_ids = [r.project_id for r in failed_results]
        # 这里需要从仓储中重新获取项目对象
        # 暂时返回空列表，实际使用时需要注入仓储
        
        return []
    
    def _calculate_project_size(self, path: Path) -> float:
        """计算项目大小（MB）"""
        try:
            total_size = sum(
                f.stat().st_size for f in path.rglob("*") 
                if f.is_file()
            )
            return total_size / (1024 * 1024)
        except Exception:
            return 0.0
    
    def _generate_processing_report(self, results: List[ProcessingResult]) -> None:
        """生成处理报告"""
        if not results:
            return
        
        total = len(results)
        success_count = len([r for r in results if r.is_success])
        failure_count = total - success_count
        
        print(f"\n📊 批量处理完成报告")
        print(f"总项目数: {total}")
        print(f"成功: {success_count}")
        print(f"失败: {failure_count}")
        print(f"成功率: {(success_count / total) * 100:.1f}%")
        
        if failure_count > 0:
            print(f"\n❌ 失败的项目:")
            for result in results:
                if result.status == ProcessingStatus.FAILED:
                    print(f"  - {result.project_name}: {result.error_message}")
        
        # 计算总处理时间
        if results:
            total_duration = sum(r.duration for r in results if r.end_time)
            print(f"\n⏱️ 总处理时间: {total_duration:.2f} 秒")
            print(f"平均处理时间: {total_duration / total:.2f} 秒/项目")
