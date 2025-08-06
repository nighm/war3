#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志管理工具
提供统一的日志记录功能
"""

import sys
import logging
from pathlib import Path
from typing import Optional
from loguru import logger


def setup_logger(name: str = "War3MapStudio", 
                log_level: str = "INFO",
                log_file: Optional[str] = None) -> logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径，如果为None则只输出到控制台
    
    Returns:
        配置好的日志记录器
    """
    
    # 移除默认的日志处理器
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    # 如果指定了日志文件，添加文件输出
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
                   "{name}:{function}:{line} - {message}",
            level=log_level,
            rotation="10 MB",  # 日志文件大小超过10MB时轮转
            retention="30 days",  # 保留30天的日志
            compression="zip"  # 压缩旧日志文件
        )
    
    return logger.bind(name=name)


class ProjectLogger:
    """项目专用日志记录器"""
    
    def __init__(self, project_name: str, project_path: Path):
        """
        初始化项目日志记录器
        
        Args:
            project_name: 项目名称
            project_path: 项目路径
        """
        self.project_name = project_name
        self.project_path = project_path
        self.log_dir = project_path / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # 设置项目日志文件
        log_file = self.log_dir / f"{project_name}.log"
        self.logger = setup_logger(
            name=f"Project.{project_name}",
            log_file=str(log_file)
        )
    
    def log_project_start(self) -> None:
        """记录项目启动"""
        self.logger.info(f"项目 '{self.project_name}' 启动")
    
    def log_project_end(self) -> None:
        """记录项目结束"""
        self.logger.info(f"项目 '{self.project_name}' 结束")
    
    def log_editor_launch(self, editor_type: str) -> None:
        """记录编辑器启动"""
        self.logger.info(f"启动编辑器: {editor_type}")
    
    def log_map_save(self, map_file: str) -> None:
        """记录地图保存"""
        self.logger.info(f"保存地图文件: {map_file}")
    
    def log_trigger_edit(self, trigger_name: str) -> None:
        """记录触发器编辑"""
        self.logger.info(f"编辑触发器: {trigger_name}")
    
    def log_unit_edit(self, unit_name: str) -> None:
        """记录单位编辑"""
        self.logger.info(f"编辑单位: {unit_name}")
    
    def log_error(self, error: Exception, context: str = "") -> None:
        """记录错误"""
        self.logger.error(f"错误 {context}: {error}")
    
    def log_warning(self, message: str) -> None:
        """记录警告"""
        self.logger.warning(message)
    
    def log_info(self, message: str) -> None:
        """记录信息"""
        self.logger.info(message)
    
    def log_debug(self, message: str) -> None:
        """记录调试信息"""
        self.logger.debug(message)


class DevelopmentLogger:
    """开发过程日志记录器"""
    
    def __init__(self, log_dir: Path):
        """
        初始化开发日志记录器
        
        Args:
            log_dir: 日志目录
        """
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 开发日志文件
        dev_log_file = self.log_dir / "development.log"
        self.logger = setup_logger(
            name="Development",
            log_file=str(dev_log_file)
        )
    
    def log_feature_start(self, feature_name: str) -> None:
        """记录功能开发开始"""
        self.logger.info(f"开始开发功能: {feature_name}")
    
    def log_feature_complete(self, feature_name: str) -> None:
        """记录功能开发完成"""
        self.logger.info(f"功能开发完成: {feature_name}")
    
    def log_test_start(self, test_name: str) -> None:
        """记录测试开始"""
        self.logger.info(f"开始测试: {test_name}")
    
    def log_test_result(self, test_name: str, success: bool) -> None:
        """记录测试结果"""
        status = "通过" if success else "失败"
        self.logger.info(f"测试结果 {test_name}: {status}")
    
    def log_bug_found(self, bug_description: str) -> None:
        """记录发现的bug"""
        self.logger.warning(f"发现Bug: {bug_description}")
    
    def log_bug_fixed(self, bug_description: str) -> None:
        """记录bug修复"""
        self.logger.info(f"Bug修复: {bug_description}")


def get_logger(name: str = "War3MapStudio") -> logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
    
    Returns:
        日志记录器实例
    """
    return logger.bind(name=name) 