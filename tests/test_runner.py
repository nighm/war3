#!/usr/bin/env python3
"""
测试运行器脚本
提供便捷的测试执行方式
"""
import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type="all", coverage=True, parallel=False):
    """运行测试"""
    cmd = ["python", "-m", "pytest"]
    
    if test_type == "unit":
        cmd.extend(["--markers", "unit"])
    elif test_type == "integration":
        cmd.extend(["--markers", "integration"])
    
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html:htmlcov", "--cov-report=term-missing"])
    
    if parallel:
        cmd.extend(["-n", "auto"])
    
    cmd.extend(["-v"])
    
    print(f"执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def run_coverage_report():
    """生成覆盖率报告"""
    print("生成覆盖率报告...")
    subprocess.run(["coverage", "report"])
    subprocess.run(["coverage", "html"])


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="测试运行器")
    parser.add_argument("--type", choices=["all", "unit", "integration"], 
                       default="all", help="测试类型")
    parser.add_argument("--no-coverage", action="store_true", 
                       help="不生成覆盖率报告")
    parser.add_argument("--parallel", action="store_true", 
                       help="并行执行测试")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("魔兽争霸3地图开发工作室 - 测试套件")
    print("=" * 50)
    
    # 检查测试目录
    test_dir = Path("tests")
    if not test_dir.exists():
        print("错误: 测试目录不存在")
        return 1
    
    # 运行测试
    print(f"开始执行{args.type}测试...")
    exit_code = run_tests(
        test_type=args.type,
        coverage=not args.no_coverage,
        parallel=args.parallel
    )
    
    if exit_code == 0:
        print("\n✅ 所有测试通过!")
        
        if not args.no_coverage:
            run_coverage_report()
            print("\n📊 覆盖率报告已生成到 htmlcov/ 目录")
    else:
        print(f"\n❌ 测试失败，退出码: {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
