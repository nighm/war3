#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理包
提供统一的配置加载、验证和管理功能
"""

from .loaders.config_factory import ConfigFactory
from .schemas.app_config import AppConfig
from .validators.config_validator import ConfigValidator

__version__ = "1.0.0"
__author__ = "War3 Map Studio Team"

# 主要接口
__all__ = [
    "ConfigFactory",
    "AppConfig", 
    "ConfigValidator",
    "load_config",
    "validate_config"
]

def load_config(environment: str = "development") -> AppConfig:
    """
    加载配置
    
    Args:
        environment: 环境名称 (development, production, testing)
    
    Returns:
        应用配置对象
    """
    factory = ConfigFactory()
    return factory.create_config(environment)

def validate_config(config: AppConfig) -> bool:
    """
    验证配置
    
    Args:
        config: 应用配置对象
    
    Returns:
        配置是否有效
    """
    validator = ConfigValidator()
    result = validator.validate(config)
    return result.is_valid
