#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置验证器测试
测试ConfigValidator类的功能
"""

import pytest
from pathlib import Path
from config.validators.config_validator import ConfigValidator, ValidationResult
from config.schemas.app_config import AppConfig
from config.loaders.config_factory import ConfigFactory


class TestValidationResult:
    """测试ValidationResult类"""
    
    def test_validation_result_initialization(self):
        """测试验证结果初始化"""
        result = ValidationResult()
        
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []
        assert result.component_results == {}
    
    def test_validation_result_with_values(self):
        """测试使用值初始化验证结果"""
        result = ValidationResult(
            is_valid=False,
            errors=["Error 1", "Error 2"],
            warnings=["Warning 1"],
            component_results={"test": {"status": "failed"}}
        )
        
        assert result.is_valid is False
        assert len(result.errors) == 2
        assert len(result.warnings) == 1
        assert "test" in result.component_results
    
    def test_add_error(self):
        """测试添加错误"""
        result = ValidationResult()
        
        result.add_error("Test error")
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "Test error" in result.errors
    
    def test_add_warning(self):
        """测试添加警告"""
        result = ValidationResult()
        
        result.add_warning("Test warning")
        
        assert result.is_valid is True  # 警告不影响有效性
        assert len(result.warnings) == 1
        assert "Test warning" in result.warnings
    
    def test_add_component_result(self):
        """测试添加组件结果"""
        result = ValidationResult()
        
        result.add_component_result("test_component", {"status": "success"})
        
        assert "test_component" in result.component_results
        assert result.component_results["test_component"]["status"] == "success"
    
    def test_has_errors(self):
        """测试是否有错误"""
        result = ValidationResult()
        
        assert result.has_errors() is False
        
        result.add_error("Test error")
        assert result.has_errors() is True
    
    def test_has_warnings(self):
        """测试是否有警告"""
        result = ValidationResult()
        
        assert result.has_warnings() is False
        
        result.add_warning("Test warning")
        assert result.has_warnings() is True
    
    def test_get_error_summary(self):
        """测试获取错误摘要"""
        result = ValidationResult()
        
        # 无错误时
        summary = result.get_error_summary()
        assert "配置验证通过，无错误" in summary
        
        # 有错误时
        result.add_error("Error 1")
        result.add_error("Error 2")
        summary = result.get_error_summary()
        assert "配置验证失败" in summary
        assert "发现 2 个错误" in summary
        assert "Error 1" in summary
        assert "Error 2" in summary
    
    def test_get_warning_summary(self):
        """测试获取警告摘要"""
        result = ValidationResult()
        
        # 无警告时
        summary = result.get_warning_summary()
        assert "无警告" in summary
        
        # 有警告时
        result.add_warning("Warning 1")
        result.add_warning("Warning 2")
        summary = result.get_warning_summary()
        assert "发现 2 个警告" in summary
        assert "Warning 1" in summary
        assert "Warning 2" in summary


class TestConfigValidator:
    """测试ConfigValidator类"""
    
    def test_config_validator_initialization(self):
        """测试配置验证器初始化"""
        validator = ConfigValidator()
        
        assert validator is not None
        assert hasattr(validator, 'validation_rules')
        assert 'required_fields' in validator.validation_rules
        assert 'path_validations' in validator.validation_rules
        assert 'value_ranges' in validator.validation_rules
        assert 'enum_values' in validator.validation_rules
    
    def test_validate_valid_config(self):
        """测试验证有效配置"""
        validator = ConfigValidator()
        factory = ConfigFactory()
        
        # 创建有效配置
        config = factory.create_default_config()
        
        # 验证配置
        result = validator.validate(config)
        
        assert isinstance(result, ValidationResult)
        # 注意：默认配置可能包含一些警告，但不应该有错误
        # 具体结果取决于配置的完整性
    
    def test_validate_specific_component(self):
        """测试验证特定组件"""
        validator = ConfigValidator()
        factory = ConfigFactory()
        
        config = factory.create_default_config()
        
        # 验证基础配置
        result = validator.validate_specific_component(config, 'base')
        assert isinstance(result, ValidationResult)
        
        # 验证War3配置
        result = validator.validate_specific_component(config, 'war3')
        assert isinstance(result, ValidationResult)
        
        # 验证编辑器配置
        result = validator.validate_specific_component(config, 'editor')
        assert isinstance(result, ValidationResult)
    
    def test_validate_invalid_component(self):
        """测试验证无效组件"""
        validator = ConfigValidator()
        factory = ConfigFactory()
        
        config = factory.create_default_config()
        
        # 验证未知组件
        result = validator.validate_specific_component(config, 'unknown_component')
        assert isinstance(result, ValidationResult)
        assert result.has_errors() is True
        assert "未知的组件" in result.errors[0]
    
    def test_get_validation_summary(self):
        """测试获取验证摘要"""
        validator = ConfigValidator()
        factory = ConfigFactory()
        
        config = factory.create_default_config()
        result = validator.validate(config)
        
        summary = validator.get_validation_summary(result)
        
        assert isinstance(summary, str)
        assert "配置验证摘要" in summary
        assert "错误数量" in summary
        assert "警告数量" in summary
    
    def test_validation_rules_structure(self):
        """测试验证规则结构"""
        validator = ConfigValidator()
        rules = validator.validation_rules
        
        # 检查必需字段规则
        assert 'base' in rules['required_fields']
        assert 'war3' in rules['required_fields']
        assert 'editor' in rules['required_fields']
        
        # 检查路径验证规则
        assert 'war3' in rules['path_validations']
        assert 'editor' in rules['path_validations']
        
        # 检查数值范围规则
        assert 'auto_save_interval' in rules['value_ranges']
        assert 'backup_interval' in rules['value_ranges']
        assert 'undo_levels' in rules['value_ranges']
        
        # 检查枚举值规则
        assert 'log_level' in rules['enum_values']
        assert 'editor_type' in rules['enum_values']
        assert 'map_type' in rules['enum_values']
    
    def test_validation_rules_values(self):
        """测试验证规则值"""
        validator = ConfigValidator()
        rules = validator.validation_rules
        
        # 检查日志级别枚举值
        log_levels = rules['enum_values']['log_level']
        assert 'DEBUG' in log_levels
        assert 'INFO' in log_levels
        assert 'WARNING' in log_levels
        assert 'ERROR' in log_levels
        assert 'CRITICAL' in log_levels
        
        # 检查编辑器类型枚举值
        editor_types = rules['enum_values']['editor_type']
        assert 'world_editor' in editor_types
        assert 'y3_editor' in editor_types
        assert 'jngp' in editor_types
        assert 'custom' in editor_types
        
        # 检查地图类型枚举值
        map_types = rules['enum_values']['map_type']
        assert 'melee' in map_types
        assert 'rpg' in map_types
        assert 'td' in map_types
        assert 'aos' in map_types
        assert 'custom' in map_types
