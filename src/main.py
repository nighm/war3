#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
魔兽争霸3地图开发项目管理工具
基于DDD架构的工作流程管理
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
from src.domain.services.map_analysis_service import DefaultMapAnalysisService
from src.infrastructure.repositories.json_map_repository import JsonMapRepository
from src.application.services.project_service import ProjectService
from src.domain.services.batch_processor import ProcessingRule


class War3MapStudio:
    """魔兽争霸3地图开发工作室主类"""
    
    def __init__(self):
        """初始化地图开发工作室"""
        self.logger = setup_logger("War3MapStudio")
        self.config = ConfigLoader()
        
        # 初始化DDD架构组件
        self.map_repository = JsonMapRepository()
        self.analysis_service = DefaultMapAnalysisService()
        self.project_service = ProjectService(self.map_repository, self.analysis_service)
        
        self.logger.info("魔兽争霸3地图开发工作室启动")
    
    def run_gui(self) -> None:
        """启动图形用户界面"""
        try:
            # 暂时使用命令行界面，GUI将在后续实现
            self.logger.info("GUI界面暂未实现，使用命令行界面")
            self.run_cli()
            
        except Exception as e:
            self.logger.error(f"界面启动失败: {e}")
            print(f"界面启动失败: {e}")
            sys.exit(1)
    
    def run_cli(self) -> None:
        """启动命令行界面"""
        try:
            print("=== 魔兽争霸3地图开发工作室 ===")
            print("1. 创建新项目")
            print("2. 打开现有项目")
            print("3. 列出所有项目")
            print("4. 分析项目")
            print("5. 批量处理")
            print("6. 退出")
            
            while True:
                choice = input("\n请选择操作 (1-5): ").strip()
                
                if choice == "1":
                    self._create_project_cli()
                elif choice == "2":
                    self._open_project_cli()
                elif choice == "3":
                    self._list_projects_cli()
                elif choice == "4":
                    self._analyze_project_cli()
                elif choice == "5":
                    self._batch_process_cli()
                elif choice == "6":
                    print("再见！")
                    break
                else:
                    print("无效选择，请重新输入")
                    
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
        except Exception as e:
            self.logger.error(f"CLI运行失败: {e}")
            print(f"CLI运行失败: {e}")
    
    def _create_project_cli(self):
        """命令行创建项目"""
        try:
            name = input("请输入项目名称: ").strip()
            if not name:
                print("项目名称不能为空")
                return
            
            print("可选项目类型:")
            print("1. rpg - 角色扮演")
            print("2. td - 塔防")
            print("3. moba - 多人在线竞技")
            print("4. survival - 生存")
            print("5. melee - 对战")
            
            type_choice = input("请选择项目类型 (1-5): ").strip()
            type_map = {
                "1": "rpg",
                "2": "td", 
                "3": "moba",
                "4": "survival",
                "5": "melee"
            }
            
            project_type = type_map.get(type_choice, "rpg")
            description = input("请输入项目描述 (可选): ").strip()
            
            project = self.project_service.create_project(name, project_type, description)
            if project:
                print(f"✅ 项目 '{name}' 创建成功")
                print(f"项目路径: {project.project_path}")
            else:
                print(f"❌ 项目 '{name}' 创建失败")
                
        except Exception as e:
            print(f"创建项目失败: {e}")
    
    def _open_project_cli(self):
        """命令行打开项目"""
        try:
            path = input("请输入项目路径: ").strip()
            if not path:
                print("项目路径不能为空")
                return
            
            project = self.project_service.open_project(path)
            if project:
                print(f"✅ 项目 '{project.name}' 打开成功")
                print(f"项目类型: {project.project_type}")
                print(f"项目路径: {project.project_path}")
            else:
                print(f"❌ 项目 '{path}' 打开失败")
                
        except Exception as e:
            print(f"打开项目失败: {e}")
    
    def _list_projects_cli(self):
        """命令行列出项目"""
        try:
            projects = self.project_service.list_projects()
            if not projects:
                print("暂无项目")
                return
            
            print(f"\n找到 {len(projects)} 个项目:")
            for i, project in enumerate(projects, 1):
                status = "活跃" if project.is_active and not project.is_archived else "归档"
                print(f"{i}. {project.name} ({project.project_type}) - {status}")
                print(f"   路径: {project.project_path}")
                print(f"   描述: {project.description}")
                print()
                
        except Exception as e:
            print(f"列出项目失败: {e}")
    
    def _analyze_project_cli(self):
        """命令行分析项目"""
        try:
            projects = self.project_service.list_projects()
            if not projects:
                print("暂无项目可分析")
                return
            
            print("请选择要分析的项目:")
            for i, project in enumerate(projects, 1):
                print(f"{i}. {project.name}")
            
            choice = input("请输入项目编号: ").strip()
            try:
                index = int(choice) - 1
                if 0 <= index < len(projects):
                    project = projects[index]
                    print(f"\n正在分析项目 '{project.name}'...")
                    
                    analysis = self.project_service.analyze_project(project)
                    
                    print("\n=== 项目分析结果 ===")
                    print(f"文件总数: {analysis['structure'].get('file_count', 0)}")
                    print(f"目录总数: {analysis['structure'].get('directory_count', 0)}")
                    print(f"总大小: {analysis['structure'].get('total_size', 0) / (1024*1024):.2f} MB")
                    print(f"资源总数: {analysis['resources'].get('total_resources', 0)}")
                    
                    # 显示优化建议
                    suggestions = analysis['performance'].get('optimization_suggestions', [])
                    if suggestions:
                        print("\n优化建议:")
                        for suggestion in suggestions:
                            print(f"- {suggestion}")
                    
                else:
                    print("无效的项目编号")
            except ValueError:
                print("请输入有效的数字")
                
        except Exception as e:
            print(f"分析项目失败: {e}")
    
    def _batch_process_cli(self):
        """命令行批量处理"""
        try:
            print("\n=== 批量处理功能 ===")
            print("1. 批量分析项目")
            print("2. 批量归档项目")
            print("3. 批量激活项目")
            print("4. 批量清理项目")
            print("5. 批量验证项目")
            print("6. 查看处理统计")
            print("7. 返回主菜单")
            
            choice = input("请选择批量操作 (1-7): ").strip()
            
            if choice == "1":
                self._batch_analyze_cli()
            elif choice == "2":
                self._batch_archive_cli()
            elif choice == "3":
                self._batch_activate_cli()
            elif choice == "4":
                self._batch_cleanup_cli()
            elif choice == "5":
                self._batch_validate_cli()
            elif choice == "6":
                self._show_batch_stats_cli()
            elif choice == "7":
                return
            else:
                print("无效选择")
                
        except Exception as e:
            print(f"批量处理失败: {e}")
    
    def _batch_analyze_cli(self):
        """批量分析项目"""
        try:
            print("\n=== 批量分析项目 ===")
            print("选择分析规则:")
            print("1. 所有项目")
            print("2. 按类型筛选")
            print("3. 按大小筛选")
            
            rule_choice = input("请选择规则 (1-3): ").strip()
            
            if rule_choice == "1":
                rule = ProcessingRule.ALL
                kwargs = {}
            elif rule_choice == "2":
                print("可选项目类型: rpg, td, moba, survival, melee")
                project_type = input("请输入项目类型: ").strip()
                rule = ProcessingRule.BY_TYPE
                kwargs = {"project_type": project_type}
            elif rule_choice == "3":
                size_limit = input("请输入大小限制(MB): ").strip()
                try:
                    size_limit = float(size_limit)
                    rule = ProcessingRule.BY_SIZE
                    kwargs = {"size_limit_mb": size_limit}
                except ValueError:
                    print("无效的大小值")
                    return
            else:
                print("无效选择")
                return
            
            print(f"\n开始批量分析项目...")
            results = self.project_service.batch_analyze_projects(rule, **kwargs)
            print(f"批量分析完成，处理了 {len(results)} 个项目")
            
        except Exception as e:
            print(f"批量分析失败: {e}")
    
    def _batch_archive_cli(self):
        """批量归档项目"""
        try:
            print("\n=== 批量归档项目 ===")
            print("选择归档规则:")
            print("1. 所有项目")
            print("2. 按类型筛选")
            print("3. 按大小筛选")
            
            rule_choice = input("请选择规则 (1-3): ").strip()
            
            if rule_choice == "1":
                rule = ProcessingRule.ALL
                kwargs = {}
            elif rule_choice == "2":
                print("可选项目类型: rpg, td, moba, survival, melee")
                project_type = input("请输入项目类型: ").strip()
                rule = ProcessingRule.BY_TYPE
                kwargs = {"project_type": project_type}
            elif rule_choice == "3":
                size_limit = input("请输入大小限制(MB): ").strip()
                try:
                    size_limit = float(size_limit)
                    rule = ProcessingRule.BY_SIZE
                    kwargs = {"size_limit_mb": size_limit}
                except ValueError:
                    print("无效的大小值")
                    return
            else:
                print("无效选择")
                return
            
            confirm = input("确定要归档选中的项目吗？(y/N): ").strip().lower()
            if confirm != 'y':
                print("操作已取消")
                return
            
            print(f"\n开始批量归档项目...")
            results = self.project_service.batch_archive_projects(rule, **kwargs)
            print(f"批量归档完成，处理了 {len(results)} 个项目")
            
        except Exception as e:
            print(f"批量归档失败: {e}")
    
    def _batch_activate_cli(self):
        """批量激活项目"""
        try:
            print("\n=== 批量激活项目 ===")
            print("选择激活规则:")
            print("1. 所有项目")
            print("2. 按类型筛选")
            
            rule_choice = input("请选择规则 (1-2): ").strip()
            
            if rule_choice == "1":
                rule = ProcessingRule.ALL
                kwargs = {}
            elif rule_choice == "2":
                print("可选项目类型: rpg, td, moba, survival, melee")
                project_type = input("请输入项目类型: ").strip()
                rule = ProcessingRule.BY_TYPE
                kwargs = {"project_type": project_type}
            else:
                print("无效选择")
                return
            
            confirm = input("确定要激活选中的项目吗？(y/N): ").strip().lower()
            if confirm != 'y':
                print("操作已取消")
                return
            
            print(f"\n开始批量激活项目...")
            results = self.project_service.batch_activate_projects(rule, **kwargs)
            print(f"批量激活完成，处理了 {len(results)} 个项目")
            
        except Exception as e:
            print(f"批量激活失败: {e}")
    
    def _batch_cleanup_cli(self):
        """批量清理项目"""
        try:
            print("\n=== 批量清理项目 ===")
            print("选择清理规则:")
            print("1. 所有项目")
            print("2. 按类型筛选")
            
            rule_choice = input("请选择规则 (1-2): ").strip()
            
            if rule_choice == "1":
                rule = ProcessingRule.ALL
                kwargs = {}
            elif rule_choice == "2":
                print("可选项目类型: rpg, td, moba, survival, melee")
                print("可选项目类型: rpg, td, moba, survival, melee")
                project_type = input("请输入项目类型: ").strip()
                rule = ProcessingRule.BY_TYPE
                kwargs = {"project_type": project_type}
            else:
                print("无效选择")
                return
            
            confirm = input("确定要清理选中的项目吗？(y/N): ").strip().lower()
            if confirm != 'y':
                print("操作已取消")
                return
            
            print(f"\n开始批量清理项目...")
            results = self.project_service.batch_cleanup_projects(rule, **kwargs)
            print(f"批量清理完成，处理了 {len(results)} 个项目")
            
        except Exception as e:
            print(f"批量清理失败: {e}")
    
    def _batch_validate_cli(self):
        """批量验证项目"""
        try:
            print("\n=== 批量验证项目 ===")
            print("选择验证规则:")
            print("1. 所有项目")
            print("2. 按类型筛选")
            
            rule_choice = input("请选择规则 (1-2): ").strip()
            
            if rule_choice == "1":
                rule = ProcessingRule.ALL
                kwargs = {}
            elif rule_choice == "2":
                print("可选项目类型: rpg, td, moba, survival, melee")
                project_type = input("请输入项目类型: ").strip()
                rule = ProcessingRule.BY_TYPE
                kwargs = {"project_type": project_type}
            else:
                print("无效选择")
                return
            
            print(f"\n开始批量验证项目...")
            results = self.project_service.batch_validate_projects(rule, **kwargs)
            print(f"批量验证完成，处理了 {len(results)} 个项目")
            
        except Exception as e:
            print(f"批量验证失败: {e}")
    
    def _show_batch_stats_cli(self):
        """显示批量处理统计"""
        try:
            stats = self.project_service.get_batch_processing_stats()
            
            print("\n=== 批量处理统计 ===")
            print(f"总处理项目数: {stats['total_processed']}")
            print(f"成功数量: {stats['success_count']}")
            print(f"失败数量: {stats['failure_count']}")
            print(f"成功率: {stats['success_rate']:.1f}%")
            print(f"平均处理时间: {stats['average_duration']} 秒")
            
        except Exception as e:
            print(f"获取统计信息失败: {e}")
    
    def check_environment(self) -> bool:
        """检查开发环境"""
        self.logger.info("检查开发环境...")
        
        # 检查Python版本
        python_version = sys.version_info
        if python_version < (3, 8):
            self.logger.error("Python版本过低，需要3.8或更高版本")
            return False
        
        self.logger.info(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # 检查必要的目录
        required_dirs = ["src", "src/domain", "src/application", "src/infrastructure"]
        for dir_path in required_dirs:
            full_path = project_root / dir_path
            if not full_path.exists():
                self.logger.error(f"缺少必要目录: {dir_path}")
                return False
        
        self.logger.info("环境检查完成")
        return True
    
    def create_project(self, project_name: str, project_type: str) -> bool:
        """创建新项目"""
        try:
            project = self.project_service.create_project(project_name, project_type)
            if project:
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
            project = self.project_service.open_project(project_path)
            if project:
                self.logger.info(f"项目 '{project_path}' 打开成功")
                return True
            else:
                self.logger.error(f"项目 '{project_path}' 打开失败")
                return False
        except Exception as e:
            self.logger.error(f"打开项目时出错: {e}")
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
    
    # 启动界面
    if args.cli:
        studio.run_cli()
    else:
        studio.run_gui()


if __name__ == "__main__":
    main() 