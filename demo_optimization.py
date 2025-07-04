#!/usr/bin/env python3
"""
演示脚本 - 展示优化前后的测试执行差异
"""
import subprocess
import sys
import os

def main():
    """演示优化前后的差异"""
    print("=" * 80)
    print("SauceDemo 测试框架优化演示")
    print("=" * 80)
    
    print("\n1. 传统模式测试收集 (每个测试独立浏览器):")
    print("-" * 50)
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "--collect-only", "tests/test_saucedemo.py", "-q"
    ], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
    
    traditional_lines = result.stdout.strip().split('\n')
    traditional_count = len([line for line in traditional_lines if '::' in line])
    
    print(f"传统模式收集到的测试: {traditional_count} 个")
    print("每个测试都会启动一个新的浏览器实例")
    
    print("\n2. 优化模式测试收集 (浏览器会话复用):")
    print("-" * 50)
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "--collect-only", "tests/test_saucedemo_optimized.py", "-q"
    ], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
    
    optimized_lines = result.stdout.strip().split('\n')
    optimized_count = len([line for line in optimized_lines if '::' in line])
    user_tests = len([line for line in optimized_lines if 'test_user_' in line])
    
    print(f"优化模式收集到的测试: {optimized_count} 个")
    print(f"其中用户级测试: {user_tests} 个 (每个启动一个浏览器会话)")
    
    print("\n3. 效率对比:")
    print("-" * 50)
    print(f"传统模式浏览器启动次数: {traditional_count}")
    print(f"优化模式浏览器启动次数: {user_tests}")
    print(f"减少的浏览器启动次数: {traditional_count - user_tests}")
    
    if traditional_count > 0:
        efficiency_gain = ((traditional_count - user_tests) / traditional_count) * 100
        print(f"效率提升: {efficiency_gain:.1f}%")
    
    print("\n4. 使用方法:")
    print("-" * 50)
    print("# 运行优化模式 (推荐)")
    print("python run_tests_enhanced.py --mode optimized")
    print("")
    print("# 运行传统模式")
    print("python run_tests_enhanced.py --mode traditional") 
    print("")
    print("# 单用户快速测试")
    print("python run_tests_enhanced.py --mode single --user standard_user")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()