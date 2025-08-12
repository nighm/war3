#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置验证器
提供配置验证和完整性检查功能
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path
from ..schemas.app_config import AppConfig


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    component_results: Dict[str, Dict[str, Any]]
    
    def __init__(self, is_valid: bool = True, errors: List[str] = None, 
                 warnings: List[str] = None, component_results: Dict[str, Dict[str, Any]] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
        self.component_results = component_results or {}
    
    def add_error(self, error: str):
        """添加错误"""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """添加警告"""
        self.warnings.append(warning)
    
    def add_component_result(self, component: str, result: Dict[str, Any]):
        """添加组件验证结果"""
        self.component_results[component] = result
    
    def has_errors(self) -> bool:
        """是否有错误"""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """是否有警告"""
        return len(self.warnings) > 0
    
    def get_error_summary(self) -> str:
        """获取错误摘要"""
        if not self.errors:
            return "配置验证通过，无错误"
        
        summary = f"配置验证失败，发现 {len(self.errors)} 个错误:\n"
        for i, error in enumerate(self.errors, 1):
            summary += f"  {i}. {error}\n"
        return summary
    
    def get_warning_summary(self) -> str:
        """获取警告摘要"""
        if not self.warnings:
            return "无警告"
        
        summary = f"发现 {len(self.warnings)} 个警告:\n"
        for i, warning in enumerate(self.warnings, 1):
            summary += f"  {i}. {warning}\n"
        return summary


class ConfigValidator:
    """配置验证器"""
    
    def __init__(self):
        """初始化验证器"""
        self.validation_rules = self._setup_validation_rules()
    
    def _setup_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """设置验证规则"""
        return {
            'required_fields': {
                'base': ['app_name', 'app_version'],
                'war3': ['installation_path'],
                'editor': ['editor_type'],
            },
            'path_validations': {
                'war3': ['installation_path', 'world_editor_path', 'maps_directory'],
                'editor': ['editor_path', 'backup_directory', 'plugin_directory'],
            },
            'value_ranges': {
                'auto_save_interval': (1, 60),
                'backup_interval': (1, 1440),  # 1分钟到24小时
                'undo_levels': (1, 1000),
                'log_max_size': (1024, 100 * 1024 * 1024),  # 1KB到100MB
            },
            'enum_values': {
                'log_level': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                'editor_type': ['world_editor', 'y3_editor', 'jngp', 'custom'],
                'map_type': ['melee', 'rpg', 'td', 'aos', 'custom'],
            }
        }
    
    def validate(self, config: AppConfig) -> ValidationResult:
        """
        验证配置
        
        Args:
            config: 应用配置对象
        
        Returns:
            验证结果
        """
        result = ValidationResult()
        
        # 验证基础配置
        self._validate_base_config(config, result)
        
        # 验证War3配置
        self._validate_war3_config(config, result)
        
        # 验证编辑器配置
        self._validate_editor_config(config, result)
        
        # 验证项目配置
        self._validate_project_config(config, result)
        
        # 验证开发配置
        self._validate_development_config(config, result)
        
        # 验证界面配置
        self._validate_interface_config(config, result)
        
        # 验证工具配置
        self._validate_tools_config(config, result)
        
        # 验证配置完整性
        self._validate_config_integrity(config, result)
        
        return result
    
    def _validate_base_config(self, config: AppConfig, result: ValidationResult):
        """验证基础配置"""
        base_result = {'errors': [], 'warnings': []}
        
        # 验证必需字段
        if not config.base.app_name:
            base_result['errors'].append("应用名称不能为空")
            result.add_error("基础配置: 应用名称不能为空")
        
        if not config.base.app_version:
            base_result['errors'].append("应用版本不能为空")
            result.add_error("基础配置: 应用版本不能为空")
        
        # 验证日志级别
        if config.base.log_level not in self.validation_rules['enum_values']['log_level']:
            base_result['errors'].append(f"无效的日志级别: {config.base.log_level}")
            result.add_error(f"基础配置: 无效的日志级别: {config.base.log_level}")
        
        # 验证路径
        if config.base.base_dir and not config.base.base_dir.exists():
            base_result['warnings'].append(f"基础目录不存在: {config.base.base_dir}")
            result.add_warning(f"基础配置: 基础目录不存在: {config.base.base_dir}")
        
        result.add_component_result('base', base_result)
    
    def _validate_war3_config(self, config: AppConfig, result: ValidationResult):
        """验证War3配置"""
        war3_result = {'errors': [], 'warnings': []}
        
        # 验证路径
        if config.war3.installation_path:
            if not config.war3.installation_path.exists():
                war3_result['errors'].append(f"War3安装路径不存在: {config.war3.installation_path}")
                result.add_error(f"War3配置: 安装路径不存在: {config.war3.installation_path}")
            else:
                # 检查War3可执行文件
                war3_exe = config.war3.installation_path / "Warcraft III.exe"
                if not war3_exe.exists():
                    war3_result['warnings'].append("未找到War3主程序")
                    result.add_warning("War3配置: 未找到War3主程序")
        
        # 验证编辑器类型
        if config.war3.editor_type not in self.validation_rules['enum_values']['editor_type']:
            war3_result['errors'].append(f"无效的编辑器类型: {config.war3.editor_type}")
            result.add_error(f"War3配置: 无效的编辑器类型: {config.war3.editor_type}")
        
        result.add_component_result('war3', war3_result)
    
    def _validate_editor_config(self, config: AppConfig, result: ValidationResult):
        """验证编辑器配置"""
        editor_result = {'errors': [], 'warnings': []}
        
        # 验证编辑器类型
        if config.editor.editor_type.value not in self.validation_rules['enum_values']['editor_type']:
            editor_result['errors'].append(f"无效的编辑器类型: {config.editor.editor_type.value}")
            result.add_error(f"编辑器配置: 无效的编辑器类型: {config.editor.editor_type.value}")
        
        # 验证数值范围
        if config.editor.auto_save_interval < self.validation_rules['value_ranges']['auto_save_interval'][0]:
            editor_result['errors'].append("自动保存间隔不能小于1分钟")
            result.add_error("编辑器配置: 自动保存间隔不能小于1分钟")
        
        if config.editor.backup_interval < self.validation_rules['value_ranges']['backup_interval'][0]:
            editor_result['errors'].append("备份间隔不能小于1分钟")
            result.add_error("编辑器配置: 备份间隔不能小于1分钟")
        
        # 验证路径
        if config.editor.editor_path and not config.editor.editor_path.exists():
            editor_result['warnings'].append(f"编辑器路径不存在: {config.editor.editor_path}")
            result.add_warning(f"编辑器配置: 编辑器路径不存在: {config.editor.editor_path}")
        
        result.add_component_result('editor', editor_result)
    
    def _validate_project_config(self, config: AppConfig, result: ValidationResult):
        """验证项目配置"""
        project_result = {'errors': [], 'warnings': []}
        
        # 验证项目类型
        if 'default_type' in config.project:
            project_type = config.project['default_type']
            if project_type not in self.validation_rules['enum_values']['map_type']:
                project_result['errors'].append(f"无效的项目类型: {project_type}")
                result.add_error(f"项目配置: 无效的项目类型: {project_type}")
        
        result.add_component_result('project', project_result)
    
    def _validate_development_config(self, config: AppConfig, result: ValidationResult):
        """验证开发配置"""
        dev_result = {'errors': [], 'warnings': []}
        
        # 验证日志级别
        if 'log_level' in config.development:
            log_level = config.development['log_level']
            if log_level not in self.validation_rules['enum_values']['log_level']:
                dev_result['errors'].append(f"无效的开发日志级别: {log_level}")
                result.add_error(f"开发配置: 无效的日志级别: {log_level}")
        
        result.add_component_result('development', dev_result)
    
    def _validate_interface_config(self, config: AppConfig, result: ValidationResult):
        """验证界面配置"""
        interface_result = {'errors': [], 'warnings': []}
        
        # 验证语言
        if 'language' in config.interface:
            language = config.interface['language']
            if language not in ['zh_CN', 'en_US']:
                interface_result['warnings'].append(f"不支持的语言: {language}")
                result.add_warning(f"界面配置: 不支持的语言: {language}")
        
        # 验证窗口大小
        if 'window_size' in config.interface:
            window_size = config.interface['window_size']
            if len(window_size) != 2 or window_size[0] < 800 or window_size[1] < 600:
                interface_result['warnings'].append("窗口大小过小，可能影响使用")
                result.add_warning("界面配置: 窗口大小过小，可能影响使用")
        
        result.add_component_result('interface', interface_result)
    
    def _validate_tools_config(self, config: AppConfig, result: ValidationResult):
        """验证工具配置"""
        tools_result = {'errors': [], 'warnings': []}
        
        # 验证工具配置
        if 'max_file_size' in config.tools:
            max_size = config.tools['max_file_size']
            if max_size > 100 * 1024 * 1024:  # 100MB
                tools_result['warnings'].append("文件大小限制过大，可能影响性能")
                result.add_warning("工具配置: 文件大小限制过大，可能影响性能")
        
        result.add_component_result('tools', tools_result)
    
    def _validate_config_integrity(self, config: AppConfig, result: ValidationResult):
        """验证配置完整性"""
        integrity_result = {'errors': [], 'warnings': []}
        
        # 检查配置一致性
        if config.war3.editor_type == 'y3_editor' and not config.editor.editor_path:
            integrity_result['warnings'].append("Y3编辑器类型但未设置编辑器路径")
            result.add_warning("配置完整性: Y3编辑器类型但未设置编辑器路径")
        
        # 检查环境配置
        if config.environment == 'production' and config.development.get('debug_mode', False):
            integrity_result['warnings'].append("生产环境启用了调试模式")
            result.add_warning("配置完整性: 生产环境启用了调试模式")
        
        result.add_component_result('integrity', integrity_result)
    
    def validate_specific_component(self, config: AppConfig, component: str) -> ValidationResult:
        """验证特定组件"""
        result = ValidationResult()
        
        if component == 'base':
            self._validate_base_config(config, result)
        elif component == 'war3':
            self._validate_war3_config(config, result)
        elif component == 'editor':
            self._validate_editor_config(config, result)
        elif component == 'project':
            self._validate_project_config(config, result)
        elif component == 'development':
            self._validate_development_config(config, result)
        elif component == 'interface':
            self._validate_interface_config(config, result)
        elif component == 'tools':
            self._validate_tools_config(config, result)
        else:
            result.add_error(f"未知的组件: {component}")
        
        return result
    
    def get_validation_summary(self, result: ValidationResult) -> str:
        """获取验证摘要"""
        summary = "配置验证摘要\n"
        summary += "=" * 50 + "\n"
        
        if result.is_valid:
            summary += "✅ 配置验证通过\n"
        else:
            summary += "❌ 配置验证失败\n"
        
        summary += f"错误数量: {len(result.errors)}\n"
        summary += f"警告数量: {len(result.warnings)}\n"
        
        if result.errors:
            summary += "\n错误详情:\n"
            summary += result.get_error_summary()
        
        if result.warnings:
            summary += "\n警告详情:\n"
            summary += result.get_warning_summary()
        
        return summary
