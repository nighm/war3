import os
import shutil
import json
import sys
from datetime import datetime

class MapManager:
    def __init__(self):
        self.y3_local_data = r"D:\Program Files\y3\games\2.0\game\LocalData"
        self.project_maps_dir = "maps"
        self.templates_dir = "templates"
        
    def list_y3_projects(self):
        """列出Y3编辑器中的所有地图项目"""
        if not os.path.exists(self.y3_local_data):
            print(f"Y3本地数据目录不存在: {self.y3_local_data}")
            return []
            
        projects = []
        for item in os.listdir(self.y3_local_data):
            if os.path.isdir(os.path.join(self.y3_local_data, item)):
                projects.append(item)
        return projects
    
    def import_project(self, project_name, target_name=None):
        """导入Y3地图项目到war3项目目录"""
        source_path = os.path.join(self.y3_local_data, project_name)
        if not os.path.exists(source_path):
            print(f"项目不存在: {project_name}")
            return False
            
        if target_name is None:
            target_name = project_name
            
        target_path = os.path.join(self.project_maps_dir, target_name)
        
        try:
            if os.path.exists(target_path):
                print(f"目标目录已存在: {target_path}")
                response = input("是否覆盖? (y/N): ")
                if response.lower() != 'y':
                    return False
                    
            shutil.copytree(source_path, target_path, dirs_exist_ok=True)
            print(f"成功导入项目: {project_name} -> {target_path}")
            
            # 创建项目信息文件
            project_info = {
                "name": target_name,
                "original_name": project_name,
                "import_time": datetime.now().isoformat(),
                "y3_path": source_path
            }
            
            info_file = os.path.join(target_path, "project_info.json")
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(project_info, f, indent=2, ensure_ascii=False)
                
            return True
        except Exception as e:
            print(f"导入失败: {e}")
            return False
    
    def list_imported_projects(self):
        """列出已导入的地图项目"""
        if not os.path.exists(self.project_maps_dir):
            return []
            
        projects = []
        for item in os.listdir(self.project_maps_dir):
            project_path = os.path.join(self.project_maps_dir, item)
            if os.path.isdir(project_path):
                projects.append(item)
        return projects
    
    def create_template(self, template_name, source_project=None):
        """创建地图项目模板"""
        template_path = os.path.join(self.templates_dir, template_name)
        
        if source_project:
            source_path = os.path.join(self.project_maps_dir, source_project)
            if not os.path.exists(source_path):
                print(f"源项目不存在: {source_project}")
                return False
                
            shutil.copytree(source_path, template_path, dirs_exist_ok=True)
            print(f"从项目 {source_project} 创建模板: {template_name}")
        else:
            # 创建空模板
            os.makedirs(template_path, exist_ok=True)
            print(f"创建空模板: {template_name}")
            
        return True
    
    def create_project_from_template(self, template_name, project_name):
        """从模板创建新项目"""
        template_path = os.path.join(self.templates_dir, template_name)
        if not os.path.exists(template_path):
            print(f"模板不存在: {template_name}")
            return False
            
        target_path = os.path.join(self.project_maps_dir, project_name)
        if os.path.exists(target_path):
            print(f"项目已存在: {project_name}")
            return False
            
        shutil.copytree(template_path, target_path)
        print(f"从模板 {template_name} 创建项目: {project_name}")
        return True
    
    def backup_project(self, project_name):
        """备份地图项目"""
        project_path = os.path.join(self.project_maps_dir, project_name)
        if not os.path.exists(project_path):
            print(f"项目不存在: {project_name}")
            return False
            
        backup_name = f"{project_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = os.path.join(self.project_maps_dir, backup_name)
        
        shutil.copytree(project_path, backup_path)
        print(f"项目备份完成: {backup_name}")
        return True
    
    def sync_to_y3(self, project_name):
        """同步项目到Y3编辑器"""
        project_path = os.path.join(self.project_maps_dir, project_name)
        if not os.path.exists(project_path):
            print(f"项目不存在: {project_name}")
            return False
            
        # 读取项目信息
        info_file = os.path.join(project_path, "project_info.json")
        if os.path.exists(info_file):
            with open(info_file, 'r', encoding='utf-8') as f:
                info = json.load(f)
                original_name = info.get("original_name", project_name)
        else:
            original_name = project_name
            
        target_path = os.path.join(self.y3_local_data, original_name)
        
        try:
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            shutil.copytree(project_path, target_path)
            print(f"项目已同步到Y3编辑器: {original_name}")
            return True
        except Exception as e:
            print(f"同步失败: {e}")
            return False

def main():
    manager = MapManager()
    
    while True:
        print("\n=== Y3地图项目管理工具 ===")
        print("1. 列出Y3编辑器中的项目")
        print("2. 导入项目到war3目录")
        print("3. 列出已导入的项目")
        print("4. 创建项目模板")
        print("5. 从模板创建项目")
        print("6. 备份项目")
        print("7. 同步项目到Y3编辑器")
        print("0. 退出")
        
        choice = input("\n请选择操作 (0-7): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            projects = manager.list_y3_projects()
            print(f"Y3编辑器中的项目: {projects}")
        elif choice == "2":
            project_name = input("请输入项目名称: ").strip()
            target_name = input("请输入目标名称 (直接回车使用原名): ").strip() or None
            manager.import_project(project_name, target_name)
        elif choice == "3":
            projects = manager.list_imported_projects()
            print(f"已导入的项目: {projects}")
        elif choice == "4":
            template_name = input("请输入模板名称: ").strip()
            source_project = input("请输入源项目名称 (直接回车创建空模板): ").strip() or None
            manager.create_template(template_name, source_project)
        elif choice == "5":
            template_name = input("请输入模板名称: ").strip()
            project_name = input("请输入项目名称: ").strip()
            manager.create_project_from_template(template_name, project_name)
        elif choice == "6":
            project_name = input("请输入项目名称: ").strip()
            manager.backup_project(project_name)
        elif choice == "7":
            project_name = input("请输入项目名称: ").strip()
            manager.sync_to_y3(project_name)
        else:
            print("无效选择，请重新输入")

if __name__ == "__main__":
    main()
