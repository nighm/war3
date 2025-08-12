#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地图项目仓储接口
定义地图项目的持久化操作
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from pathlib import Path

from ..entities.map_project import MapProject


class MapRepository(ABC):
    """地图项目仓储接口"""
    
    @abstractmethod
    def save(self, project: MapProject) -> bool:
        """保存地图项目"""
        pass
    
    @abstractmethod
    def find_by_id(self, project_id: UUID) -> Optional[MapProject]:
        """根据ID查找地图项目"""
        pass
    
    @abstractmethod
    def find_by_name(self, name: str) -> Optional[MapProject]:
        """根据名称查找地图项目"""
        pass
    
    @abstractmethod
    def find_by_path(self, path: Path) -> Optional[MapProject]:
        """根据路径查找地图项目"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[MapProject]:
        """查找所有地图项目"""
        pass
    
    @abstractmethod
    def find_by_type(self, project_type: str) -> List[MapProject]:
        """根据类型查找地图项目"""
        pass
    
    @abstractmethod
    def find_active(self) -> List[MapProject]:
        """查找所有活跃项目"""
        pass
    
    @abstractmethod
    def find_archived(self) -> List[MapProject]:
        """查找所有归档项目"""
        pass
    
    @abstractmethod
    def delete(self, project_id: UUID) -> bool:
        """删除地图项目"""
        pass
    
    @abstractmethod
    def exists(self, project_id: UUID) -> bool:
        """检查项目是否存在"""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """获取项目总数"""
        pass
    
    @abstractmethod
    def search(self, query: str) -> List[MapProject]:
        """搜索地图项目"""
        pass
    
    @abstractmethod
    def get_project_stats(self) -> Dict[str, Any]:
        """获取项目统计信息"""
        pass
