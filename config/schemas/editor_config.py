#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编辑器配置模式
定义编辑器相关的配置数据结构
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from pathlib import Path
from enum import Enum


class EditorType(Enum):
    """编辑器类型枚举"""
    WORLD_EDITOR = "world_editor"  # 官方World Editor
    Y3_EDITOR = "y3_editor"        # Y3编辑器
    JNGP = "jngp"                  # JNGP编辑器
    CUSTOM = "custom"               # 自定义编辑器


class AutoSaveMode(Enum):
    """自动保存模式枚举"""
    DISABLED = "disabled"           # 禁用
    TIME_BASED = "time_based"      # 基于时间
    CHANGE_BASED = "change_based"  # 基于变更
    HYBRID = "hybrid"              # 混合模式


@dataclass
class EditorConfig:
    """编辑器配置类"""
    
    # 基础配置
    editor_type: EditorType = EditorType.Y3_EDITOR
    editor_path: Optional[Path] = None
    editor_name: str = "Y3 Editor"
    
    # 自动保存配置
    auto_save_enabled: bool = True
    auto_save_mode: AutoSaveMode = AutoSaveMode.TIME_BASED
    auto_save_interval: int = 5  # 分钟
    auto_save_on_change: bool = True
    auto_save_max_backups: int = 10
    
    # 备份配置
    backup_enabled: bool = True
    backup_interval: int = 10  # 分钟
    backup_directory: Optional[Path] = None
    backup_compression: bool = True
    backup_retention_days: int = 30
    
    # 界面配置
    theme: str = "default"
    language: str = "zh_CN"
    window_size: tuple = (1200, 800)
    window_position: tuple = (100, 100)
    fullscreen: bool = False
    
    # 编辑配置
    undo_levels: int = 50
    redo_levels: int = 50
    auto_complete: bool = True
    syntax_highlighting: bool = True
    line_numbers: bool = True
    
    # 性能配置
    enable_auto_save: bool = True
    enable_backup: bool = True
    enable_optimization: bool = True
    max_file_size: int = 16 * 1024 * 1024  # 16MB
    
    # 插件配置
    plugins_enabled: bool = True
    plugin_directory: Optional[Path] = None
    auto_load_plugins: bool = True
    
    # 快捷键配置
    custom_shortcuts: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理"""
        if self.backup_directory is None:
            self._setup_default_backup_directory()
        
        if self.plugin_directory is None:
            self._setup_default_plugin_directory()
    
    def _setup_default_backup_directory(self):
        """设置默认备份目录"""
        if hasattr(self, 'base_dir') and self.base_dir:
            self.backup_directory = self.base_dir / "backups" / "editor"
        else:
            # 使用当前工作目录
            import os
            self.backup_directory = Path.cwd() / "backups" / "editor"
    
    def _setup_default_plugin_directory(self):
        """设置默认插件目录"""
        if hasattr(self, 'base_dir') and self.base_dir:
            self.plugin_directory = self.base_dir / "plugins"
        else:
            # 使用当前工作目录
            import os
            self.plugin_directory = Path.cwd() / "plugins"
    
    def validate_config(self) -> List[str]:
        """验证配置"""
        errors = []
        
        # 验证编辑器路径
        if self.editor_path and not self.editor_path.exists():
            errors.append(f"编辑器路径不存在: {self.editor_path}")
        
        # 验证备份目录
        if self.backup_directory and not self.backup_directory.exists():
            try:
                self.backup_directory.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"无法创建备份目录: {e}")
        
        # 验证插件目录
        if self.plugin_directory and not self.plugin_directory.exists():
            try:
                self.plugin_directory.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"无法创建插件目录: {e}")
        
        # 验证数值范围
        if self.auto_save_interval < 1:
            errors.append("自动保存间隔不能小于1分钟")
        
        if self.backup_interval < 1:
            errors.append("备份间隔不能小于1分钟")
        
        if self.undo_levels < 1:
            errors.append("撤销级别不能小于1")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, Path):
                result[field_name] = str(field_value)
            elif isinstance(field_value, Enum):
                result[field_name] = field_value.value
            elif isinstance(field_value, tuple):
                result[field_name] = list(field_value)
            else:
                result[field_name] = field_value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EditorConfig':
        """从字典创建配置"""
        # 处理路径字段
        path_fields = ['editor_path', 'backup_directory', 'plugin_directory']
        for field_name in path_fields:
            if field_name in data and data[field_name]:
                data[field_name] = Path(data[field_name])
        
        # 处理枚举字段
        if 'editor_type' in data and data['editor_type']:
            data['editor_type'] = EditorType(data['editor_type'])
        
        if 'auto_save_mode' in data and data['auto_save_mode']:
            data['auto_save_mode'] = AutoSaveMode(data['auto_save_mode'])
        
        # 处理元组字段
        if 'window_size' in data and data['window_size']:
            data['window_size'] = tuple(data['window_size'])
        
        if 'window_position' in data and data['window_position']:
            data['window_position'] = tuple(data['window_position'])
        
        return cls(**data)
