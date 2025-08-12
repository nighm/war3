#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目服务应用层
协调领域服务和基础设施层，实现业务用例
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import json
import shutil

from ...domain.entities.map_project import MapProject
from ...domain.value_objects.map_config import MapConfig
from ...domain.repositories.map_repository import MapRepository
from ...domain.services.map_analysis_service import MapAnalysisService
from ...domain.services.batch_processor import DefaultBatchProcessor, ProcessingRule
from ..use_cases.batch_process_maps import BatchProcessMapsUseCase


class ProjectService:
    """项目服务应用层"""
    
    def __init__(self, 
                 map_repository: MapRepository,
                 analysis_service: MapAnalysisService):
        """初始化项目服务"""
        self.map_repository = map_repository
        self.analysis_service = analysis_service
        
        # 初始化批量处理器
        self.batch_processor = DefaultBatchProcessor()
        self.batch_use_case = BatchProcessMapsUseCase(map_repository, self.batch_processor)
    
    def create_project(self, name: str, project_type: str, 
                      description: str = "", base_path: Optional[Path] = None) -> Optional[MapProject]:
        """创建新项目"""
        try:
            # 验证项目名称
            if not name or not name.strip():
                raise ValueError("项目名称不能为空")
            
            # 检查项目是否已存在
            existing_project = self.map_repository.find_by_name(name)
            if existing_project:
                raise ValueError(f"项目 '{name}' 已存在")
            
            # 确定项目路径
            if base_path is None:
                base_path = Path.cwd()
            
            project_path = base_path / name
            
            # 创建项目目录
            if project_path.exists():
                raise ValueError(f"目录 '{project_path}' 已存在")
            
            project_path.mkdir(parents=True, exist_ok=True)
            
            # 创建项目配置
            config = MapConfig(
                map_name=name,
                map_description=description,
                map_author="Unknown",
                game_type="custom" if project_type != "melee" else "melee"
            )
            
            # 创建项目实体
            project = MapProject(
                name=name,
                project_type=project_type,
                description=description,
                project_path=project_path,
                source_path=project_path / "source",
                output_path=project_path / "output",
                config=config.to_dict()
            )
            
            # 创建标准目录结构
            self._create_project_structure(project_path, project_type)
            
            # 保存项目
            if self.map_repository.save(project):
                return project
            else:
                # 保存失败，清理目录
                shutil.rmtree(project_path, ignore_errors=True)
                raise RuntimeError("保存项目失败")
                
        except Exception as e:
            raise RuntimeError(f"创建项目失败: {str(e)}")
    
    def open_project(self, project_path: str) -> Optional[MapProject]:
        """打开现有项目"""
        try:
            path = Path(project_path)
            
            # 查找项目
            project = self.map_repository.find_by_path(path)
            if project:
                return project
            
            # 如果路径不存在，尝试从路径推断项目信息
            if path.exists() and path.is_dir():
                # 尝试从目录结构推断项目类型
                project_type = self._infer_project_type(path)
                
                # 创建临时项目对象
                project = MapProject(
                    name=path.name,
                    project_type=project_type,
                    project_path=path,
                    source_path=path / "source",
                    output_path=path / "output"
                )
                
                # 分析项目资源
                self._analyze_existing_project(project)
                
                return project
            
            return None
            
        except Exception as e:
            raise RuntimeError(f"打开项目失败: {str(e)}")
    
    def save_project(self, project: MapProject) -> bool:
        """保存项目"""
        try:
            return self.map_repository.save(project)
        except Exception as e:
            raise RuntimeError(f"保存项目失败: {str(e)}")
    
    def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        try:
            from uuid import UUID
            project_uuid = UUID(project_id)
            
            project = self.map_repository.find_by_id(project_uuid)
            if not project:
                return False
            
            # 删除项目目录
            if project.project_path.exists():
                shutil.rmtree(project.project_path, ignore_errors=True)
            
            # 从仓储中删除
            return self.map_repository.delete(project_uuid)
            
        except Exception as e:
            raise RuntimeError(f"删除项目失败: {str(e)}")
    
    def analyze_project(self, project: MapProject) -> Dict[str, Any]:
        """分析项目"""
        try:
            return {
                "structure": self.analysis_service.analyze_project_structure(project),
                "resources": self.analysis_service.analyze_resources(project),
                "performance": self.analysis_service.analyze_performance(project)
            }
        except Exception as e:
            raise RuntimeError(f"分析项目失败: {str(e)}")
    
    def generate_report(self, project: MapProject) -> str:
        """生成项目报告"""
        try:
            return self.analysis_service.generate_analysis_report(project)
        except Exception as e:
            raise RuntimeError(f"生成报告失败: {str(e)}")
    
    def list_projects(self, project_type: Optional[str] = None) -> List[MapProject]:
        """列出项目"""
        try:
            if project_type:
                return self.map_repository.find_by_type(project_type)
            else:
                return self.map_repository.find_all()
        except Exception as e:
            raise RuntimeError(f"列出项目失败: {str(e)}")
    
    def search_projects(self, query: str) -> List[MapProject]:
        """搜索项目"""
        try:
            return self.map_repository.search(query)
        except Exception as e:
            raise RuntimeError(f"搜索项目失败: {str(e)}")
    
    # 批量处理相关方法
    def batch_analyze_projects(self, rule: ProcessingRule = ProcessingRule.ALL, **kwargs):
        """批量分析项目"""
        try:
            return self.batch_use_case.batch_analyze_projects(rule, **kwargs)
        except Exception as e:
            raise RuntimeError(f"批量分析项目失败: {str(e)}")
    
    def batch_archive_projects(self, rule: ProcessingRule = ProcessingRule.ALL, **kwargs):
        """批量归档项目"""
        try:
            return self.batch_use_case.batch_archive_projects(rule, **kwargs)
        except Exception as e:
            raise RuntimeError(f"批量归档项目失败: {str(e)}")
    
    def batch_activate_projects(self, rule: ProcessingRule = ProcessingRule.ALL, **kwargs):
        """批量激活项目"""
        try:
            return self.batch_use_case.batch_activate_projects(rule, **kwargs)
        except Exception as e:
            raise RuntimeError(f"批量激活项目失败: {str(e)}")
    
    def batch_cleanup_projects(self, rule: ProcessingRule = ProcessingRule.ALL, **kwargs):
        """批量清理项目"""
        try:
            return self.batch_use_case.batch_cleanup_projects(rule, **kwargs)
        except Exception as e:
            raise RuntimeError(f"批量清理项目失败: {str(e)}")
    
    def batch_validate_projects(self, rule: ProcessingRule = ProcessingRule.ALL, **kwargs):
        """批量验证项目"""
        try:
            return self.batch_use_case.batch_validate_projects(rule, **kwargs)
        except Exception as e:
            raise RuntimeError(f"批量验证项目失败: {str(e)}")
    
    def get_batch_processing_stats(self):
        """获取批量处理统计信息"""
        try:
            return self.batch_use_case.get_processing_statistics()
        except Exception as e:
            raise RuntimeError(f"获取批量处理统计失败: {str(e)}")
    
    def _create_project_structure(self, project_path: Path, project_type: str) -> None:
        """创建项目目录结构"""
        # 创建标准目录
        directories = [
            "source",
            "output", 
            "resources",
            "docs",
            "tests"
        ]
        
        for directory in directories:
            (project_path / directory).mkdir(exist_ok=True)
        
        # 根据项目类型创建特定目录
        if project_type in ["rpg", "td", "moba"]:
            (project_path / "resources" / "models").mkdir(parents=True, exist_ok=True)
            (project_path / "resources" / "textures").mkdir(parents=True, exist_ok=True)
            (project_path / "resources" / "sounds").mkdir(parents=True, exist_ok=True)
            (project_path / "resources" / "scripts").mkdir(parents=True, exist_ok=True)
        
        # 创建配置文件
        config_file = project_path / "project_config.json"
        if not config_file.exists():
            default_config = {
                "project_name": project_path.name,
                "project_type": project_type,
                "version": "1.0.0",
                "description": "",
                "author": "Unknown"
            }
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
    
    def _infer_project_type(self, path: Path) -> str:
        """推断项目类型"""
        # 检查是否存在特定的文件或目录来推断类型
        if (path / "maps").exists():
            return "rpg"
        elif (path / "ai.json").exists():
            return "td"
        elif (path / "custom_eca").exists():
            return "moba"
        else:
            return "melee"
    
    def _analyze_existing_project(self, project: MapProject) -> None:
        """分析现有项目"""
        try:
            # 扫描项目目录，识别资源
            if project.project_path.exists():
                for file_path in project.project_path.rglob("*"):
                    if file_path.is_file():
                        # 根据文件扩展名分类资源
                        ext = file_path.suffix.lower()
                        if ext in ['.mdx', '.mdl', '.3ds', '.obj']:
                            project.add_resource("models", str(file_path.relative_to(project.project_path)))
                        elif ext in ['.blp', '.tga', '.png', '.jpg', '.jpeg']:
                            project.add_resource("textures", str(file_path.relative_to(project.project_path)))
                        elif ext in ['.wav', '.mp3', '.ogg']:
                            project.add_resource("sounds", str(file_path.relative_to(project.project_path)))
                        elif ext in ['.lua', '.j', '.js']:
                            project.add_resource("scripts", str(file_path.relative_to(project.project_path)))
                        elif ext in ['.w3m', '.w3x', '.gmp']:
                            project.add_resource("maps", str(file_path.relative_to(project.project_path)))
        except Exception:
            # 分析失败不影响项目打开
            pass
