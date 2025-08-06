#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理工具
提供统一的配置加载和管理功能
"""

import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Union
from configparser import ConfigParser


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        初始化配置加载器
        
        Args:
            config_dir: 配置文件目录，如果为None则使用默认目录
        """
        if config_dir is None:
            # 使用项目根目录下的config目录
            project_root = Path(__file__).parent.parent.parent
            self.config_dir = project_root / "config"
        else:
            self.config_dir = config_dir
        
        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 默认配置文件
        self.default_config = {
            "war3": {
                "installation_path": "",
                "world_editor_path": "",
                "jngp_path": "",
                "maps_directory": ""
            },
            "editor": {
                "default_editor": "world_editor",
                "auto_save_interval": "5",
                "backup_enabled": "true",
                "backup_interval": "10"
            },
            "project": {
                "default_project_type": "rpg",
                "auto_backup": "true",
                "version_control": "true"
            },
            "development": {
                "log_level": "INFO",
                "debug_mode": "false",
                "test_mode": "false"
            }
        }
        
        # 加载配置
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        config = {}
        
        # 尝试加载YAML配置文件
        yaml_config_file = self.config_dir / "config.yaml"
        if yaml_config_file.exists():
            try:
                with open(yaml_config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"加载YAML配置文件失败: {e}")
        
        # 尝试加载JSON配置文件
        json_config_file = self.config_dir / "config.json"
        if json_config_file.exists():
            try:
                with open(json_config_file, 'r', encoding='utf-8') as f:
                    json_config = json.load(f)
                    config.update(json_config)
            except Exception as e:
                print(f"加载JSON配置文件失败: {e}")
        
        # 尝试加载INI配置文件
        ini_config_file = self.config_dir / "config.ini"
        if ini_config_file.exists():
            try:
                parser = ConfigParser()
                parser.read(ini_config_file, encoding='utf-8')
                
                ini_config = {}
                for section in parser.sections():
                    ini_config[section] = dict(parser[section])
                
                config.update(ini_config)
            except Exception as e:
                print(f"加载INI配置文件失败: {e}")
        
        # 合并默认配置
        merged_config = self._merge_config(self.default_config, config)
        
        return merged_config
    
    def _merge_config(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """合并配置"""
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            section: 配置节
            key: 配置键
            default: 默认值
        
        Returns:
            配置值
        """
        try:
            return self.config[section][key]
        except KeyError:
            return default
    
    def set(self, section: str, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            section: 配置节
            key: 配置键
            value: 配置值
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
    
    def save(self, format: str = "yaml") -> bool:
        """
        保存配置到文件
        
        Args:
            format: 文件格式 (yaml, json, ini)
        
        Returns:
            是否保存成功
        """
        try:
            if format.lower() == "yaml":
                config_file = self.config_dir / "config.yaml"
                with open(config_file, 'w', encoding='utf-8') as f:
                    yaml.dump(self.config, f, default_flow_style=False, 
                             allow_unicode=True, indent=2)
            
            elif format.lower() == "json":
                config_file = self.config_dir / "config.json"
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            elif format.lower() == "ini":
                config_file = self.config_dir / "config.ini"
                parser = ConfigParser()
                
                for section, items in self.config.items():
                    parser.add_section(section)
                    for key, value in items.items():
                        parser.set(section, key, str(value))
                
                with open(config_file, 'w', encoding='utf-8') as f:
                    parser.write(f)
            
            else:
                raise ValueError(f"不支持的配置格式: {format}")
            
            return True
            
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get_war3_path(self) -> Optional[Path]:
        """获取魔兽争霸3安装路径"""
        path = self.get("war3", "installation_path")
        if path and Path(path).exists():
            return Path(path)
        return None
    
    def get_world_editor_path(self) -> Optional[Path]:
        """获取World Editor路径"""
        # 首先尝试从配置中获取
        path = self.get("war3", "world_editor_path")
        if path and Path(path).exists():
            return Path(path)
        
        # 尝试从魔兽争霸3安装目录查找
        war3_path = self.get_war3_path()
        if war3_path:
            world_editor_path = war3_path / "World Editor.exe"
            if world_editor_path.exists():
                return world_editor_path
        
        return None
    
    def get_jngp_path(self) -> Optional[Path]:
        """获取JNGP路径"""
        # 首先尝试从配置中获取
        path = self.get("war3", "jngp_path")
        if path and Path(path).exists():
            return Path(path)
        
        # 尝试从魔兽争霸3安装目录查找
        war3_path = self.get_war3_path()
        if war3_path:
            jngp_path = war3_path / "JNGP" / "JNGP.exe"
            if jngp_path.exists():
                return jngp_path
        
        return None
    
    def get_maps_directory(self) -> Optional[Path]:
        """获取地图目录"""
        path = self.get("war3", "maps_directory")
        if path:
            maps_dir = Path(path)
            if maps_dir.exists():
                return maps_dir
        
        # 尝试从魔兽争霸3安装目录查找
        war3_path = self.get_war3_path()
        if war3_path:
            maps_dir = war3_path / "Maps"
            if maps_dir.exists():
                return maps_dir
        
        return None
    
    def validate_config(self) -> Dict[str, bool]:
        """
        验证配置
        
        Returns:
            验证结果字典
        """
        results = {}
        
        # 验证魔兽争霸3安装路径
        war3_path = self.get_war3_path()
        results["war3_installed"] = war3_path is not None
        
        # 验证World Editor
        world_editor_path = self.get_world_editor_path()
        results["world_editor_available"] = world_editor_path is not None
        
        # 验证JNGP
        jngp_path = self.get_jngp_path()
        results["jngp_available"] = jngp_path is not None
        
        # 验证地图目录
        maps_dir = self.get_maps_directory()
        results["maps_directory_available"] = maps_dir is not None
        
        return results


class ProjectConfig:
    """项目配置管理器"""
    
    def __init__(self, project_path: Path):
        """
        初始化项目配置管理器
        
        Args:
            project_path: 项目路径
        """
        self.project_path = project_path
        self.config_file = project_path / "project_config.yaml"
        self.config = self._load_project_config()
    
    def _load_project_config(self) -> Dict[str, Any]:
        """加载项目配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                print(f"加载项目配置文件失败: {e}")
        
        # 返回默认配置
        return {
            "project_info": {
                "name": self.project_path.name,
                "type": "rpg",
                "version": "1.0.0",
                "description": ""
            },
            "development": {
                "auto_save": True,
                "backup_enabled": True,
                "version_control": True
            },
            "map_settings": {
                "map_size": "128x128",
                "tileset": "Lordaeron Summer",
                "players": 4
            },
            "editor_settings": {
                "default_editor": "world_editor",
                "jass_mode": False
            }
        }
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """获取项目配置值"""
        try:
            return self.config[section][key]
        except KeyError:
            return default
    
    def set(self, section: str, key: str, value: Any) -> None:
        """设置项目配置值"""
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
    
    def save(self) -> bool:
        """保存项目配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            return True
        except Exception as e:
            print(f"保存项目配置失败: {e}")
            return False 