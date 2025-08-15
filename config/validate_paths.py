#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路径验证脚本
帮助用户验证和配置War3相关路径
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional


class PathValidator:
    """路径验证器"""
    
    def __init__(self):
        self.base_paths = {
            'C:\\Program Files': 'Program Files',
            'C:\\Program Files (x86)': 'Program Files (x86)',
            'D:\\Program Files': 'D盘 Program Files',
            'D:\\Program Files (x86)': 'D盘 Program Files (x86)',
        }
    
    def find_war3_installation(self) -> List[Path]:
        """查找War3安装路径"""
        found_paths = []
        
        for base_path, description in self.base_paths.items():
            base = Path(base_path)
            if base.exists():
                # 检查常见的War3目录名
                possible_names = [
                    'Warcraft III',
                    'Warcraft III - Reforged',
                    'Warcraft III Reforged',
                    'Warcraft3',
                    'War3'
                ]
                
                for name in possible_names:
                    war3_path = base / name
                    if war3_path.exists():
                        # 检查是否有War3可执行文件
                        exe_files = ['Warcraft III.exe', 'Warcraft3.exe', 'War3.exe']
                        for exe in exe_files:
                            if (war3_path / exe).exists():
                                found_paths.append(war3_path)
                                print(f"✅ 找到War3安装: {war3_path} ({description})")
                                break
        
        return found_paths
    
    def find_y3_editor(self) -> List[Path]:
        """查找Y3编辑器"""
        found_paths = []
        
        # 检查常见的Y3编辑器路径
        possible_paths = [
            Path("D:\\Program Files\\y3\\games\\2.0\\game\\Editor.exe"),
            Path("C:\\Program Files\\y3\\games\\2.0\\game\\Editor.exe"),
            Path("D:\\y3\\games\\2.0\\game\\Editor.exe"),
            Path("C:\\y3\\games\\2.0\\game\\Editor.exe"),
        ]
        
        for path in possible_paths:
            if path.exists():
                found_paths.append(path.parent)
                print(f"✅ 找到Y3编辑器: {path.parent}")
        
        return found_paths
    
    def validate_path(self, path_str: str) -> bool:
        """验证路径是否存在"""
        if not path_str:
            return False
        
        path = Path(path_str)
        if not path.exists():
            print(f"❌ 路径不存在: {path}")
            return False
        
        print(f"✅ 路径有效: {path}")
        return True
    
    def generate_env_config(self, war3_path: Optional[Path] = None, 
                           y3_path: Optional[Path] = None) -> str:
        """生成环境变量配置"""
        config = "# War3 Map Studio 路径配置\n"
        config += "# 请根据实际情况修改以下路径\n\n"
        
        if war3_path:
            config += f"WAR3_INSTALLATION_PATH={war3_path}\n"
            config += f"WAR3_WORLD_EDITOR_PATH={war3_path / 'World Editor.exe'}\n"
            config += f"WAR3_MAPS_DIRECTORY={war3_path / 'Maps'}\n"
        else:
            config += "WAR3_INSTALLATION_PATH=\n"
            config += "WAR3_WORLD_EDITOR_PATH=\n"
            config += "WAR3_MAPS_DIRECTORY=\n"
        
        config += "\n"
        
        if y3_path:
            config += f"Y3_EDITOR_PATH={y3_path / 'Editor.exe'}\n"
        else:
            config += "Y3_EDITOR_PATH=\n"
        
        return config
    
    def run_validation(self):
        """运行路径验证"""
        print("🔍 War3 Map Studio 路径验证工具")
        print("=" * 50)
        
        # 查找War3安装
        print("\n📁 查找War3安装路径...")
        war3_paths = self.find_war3_installation()
        
        if not war3_paths:
            print("❌ 未找到War3安装路径")
            print("💡 请手动安装War3或检查安装路径")
        elif len(war3_paths) == 1:
            selected_war3 = war3_paths[0]
            print(f"🎯 自动选择War3路径: {selected_war3}")
        else:
            print("🔍 找到多个War3安装，请选择:")
            for i, path in enumerate(war3_paths, 1):
                print(f"  {i}. {path}")
            
            try:
                choice = int(input("请选择 (输入数字): ")) - 1
                if 0 <= choice < len(war3_paths):
                    selected_war3 = war3_paths[choice]
                else:
                    selected_war3 = None
            except (ValueError, KeyboardInterrupt):
                selected_war3 = None
        
        # 查找Y3编辑器
        print("\n📁 查找Y3编辑器...")
        y3_paths = self.find_y3_editor()
        
        if not y3_paths:
            print("❌ 未找到Y3编辑器")
            print("💡 请手动安装Y3编辑器或检查安装路径")
            selected_y3 = None
        elif len(y3_paths) == 1:
            selected_y3 = y3_paths[0]
            print(f"🎯 自动选择Y3编辑器路径: {selected_y3}")
        else:
            print("🔍 找到多个Y3编辑器，请选择:")
            for i, path in enumerate(y3_paths, 1):
                print(f"  {i}. {path}")
            
            try:
                choice = int(input("请选择 (输入数字): ")) - 1
                if 0 <= choice < len(y3_paths):
                    selected_y3 = y3_paths[choice]
                else:
                    selected_y3 = None
            except (ValueError, KeyboardInterrupt):
                selected_y3 = None
        
        # 生成配置
        print("\n📝 生成环境变量配置...")
        env_config = self.generate_env_config(selected_war3, selected_y3)
        
        # 保存配置
        config_file = Path("config/environments/env.local")
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(env_config)
        
        print(f"✅ 配置已保存到: {config_file}")
        print("\n📋 配置内容:")
        print("-" * 30)
        print(env_config)
        
        # 验证生成的配置
        print("\n🔍 验证生成的配置...")
        if selected_war3:
            self.validate_path(str(selected_war3))
            self.validate_path(str(selected_war3 / "World Editor.exe"))
            self.validate_path(str(selected_war3 / "Maps"))
        
        if selected_y3:
            self.validate_path(str(selected_y3 / "Editor.exe"))
        
        print("\n🎉 路径验证完成！")
        print("💡 请检查生成的配置文件并根据需要调整路径")


def main():
    """主函数"""
    validator = PathValidator()
    try:
        validator.run_validation()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 验证过程中出现错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
