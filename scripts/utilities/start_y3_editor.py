import os
import subprocess
import sys

# Y3编辑器实际安装路径和主程序名
Y3_PATH = r"D:\Program Files\y3\games\2.0\game\Editor.exe"

def main():
    if not os.path.exists(Y3_PATH):
        print(f"未找到Y3编辑器主程序：{Y3_PATH}")
        print("请检查安装路径和文件名，或在脚本中修改Y3_PATH变量为实际路径。")
        sys.exit(1)
    try:
        print(f"正在启动Y3编辑器：{Y3_PATH}")
        subprocess.Popen([Y3_PATH])
        print("Y3编辑器已启动。")
    except Exception as e:
        print(f"启动失败：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()