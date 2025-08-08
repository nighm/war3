#!/usr/bin/env python3
"""
快速导入Y3地图项目到war3项目目录
"""

import os
import shutil
import json
from datetime import datetime

def quick_import_project():
    """快速导入ProjectName001_1项目"""
    
    # 配置路径
    y3_local_data = r"D:\Program Files\y3\games\2.0\game\LocalData"
    source_project = "ProjectName001_1"
    target_project = "ProjectName001_1"
    
    source_path = os.path.join(y3_local_data, source_project)
    target_path = os.path.join("maps", target_project)
    
    # 检查源项目是否存在
    if not os.path.exists(source_path):
        print(f"错误: Y3项目不存在 - {source_path}")
        print("请确保已在Y3编辑器中创建并保存了地图项目")
        return False
    
    # 检查目标目录
    if os.path.exists(target_path):
        print(f"警告: 目标目录已存在 - {target_path}")
        response = input("是否覆盖? (y/N): ")
        if response.lower() != 'y':
            print("导入已取消")
            return False
    
    try:
        # 复制项目
        shutil.copytree(source_path, target_path, dirs_exist_ok=True)
        print(f"✓ 成功导入项目: {source_project} -> {target_path}")
        
        # 创建项目信息文件
        project_info = {
            "name": target_project,
            "original_name": source_project,
            "import_time": datetime.now().isoformat(),
            "y3_path": source_path,
            "description": "从Y3编辑器导入的地图项目"
        }
        
        info_file = os.path.join(target_path, "project_info.json")
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(project_info, f, indent=2, ensure_ascii=False)
        
        print("✓ 项目信息文件已创建")
        print(f"✓ 项目已集成到war3项目中，路径: {target_path}")
        print("\n下一步建议:")
        print("1. 使用 'python tools/map_manager.py' 进行项目管理")
        print("2. 用Git提交项目变更: 'python sync_to_github.py'")
        print("3. 开始在地图项目中进行开发和优化")
        
        return True
        
    except Exception as e:
        print(f"错误: 导入失败 - {e}")
        return False

if __name__ == "__main__":
    print("=== 快速导入Y3地图项目 ===")
    quick_import_project()
