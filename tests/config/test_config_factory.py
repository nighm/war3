#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置工厂测试
测试ConfigFactory类的功能
"""

import pytest
import tempfile
import os
from pathlib import Path
from config.loaders.config_factory import ConfigFactory
from config.schemas.app_config import AppConfig


class TestConfigFactory:
    """测试配置工厂类"""
    
    def test_config_factory_initialization(self):
        """测试配置工厂初始化"""
        factory = ConfigFactory()
        
        assert factory is not None
        assert hasattr(factory, 'yaml_loader')
        assert hasattr(factory, 'json_loader')
        assert hasattr(factory, 'env_loader')
        assert hasattr(factory, 'validator')
        
        # 检查支持的扩展名
        assert '.yaml' in factory.supported_extensions
        assert '.yml' in factory.supported_extensions
        assert '.json' in factory.supported_extensions
        assert '.env' in factory.supported_extensions
        
        # 检查环境配置映射
        assert 'development' in factory.environment_configs
        assert 'production' in factory.environment_configs
        assert 'testing' in factory.environment_configs
    
    def test_create_default_config(self):
        """测试创建默认配置"""
        factory = ConfigFactory()
        
        config = factory.create_default_config()
        assert isinstance(config, AppConfig)
        assert config.environment == "development"
        assert config.base is not None
    
    def test_create_config_with_environment(self):
        """测试使用指定环境创建配置"""
        factory = ConfigFactory()
        
        # 测试开发环境
        dev_config = factory.create_config("development")
        assert dev_config.environment == "development"
        
        # 测试生产环境
        prod_config = factory.create_config("production")
        assert prod_config.environment == "production"
        
        # 测试测试环境
        test_config = factory.create_config("testing")
        assert test_config.environment == "testing"
    
    def test_create_minimal_config(self):
        """测试创建最小配置"""
        factory = ConfigFactory()
        
        config = factory.create_minimal_config()
        assert isinstance(config, AppConfig)
        assert config.environment == "development"
    
    def test_get_loader_info(self):
        """测试获取加载器信息"""
        factory = ConfigFactory()
        
        info = factory.get_loader_info()
        
        assert 'supported_extensions' in info
        assert 'environment_configs' in info
        assert 'yaml_loader_cache' in info
        assert 'json_loader_cache' in info
        assert 'env_loader_cache' in info
        
        # 检查扩展名列表
        assert isinstance(info['supported_extensions'], list)
        assert len(info['supported_extensions']) > 0
        
        # 检查环境配置列表
        assert isinstance(info['environment_configs'], list)
        assert len(info['environment_configs']) > 0
    
    def test_clear_all_caches(self):
        """测试清除所有缓存"""
        factory = ConfigFactory()
        
        # 清除缓存前获取信息
        info_before = factory.get_loader_info()
        
        # 清除所有缓存
        factory.clear_all_caches()
        
        # 清除缓存后获取信息
        info_after = factory.get_loader_info()
        
        # 检查缓存是否被清除
        assert info_after['yaml_loader_cache']['cache_size'] == 0
        assert info_after['json_loader_cache']['cache_size'] == 0
        assert info_after['env_loader_cache']['env_cache_size'] == 0
        assert info_after['env_loader_cache']['file_cache_size'] == 0
    
    def test_validate_config(self):
        """测试配置验证"""
        factory = ConfigFactory()
        
        # 创建有效配置
        config = factory.create_default_config()
        
        # 验证配置
        result = factory.validate_config(config)
        
        assert result is not None
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'errors')
        assert hasattr(result, 'warnings')
    
    def test_export_config_yaml(self):
        """测试导出YAML配置"""
        factory = ConfigFactory()
        config = factory.create_default_config()
        
        # 导出为YAML字符串
        yaml_output = factory.export_config(config, "yaml")
        
        assert isinstance(yaml_output, str)
        assert "environment" in yaml_output
        assert "base" in yaml_output
        assert "war3" in yaml_output
        assert "editor" in yaml_output
    
    def test_export_config_json(self):
        """测试导出JSON配置"""
        factory = ConfigFactory()
        config = factory.create_default_config()
        
        # 导出为JSON字符串
        json_output = factory.export_config(config, "json")
        
        assert isinstance(json_output, str)
        assert "environment" in json_output
        assert "base" in json_output
        assert "war3" in json_output
        assert "editor" in json_output
    
    def test_export_config_invalid_format(self):
        """测试导出无效格式配置"""
        factory = ConfigFactory()
        config = factory.create_default_config()
        
        # 测试无效格式
        with pytest.raises(ValueError, match="不支持的导出格式"):
            factory.export_config(config, "invalid_format")
    
    def test_supported_extensions_mapping(self):
        """测试支持的扩展名映射"""
        factory = ConfigFactory()
        
        # 检查每个扩展名都有对应的加载器
        for ext, loader in factory.supported_extensions.items():
            assert loader is not None
            assert hasattr(loader, 'load_from_file')
            # 只有YAML和JSON加载器有save_to_file方法
            if ext in ['.yaml', '.yml', '.json']:
                assert hasattr(loader, 'save_to_file')
    
    def test_environment_configs_mapping(self):
        """测试环境配置映射"""
        factory = ConfigFactory()
        
        # 检查每个环境都有对应的配置类
        for env_name, config_class in factory.environment_configs.items():
            assert config_class is not None
            # 可以实例化
            config_instance = config_class()
            assert config_instance is not None
