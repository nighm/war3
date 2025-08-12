#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置工厂
提供统一的配置加载接口，支持多种配置源
"""

from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from ..schemas.app_config import AppConfig
from ..validators.config_validator import ConfigValidator, ValidationResult
from .yaml_loader import YamlLoader
from .json_loader import JsonLoader
from .env_loader import EnvLoader
from ..settings.development import DevelopmentConfig
from ..settings.production import ProductionConfig
from ..settings.testing import TestingConfig


class ConfigFactory:
    """配置工厂类"""
    
    def __init__(self):
        """初始化配置工厂"""
        self.yaml_loader = YamlLoader()
        self.json_loader = JsonLoader()
        self.env_loader = EnvLoader()
        self.validator = ConfigValidator()
        
        # 支持的配置文件扩展名
        self.supported_extensions = {
            '.yaml': self.yaml_loader,
            '.yml': self.yaml_loader,
            '.json': self.json_loader,
            '.env': self.env_loader,
        }
        
        # 环境配置映射
        self.environment_configs = {
            'development': DevelopmentConfig,
            'production': ProductionConfig,
            'testing': TestingConfig,
        }
    
    def create_config(self, environment: str = "development", 
                     config_path: Optional[Union[str, Path]] = None,
                     env_file_path: Optional[Union[str, Path]] = None,
                     validate: bool = True) -> AppConfig:
        """
        创建配置对象
        
        Args:
            environment: 环境名称 (development, production, testing)
            config_path: 配置文件路径（可选）
            env_file_path: 环境变量文件路径（可选）
            validate: 是否验证配置
        
        Returns:
            应用配置对象
        """
        # 创建基础配置
        config = self._create_base_config(environment)
        
        # 加载配置文件（如果指定）
        if config_path:
            config = self._load_config_file(config_path, config, validate)
        
        # 加载环境变量（如果指定）
        if env_file_path:
            config = self._load_env_config(env_file_path, config, validate)
        
        # 最终验证
        if validate:
            validation_result = self.validator.validate(config)
            if not validation_result.is_valid:
                raise ValueError(f"配置验证失败:\n{validation_result.get_error_summary()}")
        
        return config
    
    def create_config_from_files(self, config_files: List[Union[str, Path]], 
                                environment: str = "development",
                                validate: bool = True) -> AppConfig:
        """
        从多个配置文件创建配置
        
        Args:
            config_files: 配置文件路径列表
            environment: 环境名称
            validate: 是否验证配置
        
        Returns:
            应用配置对象
        """
        if not config_files:
            raise ValueError("配置文件列表不能为空")
        
        # 创建基础配置
        config = self._create_base_config(environment)
        
        # 依次加载并合并配置文件
        for config_file in config_files:
            config = self._load_config_file(config_file, config, validate=False)
        
        # 最终验证
        if validate:
            validation_result = self.validator.validate(config)
            if not validation_result.is_valid:
                raise ValueError(f"配置验证失败:\n{validation_result.get_error_summary()}")
        
        return config
    
    def create_config_from_directory(self, config_dir: Union[str, Path], 
                                   environment: str = "development",
                                   validate: bool = True) -> AppConfig:
        """
        从配置目录创建配置
        
        Args:
            config_dir: 配置目录路径
            environment: 环境名称
            validate: 是否验证配置
        
        Returns:
            应用配置对象
        """
        config_dir = Path(config_dir)
        
        if not config_dir.exists():
            raise FileNotFoundError(f"配置目录不存在: {config_dir}")
        
        if not config_dir.is_dir():
            raise ValueError(f"路径不是目录: {config_dir}")
        
        # 查找配置文件
        config_files = []
        for ext in self.supported_extensions.keys():
            config_files.extend(config_dir.glob(f"*{ext}"))
        
        # 按优先级排序
        config_files = self._sort_config_files_by_priority(config_files)
        
        if not config_files:
            raise ValueError(f"配置目录中没有找到支持的配置文件: {config_dir}")
        
        return self.create_config_from_files(config_files, environment, validate)
    
    def _create_base_config(self, environment: str) -> AppConfig:
        """
        创建基础配置
        
        Args:
            environment: 环境名称
        
        Returns:
            基础配置对象
        """
        # 创建环境特定的基础配置
        if environment in self.environment_configs:
            base_config = self.environment_configs[environment]()
        else:
            # 默认使用开发环境配置
            base_config = DevelopmentConfig()
        
        # 创建应用配置
        config = AppConfig()
        config.base = base_config
        config.environment = environment
        
        return config
    
    def _load_config_file(self, config_path: Union[str, Path], 
                          base_config: AppConfig, validate: bool) -> AppConfig:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            base_config: 基础配置对象
            validate: 是否验证配置
        
        Returns:
            合并后的配置对象
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        # 确定加载器
        loader = self._get_loader_for_file(config_path)
        
        if not loader:
            raise ValueError(f"不支持的文件格式: {config_path.suffix}")
        
        try:
            # 加载配置
            if isinstance(loader, YamlLoader):
                file_config = loader.load_from_file(config_path, validate=False)
            elif isinstance(loader, JsonLoader):
                file_config = loader.load_from_file(config_path, validate=False)
            else:
                raise ValueError(f"不支持的加载器类型: {type(loader)}")
            
            # 合并配置
            merged_config = base_config.merge_with(file_config)
            
            return merged_config
            
        except Exception as e:
            raise ValueError(f"配置文件加载失败 {config_path}: {e}")
    
    def _load_env_config(self, env_file_path: Union[str, Path], 
                         base_config: AppConfig, validate: bool) -> AppConfig:
        """
        加载环境变量配置
        
        Args:
            env_file_path: 环境变量文件路径
            base_config: 基础配置对象
            validate: 是否验证配置
        
        Returns:
            合并后的配置对象
        """
        try:
            # 加载环境变量配置
            env_config = self.env_loader.load_from_file(env_file_path, validate=False)
            
            # 合并配置
            merged_config = base_config.merge_with(env_config)
            
            return merged_config
            
        except Exception as e:
            raise ValueError(f"环境变量文件加载失败 {env_file_path}: {e}")
    
    def _get_loader_for_file(self, file_path: Path):
        """
        根据文件扩展名获取对应的加载器
        
        Args:
            file_path: 文件路径
        
        Returns:
            配置加载器
        """
        suffix = file_path.suffix.lower()
        return self.supported_extensions.get(suffix)
    
    def _sort_config_files_by_priority(self, config_files: List[Path]) -> List[Path]:
        """
        按优先级排序配置文件
        
        Args:
            config_files: 配置文件列表
        
        Returns:
            排序后的配置文件列表
        """
        # 定义优先级顺序
        priority_order = [
            'base', 'common', 'default',  # 基础配置
            'development', 'production', 'testing',  # 环境配置
            'local', 'override', 'custom'  # 本地/覆盖配置
        ]
        
        def get_priority(file_path: Path) -> int:
            filename = file_path.stem.lower()
            for i, priority in enumerate(priority_order):
                if priority in filename:
                    return i
            return len(priority_order)  # 未匹配的放在最后
        
        return sorted(config_files, key=get_priority)
    
    def get_loader_info(self) -> Dict[str, Any]:
        """获取加载器信息"""
        return {
            'supported_extensions': list(self.supported_extensions.keys()),
            'environment_configs': list(self.environment_configs.keys()),
            'yaml_loader_cache': self.yaml_loader.get_cache_info(),
            'json_loader_cache': self.json_loader.get_cache_info(),
            'env_loader_cache': self.env_loader.get_cache_info(),
        }
    
    def clear_all_caches(self) -> None:
        """清除所有缓存"""
        self.yaml_loader.clear_cache()
        self.json_loader.clear_cache()
        self.env_loader.clear_cache()
    
    def validate_config(self, config: AppConfig) -> ValidationResult:
        """
        验证配置
        
        Args:
            config: 应用配置对象
        
        Returns:
            验证结果
        """
        return self.validator.validate(config)
    
    def export_config(self, config: AppConfig, format: str = "yaml", 
                     output_path: Optional[Union[str, Path]] = None) -> Union[str, None]:
        """
        导出配置
        
        Args:
            config: 应用配置对象
            format: 导出格式 (yaml, json)
            output_path: 输出路径（可选）
        
        Returns:
            导出的配置字符串（如果不指定输出路径）
        """
        if format.lower() == "yaml":
            if output_path:
                self.yaml_loader.save_to_file(config, output_path)
                return None
            else:
                import yaml
                return yaml.dump(config.to_dict(), default_flow_style=False, 
                               allow_unicode=True, indent=2)
        
        elif format.lower() == "json":
            if output_path:
                self.json_loader.save_to_file(config, output_path)
                return None
            else:
                import json
                return json.dumps(config.to_dict(), ensure_ascii=False, indent=2)
        
        else:
            raise ValueError(f"不支持的导出格式: {format}")
    
    def create_default_config(self, environment: str = "development") -> AppConfig:
        """
        创建默认配置
        
        Args:
            environment: 环境名称
        
        Returns:
            默认配置对象
        """
        return self.create_config(environment)
    
    def create_minimal_config(self) -> AppConfig:
        """
        创建最小配置
        
        Returns:
            最小配置对象
        """
        config = AppConfig()
        config.environment = "development"
        return config
