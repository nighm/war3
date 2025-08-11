import subprocess
import sys
import os
import socket

def run_cmd(cmd, check=True, encoding='utf-8'):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding=encoding)
    if result.returncode != 0:
        print(f"命令失败: {cmd}\n错误信息: {result.stderr}")
        if check:
            sys.exit(result.returncode)
    return result.stdout.strip()

def check_git_proxy():
    http_proxy = run_cmd('git config --global --get http.proxy', check=False)
    https_proxy = run_cmd('git config --global --get https.proxy', check=False)
    if http_proxy or https_proxy:
        print(f"[检测] 当前Git代理配置:")
        print(f"  http.proxy: {http_proxy}")
        print(f"  https.proxy: {https_proxy}")
        # 检查本地代理端口是否可用
        for proxy in [http_proxy, https_proxy]:
            if proxy and '127.0.0.1' in proxy:
                try:
                    host, port = proxy.split('//')[-1].split(':')
                    port = int(port)
                    with socket.create_connection((host, port), timeout=2):
                        print(f"  [OK] 本地代理端口 {host}:{port} 可用")
                except Exception:
                    print(f"  [警告] 本地代理端口 {proxy} 不可用！")
                    print("  可能未启动代理软件，或端口配置错误。建议：")
                    print("    1. 启动你的代理软件（如Clash、V2RayN等）")
                    print("    2. 或取消Git代理配置：\n       git config --global --unset http.proxy\n       git config --global --unset https.proxy")
    else:
        print("[检测] 当前Git未配置代理。")

def check_github_connectivity():
    print("[检测] 测试github.com:443连通性...")
    try:
        with socket.create_connection(("github.com", 443), timeout=3):
            print("  [OK] 可以连接github.com:443")
            return True
    except Exception:
        print("  [警告] 无法连接github.com:443，可能是网络或代理问题。")
        print("  请检查网络环境，或配置可用的代理。")
        return False

def main():
    print("[0/3] 检查Git代理配置和网络连通性...")
    check_git_proxy()
    if not check_github_connectivity():
        print("[终止] 网络不通，无法推送到GitHub。请先解决网络问题！")
        sys.exit(1)

    print("[1/3] 添加所有更改到暂存区 (git add .)")
    run_cmd("git add .")

    print("[2/3] 请输入本次提交说明（直接回车将使用默认信息）：")
    msg = input().strip()
    if not msg:
        msg = "docs: update project documentation"
    run_cmd(f'git commit -m "{msg}"', check=False)

    print("[3/3] 推送到GitHub远程仓库 (git push)")
    try:
        run_cmd("git push")
        print("\n✅ 已成功同步到GitHub！")
    except SystemExit:
        print("\n❌ 推送失败！请根据上方检测结果修复网络或代理问题，再重试。\n")
        sys.exit(1)

if __name__ == "__main__":
    main()