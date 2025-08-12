#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开发环境配置
继承基础配置，添加开发环境特定配置
"""

from dataclasses import dataclass
from typing import Dict, Any
from pathlib import Path
from .base import BaseConfig


@dataclass
class DevelopmentConfig(BaseConfig):
    """开发环境配置"""
    
    # 开发环境标识
    environment: str = "development"
    
    # 开发模式配置
    debug_mode: bool = True
    test_mode: bool = True
    verbose_logging: bool = True
    
    # 日志配置（开发环境）
    log_level: str = "DEBUG"
    log_to_console: bool = True
    log_to_file: bool = True
    
    # 性能监控（开发环境）
    enable_profiling: bool = True
    enable_memory_tracking: bool = True
    enable_slow_query_log: bool = True
    
    # 开发工具配置
    auto_reload: bool = True
    hot_swap: bool = True
    development_tools: bool = True
    
    # 测试配置
    run_tests_on_startup: bool = False
    test_coverage: bool = True
    test_timeout: int = 30
    
    # 调试配置
    enable_breakpoints: bool = True
    enable_stack_traces: bool = True
    enable_variable_inspection: bool = True
    
    # 开发服务器配置
    dev_server_host: str = "localhost"
    dev_server_port: int = 8000
    dev_server_debug: bool = True
    
    # 数据库配置（开发环境）
    database_url: str = "sqlite:///./dev.db"
    database_echo: bool = True
    database_pool_size: int = 5
    
    # 缓存配置（开发环境）
    cache_backend: str = "memory"
    cache_ttl: int = 300  # 5分钟
    
    def __post_init__(self):
        """初始化后处理"""
        super().__post_init__()
        
        # 开发环境特定路径
        if self.base_dir:
            self.temp_dir = self.base_dir / "temp" / "dev"
            self.logs_dir = self.base_dir / "logs" / "dev"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = super().to_dict()
        result['environment'] = self.environment
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DevelopmentConfig':
        """从字典创建配置"""
        return cls(**data)
