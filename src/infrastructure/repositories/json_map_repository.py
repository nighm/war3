#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON文件存储的地图项目仓储实现
"""

import json
import shutil
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from uuid import UUID

from ...domain.entities.map_project import MapProject
from ...domain.repositories.map_repository import MapRepository


class JsonMapRepository(MapRepository):
    """JSON文件存储的地图项目仓储实现"""
    
    def __init__(self, storage_path: Path = None):
        """初始化仓储"""
        if storage_path is None:
            storage_path = Path.home() / ".war3studio" / "projects"
        
        self.storage_path = storage_path
        self.projects_file = storage_path / "projects.json"
        self.projects: Dict[str, MapProject] = {}
        
        # 确保存储目录存在
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 加载现有项目
        self._load_projects()
    
    def save(self, project: MapProject) -> bool:
        """保存地图项目"""
        try:
            # 更新项目
            self.projects[str(project.id)] = project
            
            # 保存到文件
            return self._save_projects()
            
        except Exception as e:
            print(f"保存项目失败: {e}")
            return False
    
    def find_by_id(self, project_id: UUID) -> Optional[MapProject]:
        """根据ID查找地图项目"""
        return self.projects.get(str(project_id))
    
    def find_by_name(self, name: str) -> Optional[MapProject]:
        """根据名称查找地图项目"""
        for project in self.projects.values():
            if project.name == name:
                return project
        return None
    
    def find_by_path(self, path: Path) -> Optional[MapProject]:
        """根据路径查找地图项目"""
        path_str = str(path.absolute())
        for project in self.projects.values():
            if str(project.project_path.absolute()) == path_str:
                return project
        return None
    
    def find_all(self) -> List[MapProject]:
        """查找所有地图项目"""
        return list(self.projects.values())
    
    def find_by_type(self, project_type: str) -> List[MapProject]:
        """根据类型查找地图项目"""
        return [p for p in self.projects.values() if p.project_type == project_type]
    
    def find_active(self) -> List[MapProject]:
        """查找所有活跃项目"""
        return [p for p in self.projects.values() if p.is_active and not p.is_archived]
    
    def find_archived(self) -> List[MapProject]:
        """查找所有归档项目"""
        return [p for p in self.projects.values() if p.is_archived]
    
    def delete(self, project_id: UUID) -> bool:
        """删除地图项目"""
        try:
            project_id_str = str(project_id)
            if project_id_str in self.projects:
                del self.projects[project_id_str]
                return self._save_projects()
            return False
            
        except Exception as e:
            print(f"删除项目失败: {e}")
            return False
    
    def exists(self, project_id: UUID) -> bool:
        """检查项目是否存在"""
        return str(project_id) in self.projects
    
    def count(self) -> int:
        """获取项目总数"""
        return len(self.projects)
    
    def search(self, query: str) -> List[MapProject]:
        """搜索地图项目"""
        query_lower = query.lower()
        results = []
        
        for project in self.projects.values():
            # 搜索项目名称
            if query_lower in project.name.lower():
                results.append(project)
                continue
            
            # 搜索项目描述
            if query_lower in project.description.lower():
                results.append(project)
                continue
            
            # 搜索项目类型
            if query_lower in project.project_type.lower():
                results.append(project)
                continue
        
        return results
    
    def get_project_stats(self) -> Dict[str, Any]:
        """获取项目统计信息"""
        total_projects = len(self.projects)
        active_projects = len(self.find_active())
        archived_projects = len(self.find_archived())
        
        # 按类型统计
        type_stats = {}
        for project in self.projects.values():
            project_type = project.project_type
            if project_type not in type_stats:
                type_stats[project_type] = 0
            type_stats[project_type] += 1
        
        return {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "archived_projects": archived_projects,
            "type_distribution": type_stats
        }
    
    def _load_projects(self) -> None:
        """从文件加载项目"""
        try:
            if self.projects_file.exists():
                with open(self.projects_file, 'r', encoding='utf-8') as f:
                    projects_data = json.load(f)
                
                for project_id, project_data in projects_data.items():
                    try:
                        project = MapProject.from_dict(project_data)
                        self.projects[project_id] = project
                    except Exception as e:
                        print(f"加载项目 {project_id} 失败: {e}")
                        continue
                        
        except Exception as e:
            print(f"加载项目文件失败: {e}")
            # 如果加载失败，创建新的空文件
            self._save_projects()
    
    def _save_projects(self) -> bool:
        """保存项目到文件"""
        try:
            # 准备数据
            projects_data = {}
            for project_id, project in self.projects.items():
                projects_data[project_id] = project.to_dict()
            
            # 写入文件
            with open(self.projects_file, 'w', encoding='utf-8') as f:
                json.dump(projects_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"保存项目文件失败: {e}")
            return False
    
    def backup_projects(self, backup_path: Path) -> bool:
        """备份项目数据"""
        try:
            if not backup_path.exists():
                backup_path.mkdir(parents=True, exist_ok=True)
            
            # 复制项目文件
            backup_file = backup_path / f"projects_backup_{int(time.time())}.json"
            shutil.copy2(self.projects_file, backup_file)
            
            return True
            
        except Exception as e:
            print(f"备份项目失败: {e}")
            return False
    
    def restore_projects(self, backup_file: Path) -> bool:
        """从备份恢复项目数据"""
        try:
            if not backup_file.exists():
                return False
            
            # 备份当前数据
            current_backup = self.storage_path / f"projects_backup_before_restore_{int(time.time())}.json"
            shutil.copy2(self.projects_file, current_backup)
            
            # 恢复备份数据
            shutil.copy2(backup_file, self.projects_file)
            
            # 重新加载
            self.projects.clear()
            self._load_projects()
            
            return True
            
        except Exception as e:
            print(f"恢复项目失败: {e}")
            return False
