#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境变量加载器
支持从环境变量文件加载配置
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
from ..schemas.app_config import AppConfig
from ..validators.config_validator import ConfigValidator, ValidationResult


class EnvLoader:
    """环境变量加载器"""
    
    def __init__(self):
        """初始化环境变量加载器"""
        self.validator = ConfigValidator()
        self._env_cache = {}
        self._file_cache = {}
    
    def load_from_file(self, file_path: Union[str, Path], 
                       validate: bool = True) -> AppConfig:
        """
        从环境变量文件加载配置
        
        Args:
            file_path: 环境变量文件路径
            validate: 是否验证配置
        
        Returns:
            应用配置对象
        
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 配置验证失败
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"环境变量文件不存在: {file_path}")
        
        # 检查缓存
        cache_key = str(file_path.absolute())
        if cache_key in self._file_cache:
            return self._file_cache[cache_key]
        
        try:
            # 读取环境变量文件
            env_vars = self._parse_env_file(file_path)
            
            # 转换为AppConfig对象
            config = self._convert_env_to_app_config(env_vars)
            
            # 验证配置
            if validate:
                validation_result = self.validator.validate(config)
                if not validation_result.is_valid:
                    raise ValueError(f"配置验证失败:\n{validation_result.get_error_summary()}")
            
            # 缓存结果
            self._file_cache[cache_key] = config
            
            return config
            
        except Exception as e:
            raise ValueError(f"环境变量配置加载失败: {e}")
    
    def load_from_environment(self, validate: bool = True) -> AppConfig:
        """
        从系统环境变量加载配置
        
        Args:
            validate: 是否验证配置
        
        Returns:
            应用配置对象
        """
        # 检查缓存
        if 'system_env' in self._env_cache:
            return self._env_cache['system_env']
        
        try:
            # 获取所有环境变量
            env_vars = dict(os.environ)
            
            # 转换为AppConfig对象
            config = self._convert_env_to_app_config(env_vars)
            
            # 验证配置
            if validate:
                validation_result = self.validator.validate(config)
                if not validation_result.is_valid:
                    raise ValueError(f"配置验证失败:\n{validation_result.get_error_summary()}")
            
            # 缓存结果
            self._env_cache['system_env'] = config
            
            return config
            
        except Exception as e:
            raise ValueError(f"系统环境变量配置加载失败: {e}")
    
    def load_merged(self, env_file_path: Optional[Union[str, Path]] = None,
                    validate: bool = True) -> AppConfig:
        """
        加载合并的环境变量配置（文件 + 系统环境变量）
        
        Args:
            env_file_path: 环境变量文件路径（可选）
            validate: 是否验证配置
        
        Returns:
            合并后的应用配置对象
        """
        # 从系统环境变量加载基础配置
        base_config = self.load_from_environment(validate=False)
        
        # 如果指定了文件，则加载并合并
        if env_file_path:
            try:
                file_config = self.load_from_file(env_file_path, validate=False)
                base_config = base_config.merge_with(file_config)
            except Exception as e:
                print(f"警告: 无法加载环境变量文件 {env_file_path}: {e}")
        
        # 最终验证
        if validate:
            validation_result = self.validator.validate(base_config)
            if not validation_result.is_valid:
                raise ValueError(f"配置验证失败:\n{validation_result.get_error_summary()}")
        
        return base_config
    
    def _parse_env_file(self, file_path: Path) -> Dict[str, str]:
        """
        解析环境变量文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            环境变量字典
        """
        env_vars = {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue
                
                # 解析键值对
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # 移除引号
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    env_vars[key] = value
                else:
                    print(f"警告: 第{line_num}行格式无效: {line}")
        
        return env_vars
    
    def _convert_env_to_app_config(self, env_vars: Dict[str, str]) -> AppConfig:
        """
        将环境变量转换为AppConfig对象
        
        Args:
            env_vars: 环境变量字典
        
        Returns:
            AppConfig对象
        """
        # 创建基础配置
        config = AppConfig()
        
        # 映射环境变量到配置
        self._map_env_to_base_config(env_vars, config)
        self._map_env_to_war3_config(env_vars, config)
        self._map_env_to_editor_config(env_vars, config)
        self._map_env_to_project_config(env_vars, config)
        self._map_env_to_development_config(env_vars, config)
        self._map_env_to_interface_config(env_vars, config)
        self._map_env_to_tools_config(env_vars, config)
        
        return config
    
    def _map_env_to_base_config(self, env_vars: Dict[str, str], config: AppConfig):
        """映射环境变量到基础配置"""
        # 应用基础配置
        if 'APP_NAME' in env_vars:
            config.base.app_name = env_vars['APP_NAME']
        if 'APP_VERSION' in env_vars:
            config.base.app_version = env_vars['APP_VERSION']
        if 'APP_ENVIRONMENT' in env_vars:
            config.environment = env_vars['APP_ENVIRONMENT']
        
        # 路径配置
        if 'BASE_DIR' in env_vars:
            config.base.base_dir = Path(env_vars['BASE_DIR'])
        if 'CONFIG_DIR' in env_vars:
            config.base.config_dir = Path(env_vars['CONFIG_DIR'])
        if 'LOGS_DIR' in env_vars:
            config.base.logs_dir = Path(env_vars['LOGS_DIR'])
        if 'TEMP_DIR' in env_vars:
            config.base.temp_dir = Path(env_vars['TEMP_DIR'])
        
        # 日志配置
        if 'LOG_LEVEL' in env_vars:
            config.base.log_level = env_vars['LOG_LEVEL']
        if 'LOG_FORMAT' in env_vars:
            config.base.log_format = env_vars['LOG_FORMAT']
        if 'LOG_FILE' in env_vars:
            config.base.log_file = env_vars['LOG_FILE']
    
    def _map_env_to_war3_config(self, env_vars: Dict[str, str], config: AppConfig):
        """映射环境变量到War3配置"""
        if 'WAR3_INSTALLATION_PATH' in env_vars:
            config.war3.installation_path = Path(env_vars['WAR3_INSTALLATION_PATH'])
        if 'WAR3_WORLD_EDITOR_PATH' in env_vars:
            config.war3.world_editor_path = Path(env_vars['WAR3_WORLD_EDITOR_PATH'])
        if 'WAR3_JNGP_PATH' in env_vars:
            config.war3.jngp_path = Path(env_vars['WAR3_JNGP_PATH'])
        if 'WAR3_MAPS_DIRECTORY' in env_vars:
            config.war3.maps_directory = Path(env_vars['WAR3_MAPS_DIRECTORY'])
    
    def _map_env_to_editor_config(self, env_vars: Dict[str, str], config: AppConfig):
        """映射环境变量到编辑器配置"""
        if 'EDITOR_DEFAULT_EDITOR' in env_vars:
            config.editor.editor_type.value = env_vars['EDITOR_DEFAULT_EDITOR']
        if 'EDITOR_AUTO_SAVE_INTERVAL' in env_vars:
            config.editor.auto_save_interval = int(env_vars['EDITOR_AUTO_SAVE_INTERVAL'])
        if 'EDITOR_BACKUP_ENABLED' in env_vars:
            config.editor.backup_enabled = env_vars['EDITOR_BACKUP_ENABLED'].lower() == 'true'
        if 'EDITOR_BACKUP_INTERVAL' in env_vars:
            config.editor.backup_interval = int(env_vars['EDITOR_BACKUP_INTERVAL'])
        if 'Y3_EDITOR_PATH' in env_vars:
            config.editor.editor_path = Path(env_vars['Y3_EDITOR_PATH'])
    
    def _map_env_to_project_config(self, env_vars: Dict[str, str], config: AppConfig):
        """映射环境变量到项目配置"""
        if 'PROJECT_DEFAULT_TYPE' in env_vars:
            config.project['default_type'] = env_vars['PROJECT_DEFAULT_TYPE']
        if 'PROJECT_AUTO_BACKUP' in env_vars:
            config.project['auto_backup'] = env_vars['PROJECT_AUTO_BACKUP'].lower() == 'true'
        if 'PROJECT_VERSION_CONTROL' in env_vars:
            config.project['version_control'] = env_vars['PROJECT_VERSION_CONTROL'].lower() == 'true'
    
    def _map_env_to_development_config(self, env_vars: Dict[str, str], config: AppConfig):
        """映射环境变量到开发配置"""
        if 'DEVELOPMENT_LOG_LEVEL' in env_vars:
            config.development['log_level'] = env_vars['DEVELOPMENT_LOG_LEVEL']
        if 'DEVELOPMENT_DEBUG_MODE' in env_vars:
            config.development['debug_mode'] = env_vars['DEVELOPMENT_DEBUG_MODE'].lower() == 'true'
        if 'DEVELOPMENT_TEST_MODE' in env_vars:
            config.development['test_mode'] = env_vars['DEVELOPMENT_TEST_MODE'].lower() == 'true'
        if 'DEVELOPMENT_VERBOSE_LOGGING' in env_vars:
            config.development['verbose_logging'] = env_vars['DEVELOPMENT_VERBOSE_LOGGING'].lower() == 'true'
    
    def _map_env_to_interface_config(self, env_vars: Dict[str, str], config: AppConfig):
        """映射环境变量到界面配置"""
        if 'INTERFACE_LANGUAGE' in env_vars:
            config.interface['language'] = env_vars['INTERFACE_LANGUAGE']
        if 'INTERFACE_THEME' in env_vars:
            config.interface['theme'] = env_vars['INTERFACE_THEME']
        if 'INTERFACE_WINDOW_SIZE' in env_vars:
            size_str = env_vars['INTERFACE_WINDOW_SIZE']
            try:
                width, height = map(int, size_str.split(','))
                config.interface['window_size'] = [width, height]
            except ValueError:
                print(f"警告: 无效的窗口大小格式: {size_str}")
    
    def _map_env_to_tools_config(self, env_vars: Dict[str, str], config: AppConfig):
        """映射环境变量到工具配置"""
        if 'TOOLS_MAP_OPTIMIZATION' in env_vars:
            config.tools['map_optimization'] = env_vars['TOOLS_MAP_OPTIMIZATION'].lower() == 'true'
        if 'TOOLS_RESOURCE_COMPRESSION' in env_vars:
            config.tools['resource_compression'] = env_vars['TOOLS_RESOURCE_COMPRESSION'].lower() == 'true'
        if 'TOOLS_AUTO_TEST' in env_vars:
            config.tools['auto_test'] = env_vars['TOOLS_AUTO_TEST'].lower() == 'true'
    
    def clear_cache(self) -> None:
        """清除缓存"""
        self._env_cache.clear()
        self._file_cache.clear()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        return {
            'env_cache_size': len(self._env_cache),
            'file_cache_size': len(self._file_cache),
            'cached_env_files': list(self._file_cache.keys())
        }
