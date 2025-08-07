import subprocess
import sys


def run_cmd(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"命令失败: {cmd}\n错误信息: {result.stderr}")
        if check:
            sys.exit(result.returncode)
    return result.stdout.strip()


def main():
    print("[1/3] 添加所有更改到暂存区 (git add .)")
    run_cmd("git add .")

    print("[2/3] 请输入本次提交说明（直接回车将使用默认信息）：")
    msg = input().strip()
    if not msg:
        msg = "docs: update project documentation"
    run_cmd(f'git commit -m "{msg}"', check=False)

    print("[3/3] 推送到GitHub远程仓库 (git push)")
    run_cmd("git push")
    print("\n✅ 已成功同步到GitHub！")

if __name__ == "__main__":
    main()