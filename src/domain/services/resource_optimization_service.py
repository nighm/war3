#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资源优化领域服务
负责地图资源的优化和压缩
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import shutil
import zipfile
import json

from ..entities.map_project import MapProject


class OptimizationType(Enum):
    """优化类型枚举"""
    COMPRESSION = "compression"
    DEDUPLICATION = "deduplication"
    CLEANUP = "cleanup"
    CONVERSION = "conversion"


class OptimizationLevel(Enum):
    """优化级别枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CUSTOM = "custom"


@dataclass
class OptimizationResult:
    """优化结果"""
    optimization_type: OptimizationType
    original_size: int
    optimized_size: int
    saved_space: int
    optimization_level: OptimizationLevel
    details: Dict[str, Any]
    
    @property
    def compression_ratio(self) -> float:
        """计算压缩比"""
        if self.original_size == 0:
            return 0.0
        return (1 - self.optimized_size / self.original_size) * 100
    
    @property
    def is_effective(self) -> bool:
        """优化是否有效"""
        return self.saved_space > 0


class ResourceOptimizationService(ABC):
    """资源优化服务接口"""
    
    @abstractmethod
    def optimize_project(self, project: MapProject, 
                        optimization_type: OptimizationType,
                        level: OptimizationLevel = OptimizationLevel.MEDIUM,
                        **kwargs) -> OptimizationResult:
        """优化项目资源"""
        pass
    
    @abstractmethod
    def get_optimization_suggestions(self, project: MapProject) -> List[str]:
        """获取优化建议"""
        pass
    
    @abstractmethod
    def can_optimize(self, project: MapProject, 
                     optimization_type: OptimizationType) -> bool:
        """检查是否可以优化"""
        pass


class DefaultResourceOptimizationService(ResourceOptimizationService):
    """默认资源优化服务实现"""
    
    def __init__(self):
        """初始化优化服务"""
        self.optimization_history: List[OptimizationResult] = []
    
    def optimize_project(self, project: MapProject, 
                        optimization_type: OptimizationType,
                        level: OptimizationLevel = OptimizationLevel.MEDIUM,
                        **kwargs) -> OptimizationResult:
        """优化项目资源"""
        if not self.can_optimize(project, optimization_type):
            raise ValueError(f"项目 '{project.name}' 不支持 {optimization_type.value} 优化")
        
        # 计算原始大小
        original_size = self._calculate_project_size(project.project_path)
        
        # 执行优化
        if optimization_type == OptimizationType.COMPRESSION:
            optimized_size = self._compress_project(project, level, **kwargs)
        elif optimization_type == OptimizationType.DEDUPLICATION:
            optimized_size = self._deduplicate_resources(project, level, **kwargs)
        elif optimization_type == OptimizationType.CLEANUP:
            optimized_size = self._cleanup_project(project, level, **kwargs)
        elif optimization_type == OptimizationType.CONVERSION:
            optimized_size = self._convert_resources(project, level, **kwargs)
        else:
            raise ValueError(f"不支持的优化类型: {optimization_type}")
        
        # 创建优化结果
        result = OptimizationResult(
            optimization_type=optimization_type,
            original_size=original_size,
            optimized_size=optimized_size,
            saved_space=original_size - optimized_size,
            optimization_level=level,
            details=self._get_optimization_details(project, optimization_type, level)
        )
        
        # 记录优化历史
        self.optimization_history.append(result)
        
        return result
    
    def get_optimization_suggestions(self, project: MapProject) -> List[str]:
        """获取优化建议"""
        suggestions = []
        
        if not project.project_path.exists():
            return ["项目路径不存在，无法提供优化建议"]
        
        # 分析项目大小
        project_size = self._calculate_project_size(project.project_path)
        if project_size > 100 * 1024 * 1024:  # 100MB
            suggestions.append("项目大小超过100MB，建议进行压缩优化")
        
        # 分析文件类型分布
        file_types = self._analyze_file_types(project.project_path)
        
        # 检查是否有重复文件
        duplicate_files = self._find_duplicate_files(project.project_path)
        if duplicate_files:
            suggestions.append(f"发现 {len(duplicate_files)} 个重复文件，建议进行去重优化")
        
        # 检查临时文件
        temp_files = self._find_temp_files(project.project_path)
        if temp_files:
            suggestions.append(f"发现 {len(temp_files)} 个临时文件，建议进行清理优化")
        
        # 检查资源文件格式
        resource_files = self._find_resource_files(project.project_path)
        if resource_files.get('large_textures', 0) > 0:
            suggestions.append("发现大尺寸纹理文件，建议转换为压缩格式")
        
        if not suggestions:
            suggestions.append("项目结构良好，无需特殊优化")
        
        return suggestions
    
    def can_optimize(self, project: MapProject, 
                     optimization_type: OptimizationType) -> bool:
        """检查是否可以优化"""
        if not project.project_path.exists():
            return False
        
        if optimization_type == OptimizationType.COMPRESSION:
            return self._has_compressible_files(project.project_path)
        elif optimization_type == OptimizationType.DEDUPLICATION:
            return self._has_duplicate_files(project.project_path)
        elif optimization_type == OptimizationType.CLEANUP:
            return self._has_cleanup_targets(project.project_path)
        elif optimization_type == OptimizationType.CONVERSION:
            return self._has_convertible_files(project.project_path)
        
        return False
    
    def get_optimization_history(self) -> List[OptimizationResult]:
        """获取优化历史"""
        return self.optimization_history.copy()
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """获取优化统计信息"""
        if not self.optimization_history:
            return {
                "total_optimizations": 0,
                "total_saved_space": 0,
                "average_compression_ratio": 0.0
            }
        
        total_optimizations = len(self.optimization_history)
        total_saved_space = sum(r.saved_space for r in self.optimization_history)
        
        # 计算平均压缩比
        effective_optimizations = [r for r in self.optimization_history if r.is_effective]
        if effective_optimizations:
            avg_compression_ratio = sum(r.compression_ratio for r in effective_optimizations) / len(effective_optimizations)
        else:
            avg_compression_ratio = 0.0
        
        return {
            "total_optimizations": total_optimizations,
            "total_saved_space": total_saved_space,
            "total_saved_space_mb": round(total_saved_space / (1024 * 1024), 2),
            "average_compression_ratio": round(avg_compression_ratio, 2),
            "effective_optimizations": len(effective_optimizations)
        }
    
    def _compress_project(self, project: MapProject, level: OptimizationLevel, **kwargs) -> int:
        """压缩项目"""
        compression_levels = {
            OptimizationLevel.LOW: 1,
            OptimizationLevel.MEDIUM: 6,
            OptimizationLevel.HIGH: 9
        }
        
        compression_level = compression_levels.get(level, 6)
        
        # 创建压缩文件
        archive_path = project.project_path.parent / f"{project.name}_optimized.zip"
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zipf:
            for file_path in project.project_path.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(project.project_path)
                    zipf.write(file_path, arcname)
        
        return archive_path.stat().st_size
    
    def _deduplicate_resources(self, project: MapProject, level: OptimizationLevel, **kwargs) -> int:
        """去重资源"""
        duplicate_files = self._find_duplicate_files(project.project_path)
        total_saved = 0
        
        for file_hash, files in duplicate_files.items():
            if len(files) > 1:
                # 保留第一个文件，删除其他重复文件
                for duplicate_file in files[1:]:
                    try:
                        file_size = duplicate_file.stat().st_size
                        duplicate_file.unlink()
                        total_saved += file_size
                    except Exception:
                        continue
        
        # 重新计算项目大小
        return self._calculate_project_size(project.project_path)
    
    def _cleanup_project(self, project: MapProject, level: OptimizationLevel, **kwargs) -> int:
        """清理项目"""
        temp_files = self._find_temp_files(project.project_path)
        total_saved = 0
        
        for temp_file in temp_files:
            try:
                file_size = temp_file.stat().st_size
                temp_file.unlink()
                total_saved += file_size
            except Exception:
                continue
        
        # 重新计算项目大小
        return self._calculate_project_size(project.project_path)
    
    def _convert_resources(self, project: MapProject, level: OptimizationLevel, **kwargs) -> int:
        """转换资源格式"""
        # 这里可以实现资源格式转换逻辑
        # 例如：将大尺寸纹理转换为压缩格式
        # 暂时返回原始大小
        return self._calculate_project_size(project.project_path)
    
    def _calculate_project_size(self, path: Path) -> int:
        """计算项目大小（字节）"""
        try:
            return sum(
                f.stat().st_size for f in path.rglob("*") 
                if f.is_file()
            )
        except Exception:
            return 0
    
    def _analyze_file_types(self, path: Path) -> Dict[str, int]:
        """分析文件类型分布"""
        file_types = {}
        
        for file_path in path.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + 1
        
        return file_types
    
    def _find_duplicate_files(self, path: Path) -> Dict[str, List[Path]]:
        """查找重复文件"""
        import hashlib
        
        file_hashes = {}
        
        for file_path in path.rglob("*"):
            if file_path.is_file():
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                        if file_hash not in file_hashes:
                            file_hashes[file_hash] = []
                        file_hashes[file_hash].append(file_path)
                except Exception:
                    continue
        
        # 只返回有重复的文件
        return {k: v for k, v in file_hashes.items() if len(v) > 1}
    
    def _find_temp_files(self, path: Path) -> List[Path]:
        """查找临时文件"""
        temp_extensions = ['.tmp', '.temp', '.log', '.cache', '.bak', '.old']
        temp_files = []
        
        for file_path in path.rglob("*"):
            if file_path.is_file():
                if file_path.suffix.lower() in temp_extensions:
                    temp_files.append(file_path)
        
        return temp_files
    
    def _find_resource_files(self, path: Path) -> Dict[str, int]:
        """查找资源文件"""
        resource_patterns = {
            'large_textures': ['.tga', '.png', '.jpg', '.jpeg'],
            'models': ['.mdx', '.mdl', '.3ds', '.obj'],
            'sounds': ['.wav', '.mp3', '.ogg'],
            'scripts': ['.lua', '.j', '.js']
        }
        
        resource_files = {}
        
        for category, extensions in resource_patterns.items():
            count = 0
            for ext in extensions:
                count += len(list(path.rglob(f"*{ext}")))
                count += len(list(path.rglob(f"*{ext.upper()}")))
            resource_files[category] = count
        
        return resource_files
    
    def _has_compressible_files(self, path: Path) -> bool:
        """检查是否有可压缩文件"""
        compressible_extensions = ['.txt', '.json', '.xml', '.md', '.py', '.js', '.css', '.html']
        
        for ext in compressible_extensions:
            if list(path.rglob(f"*{ext}")):
                return True
        return False
    
    def _has_duplicate_files(self, path: Path) -> bool:
        """检查是否有重复文件"""
        duplicate_files = self._find_duplicate_files(path)
        return len(duplicate_files) > 0
    
    def _has_cleanup_targets(self, path: Path) -> bool:
        """检查是否有清理目标"""
        temp_files = self._find_temp_files(path)
        return len(temp_files) > 0
    
    def _has_convertible_files(self, path: Path) -> bool:
        """检查是否有可转换文件"""
        # 这里可以添加更多可转换的文件类型检查
        return False
    
    def _get_optimization_details(self, project: MapProject, 
                                 optimization_type: OptimizationType,
                                 level: OptimizationLevel) -> Dict[str, Any]:
        """获取优化详情"""
        return {
            "project_name": project.name,
            "project_type": project.project_type,
            "optimization_type": optimization_type.value,
            "optimization_level": level.value,
            "timestamp": project.updated_at.isoformat()
        }
