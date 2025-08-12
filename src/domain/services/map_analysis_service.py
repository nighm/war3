#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地图分析领域服务
负责地图项目的分析和评估
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from ..entities.map_project import MapProject
from ..value_objects.map_config import MapConfig


class MapAnalysisService(ABC):
    """地图分析服务接口"""
    
    @abstractmethod
    def analyze_project_structure(self, project: MapProject) -> Dict[str, Any]:
        """分析项目结构"""
        pass
    
    @abstractmethod
    def analyze_resources(self, project: MapProject) -> Dict[str, Any]:
        """分析项目资源"""
        pass
    
    @abstractmethod
    def analyze_performance(self, project: MapProject) -> Dict[str, Any]:
        """分析项目性能"""
        pass
    
    @abstractmethod
    def generate_analysis_report(self, project: MapProject) -> str:
        """生成分析报告"""
        pass


class DefaultMapAnalysisService(MapAnalysisService):
    """默认地图分析服务实现"""
    
    def analyze_project_structure(self, project: MapProject) -> Dict[str, Any]:
        """分析项目结构"""
        analysis = {
            "project_name": project.name,
            "project_type": project.project_type,
            "structure_analysis": {},
            "file_count": 0,
            "directory_count": 0,
            "total_size": 0
        }
        
        if project.project_path.exists():
            try:
                # 统计文件和目录
                file_count = 0
                directory_count = 0
                total_size = 0
                
                for item in project.project_path.rglob("*"):
                    if item.is_file():
                        file_count += 1
                        total_size += item.stat().st_size
                    elif item.is_dir():
                        directory_count += 1
                
                analysis["file_count"] = file_count
                analysis["directory_count"] = directory_count
                analysis["total_size"] = total_size
                
                # 分析目录结构
                structure = self._analyze_directory_structure(project.project_path)
                analysis["structure_analysis"] = structure
                
            except Exception as e:
                analysis["error"] = str(e)
        
        return analysis
    
    def analyze_resources(self, project: MapProject) -> Dict[str, Any]:
        """分析项目资源"""
        analysis = {
            "project_name": project.name,
            "resource_analysis": {},
            "resource_types": {},
            "total_resources": 0
        }
        
        # 分析资源类型分布
        resource_types = {}
        total_resources = 0
        
        for resource_type, resources in project.resources.items():
            count = len(resources)
            resource_types[resource_type] = {
                "count": count,
                "resources": resources
            }
            total_resources += count
        
        analysis["resource_types"] = resource_types
        analysis["total_resources"] = total_resources
        
        # 分析资源文件
        if project.project_path.exists():
            resource_analysis = self._analyze_resource_files(project.project_path)
            analysis["resource_analysis"] = resource_analysis
        
        return analysis
    
    def analyze_performance(self, project: MapProject) -> Dict[str, Any]:
        """分析项目性能"""
        analysis = {
            "project_name": project.name,
            "performance_metrics": {},
            "optimization_suggestions": []
        }
        
        # 基础性能指标
        metrics = {}
        
        # 文件大小分析
        if project.project_path.exists():
            total_size = sum(
                f.stat().st_size for f in project.project_path.rglob("*") 
                if f.is_file()
            )
            metrics["total_size_mb"] = round(total_size / (1024 * 1024), 2)
            
            # 文件数量
            file_count = len([f for f in project.project_path.rglob("*") if f.is_file()])
            metrics["file_count"] = file_count
            
            # 平均文件大小
            if file_count > 0:
                metrics["avg_file_size_kb"] = round(total_size / file_count / 1024, 2)
        
        analysis["performance_metrics"] = metrics
        
        # 生成优化建议
        suggestions = self._generate_optimization_suggestions(metrics)
        analysis["optimization_suggestions"] = suggestions
        
        return analysis
    
    def generate_analysis_report(self, project: MapProject) -> str:
        """生成分析报告"""
        structure_analysis = self.analyze_project_structure(project)
        resource_analysis = self.analyze_resources(project)
        performance_analysis = self.analyze_performance(project)
        
        report = f"""
# 地图项目分析报告

## 项目基本信息
- 项目名称: {project.name}
- 项目类型: {project.project_type}
- 创建时间: {project.created_at.strftime('%Y-%m-%d %H:%M:%S')}
- 最后更新: {project.updated_at.strftime('%Y-%m-%d %H:%M:%S')}

## 项目结构分析
- 文件总数: {structure_analysis.get('file_count', 0)}
- 目录总数: {structure_analysis.get('directory_count', 0)}
- 总大小: {structure_analysis.get('total_size', 0) / (1024*1024):.2f} MB

## 资源分析
- 资源类型数: {len(resource_analysis.get('resource_types', {}))}
- 总资源数: {resource_analysis.get('total_resources', 0)}

## 性能分析
- 总大小: {performance_analysis.get('performance_metrics', {}).get('total_size_mb', 0)} MB
- 文件数量: {performance_analysis.get('performance_metrics', {}).get('file_count', 0)}
- 平均文件大小: {performance_analysis.get('performance_metrics', {}).get('avg_file_size_kb', 0)} KB

## 优化建议
"""
        
        for suggestion in performance_analysis.get('optimization_suggestions', []):
            report += f"- {suggestion}\n"
        
        return report
    
    def _analyze_directory_structure(self, path: Path) -> Dict[str, Any]:
        """分析目录结构"""
        structure = {}
        
        try:
            for item in path.iterdir():
                if item.is_dir():
                    structure[item.name] = {
                        "type": "directory",
                        "children": self._analyze_directory_structure(item)
                    }
                else:
                    structure[item.name] = {
                        "type": "file",
                        "size": item.stat().st_size
                    }
        except Exception:
            pass
        
        return structure
    
    def _analyze_resource_files(self, path: Path) -> Dict[str, Any]:
        """分析资源文件"""
        resource_files = {}
        
        # 常见的资源文件扩展名
        resource_extensions = {
            "模型": [".mdx", ".mdl", ".3ds", ".obj"],
            "纹理": [".blp", ".tga", ".png", ".jpg", ".jpeg"],
            "音效": [".wav", ".mp3", ".ogg"],
            "脚本": [".lua", ".j", ".js"],
            "地图": [".w3m", ".w3x", ".gmp"]
        }
        
        for ext_type, extensions in resource_extensions.items():
            files = []
            for ext in extensions:
                files.extend(path.rglob(f"*{ext}"))
                files.extend(path.rglob(f"*{ext.upper()}"))
            
            if files:
                resource_files[ext_type] = {
                    "count": len(files),
                    "files": [str(f.relative_to(path)) for f in files]
                }
        
        return resource_files
    
    def _generate_optimization_suggestions(self, metrics: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        total_size_mb = metrics.get('total_size_mb', 0)
        file_count = metrics.get('file_count', 0)
        avg_file_size_kb = metrics.get('avg_file_size_kb', 0)
        
        if total_size_mb > 100:
            suggestions.append("项目总大小超过100MB，建议压缩资源文件")
        
        if file_count > 1000:
            suggestions.append("文件数量过多，建议整理和合并小文件")
        
        if avg_file_size_kb > 5000:
            suggestions.append("平均文件大小较大，建议优化大文件")
        
        if not suggestions:
            suggestions.append("项目结构良好，无需特殊优化")
        
        return suggestions
