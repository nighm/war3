#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能GitHub同步管理器 - 文件分类与上传建议
功能：智能分析项目文件，提供上传建议，自动过滤临时文件
"""

import subprocess
import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class FileCategory(Enum):
    """文件分类枚举"""
    UPLOAD_TO_GITHUB = "上传到GitHub"      # 核心代码、文档、配置
    LOCAL_ONLY = "仅本地保存"              # 敏感信息、本地配置
    TEMPORARY = "临时文件"                  # 缓存、日志、临时文件
    IGNORE = "忽略文件"                     # 系统文件、IDE配置

@dataclass
class FileInfo:
    """文件信息"""
    path: str
    category: FileCategory
    reason: str
    size: int
    last_modified: float
    git_status: str

class SmartFileAnalyzer:
    """智能文件分析器"""
    
    def __init__(self):
        # 文件分类规则
        self.category_rules = {
            # 上传到GitHub的文件
            FileCategory.UPLOAD_TO_GITHUB: {
                'extensions': {'.py', '.md', '.txt', '.json', '.yml', '.yaml', '.toml', '.cfg', '.ini'},
                'patterns': {
                    'src/', 'docs/', 'tools/', 'templates/', 'config/',
                    'README', 'CHANGELOG', 'LICENSE', 'requirements', 'pyproject',
                    'sync_to_github', 'smart_github_sync'
                },
                'exclude_patterns': {'__pycache__', '.pyc', '.pyo', '.pyd'}
            },
            
            # 仅本地保存的文件
            FileCategory.LOCAL_ONLY: {
                'patterns': {
                    '.env', '.env.local', '.env.prod', 'config.local.json',
                    'secrets.json', 'private.key', 'local_settings.py'
                }
            },
            
            # 临时文件
            FileCategory.TEMPORARY: {
                'extensions': {'.log', '.tmp', '.temp', '.cache', '.bak', '.swp'},
                'patterns': {
                    '__pycache__', '.pytest_cache', '.coverage', '.cache',
                    '*.log', '*.tmp', '*.temp', '*.bak', '*.swp'
                }
            },
            
            # 忽略文件
            FileCategory.IGNORE: {
                'patterns': {
                    '.git/', '.vscode/', '.idea/', 'node_modules/',
                    '.DS_Store', 'Thumbs.db', 'desktop.ini'
                }
            }
        }
    
    def analyze_file(self, file_path: str, git_status: str = "") -> FileInfo:
        """分析单个文件"""
        path = Path(file_path)
        
        # 获取文件信息
        try:
            stat = path.stat()
            size = stat.st_size
            last_modified = stat.st_mtime
        except:
            size = 0
            last_modified = 0
        
        # 分类文件
        category, reason = self._categorize_file(path)
        
        return FileInfo(
            path=str(file_path),
            category=category,
            reason=reason,
            size=size,
            last_modified=last_modified,
            git_status=git_status
        )
    
    def _categorize_file(self, path: Path) -> Tuple[FileCategory, str]:
        """分类文件"""
        path_str = str(path)
        name = path.name.lower()
        
        # 检查忽略文件
        for pattern in self.category_rules[FileCategory.IGNORE]['patterns']:
            if pattern in path_str:
                return FileCategory.IGNORE, f"匹配忽略模式: {pattern}"
        
        # 检查临时文件
        for pattern in self.category_rules[FileCategory.TEMPORARY]['patterns']:
            if pattern in path_str or name.endswith(tuple(self.category_rules[FileCategory.TEMPORARY].get('extensions', {}))):
                return FileCategory.TEMPORARY, f"匹配临时文件模式: {pattern}"
        
        # 检查仅本地文件
        for pattern in self.category_rules[FileCategory.LOCAL_ONLY]['patterns']:
            if pattern in path_str:
                return FileCategory.LOCAL_ONLY, f"匹配本地文件模式: {pattern}"
        
        # 检查上传文件
        for pattern in self.category_rules[FileCategory.UPLOAD_TO_GITHUB]['patterns']:
            if pattern in path_str:
                return FileCategory.UPLOAD_TO_GITHUB, f"匹配上传模式: {pattern}"
        
        # 检查扩展名
        if path.suffix.lower() in self.category_rules[FileCategory.UPLOAD_TO_GITHUB].get('extensions', {}):
            return FileCategory.UPLOAD_TO_GITHUB, f"支持的文件扩展名: {path.suffix}"
        
        # 默认分类
        if path.is_file():
            return FileCategory.UPLOAD_TO_GITHUB, "默认分类为上传文件"
        else:
            return FileCategory.IGNORE, "目录或系统文件"

class SmartSyncManager:
    """智能同步管理器"""
    
    def __init__(self):
        self.analyzer = SmartFileAnalyzer()
        self.project_root = Path.cwd()
        
    def analyze_project(self) -> Dict[FileCategory, List[FileInfo]]:
        """分析整个项目"""
        print("🔍 正在分析项目文件...")
        
        # 获取git状态
        git_status = self._get_git_status()
        
        # 分析所有文件
        categorized_files = {category: [] for category in FileCategory}
        
        for file_path in self._get_all_files():
            if file_path.startswith('.git/'):
                continue
                
            git_status_for_file = git_status.get(str(file_path), "")
            file_info = self.analyzer.analyze_file(file_path, git_status_for_file)
            categorized_files[file_info.category].append(file_info)
        
        return categorized_files
    
    def _get_git_status(self) -> Dict[str, str]:
        """获取git状态"""
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            if result.returncode == 0:
                status_map = {}
                for line in result.stdout.strip().split('\n'):
                    if line:
                        status = line[:2].strip()
                        file_path = line[3:]
                        status_map[file_path] = status
                return status_map
        except:
            pass
        return {}
    
    def _get_all_files(self) -> List[str]:
        """获取所有文件路径"""
        files = []
        for root, dirs, filenames in os.walk(self.project_root):
            # 跳过.git目录
            if '.git' in dirs:
                dirs.remove('.git')
            
            for filename in filenames:
                file_path = Path(root) / filename
                files.append(str(file_path.relative_to(self.project_root)))
        
        return files
    
    def generate_report(self, categorized_files: Dict[FileCategory, List[FileInfo]]) -> str:
        """生成分析报告"""
        report = []
        report.append("📊 项目文件分析报告")
        report.append("=" * 50)
        
        total_files = sum(len(files) for files in categorized_files.values())
        total_size = sum(sum(f.size for f in files) for files in categorized_files.values())
        
        report.append(f"📁 总文件数: {total_files}")
        report.append(f"💾 总大小: {self._format_size(total_size)}")
        report.append("")
        
        for category in FileCategory:
            files = categorized_files[category]
            if files:
                category_size = sum(f.size for f in files)
                report.append(f"🔸 {category.value} ({len(files)} 个文件, {self._format_size(category_size)})")
                
                for file_info in sorted(files, key=lambda x: x.path):
                    status_icon = self._get_status_icon(file_info.git_status)
                    report.append(f"   {status_icon} {file_info.path}")
                    report.append(f"      └─ {file_info.reason}")
                
                report.append("")
        
        return "\n".join(report)
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def _get_status_icon(self, git_status: str) -> str:
        """获取git状态图标"""
        status_icons = {
            "M": "📝",  # 修改
            "A": "➕",  # 新增
            "D": "🗑️",  # 删除
            "R": "🔄",  # 重命名
            "C": "📋",  # 复制
            "U": "⚠️",  # 未合并
            "": "📄"   # 无状态
        }
        return status_icons.get(git_status, "📄")
    
    def get_upload_recommendations(self, categorized_files: Dict[FileCategory, List[FileInfo]]) -> str:
        """获取上传建议"""
        recommendations = []
        recommendations.append("🚀 上传建议")
        recommendations.append("=" * 30)
        
        # 应该上传的文件
        upload_files = categorized_files[FileCategory.UPLOAD_TO_GITHUB]
        if upload_files:
            recommendations.append("✅ 建议上传到GitHub:")
            for file_info in upload_files:
                if file_info.git_status:  # 有git状态的文件
                    recommendations.append(f"   git add {file_info.path}")
            recommendations.append("")
        
        # 应该忽略的文件
        ignore_files = categorized_files[FileCategory.IGNORE]
        if ignore_files:
            recommendations.append("❌ 应该忽略的文件:")
            for file_info in ignore_files:
                recommendations.append(f"   echo '{file_info.path}' >> .gitignore")
            recommendations.append("")
        
        # 临时文件清理建议
        temp_files = categorized_files[FileCategory.TEMPORARY]
        if temp_files:
            recommendations.append("🧹 建议清理的临时文件:")
            for file_info in temp_files:
                recommendations.append(f"   rm -rf {file_info.path}")
            recommendations.append("")
        
        # 本地文件提醒
        local_files = categorized_files[FileCategory.LOCAL_ONLY]
        if local_files:
            recommendations.append("🔒 仅本地保存的文件:")
            for file_info in local_files:
                recommendations.append(f"   {file_info.path} - {file_info.reason}")
            recommendations.append("")
        
        return "\n".join(recommendations)
    
    def create_gitignore_template(self, categorized_files: Dict[FileCategory, List[FileInfo]]) -> str:
        """创建.gitignore模板"""
        gitignore_content = []
        gitignore_content.append("# 自动生成的.gitignore文件")
        gitignore_content.append("# 基于项目文件分析生成")
        gitignore_content.append("")
        
        # 添加临时文件
        temp_files = categorized_files[FileCategory.TEMPORARY]
        if temp_files:
            gitignore_content.append("# 临时文件")
            for file_info in temp_files:
                gitignore_content.append(file_info.path)
            gitignore_content.append("")
        
        # 添加忽略文件
        ignore_files = categorized_files[FileCategory.IGNORE]
        if ignore_files:
            gitignore_content.append("# 系统文件")
            for file_info in ignore_files:
                gitignore_content.append(file_info.path)
            gitignore_content.append("")
        
        # 添加本地文件
        local_files = categorized_files[FileCategory.LOCAL_ONLY]
        if local_files:
            gitignore_content.append("# 本地配置文件")
            for file_info in local_files:
                gitignore_content.append(file_info.path)
            gitignore_content.append("")
        
        # 添加通用规则
        gitignore_content.append("# Python通用规则")
        gitignore_content.append("__pycache__/")
        gitignore_content.append("*.py[cod]")
        gitignore_content.append("*.so")
        gitignore_content.append(".Python")
        gitignore_content.append("build/")
        gitignore_content.append("develop-eggs/")
        gitignore_content.append("dist/")
        gitignore_content.append("downloads/")
        gitignore_content.append("eggs/")
        gitignore_content.append(".eggs/")
        gitignore_content.append("lib/")
        gitignore_content.append("lib64/")
        gitignore_content.append("parts/")
        gitignore_content.append("sdist/")
        gitignore_content.append("var/")
        gitignore_content.append("wheels/")
        gitignore_content.append("*.egg-info/")
        gitignore_content.append(".installed.cfg")
        gitignore_content.append("*.egg")
        gitignore_content.append("MANIFEST")
        gitignore_content.append("")
        gitignore_content.append("# IDE文件")
        gitignore_content.append(".vscode/")
        gitignore_content.append(".idea/")
        gitignore_content.append("*.swp")
        gitignore_content.append("*.swo")
        gitignore_content.append("")
        gitignore_content.append("# 操作系统文件")
        gitignore_content.append(".DS_Store")
        gitignore_content.append("Thumbs.db")
        gitignore_content.append("desktop.ini")
        
        return "\n".join(gitignore_content)

def main():
    """主函数"""
    print("🤖 智能GitHub同步管理器")
    print("=" * 40)
    
    # 检查是否在git仓库中
    if not Path('.git').exists():
        print("❌ 错误：当前目录不是git仓库！")
        print("请在git仓库根目录运行此脚本。")
        sys.exit(1)
    
    try:
        # 创建同步管理器
        sync_manager = SmartSyncManager()
        
        # 分析项目
        categorized_files = sync_manager.analyze_project()
        
        # 生成报告
        report = sync_manager.generate_report(categorized_files)
        print(report)
        
        print("\n" + "=" * 50)
        
        # 生成上传建议
        recommendations = sync_manager.get_upload_recommendations(categorized_files)
        print(recommendations)
        
        # 询问是否生成.gitignore
        print("\n" + "=" * 50)
        response = input("是否生成优化的.gitignore文件？(y/n): ").lower().strip()
        
        if response in ['y', 'yes', '是']:
            gitignore_content = sync_manager.create_gitignore_template(categorized_files)
            
            # 写入.gitignore文件
            gitignore_path = Path('.gitignore')
            if gitignore_path.exists():
                backup_path = Path('.gitignore.backup')
                gitignore_path.rename(backup_path)
                print(f"📋 已备份原.gitignore到 {backup_path}")
            
            with open('.gitignore', 'w', encoding='utf-8') as f:
                f.write(gitignore_content)
            
            print("✅ 已生成优化的.gitignore文件！")
            print("📝 建议检查并调整.gitignore内容后提交。")
        
        print("\n🎯 下一步操作建议：")
        print("1. 检查分析报告，确认文件分类正确")
        print("2. 根据上传建议执行git命令")
        print("3. 清理临时文件")
        print("4. 提交更改并推送到GitHub")
        
    except Exception as e:
        print(f"❌ 程序异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
