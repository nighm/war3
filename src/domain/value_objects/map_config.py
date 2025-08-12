#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地图配置值对象
不可变的地图配置信息
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from pathlib import Path


@dataclass(frozen=True)
class MapConfig:
    """地图配置值对象"""
    
    # 基础配置
    map_name: str
    map_description: str
    map_author: str
    map_version: str = "1.0.0"
    
    # 游戏设置
    max_players: int = 12
    game_type: str = "melee"  # melee, custom, campaign
    difficulty: str = "normal"  # easy, normal, hard
    
    # 地图设置
    map_size: str = "medium"  # small, medium, large, extra_large
    terrain_type: str = "forest"  # forest, desert, snow, city, etc.
    weather_effects: bool = False
    
    # 资源设置
    starting_gold: int = 1000
    starting_lumber: int = 200
    starting_food: int = 5
    
    # 编辑器设置
    editor_version: str = "1.0.0"
    custom_scripts: bool = False
    custom_models: bool = False
    
    # 扩展配置
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """验证配置值"""
        if self.max_players < 1 or self.max_players > 12:
            raise ValueError("玩家数量必须在1-12之间")
        
        if self.starting_gold < 0:
            raise ValueError("初始金币不能为负数")
        
        if self.starting_lumber < 0:
            raise ValueError("初始木材不能为负数")
        
        if self.starting_food < 0:
            raise ValueError("初始人口不能为负数")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """获取自定义设置"""
        return self.custom_settings.get(key, default)
    
    def has_setting(self, key: str) -> bool:
        """检查是否有指定设置"""
        return key in self.custom_settings
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "map_name": self.map_name,
            "map_description": self.map_description,
            "map_author": self.map_author,
            "map_version": self.map_version,
            "max_players": self.max_players,
            "game_type": self.game_type,
            "difficulty": self.difficulty,
            "map_size": self.map_size,
            "terrain_type": self.terrain_type,
            "weather_effects": self.weather_effects,
            "starting_gold": self.starting_gold,
            "starting_lumber": self.starting_lumber,
            "starting_food": self.starting_food,
            "editor_version": self.editor_version,
            "custom_scripts": self.custom_scripts,
            "custom_models": self.custom_models,
            "custom_settings": self.custom_settings.copy()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MapConfig':
        """从字典创建实例"""
        return cls(**data)
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"MapConfig({self.map_name}, {self.map_author}, v{self.map_version})"
