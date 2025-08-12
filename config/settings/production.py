#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产环境配置
继承基础配置，添加生产环境特定配置
"""

from dataclasses import dataclass
from typing import Dict, Any
from pathlib import Path
from .base import BaseConfig


@dataclass
class ProductionConfig(BaseConfig):
    """生产环境配置"""
    
    # 生产环境标识
    environment: str = "production"
    
    # 生产模式配置
    debug_mode: bool = False
    test_mode: bool = False
    verbose_logging: bool = False
    
    # 日志配置（生产环境）
    log_level: str = "WARNING"
    log_to_console: bool = False
    log_to_file: bool = True
    log_rotation: bool = True
    log_compression: bool = True
    
    # 性能配置（生产环境）
    enable_profiling: bool = False
    enable_memory_tracking: bool = False
    enable_slow_query_log: bool = False
    
    # 安全配置（生产环境）
    enable_security_headers: bool = True
    enable_rate_limiting: bool = True
    enable_cors: bool = False
    
    # 缓存配置（生产环境）
    cache_backend: str = "redis"
    cache_ttl: int = 3600  # 1小时
    cache_max_size: int = 1000
    
    # 数据库配置（生产环境）
    database_url: str = "postgresql://user:pass@localhost/war3_studio"
    database_echo: bool = False
    database_pool_size: int = 20
    database_max_overflow: int = 30
    
    # 监控配置（生产环境）
    enable_health_checks: bool = True
    enable_metrics: bool = True
    enable_alerting: bool = True
    
    # 备份配置（生产环境）
    backup_enabled: bool = True
    backup_interval: int = 24  # 小时
    backup_retention: int = 30  # 天
    
    def __post_init__(self):
        """初始化后处理"""
        super().__post_init__()
        
        # 生产环境特定路径
        if self.base_dir:
            self.temp_dir = self.base_dir / "temp" / "prod"
            self.logs_dir = self.base_dir / "logs" / "prod"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = super().to_dict()
        result['environment'] = self.environment
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProductionConfig':
        """从字典创建配置"""
        return cls(**data)
