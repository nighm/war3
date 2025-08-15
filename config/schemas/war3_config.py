#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
War3配置模式
定义War3相关的配置数据结构
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from pathlib import Path
from enum import Enum


class War3Version(Enum):
    """War3版本枚举"""
    CLASSIC = "classic"  # 经典版
    REIGN_OF_CHAOS = "roc"  # 混乱之治
    FROZEN_THRONE = "tft"  # 冰封王座
    REFORGED = "reforged"  # 重制版


class MapType(Enum):
    """地图类型枚举"""
    MELEE = "melee"  # 对战
    RPG = "rpg"  # 角色扮演
    TD = "td"  # 塔防
    AOS = "aos"  # 竞技场
    CUSTOM = "custom"  # 自定义


@dataclass
class War3Config:
    """War3配置类"""
    
    # 基础路径配置
    installation_path: Optional[Path] = None
    world_editor_path: Optional[Path] = None
    jngp_path: Optional[Path] = None
    maps_directory: Optional[Path] = None
    
    # 版本配置
    version: War3Version = War3Version.FROZEN_THRONE
    custom_patch: Optional[str] = None
    
    # 编辑器配置
    editor_type: str = "world_editor"  # world_editor, y3_editor, jngp
    editor_path: Optional[Path] = None
    
    # 地图配置
    default_map_type: MapType = MapType.MELEE
    default_map_size: str = "128x128"
    default_tileset: str = "Lordaeron Summer"
    default_players: int = 4
    
    # 资源配置
    custom_models: List[Path] = field(default_factory=list)
    custom_textures: List[Path] = field(default_factory=list)
    custom_sounds: List[Path] = field(default_factory=list)
    custom_scripts: List[Path] = field(default_factory=list)
    
    # 性能配置
    enable_optimization: bool = True
    enable_compression: bool = True
    max_file_size: int = 8 * 1024 * 1024  # 8MB
    
    # 兼容性配置
    backward_compatibility: bool = True
    support_old_versions: bool = True
    
    def __post_init__(self):
        """初始化后处理"""
        # 自动检测路径
        if self.installation_path is None:
            self._detect_installation_path()
        
        if self.world_editor_path is None and self.installation_path:
            self._detect_world_editor_path()
        
        if self.maps_directory is None and self.installation_path:
            self._detect_maps_directory()
    
    def _detect_installation_path(self):
        """自动检测War3安装路径"""
        # 优先从环境变量读取
        import os
        env_path = os.getenv('WAR3_INSTALLATION_PATH')
        if env_path and Path(env_path).exists():
            self.installation_path = Path(env_path)
            return
        
        # 从配置文件读取
        # 这里应该通过配置管理器获取，而不是硬编码
        # 如果都没有配置，则设置为None，由用户手动配置
        
        # 注释掉硬编码的路径检测，改为提示用户配置
        # possible_paths = [
        #     Path("C:\\Program Files\\Warcraft III"),
        #     Path("C:\\Program Files (x86)\\Warcraft III"),
        #     Path("D:\\Program Files\\Warcraft III"),
        #     Path("D:\\Program Files (x86)\\Warcraft III"),
        # ]
        # 
        # for path in possible_paths:
        #     if path.exists() and (path / "Warcraft III.exe").exists():
        #         self.installation_path = path
        #         break
        
        # 提示用户需要配置路径
        self.installation_path = None
    
    def _detect_world_editor_path(self):
        """自动检测World Editor路径"""
        if self.installation_path:
            world_editor_path = self.installation_path / "World Editor.exe"
            if world_editor_path.exists():
                self.world_editor_path = world_editor_path
    
    def _detect_maps_directory(self):
        """自动检测地图目录"""
        if self.installation_path:
            maps_dir = self.installation_path / "Maps"
            if maps_dir.exists():
                self.maps_directory = maps_dir
    
    def validate_paths(self) -> List[str]:
        """验证路径配置"""
        errors = []
        
        if self.installation_path and not self.installation_path.exists():
            errors.append(f"War3安装路径不存在: {self.installation_path}")
        
        if self.world_editor_path and not self.world_editor_path.exists():
            errors.append(f"World Editor路径不存在: {self.world_editor_path}")
        
        if self.maps_directory and not self.maps_directory.exists():
            errors.append(f"地图目录不存在: {self.maps_directory}")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, Path):
                result[field_name] = str(field_value)
            elif isinstance(field_value, Enum):
                result[field_name] = field_value.value
            elif isinstance(field_value, list):
                result[field_name] = [str(p) if isinstance(p, Path) else p for p in field_value]
            else:
                result[field_name] = field_value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'War3Config':
        """从字典创建配置"""
        # 处理路径字段
        path_fields = ['installation_path', 'world_editor_path', 'jngp_path', 'maps_directory']
        for field_name in path_fields:
            if field_name in data and data[field_name]:
                data[field_name] = Path(data[field_name])
        
        # 处理枚举字段
        if 'version' in data and data['version']:
            data['version'] = War3Version(data['version'])
        
        if 'default_map_type' in data and data['default_map_type']:
            data['default_map_type'] = MapType(data['default_map_type'])
        
        # 处理列表字段
        list_fields = ['custom_models', 'custom_textures', 'custom_sounds', 'custom_scripts']
        for field_name in list_fields:
            if field_name in data and data[field_name]:
                data[field_name] = [Path(p) for p in data[field_name]]
        
        return cls(**data)
