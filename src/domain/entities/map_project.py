#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地图项目实体
负责管理地图项目的核心业务逻辑
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4


@dataclass
class MapProject:
    """地图项目实体"""
    
    # 核心属性
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    project_type: str = "rpg"  # rpg, td, moba, survival, melee
    description: str = ""
    
    # 路径信息
    project_path: Path = field(default_factory=Path)
    source_path: Path = field(default_factory=Path)
    output_path: Path = field(default_factory=Path)
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    
    # 配置信息
    config: Dict[str, Any] = field(default_factory=dict)
    
    # 资源信息
    resources: Dict[str, List[str]] = field(default_factory=dict)
    
    # 状态信息
    is_active: bool = True
    is_archived: bool = False
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.project_path:
            self.project_path = Path.cwd() / self.name
    
    def update_project_info(self, **kwargs) -> None:
        """更新项目信息"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def add_resource(self, resource_type: str, resource_path: str) -> None:
        """添加资源"""
        if resource_type not in self.resources:
            self.resources[resource_type] = []
        if resource_path not in self.resources[resource_type]:
            self.resources[resource_type].append(resource_path)
    
    def remove_resource(self, resource_type: str, resource_path: str) -> bool:
        """移除资源"""
        if resource_type in self.resources and resource_path in self.resources[resource_type]:
            self.resources[resource_type].remove(resource_path)
            return True
        return False
    
    def get_resource_count(self, resource_type: str) -> int:
        """获取指定类型资源数量"""
        return len(self.resources.get(resource_type, []))
    
    def archive_project(self) -> None:
        """归档项目"""
        self.is_archived = True
        self.is_active = False
        self.updated_at = datetime.now()
    
    def activate_project(self) -> None:
        """激活项目"""
        self.is_archived = False
        self.is_active = True
        self.updated_at = datetime.now()
    
    def validate_project(self) -> List[str]:
        """验证项目完整性"""
        errors = []
        
        if not self.name:
            errors.append("项目名称不能为空")
        
        if not self.project_path.exists():
            errors.append("项目路径不存在")
        
        if self.project_type not in ["rpg", "td", "moba", "survival", "melee"]:
            errors.append("无效的项目类型")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": str(self.id),
            "name": self.name,
            "project_type": self.project_type,
            "description": self.description,
            "project_path": str(self.project_path),
            "source_path": str(self.source_path),
            "output_path": str(self.output_path),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "config": self.config,
            "resources": self.resources,
            "is_active": self.is_active,
            "is_archived": self.is_archived
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MapProject':
        """从字典创建实例"""
        # 处理路径
        if "project_path" in data:
            data["project_path"] = Path(data["project_path"])
        if "source_path" in data:
            data["source_path"] = Path(data["source_path"])
        if "output_path" in data:
            data["output_path"] = Path(data["output_path"])
        
        # 处理时间
        if "created_at" in data:
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        
        # 处理UUID
        if "id" in data:
            data["id"] = UUID(data["id"])
        
        return cls(**data)
