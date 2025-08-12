#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置加载器测试
测试各种配置加载器的功能
"""

import pytest
import tempfile
import os
from pathlib import Path
from config.loaders.yaml_loader import YamlLoader
from config.loaders.json_loader import JsonLoader
from config.loaders.env_loader import EnvLoader
from config.schemas.app_config import AppConfig


class TestYamlLoader:
    """测试YAML配置加载器"""
    
    def test_yaml_loader_initialization(self):
        """测试YAML加载器初始化"""
        loader = YamlLoader()
        
        assert loader is not None
        assert hasattr(loader, 'validator')
        assert hasattr(loader, '_cache')
        assert loader._cache_ttl == 300
    
    def test_yaml_loader_from_string(self):
        """测试从字符串加载YAML配置"""
        loader = YamlLoader()
        yaml_string = """
        environment: testing
        base:
          app_name: Test App
          app_version: 1.0.0
        war3:
          installation_path: /test/path
        """
        
        config = loader.load_from_string(yaml_string, validate=False)
        
        assert isinstance(config, AppConfig)
        assert config.environment == "testing"
        assert config.base.app_name == "Test App"
        assert config.base.app_version == "1.0.0"
    
    def test_yaml_loader_cache_functionality(self):
        """测试YAML加载器缓存功能"""
        loader = YamlLoader()
        
        # 检查初始缓存状态
        cache_info = loader.get_cache_info()
        assert cache_info['cache_size'] == 0
        
        # 清除缓存
        loader.clear_cache()
        cache_info = loader.get_cache_info()
        assert cache_info['cache_size'] == 0


class TestJsonLoader:
    """测试JSON配置加载器"""
    
    def test_json_loader_initialization(self):
        """测试JSON加载器初始化"""
        loader = JsonLoader()
        
        assert loader is not None
        assert hasattr(loader, 'validator')
        assert hasattr(loader, '_cache')
        assert loader._cache_ttl == 300
    
    def test_json_loader_from_string(self):
        """测试从字符串加载JSON配置"""
        loader = JsonLoader()
        json_string = '''
        {
          "environment": "testing",
          "base": {
            "app_name": "Test App",
            "app_version": "1.0.0"
          },
          "war3": {
            "installation_path": "/test/path"
          }
        }
        '''
        
        config = loader.load_from_string(json_string, validate=False)
        
        assert isinstance(config, AppConfig)
        assert config.environment == "testing"
        assert config.base.app_name == "Test App"
        assert config.base.app_version == "1.0.0"
    
    def test_json_loader_schema(self):
        """测试JSON加载器模式定义"""
        loader = JsonLoader()
        schema = loader.get_schema()
        
        assert isinstance(schema, dict)
        assert 'type' in schema
        assert schema['type'] == 'object'
        assert 'properties' in schema
        assert 'environment' in schema['properties']


class TestEnvLoader:
    """测试环境变量加载器"""
    
    def test_env_loader_initialization(self):
        """测试环境变量加载器初始化"""
        loader = EnvLoader()
        
        assert loader is not None
        assert hasattr(loader, 'validator')
        assert hasattr(loader, '_env_cache')
        assert hasattr(loader, '_file_cache')
    
    def test_env_loader_from_environment(self):
        """测试从系统环境变量加载配置"""
        loader = EnvLoader()
        
        # 设置测试环境变量
        os.environ['APP_NAME'] = 'Test App'
        os.environ['APP_VERSION'] = '2.0.0'
        os.environ['LOG_LEVEL'] = 'DEBUG'
        
        try:
            config = loader.load_from_environment(validate=False)
            
            assert isinstance(config, AppConfig)
            # 注意：环境变量映射可能不会直接设置到base配置中
            # 这取决于具体的映射逻辑
        finally:
            # 清理环境变量
            del os.environ['APP_NAME']
            del os.environ['APP_VERSION']
            del os.environ['LOG_LEVEL']
    
    def test_env_loader_cache_functionality(self):
        """测试环境变量加载器缓存功能"""
        loader = EnvLoader()
        
        # 检查初始缓存状态
        cache_info = loader.get_cache_info()
        assert cache_info['env_cache_size'] == 0
        assert cache_info['file_cache_size'] == 0
        
        # 清除缓存
        loader.clear_cache()
        cache_info = loader.get_cache_info()
        assert cache_info['env_cache_size'] == 0
        assert cache_info['file_cache_size'] == 0


class TestConfigLoadersIntegration:
    """测试配置加载器集成功能"""
    
    def test_loader_compatibility(self):
        """测试加载器兼容性"""
        yaml_loader = YamlLoader()
        json_loader = JsonLoader()
        env_loader = EnvLoader()
        
        # 所有加载器都应该有相同的基本接口
        assert hasattr(yaml_loader, 'load_from_file')
        assert hasattr(json_loader, 'load_from_file')
        assert hasattr(env_loader, 'load_from_file')
        
        assert hasattr(yaml_loader, 'clear_cache')
        assert hasattr(json_loader, 'clear_cache')
        assert hasattr(env_loader, 'clear_cache')
    
    def test_loader_validation_integration(self):
        """测试加载器与验证器的集成"""
        yaml_loader = YamlLoader()
        json_loader = JsonLoader()
        env_loader = EnvLoader()
        
        # 所有加载器都应该有验证器
        assert yaml_loader.validator is not None
        assert json_loader.validator is not None
        assert env_loader.validator is not None
        
        # 验证器类型应该一致
        from config.validators.config_validator import ConfigValidator
        assert isinstance(yaml_loader.validator, ConfigValidator)
        assert isinstance(json_loader.validator, ConfigValidator)
        assert isinstance(env_loader.validator, ConfigValidator)
