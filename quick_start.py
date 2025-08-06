#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
魔兽争霸3地图开发快速开始脚本
帮助用户快速设置开发环境并创建第一个项目
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional


class QuickStart:
    """快速开始助手"""
    
    def __init__(self):
        """初始化快速开始助手"""
        self.project_root = Path(__file__).parent
        self.config_file = self.project_root / "config" / "config.yaml"
    
    def check_python_version(self) -> bool:
        """检查Python版本"""
        print("🔍 检查Python版本...")
        
        if sys.version_info < (3, 8):
            print("❌ Python版本过低，需要Python 3.8或更高版本")
            print(f"当前版本: {sys.version}")
            return False
        
        print(f"✅ Python版本检查通过: {sys.version}")
        return True
    
    def check_dependencies(self) -> bool:
        """检查依赖包"""
        print("🔍 检查依赖包...")
        
        try:
            import PyQt6
            print("✅ PyQt6已安装")
        except ImportError:
            print("❌ PyQt6未安装，正在安装...")
            subprocess.run([sys.executable, "-m", "pip", "install", "PyQt6"])
        
        try:
            import yaml
            print("✅ PyYAML已安装")
        except ImportError:
            print("❌ PyYAML未安装，正在安装...")
            subprocess.run([sys.executable, "-m", "pip", "install", "PyYAML"])
        
        try:
            import loguru
            print("✅ loguru已安装")
        except ImportError:
            print("❌ loguru未安装，正在安装...")
            subprocess.run([sys.executable, "-m", "pip", "install", "loguru"])
        
        print("✅ 依赖包检查完成")
        return True
    
    def setup_virtual_environment(self) -> bool:
        """设置虚拟环境"""
        print("🔧 设置虚拟环境...")
        
        venv_path = self.project_root / "venv"
        
        if not venv_path.exists():
            print("创建虚拟环境...")
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)])
            print("✅ 虚拟环境创建完成")
        else:
            print("✅ 虚拟环境已存在")
        
        # 安装依赖
        print("安装项目依赖...")
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
            print("✅ 依赖安装完成")
        else:
            print("⚠️ 未找到requirements.txt文件")
        
        return True
    
    def configure_war3_path(self) -> bool:
        """配置魔兽争霸3路径"""
        print("🔧 配置魔兽争霸3路径...")
        
        # 常见的魔兽争霸3安装路径
        common_paths = [
            "C:\\Program Files\\Warcraft III",
            "C:\\Program Files (x86)\\Warcraft III",
            "D:\\Program Files\\Warcraft III",
            "D:\\Program Files (x86)\\Warcraft III"
        ]
        
        war3_path = None
        for path in common_paths:
            if Path(path).exists():
                war3_path = path
                break
        
        if war3_path:
            print(f"✅ 找到魔兽争霸3安装路径: {war3_path}")
            
            # 更新配置文件
            if self.config_file.exists():
                import yaml
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                config['war3']['installation_path'] = war3_path
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False, 
                             allow_unicode=True, indent=2)
                
                print("✅ 配置文件已更新")
        else:
            print("⚠️ 未找到魔兽争霸3安装路径")
            print("请手动编辑 config/config.yaml 文件，设置正确的安装路径")
        
        return True
    
    def create_sample_project(self) -> bool:
        """创建示例项目"""
        print("🔧 创建示例项目...")
        
        sample_project_name = "我的第一个地图"
        
        # 检查项目模板生成器
        template_script = self.project_root / "scripts" / "create_project_template.py"
        if template_script.exists():
            try:
                subprocess.run([
                    sys.executable, str(template_script),
                    sample_project_name,
                    "--type", "rpg",
                    "--author", "新手开发者",
                    "--description", "我的第一个魔兽争霸3地图项目"
                ], check=True)
                
                print(f"✅ 示例项目创建成功: {sample_project_name}")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ 创建示例项目失败: {e}")
                return False
        else:
            print("⚠️ 未找到项目模板生成器")
            return False
    
    def show_next_steps(self) -> None:
        """显示下一步操作指南"""
        print("\n" + "="*50)
        print("🎉 快速设置完成！")
        print("="*50)
        
        print("\n📝 下一步操作:")
        print("1. 进入项目目录:")
        print("   cd 我的第一个地图")
        
        print("\n2. 阅读项目文档:")
        print("   # 查看README.md了解项目结构")
        print("   # 查看docs/使用指南.md了解开发流程")
        
        print("\n3. 启动World Editor:")
        print("   # 找到魔兽争霸3安装目录")
        print("   # 运行 World Editor.exe")
        
        print("\n4. 开始地图开发:")
        print("   # 创建新地图")
        print("   # 设计地形")
        print("   # 添加单位")
        print("   # 编写触发器")
        
        print("\n5. 测试地图:")
        print("   # 在魔兽争霸3中测试地图")
        print("   # 调试和优化")
        
        print("\n📚 学习资源:")
        print("- 查看 docs/地图开发指南.md")
        print("- 参考 docs/使用指南.md")
        print("- 访问魔兽争霸3官方论坛")
        print("- 加入地图制作社区")
        
        print("\n🔧 开发工具:")
        print("- World Editor: 官方地图编辑器")
        print("- JNGP: 增强的JASS编辑器（可选）")
        print("- MPQ Editor: 资源文件管理工具")
        
        print("\n💡 提示:")
        print("- 定期备份地图文件")
        print("- 使用版本控制管理项目")
        print("- 测试地图在不同环境下的表现")
        print("- 收集玩家反馈并持续改进")
        
        print("\n" + "="*50)
        print("祝您地图开发愉快！")
        print("="*50)
    
    def run(self) -> bool:
        """运行快速开始流程"""
        print("🚀 魔兽争霸3地图开发快速开始")
        print("="*50)
        
        # 检查Python版本
        if not self.check_python_version():
            return False
        
        # 检查依赖包
        if not self.check_dependencies():
            return False
        
        # 设置虚拟环境
        if not self.setup_virtual_environment():
            return False
        
        # 配置魔兽争霸3路径
        if not self.configure_war3_path():
            return False
        
        # 创建示例项目
        if not self.create_sample_project():
            return False
        
        # 显示下一步操作指南
        self.show_next_steps()
        
        return True


def main():
    """主函数"""
    quick_start = QuickStart()
    
    try:
        success = quick_start.run()
        if success:
            print("\n✅ 快速设置完成！")
        else:
            print("\n❌ 快速设置失败！")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 