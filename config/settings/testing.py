#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试环境配置
继承基础配置，添加测试环境特定配置
"""

from dataclasses import dataclass
from typing import Dict, Any
from pathlib import Path
from .base import BaseConfig


@dataclass
class TestingConfig(BaseConfig):
    """测试环境配置"""
    
    # 测试环境标识
    environment: str = "testing"
    
    # 测试模式配置
    debug_mode: bool = False
    test_mode: bool = True
    verbose_logging: bool = True
    
    # 日志配置（测试环境）
    log_level: str = "DEBUG"
    log_to_console: bool = True
    log_to_file: bool = False  # 测试时不写文件
    
    # 测试配置
    test_timeout: int = 60
    test_parallel: bool = True
    test_coverage: bool = True
    test_coverage_min: int = 80
    
    # 数据库配置（测试环境）
    database_url: str = "sqlite:///./test.db"
    database_echo: bool = False
    database_pool_size: int = 1
    database_isolation_level: str = "SERIALIZABLE"
    
    # 缓存配置（测试环境）
    cache_backend: str = "memory"
    cache_ttl: int = 60  # 1分钟
    cache_clear_on_test: bool = True
    
    # 文件系统配置（测试环境）
    use_temp_directories: bool = True
    cleanup_after_test: bool = True
    preserve_test_artifacts: bool = False
    
    # 模拟配置（测试环境）
    enable_mocks: bool = True
    enable_fixtures: bool = True
    enable_test_data: bool = True
    
    # 性能配置（测试环境）
    enable_profiling: bool = False
    enable_memory_tracking: bool = False
    enable_slow_query_log: bool = False
    
    def __post_init__(self):
        """初始化后处理"""
        super().__post_init__()
        
        # 测试环境特定路径
        if self.base_dir:
            self.temp_dir = self.base_dir / "temp" / "test"
            self.logs_dir = self.base_dir / "logs" / "test"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = super().to_dict()
        result['environment'] = self.environment
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestingConfig':
        """从字典创建配置"""
        return cls(**data)
