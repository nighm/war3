#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YAML配置加载器
支持从YAML文件加载配置
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from ..schemas.app_config import AppConfig
from ..validators.config_validator import ConfigValidator, ValidationResult


class YamlLoader:
    """YAML配置加载器"""
    
    def __init__(self):
        """初始化YAML加载器"""
        self.validator = ConfigValidator()
        self._cache = {}
        self._cache_ttl = 300  # 5分钟缓存
    
    def load_from_file(self, file_path: Union[str, Path], validate: bool = True) -> AppConfig:
        """
        从YAML文件加载配置
        
        Args:
            file_path: YAML文件路径
            validate: 是否验证配置
        
        Returns:
            应用配置对象
        
        Raises:
            FileNotFoundError: 文件不存在
            yaml.YAMLError: YAML解析错误
            ValueError: 配置验证失败
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {file_path}")
        
        # 检查缓存
        cache_key = str(file_path.absolute())
        if cache_key in self._cache:
            cached_data = self._cache[cache_key]
            if self._is_cache_valid(cached_data):
                return cached_data['config']
        
        try:
            # 读取YAML文件
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            # 转换为AppConfig对象
            config = self._convert_to_app_config(yaml_data)
            
            # 验证配置
            if validate:
                validation_result = self.validator.validate(config)
                if not validation_result.is_valid:
                    raise ValueError(f"配置验证失败:\n{validation_result.get_error_summary()}")
            
            # 缓存结果
            self._cache[cache_key] = {
                'config': config,
                'timestamp': self._get_current_timestamp(),
                'file_path': file_path
            }
            
            return config
            
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"YAML解析错误: {e}")
        except Exception as e:
            raise ValueError(f"配置加载失败: {e}")
    
    def load_from_string(self, yaml_string: str, validate: bool = True) -> AppConfig:
        """
        从YAML字符串加载配置
        
        Args:
            yaml_string: YAML格式的字符串
            validate: 是否验证配置
        
        Returns:
            应用配置对象
        
        Raises:
            yaml.YAMLError: YAML解析错误
            ValueError: 配置验证失败
        """
        try:
            # 解析YAML字符串
            yaml_data = yaml.safe_load(yaml_string)
            
            # 转换为AppConfig对象
            config = self._convert_to_app_config(yaml_data)
            
            # 验证配置
            if validate:
                validation_result = self.validator.validate(config)
                if not validation_result.is_valid:
                    raise ValueError(f"配置验证失败:\n{validation_result.get_error_summary()}")
            
            return config
            
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"YAML解析错误: {e}")
        except Exception as e:
            raise ValueError(f"配置加载失败: {e}")
    
    def load_multiple_files(self, file_paths: list[Union[str, Path]], 
                           validate: bool = True) -> AppConfig:
        """
        从多个YAML文件加载配置并合并
        
        Args:
            file_paths: YAML文件路径列表
            validate: 是否验证配置
        
        Returns:
            合并后的应用配置对象
        """
        if not file_paths:
            raise ValueError("文件路径列表不能为空")
        
        # 加载第一个文件作为基础配置
        base_config = self.load_from_file(file_paths[0], validate=False)
        
        # 依次加载并合并其他文件
        for file_path in file_paths[1:]:
            try:
                overlay_config = self.load_from_file(file_path, validate=False)
                base_config = base_config.merge_with(overlay_config)
            except Exception as e:
                # 记录警告但继续处理
                print(f"警告: 无法加载配置文件 {file_path}: {e}")
        
        # 最终验证
        if validate:
            validation_result = self.validator.validate(base_config)
            if not validation_result.is_valid:
                raise ValueError(f"配置验证失败:\n{validation_result.get_error_summary()}")
        
        return base_config
    
    def save_to_file(self, config: AppConfig, file_path: Union[str, Path]) -> None:
        """
        将配置保存到YAML文件
        
        Args:
            config: 应用配置对象
            file_path: 保存路径
        
        Raises:
            IOError: 文件写入失败
        """
        file_path = Path(file_path)
        
        try:
            # 确保目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 转换为字典
            config_dict = config.to_dict()
            
            # 写入YAML文件
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, 
                         allow_unicode=True, indent=2, sort_keys=False)
            
            # 清除缓存
            cache_key = str(file_path.absolute())
            if cache_key in self._cache:
                del self._cache[cache_key]
                
        except Exception as e:
            raise IOError(f"配置保存失败: {e}")
    
    def _convert_to_app_config(self, yaml_data: Dict[str, Any]) -> AppConfig:
        """
        将YAML数据转换为AppConfig对象
        
        Args:
            yaml_data: YAML解析后的数据
        
        Returns:
            AppConfig对象
        """
        if not isinstance(yaml_data, dict):
            raise ValueError("YAML数据必须是字典格式")
        
        # 设置环境标识
        environment = yaml_data.get('environment', 'development')
        
        # 创建AppConfig对象
        config = AppConfig.from_dict(yaml_data)
        config.environment = environment
        
        return config
    
    def _is_cache_valid(self, cached_data: Dict[str, Any]) -> bool:
        """检查缓存是否有效"""
        if 'timestamp' not in cached_data:
            return False
        
        current_time = self._get_current_timestamp()
        return (current_time - cached_data['timestamp']) < self._cache_ttl
    
    def _get_current_timestamp(self) -> float:
        """获取当前时间戳"""
        import time
        return time.time()
    
    def clear_cache(self) -> None:
        """清除缓存"""
        self._cache.clear()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        return {
            'cache_size': len(self._cache),
            'cache_ttl': self._cache_ttl,
            'cached_files': list(self._cache.keys())
        }
    
    def validate_file(self, file_path: Union[str, Path]) -> ValidationResult:
        """
        验证YAML配置文件
        
        Args:
            file_path: YAML文件路径
        
        Returns:
            验证结果
        """
        try:
            config = self.load_from_file(file_path, validate=False)
            return self.validator.validate(config)
        except Exception as e:
            result = ValidationResult()
            result.add_error(f"文件加载失败: {e}")
            return result
