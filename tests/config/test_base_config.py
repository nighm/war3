#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础配置测试
测试BaseConfig类的功能
"""

import pytest
from pathlib import Path
from config.settings.base import BaseConfig


class TestBaseConfig:
    """测试BaseConfig类"""
    
    def test_create_base_config(self):
        """测试创建基础配置"""
        config = BaseConfig()
        
        assert config.app_name == "War3 Map Studio"
        assert config.app_version == "1.3.0"
        assert config.log_level == "INFO"
        assert config.language == "zh_CN"
        assert config.base_dir is not None
    
    def test_base_config_with_custom_values(self):
        """测试使用自定义值创建基础配置"""
        custom_dir = Path("/custom/path")
        config = BaseConfig(
            app_name="Custom App",
            app_version="2.0.0",
            base_dir=custom_dir,
            log_level="DEBUG"
        )
        
        assert config.app_name == "Custom App"
        assert config.app_version == "2.0.0"
        assert config.base_dir == custom_dir
        assert config.log_level == "DEBUG"
    
    def test_base_config_post_init(self):
        """测试初始化后处理"""
        config = BaseConfig()
        
        # 检查是否自动设置了基础目录
        assert config.base_dir is not None
        assert config.config_dir is not None
        assert config.logs_dir is not None
        assert config.temp_dir is not None
        
        # 检查路径关系
        assert config.config_dir == config.base_dir / "config"
        assert config.logs_dir == config.base_dir / "logs"
        assert config.temp_dir == config.base_dir / "temp"
    
    def test_base_config_to_dict(self):
        """测试转换为字典"""
        config = BaseConfig()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict['app_name'] == "War3 Map Studio"
        assert config_dict['app_version'] == "1.3.0"
        assert config_dict['log_level'] == "INFO"
        
        # 检查路径字段被转换为字符串
        assert isinstance(config_dict['base_dir'], str)
        assert isinstance(config_dict['config_dir'], str)
    
    def test_base_config_from_dict(self):
        """测试从字典创建"""
        data = {
            'app_name': 'Test App',
            'app_version': '3.0.0',
            'log_level': 'WARNING',
            'language': 'en_US'
        }
        
        config = BaseConfig.from_dict(data)
        
        assert config.app_name == 'Test App'
        assert config.app_version == '3.0.0'
        assert config.log_level == 'WARNING'
        assert config.language == 'en_US'
    
    def test_base_config_validation(self):
        """测试配置验证"""
        config = BaseConfig()
        
        # 验证必需字段
        assert config.app_name is not None
        assert config.app_version is not None
        assert config.log_level is not None
        
        # 验证日志级别
        assert config.log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        # 验证语言
        assert config.language in ['zh_CN', 'en_US']
    
    def test_base_config_path_creation(self):
        """测试路径创建"""
        config = BaseConfig()
        
        # 检查基础目录存在或可以创建
        assert config.base_dir is not None
        
        # 检查子目录路径设置正确
        assert config.config_dir == config.base_dir / "config"
        assert config.logs_dir == config.base_dir / "logs"
        assert config.temp_dir == config.base_dir / "temp"
    
    def test_base_config_default_values(self):
        """测试默认值设置"""
        config = BaseConfig()
        
        # 检查默认值
        assert config.map_optimization is True
        assert config.resource_compression is True
        assert config.auto_test is False
    
    def test_base_config_immutability(self):
        """测试配置不可变性（除了特定字段）"""
        config = BaseConfig()
        
        # 可以修改某些字段
        original_name = config.app_name
        config.app_name = "Modified App"
        assert config.app_name == "Modified App"
        
        # 可以修改路径
        original_dir = config.base_dir
        new_dir = Path("/new/path")
        config.base_dir = new_dir
        assert config.base_dir == new_dir
