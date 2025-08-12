#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础配置类
定义所有环境共享的配置项
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pathlib import Path


@dataclass
class BaseConfig:
    """基础配置类"""
    
    # 应用基本信息
    app_name: str = "War3 Map Studio"
    app_version: str = "1.3.0"
    app_description: str = "魔兽争霸3地图开发工作室"
    
    # 基础路径配置
    base_dir: Optional[Path] = None
    config_dir: Optional[Path] = None
    logs_dir: Optional[Path] = None
    temp_dir: Optional[Path] = None
    
    # 日志配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "war3_studio.log"
    log_max_size: int = 10 * 1024 * 1024  # 10MB
    log_backup_count: int = 5
    
    # 界面配置
    language: str = "zh_CN"
    theme: str = "default"
    window_size: tuple = (1200, 800)
    window_position: tuple = (100, 100)
    
    # 工具配置
    map_optimization: bool = True
    resource_compression: bool = True
    auto_test: bool = False
    
    def __post_init__(self):
        """初始化后处理"""
        if self.base_dir is None:
            # 自动检测项目根目录
            import sys
            if hasattr(sys, '_getframe'):
                frame = sys._getframe(1)
                while frame:
                    if frame.f_code.co_name == '<module>':
                        self.base_dir = Path(frame.f_code.co_filename).parent
                        break
                    frame = frame.f_back
        
        if self.config_dir is None and self.base_dir:
            self.config_dir = self.base_dir / "config"
        
        if self.logs_dir is None and self.base_dir:
            self.logs_dir = self.base_dir / "logs"
        
        if self.temp_dir is None and self.base_dir:
            self.temp_dir = self.base_dir / "temp"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, Path):
                result[field_name] = str(field_value)
            else:
                result[field_name] = field_value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseConfig':
        """从字典创建配置"""
        # 处理路径字段
        if 'base_dir' in data and data['base_dir']:
            data['base_dir'] = Path(data['base_dir'])
        if 'config_dir' in data and data['config_dir']:
            data['config_dir'] = Path(data['config_dir'])
        if 'logs_dir' in data and data['logs_dir']:
            data['logs_dir'] = Path(data['logs_dir'])
        if 'temp_dir' in data and data['temp_dir']:
            data['temp_dir'] = Path(data['temp_dir'])
        
        return cls(**data)
