#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理地图项目应用用例
实现批量操作的业务逻辑
"""

from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from datetime import datetime

from ...domain.entities.map_project import MapProject
from ...domain.services.batch_processor import (
    BatchProcessor, 
    DefaultBatchProcessor, 
    ProcessingRule, 
    ProcessingResult
)
from ...domain.repositories.map_repository import MapRepository


class BatchProcessMapsUseCase:
    """批量处理地图项目用例"""
    
    def __init__(self, 
                 map_repository: MapRepository,
                 batch_processor: Optional[BatchProcessor] = None):
        """初始化用例"""
        self.map_repository = map_repository
        self.batch_processor = batch_processor or DefaultBatchProcessor()
    
    def batch_analyze_projects(self, 
                              rule: ProcessingRule = ProcessingRule.ALL,
                              **kwargs) -> List[ProcessingResult]:
        """批量分析项目"""
        projects = self.map_repository.find_all()
        
        def analyze_operation(project: MapProject) -> Dict[str, Any]:
            """分析操作"""
            # 这里可以注入分析服务
            return {
                "project_name": project.name,
                "project_type": project.project_type,
                "file_count": self._count_files(project.project_path),
                "size_mb": self._calculate_size_mb(project.project_path)
            }
        
        return self.batch_processor.process_projects(
            projects, analyze_operation, rule, **kwargs
        )
    
    def batch_archive_projects(self, 
                              rule: ProcessingRule = ProcessingRule.ALL,
                              **kwargs) -> List[ProcessingResult]:
        """批量归档项目"""
        projects = self.map_repository.find_all()
        
        def archive_operation(project: MapProject) -> bool:
            """归档操作"""
            project.archive_project()
            return self.map_repository.save(project)
        
        return self.batch_processor.process_projects(
            projects, archive_operation, rule, **kwargs
        )
    
    def batch_activate_projects(self, 
                               rule: ProcessingRule = ProcessingRule.ALL,
                               **kwargs) -> List[ProcessingResult]:
        """批量激活项目"""
        projects = self.map_repository.find_all()
        
        def activate_operation(project: MapProject) -> bool:
            """激活操作"""
            project.activate_project()
            return self.map_repository.save(project)
        
        return self.batch_processor.process_projects(
            projects, activate_operation, rule, **kwargs
        )
    
    def batch_cleanup_projects(self, 
                              rule: ProcessingRule = ProcessingRule.ALL,
                              **kwargs) -> List[ProcessingResult]:
        """批量清理项目"""
        projects = self.map_repository.find_all()
        
        def cleanup_operation(project: MapProject) -> Dict[str, Any]:
            """清理操作"""
            cleanup_info = {
                "cleaned_files": 0,
                "cleaned_size_mb": 0.0
            }
            
            if project.project_path.exists():
                # 清理临时文件
                temp_extensions = ['.tmp', '.temp', '.log', '.cache']
                for ext in temp_extensions:
                    for temp_file in project.project_path.rglob(f"*{ext}"):
                        try:
                            file_size = temp_file.stat().st_size
                            temp_file.unlink()
                            cleanup_info["cleaned_files"] += 1
                            cleanup_info["cleaned_size_mb"] += file_size / (1024 * 1024)
                        except Exception:
                            pass
            
            return cleanup_info
        
        return self.batch_processor.process_projects(
            projects, cleanup_operation, rule, **kwargs
        )
    
    def batch_export_projects(self, 
                             export_path: Path,
                             rule: ProcessingRule = ProcessingRule.ALL,
                             **kwargs) -> List[ProcessingResult]:
        """批量导出项目"""
        projects = self.map_repository.find_all()
        
        def export_operation(project: MapProject) -> Dict[str, Any]:
            """导出操作"""
            export_info = {
                "exported_path": "",
                "exported_size_mb": 0.0
            }
            
            try:
                # 创建导出目录
                project_export_path = export_path / project.name
                project_export_path.mkdir(parents=True, exist_ok=True)
                
                # 复制项目文件
                import shutil
                if project.project_path.exists():
                    shutil.copytree(
                        project.project_path, 
                        project_export_path, 
                        dirs_exist_ok=True
                    )
                    
                    # 计算导出大小
                    export_size = sum(
                        f.stat().st_size for f in project_export_path.rglob("*") 
                        if f.is_file()
                    )
                    export_info["exported_path"] = str(project_export_path)
                    export_info["exported_size_mb"] = export_size / (1024 * 1024)
                
            except Exception as e:
                raise RuntimeError(f"导出失败: {e}")
            
            return export_info
        
        return self.batch_processor.process_projects(
            projects, export_operation, rule, **kwargs
        )
    
    def batch_validate_projects(self, 
                               rule: ProcessingRule = ProcessingRule.ALL,
                               **kwargs) -> List[ProcessingResult]:
        """批量验证项目"""
        projects = self.map_repository.find_all()
        
        def validate_operation(project: MapProject) -> Dict[str, Any]:
            """验证操作"""
            validation_result = {
                "is_valid": True,
                "errors": [],
                "warnings": []
            }
            
            # 验证项目完整性
            errors = project.validate_project()
            if errors:
                validation_result["is_valid"] = False
                validation_result["errors"] = errors
            
            # 检查项目路径
            if not project.project_path.exists():
                validation_result["is_valid"] = False
                validation_result["errors"].append("项目路径不存在")
            
            # 检查项目大小
            if project.project_path.exists():
                size_mb = self._calculate_size_mb(project.project_path)
                if size_mb > 500:  # 500MB警告
                    validation_result["warnings"].append(f"项目大小过大: {size_mb:.1f}MB")
            
            return validation_result
        
        return self.batch_processor.process_projects(
            projects, validate_operation, rule, **kwargs
        )
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        return self.batch_processor.get_processing_stats()
    
    def get_failed_processing_results(self) -> List[ProcessingResult]:
        """获取失败的处理结果"""
        return self.batch_processor.get_failed_projects()
    
    def retry_failed_operations(self, 
                               operation_type: str,
                               **kwargs) -> List[ProcessingResult]:
        """重试失败的操作"""
        failed_results = self.get_failed_processing_results()
        if not failed_results:
            return []
        
        # 根据操作类型选择重试操作
        operation_map = {
            "analyze": self.batch_analyze_projects,
            "archive": self.batch_archive_projects,
            "activate": self.batch_activate_projects,
            "cleanup": self.batch_cleanup_projects,
            "export": self.batch_export_projects,
            "validate": self.batch_validate_projects
        }
        
        operation = operation_map.get(operation_type)
        if not operation:
            raise ValueError(f"不支持的操作类型: {operation_type}")
        
        # 获取失败的项目ID
        failed_project_ids = [r.project_id for r in failed_results]
        
        # 重新获取项目对象
        failed_projects = []
        for project_id in failed_project_ids:
            try:
                from uuid import UUID
                project = self.map_repository.find_by_id(UUID(project_id))
                if project:
                    failed_projects.append(project)
            except Exception:
                continue
        
        # 重试操作
        if failed_projects:
            return operation(ProcessingRule.CUSTOM, custom_filter=lambda p: p.id in [fp.id for fp in failed_projects])
        
        return []
    
    def _count_files(self, path: Path) -> int:
        """计算文件数量"""
        try:
            return len([f for f in path.rglob("*") if f.is_file()])
        except Exception:
            return 0
    
    def _calculate_size_mb(self, path: Path) -> float:
        """计算目录大小（MB）"""
        try:
            total_size = sum(
                f.stat().st_size for f in path.rglob("*") 
                if f.is_file()
            )
            return total_size / (1024 * 1024)
        except Exception:
            return 0.0
