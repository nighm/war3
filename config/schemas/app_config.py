#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用配置模式
整合所有配置组件，提供统一的配置接口
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from pathlib import Path
from .war3_config import War3Config
from .editor_config import EditorConfig
from ..settings.base import BaseConfig


@dataclass
class AppConfig:
    """应用配置类"""
    
    # 基础配置
    base: BaseConfig = field(default_factory=BaseConfig)
    
    # 组件配置
    war3: War3Config = field(default_factory=War3Config)
    editor: EditorConfig = field(default_factory=EditorConfig)
    
    # 项目配置
    project: Dict[str, Any] = field(default_factory=dict)
    
    # 开发配置
    development: Dict[str, Any] = field(default_factory=dict)
    
    # 界面配置
    interface: Dict[str, Any] = field(default_factory=dict)
    
    # 工具配置
    tools: Dict[str, Any] = field(default_factory=dict)
    
    # 环境标识
    environment: str = "development"
    
    def __post_init__(self):
        """初始化后处理"""
        # 设置基础目录引用
        if self.base.base_dir:
            self.war3.base_dir = self.base.base_dir
            self.editor.base_dir = self.base.base_dir
        
        # 设置默认项目配置
        if not self.project:
            self.project = self._get_default_project_config()
        
        # 设置默认开发配置
        if not self.development:
            self.development = self._get_default_development_config()
        
        # 设置默认界面配置
        if not self.interface:
            self.interface = self._get_default_interface_config()
        
        # 设置默认工具配置
        if not self.tools:
            self.tools = self._get_default_tools_config()
    
    def _get_default_project_config(self) -> Dict[str, Any]:
        """获取默认项目配置"""
        return {
            "default_type": "rpg",
            "auto_backup": True,
            "version_control": True,
            "template_directory": str(self.base.base_dir / "templates") if self.base.base_dir else "",
            "output_directory": str(self.base.base_dir / "output") if self.base.base_dir else "",
        }
    
    def _get_default_development_config(self) -> Dict[str, Any]:
        """获取默认开发配置"""
        return {
            "log_level": "INFO",
            "debug_mode": False,
            "test_mode": False,
            "enable_profiling": False,
            "enable_memory_tracking": False,
        }
    
    def _get_default_interface_config(self) -> Dict[str, Any]:
        """获取默认界面配置"""
        return {
            "language": "zh_CN",
            "theme": "default",
            "window_size": [1200, 800],
            "window_position": [100, 100],
            "show_toolbar": True,
            "show_statusbar": True,
        }
    
    def _get_default_tools_config(self) -> Dict[str, Any]:
        """获取默认工具配置"""
        return {
            "map_optimization": True,
            "resource_compression": True,
            "auto_test": False,
            "code_quality_check": True,
            "performance_monitoring": True,
        }
    
    def validate_all(self) -> Dict[str, List[str]]:
        """验证所有配置"""
        validation_results = {}
        
        # 验证基础配置
        base_errors = self._validate_base_config()
        if base_errors:
            validation_results['base'] = base_errors
        
        # 验证War3配置
        war3_errors = self.war3.validate_paths()
        if war3_errors:
            validation_results['war3'] = war3_errors
        
        # 验证编辑器配置
        editor_errors = self.editor.validate_config()
        if editor_errors:
            validation_results['editor'] = editor_errors
        
        # 验证项目配置
        project_errors = self._validate_project_config()
        if project_errors:
            validation_results['project'] = project_errors
        
        # 验证开发配置
        development_errors = self._validate_development_config()
        if development_errors:
            validation_results['development'] = development_errors
        
        return validation_results
    
    def _validate_base_config(self) -> List[str]:
        """验证基础配置"""
        errors = []
        
        if not self.base.app_name:
            errors.append("应用名称不能为空")
        
        if not self.base.app_version:
            errors.append("应用版本不能为空")
        
        if self.base.log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            errors.append("日志级别无效")
        
        return errors
    
    def _validate_project_config(self) -> List[str]:
        """验证项目配置"""
        errors = []
        
        if 'default_type' in self.project:
            valid_types = ['rpg', 'melee', 'td', 'aos', 'custom']
            if self.project['default_type'] not in valid_types:
                errors.append(f"项目类型无效: {self.project['default_type']}")
        
        return errors
    
    def _validate_development_config(self) -> List[str]:
        """验证开发配置"""
        errors = []
        
        if 'log_level' in self.development:
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if self.development['log_level'] not in valid_levels:
                errors.append(f"开发日志级别无效: {self.development['log_level']}")
        
        return errors
    
    def is_valid(self) -> bool:
        """检查配置是否有效"""
        validation_results = self.validate_all()
        return len(validation_results) == 0
    
    def get_errors(self) -> List[str]:
        """获取所有错误信息"""
        validation_results = self.validate_all()
        errors = []
        for component, component_errors in validation_results.items():
            for error in component_errors:
                errors.append(f"[{component}] {error}")
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'base': self.base.to_dict(),
            'war3': self.war3.to_dict(),
            'editor': self.editor.to_dict(),
            'project': self.project,
            'development': self.development,
            'interface': self.interface,
            'tools': self.tools,
            'environment': self.environment,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppConfig':
        """从字典创建配置"""
        # 处理基础配置
        base_data = data.get('base', {})
        base_config = BaseConfig.from_dict(base_data)
        
        # 处理War3配置
        war3_data = data.get('war3', {})
        war3_config = War3Config.from_dict(war3_data)
        
        # 处理编辑器配置
        editor_data = data.get('editor', {})
        editor_config = EditorConfig.from_dict(editor_data)
        
        return cls(
            base=base_config,
            war3=war3_config,
            editor=editor_config,
            project=data.get('project', {}),
            development=data.get('development', {}),
            interface=data.get('interface', {}),
            tools=data.get('tools', {}),
            environment=data.get('environment', 'development'),
        )
    
    def merge_with(self, other: 'AppConfig') -> 'AppConfig':
        """与其他配置合并"""
        # 创建新的配置对象
        merged = AppConfig()
        
        # 合并基础配置
        merged.base = self.base
        if other.base:
            # 这里可以实现更复杂的合并逻辑
            pass
        
        # 合并组件配置
        merged.war3 = other.war3 if other.war3 else self.war3
        merged.editor = other.editor if other.editor else self.editor
        
        # 合并字典配置
        merged.project = {**self.project, **other.project}
        merged.development = {**self.development, **other.development}
        merged.interface = {**self.interface, **other.interface}
        merged.tools = {**self.tools, **other.tools}
        
        # 环境配置
        merged.environment = other.environment if other.environment else self.environment
        
        return merged
