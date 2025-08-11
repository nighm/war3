#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub同步脚本 - 优化版本
功能：自动检测网络环境、代理配置，一键同步代码到GitHub
"""

import subprocess
import sys
import os
import socket
import time
import json
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

# 配置常量
CONFIG_FILE = Path.home() / '.sync_github_config.json'
DEFAULT_TIMEOUT = 5
DEFAULT_COMMIT_MSG = "docs: update project documentation"

class Colors:
    """终端颜色支持"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def colored(text: str, color: str) -> str:
    """添加颜色到文本"""
    return f"{color}{text}{Colors.ENDC}"

class GitSyncError(Exception):
    """Git同步相关错误"""
    pass

class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"{colored('警告', Colors.WARNING)}: 配置文件损坏，使用默认配置: {e}")
        
        return {
            'default_commit_msg': DEFAULT_COMMIT_MSG,
            'auto_push': True,
            'check_proxy': True,
            'timeout': DEFAULT_TIMEOUT,
            'retry_count': 3
        }
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"{colored('警告', Colors.WARNING)}: 无法保存配置文件: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        self.config[key] = value
        self.save_config()

class GitManager:
    """Git操作管理器"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.check_git_repo()
    
    def check_git_repo(self):
        """检查是否为Git仓库"""
        if not Path('.git').exists():
            raise GitSyncError("当前目录不是Git仓库！请在Git仓库根目录运行此脚本。")
    
    def run_cmd(self, cmd: str, check: bool = True, encoding: str = 'utf-8') -> str:
        """执行Git命令"""
        try:
            # 对于push操作，使用更长的超时时间
            timeout = self.config.get('timeout', DEFAULT_TIMEOUT)
            if 'push' in cmd.lower():
                timeout = max(30, timeout)  # push操作至少30秒
            
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                encoding=encoding,
                timeout=timeout
            )
            
            if result.returncode != 0:
                error_msg = f"命令失败: {cmd}\n错误信息: {result.stderr}"
                if check:
                    raise GitSyncError(error_msg)
                else:
                    print(f"{colored('警告', Colors.WARNING)}: {error_msg}")
                    return ""
            
            return result.stdout.strip()
            
        except subprocess.TimeoutExpired:
            error_msg = f"命令超时: {cmd} (超时时间: {timeout}秒)"
            if check:
                raise GitSyncError(error_msg)
            else:
                print(f"{colored('警告', Colors.WARNING)}: {error_msg}")
                return ""
        except Exception as e:
            error_msg = f"执行命令时出错: {e}"
            if check:
                raise GitSyncError(error_msg)
            else:
                print(f"{colored('警告', Colors.WARNING)}: {error_msg}")
                return ""
    
    def get_status(self) -> Dict[str, Any]:
        """获取Git状态"""
        status = self.run_cmd("git status --porcelain")
        if not status:
            return {'has_changes': False, 'files': []}
        
        files = [line.split(' ', 1)[1] for line in status.split('\n') if line.strip()]
        return {'has_changes': True, 'files': files}
    
    def get_branch_info(self) -> Dict[str, str]:
        """获取分支信息"""
        current_branch = self.run_cmd("git branch --show-current")
        remote_branch = self.run_cmd("git rev-parse --abbrev-ref --symbolic-full-name @{u}", check=False)
        
        return {
            'current': current_branch,
            'remote': remote_branch if remote_branch else '未设置上游分支'
        }

class NetworkChecker:
    """网络检查器"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
    
    def check_git_proxy(self) -> Dict[str, Any]:
        """检查Git代理配置"""
        if not self.config.get('check_proxy', True):
            return {'enabled': False}
        
        http_proxy = self._get_git_config('http.proxy')
        https_proxy = self._get_git_config('https.proxy')
        
        result = {
            'enabled': bool(http_proxy or https_proxy),
            'http': http_proxy,
            'https': https_proxy,
            'local_proxies': []
        }
        
        if result['enabled']:
            print(f"{colored('[检测]', Colors.OKBLUE)} 当前Git代理配置:")
            print(f"  http.proxy: {http_proxy or '未设置'}")
            print(f"  https.proxy: {https_proxy or '未设置'}")
            
            # 检查本地代理端口
            for proxy_type, proxy_url in [('HTTP', http_proxy), ('HTTPS', https_proxy)]:
                if proxy_url and self._is_local_proxy(proxy_url):
                    status = self._check_proxy_connectivity(proxy_url)
                    result['local_proxies'].append({
                        'type': proxy_type,
                        'url': proxy_url,
                        'status': status
                    })
        else:
            print(f"{colored('[检测]', Colors.OKBLUE)} 当前Git未配置代理。")
        
        return result
    
    def _get_git_config(self, key: str) -> Optional[str]:
        """获取Git配置值"""
        try:
            result = subprocess.run(
                ['git', 'config', '--global', '--get', key],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            return None
    
    def _is_local_proxy(self, proxy_url: str) -> bool:
        """判断是否为本地代理"""
        return '127.0.0.1' in proxy_url or 'localhost' in proxy_url
    
    def _check_proxy_connectivity(self, proxy_url: str) -> str:
        """检查代理连通性"""
        try:
            # 解析代理URL
            if '://' in proxy_url:
                host_port = proxy_url.split('://')[-1]
            else:
                host_port = proxy_url
            
            if ':' in host_port:
                host, port_str = host_port.rsplit(':', 1)
                port = int(port_str)
            else:
                host, port = host_port, 80
            
            # 测试连接
            with socket.create_connection((host, port), timeout=2):
                status = "可用"
                print(f"  {colored('[OK]', Colors.OKGREEN)} 本地代理端口 {host}:{port} 可用")
            return status
            
        except Exception as e:
            status = "不可用"
            print(f"  {colored('[警告]', Colors.WARNING)} 本地代理端口 {proxy_url} 不可用！")
            print(f"    错误: {e}")
            print("    建议:")
            print("      1. 启动代理软件（如Clash、V2RayN等）")
            print("      2. 或取消Git代理配置:")
            print("         git config --global --unset http.proxy")
            print("         git config --global --unset https.proxy")
            return status
    
    def check_github_connectivity(self) -> bool:
        """检查GitHub连通性"""
        print(f"{colored('[检测]', Colors.OKBLUE)} 测试github.com:443连通性...")
        
        for attempt in range(self.config.get('retry_count', 3)):
            try:
                with socket.create_connection(("github.com", 443), timeout=3):
                    print(f"  {colored('[OK]', Colors.OKGREEN)} 可以连接github.com:443")
                    return True
            except Exception as e:
                if attempt < self.config.get('retry_count', 3) - 1:
                    print(f"  {colored('[重试]', Colors.WARNING)} 第{attempt + 1}次连接失败，正在重试...")
                    time.sleep(1)
                else:
                    print(f"  {colored('[失败]', Colors.FAIL)} 无法连接github.com:443")
                    print(f"    错误: {e}")
                    print("    请检查网络环境，或配置可用的代理。")
        
        return False

class SyncManager:
    """同步管理器"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.git = GitManager(config)
        self.network = NetworkChecker(config)
    
    def sync(self):
        """执行同步流程"""
        try:
            print(f"{colored('🚀 GitHub同步工具', Colors.HEADER)}")
            print("=" * 50)
            
            # 步骤1: 检查环境
            self._check_environment()
            
            # 步骤2: 检查Git状态
            self._check_git_status()
            
            # 步骤3: 添加文件
            self._add_files()
            
            # 步骤4: 提交更改
            self._commit_changes()
            
            # 步骤5: 推送到远程
            self._push_to_remote()
            
            print(f"\n{colored('✅ 同步完成！', Colors.OKGREEN)}")
            
        except GitSyncError as e:
            print(f"\n{colored('❌ 同步失败', Colors.FAIL)}: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print(f"\n{colored('⚠️  用户取消操作', Colors.WARNING)}")
            sys.exit(0)
    
    def _check_environment(self):
        """检查环境"""
        print(f"{colored('[1/5]', Colors.OKBLUE)} 检查Git代理配置和网络连通性...")
        self.network.check_git_proxy()
        
        if not self.network.check_github_connectivity():
            raise GitSyncError("网络不通，无法推送到GitHub。请先解决网络问题！")
    
    def _check_git_status(self):
        """检查Git状态"""
        print(f"{colored('[2/5]', Colors.OKBLUE)} 检查Git状态...")
        
        status = self.git.get_status()
        if not status['has_changes']:
            print("  没有需要提交的更改。")
            
            # 检查是否有未推送的提交
            try:
                unpushed_commits = self.git.run_cmd("git log --oneline origin/main..HEAD", check=False)
                if unpushed_commits:
                    print(f"  发现 {len(unpushed_commits.splitlines())} 个未推送的提交:")
                    for commit in unpushed_commits.splitlines()[:5]:  # 显示前5个
                        print(f"    {commit}")
                    if len(unpushed_commits.splitlines()) > 5:
                        print(f"    ... 还有 {len(unpushed_commits.splitlines()) - 5} 个提交")
                    
                    choice = input("  是否继续推送到远程？(y/N): ").lower()
                    if choice != 'y':
                        sys.exit(0)
                    return  # 有未推送的提交，继续执行
                else:
                    print("  所有提交都已推送到远程仓库。")
                    choice = input("  是否仍要继续同步流程？(y/N): ").lower()
                    if choice != 'y':
                        sys.exit(0)
            except Exception:
                print("  无法检查未推送的提交，继续执行...")
        else:
            print(f"  发现 {len(status['files'])} 个文件有更改:")
            for file in status['files'][:10]:  # 只显示前10个
                print(f"    {file}")
            if len(status['files']) > 10:
                print(f"    ... 还有 {len(status['files']) - 10} 个文件")
        
        branch_info = self.git.get_branch_info()
        print(f"  当前分支: {branch_info['current']}")
        print(f"  上游分支: {branch_info['remote']}")
    
    def _add_files(self):
        """添加文件到暂存区"""
        print(f"{colored('[3/5]', Colors.OKBLUE)} 添加所有更改到暂存区...")
        
        # 检查是否有实际更改
        status = self.git.get_status()
        if not status['has_changes']:
            print("  没有文件需要添加，跳过此步骤")
            return
        
        self.git.run_cmd("git add .")
        print("  ✅ 文件已添加到暂存区")
    
    def _commit_changes(self):
        """提交更改"""
        print(f"{colored('[4/5]', Colors.OKBLUE)} 提交更改...")
        
        # 检查是否有暂存区的更改
        try:
            staged_changes = self.git.run_cmd("git diff --cached --name-only", check=False)
            if not staged_changes:
                print("  没有暂存区的更改需要提交")
                return
        except Exception:
            print("  无法检查暂存区状态，尝试继续...")
        
        # 获取提交信息
        default_msg = self.config.get('default_commit_msg', DEFAULT_COMMIT_MSG)
        print(f"  默认提交信息: {default_msg}")
        
        msg = input("  请输入本次提交说明（直接回车使用默认）: ").strip()
        if not msg:
            msg = default_msg
        
        # 执行提交
        result = self.git.run_cmd(f'git commit -m "{msg}"', check=False)
        if result:
            print("  ✅ 更改已提交")
        else:
            print("  ⚠️  提交失败或没有更改需要提交")
    
    def _push_to_remote(self):
        """推送到远程仓库"""
        print(f"{colored('[5/5]', Colors.OKBLUE)} 推送到GitHub远程仓库...")
        
        try:
            # 检查是否有需要推送的提交
            try:
                unpushed_commits = self.git.run_cmd("git log --oneline origin/main..HEAD", check=False)
                if not unpushed_commits:
                    print("  没有需要推送的提交")
                    return
            except Exception:
                print("  无法检查未推送的提交，尝试继续推送...")
            
            # 使用更长的超时时间进行push操作
            original_timeout = self.config.get('timeout', DEFAULT_TIMEOUT)
            self.config.set('timeout', max(30, original_timeout))  # push操作至少30秒超时
            
            try:
                self.git.run_cmd("git push")
                print("  ✅ 已成功推送到GitHub！")
            finally:
                # 恢复原始超时设置
                self.config.set('timeout', original_timeout)
                
        except GitSyncError as e:
            print(f"  ❌ 推送失败: {e}")
            
            # 提供更详细的错误诊断
            print("  诊断信息:")
            try:
                remote_status = self.git.run_cmd("git remote -v", check=False)
                print(f"    远程仓库: {remote_status}")
            except Exception:
                print("    无法获取远程仓库信息")
            
            try:
                branch_status = self.git.run_cmd("git status -sb", check=False)
                print(f"    分支状态: {branch_status}")
            except Exception:
                print("    无法获取分支状态")
            
            raise

def show_help():
    """显示帮助信息"""
    help_text = """
GitHub同步脚本 - 使用说明

用法: python sync_to_github.py [选项]

选项:
  -h, --help     显示此帮助信息
  -c, --config   显示当前配置
  -s, --set      设置配置项 (格式: -s key=value)
  -r, --reset    重置为默认配置

配置项:
  default_commit_msg  默认提交信息
  auto_push          是否自动推送 (true/false)
  check_proxy        是否检查代理 (true/false)
  timeout            命令超时时间(秒)
  retry_count        网络重试次数

示例:
  python sync_to_github.py
  python sync_to_github.py -c
  python sync_to_github.py -s default_commit_msg="feat: add new feature"
  python sync_to_github.py -r
"""
    print(help_text)

def main():
    """主函数"""
    # 解析命令行参数
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ['-h', '--help']:
            show_help()
            return
        elif arg in ['-c', '--config']:
            config = ConfigManager()
            print("当前配置:")
            for key, value in config.config.items():
                print(f"  {key}: {value}")
            return
        elif arg in ['-s', '--set'] and len(sys.argv) > 2:
            config = ConfigManager()
            try:
                key, value = sys.argv[2].split('=', 1)
                # 类型转换
                if value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                config.set(key, value)
                print(f"配置已更新: {key} = {value}")
            except ValueError:
                print("错误: 配置格式应为 key=value")
            return
        elif arg in ['-r', '--reset']:
            if CONFIG_FILE.exists():
                CONFIG_FILE.unlink()
                print("配置已重置为默认值")
            return
    
    # 执行同步
    try:
        config = ConfigManager()
        sync_manager = SyncManager(config)
        sync_manager.sync()
    except Exception as e:
        print(f"{colored('❌ 程序异常', Colors.FAIL)}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()