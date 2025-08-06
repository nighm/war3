#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
魔兽争霸3地图开发项目管理工具
基于现有编辑器的工作流程管理
"""

import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.shared.utils.logger import setup_logger
from src.shared.utils.config_loader import ConfigLoader
from src.interfaces.gui.main_window import MainWindow
from src.application.services.project_service import ProjectService
from src.infrastructure.tools.war3_editor_launcher import War3EditorLauncher


class War3MapStudio:
    """魔兽争霸3地图开发工作室主类"""
    
    def __init__(self):
        """初始化地图开发工作室"""
        self.logger = setup_logger("War3MapStudio")
        self.config = ConfigLoader()
        self.project_service = ProjectService()
        self.editor_launcher = War3EditorLauncher()
        
        self.logger.info("魔兽争霸3地图开发工作室启动")
    
    def run_gui(self) -> None:
        """启动图形用户界面"""
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import Qt
            
            app = QApplication(sys.argv)
            app.setApplicationName("War3 Map Studio")
            app.setApplicationVersion("0.1.0")
            
            # 设置应用程序图标
            icon_path = project_root / "resources" / "icons" / "app_icon.png"
            if icon_path.exists():
                from PyQt6.QtGui import QIcon
                app.setWindowIcon(QIcon(str(icon_path)))
            
            # 创建主窗口
            main_window = MainWindow(self.project_service, self.editor_launcher)
            main_window.show()
            
            self.logger.info("GUI界面启动成功")
            sys.exit(app.exec())
            
        except ImportError as e:
            self.logger.error(f"PyQt6未安装: {e}")
            print("请安装PyQt6: pip install PyQt6")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"GUI启动失败: {e}")
            sys.exit(1)
    
    def run_cli(self) -> None:
        """启动命令行界面"""
        try:
            from src.interfaces.cli.cli_interface import CLIInterface
            
            cli = CLIInterface(self.project_service, self.editor_launcher)
            cli.run()
            
        except Exception as e:
            self.logger.error(f"CLI启动失败: {e}")
            sys.exit(1)
    
    def check_environment(self) -> bool:
        """检查开发环境"""
        self.logger.info("检查开发环境...")
        
        # 检查魔兽争霸3安装
        war3_path = self.config.get("war3", "installation_path")
        if not war3_path or not Path(war3_path).exists():
            self.logger.warning("未找到魔兽争霸3安装路径")
            return False
        
        # 检查World Editor
        world_editor_path = Path(war3_path) / "World Editor.exe"
        if not world_editor_path.exists():
            self.logger.warning("未找到World Editor")
            return False
        
        # 检查JNGP（可选）
        jngp_path = Path(war3_path) / "JNGP" / "JNGP.exe"
        if jngp_path.exists():
            self.logger.info("找到JNGP工具")
        else:
            self.logger.info("未找到JNGP工具（可选）")
        
        self.logger.info("环境检查完成")
        return True
    
    def create_project(self, project_name: str, project_type: str) -> bool:
        """创建新项目"""
        try:
            success = self.project_service.create_project(project_name, project_type)
            if success:
                self.logger.info(f"项目 '{project_name}' 创建成功")
                return True
            else:
                self.logger.error(f"项目 '{project_name}' 创建失败")
                return False
        except Exception as e:
            self.logger.error(f"创建项目时出错: {e}")
            return False
    
    def open_project(self, project_path: str) -> bool:
        """打开现有项目"""
        try:
            success = self.project_service.open_project(project_path)
            if success:
                self.logger.info(f"项目 '{project_path}' 打开成功")
                return True
            else:
                self.logger.error(f"项目 '{project_path}' 打开失败")
                return False
        except Exception as e:
            self.logger.error(f"打开项目时出错: {e}")
            return False
    
    def launch_editor(self, editor_type: str = "world_editor") -> bool:
        """启动地图编辑器"""
        try:
            success = self.editor_launcher.launch(editor_type)
            if success:
                self.logger.info(f"编辑器 '{editor_type}' 启动成功")
                return True
            else:
                self.logger.error(f"编辑器 '{editor_type}' 启动失败")
                return False
        except Exception as e:
            self.logger.error(f"启动编辑器时出错: {e}")
            return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="魔兽争霸3地图开发工作室")
    parser.add_argument("--cli", action="store_true", help="使用命令行界面")
    parser.add_argument("--create-project", type=str, help="创建新项目")
    parser.add_argument("--project-type", type=str, default="rpg", 
                       choices=["rpg", "td", "moba", "survival", "melee"],
                       help="项目类型")
    parser.add_argument("--open-project", type=str, help="打开现有项目")
    parser.add_argument("--launch-editor", type=str, 
                       choices=["world_editor", "jngp"], 
                       default="world_editor", help="启动编辑器")
    parser.add_argument("--check-env", action="store_true", help="检查开发环境")
    
    args = parser.parse_args()
    
    # 创建工作室实例
    studio = War3MapStudio()
    
    # 检查环境
    if args.check_env:
        if studio.check_environment():
            print("✅ 开发环境检查通过")
        else:
            print("❌ 开发环境检查失败")
        return
    
    # 创建项目
    if args.create_project:
        if studio.create_project(args.create_project, args.project_type):
            print(f"✅ 项目 '{args.create_project}' 创建成功")
        else:
            print(f"❌ 项目 '{args.create_project}' 创建失败")
        return
    
    # 打开项目
    if args.open_project:
        if studio.open_project(args.open_project):
            print(f"✅ 项目 '{args.open_project}' 打开成功")
        else:
            print(f"❌ 项目 '{args.open_project}' 打开失败")
        return
    
    # 启动编辑器
    if args.launch_editor:
        if studio.launch_editor(args.launch_editor):
            print(f"✅ 编辑器 '{args.launch_editor}' 启动成功")
        else:
            print(f"❌ 编辑器 '{args.launch_editor}' 启动失败")
        return
    
    # 启动界面
    if args.cli:
        studio.run_cli()
    else:
        studio.run_gui()


if __name__ == "__main__":
    main() 