"""
测试运行脚本 - 支持优化和传统模式
"""
import pytest
import sys
import os
import argparse
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from core.logger_config import logger
from reports.test_reporter import test_reporter
from config import REPORTS_DIR


def run_optimized_tests():
    """运行优化版测试 - 浏览器会话复用模式"""
    logger.info("=" * 60)
    logger.info("开始运行SauceDemo自动化测试 - 优化模式（浏览器会话复用）")
    logger.info("=" * 60)
    
    # 确保报告目录存在
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
    
    # 生成带时间戳的HTML报告文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_report_path = os.path.join(REPORTS_DIR, f"pytest_report_optimized_{timestamp}.html")
    
    # pytest运行参数 - 优化版
    pytest_args = [
        "tests/test_saucedemo_optimized.py",  # 优化版测试文件
        "-v",  # 详细输出
        "--tb=short",  # 简短的traceback
        "--capture=no",  # 不捕获输出
        f"--html={html_report_path}",  # 生成HTML报告
        "--self-contained-html",  # 生成自包含的HTML文件
        "--order-dependencies",  # 启用测试顺序依赖
    ]
    
    try:
        logger.info(f"HTML报告将保存到: {html_report_path}")
        exit_code = pytest.main(pytest_args)
        
        # 打印测试摘要
        summary = test_reporter.get_test_summary()
        logger.info("=" * 60)
        logger.info("优化模式测试执行完成")
        logger.info(f"总测试数: {summary['total']}")
        logger.info(f"通过数: {summary['passed']}")
        logger.info(f"失败数: {summary['failed']}")
        logger.info(f"通过率: {summary['pass_rate']}%")
        logger.info(f"HTML报告已生成: {html_report_path}")
        logger.info("=" * 60)
        
        return exit_code
        
    except Exception as e:
        logger.error(f"运行优化测试时发生错误: {str(e)}")
        return 1


def run_traditional_tests():
    """运行传统版测试 - 每个测试独立浏览器"""
    logger.info("=" * 60)
    logger.info("开始运行SauceDemo自动化测试 - 传统模式（每个测试独立浏览器）")
    logger.info("=" * 60)
    
    # 确保报告目录存在
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
    
    # 生成带时间戳的HTML报告文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_report_path = os.path.join(REPORTS_DIR, f"pytest_report_traditional_{timestamp}.html")
    
    # pytest运行参数 - 传统版
    pytest_args = [
        "tests/test_saucedemo.py",  # 传统测试文件
        "-v",  # 详细输出
        "--tb=short",  # 简短的traceback
        "--capture=no",  # 不捕获输出
        f"--html={html_report_path}",  # 生成HTML报告
        "--self-contained-html",  # 生成自包含的HTML文件
    ]
    
    try:
        logger.info(f"HTML报告将保存到: {html_report_path}")
        exit_code = pytest.main(pytest_args)
        
        # 打印测试摘要
        summary = test_reporter.get_test_summary()
        logger.info("=" * 60)
        logger.info("传统模式测试执行完成")
        logger.info(f"总测试数: {summary['total']}")
        logger.info(f"通过数: {summary['passed']}")
        logger.info(f"失败数: {summary['failed']}")
        logger.info(f"通过率: {summary['pass_rate']}%")
        logger.info(f"HTML报告已生成: {html_report_path}")
        logger.info("=" * 60)
        
        return exit_code
        
    except Exception as e:
        logger.error(f"运行传统测试时发生错误: {str(e)}")
        return 1


def run_single_user_tests(username):
    """运行单用户快速测试"""
    logger.info("=" * 60)
    logger.info(f"开始运行单用户快速测试 - 用户: {username}")
    logger.info("=" * 60)
    
    # 确保报告目录存在
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
    
    # 生成带时间戳的HTML报告文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_report_path = os.path.join(REPORTS_DIR, f"pytest_report_single_user_{username}_{timestamp}.html")
    
    # pytest运行参数 - 单用户模式
    pytest_args = [
        "tests/test_saucedemo_optimized.py",
        "-k", f"test_user_{username}",  # 只运行指定用户的测试
        "-v",
        "--tb=short",
        "--capture=no",
        f"--html={html_report_path}",
        "--self-contained-html",
    ]
    
    try:
        logger.info(f"HTML报告将保存到: {html_report_path}")
        exit_code = pytest.main(pytest_args)
        
        # 打印测试摘要
        summary = test_reporter.get_test_summary()
        logger.info("=" * 60)
        logger.info(f"单用户测试执行完成 - 用户: {username}")
        logger.info(f"总测试数: {summary['total']}")
        logger.info(f"通过数: {summary['passed']}")
        logger.info(f"失败数: {summary['failed']}")
        logger.info(f"通过率: {summary['pass_rate']}%")
        logger.info(f"HTML报告已生成: {html_report_path}")
        logger.info("=" * 60)
        
        return exit_code
        
    except Exception as e:
        logger.error(f"运行单用户测试时发生错误: {str(e)}")
        return 1


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(description='SauceDemo 自动化测试运行器')
    parser.add_argument('--mode', 
                        choices=['optimized', 'traditional', 'single'], 
                        default='optimized',
                        help='测试运行模式：optimized=优化模式（浏览器复用），traditional=传统模式（每测试独立浏览器），single=单用户模式')
    parser.add_argument('--user', 
                        choices=['standard_user', 'visual_user'], 
                        help='单用户模式下指定要测试的用户（仅在single模式下有效）')
    
    args = parser.parse_args()
    
    if args.mode == 'optimized':
        return run_optimized_tests()
    elif args.mode == 'traditional':
        return run_traditional_tests()
    elif args.mode == 'single':
        if not args.user:
            logger.error("单用户模式需要指定 --user 参数")
            return 1
        return run_single_user_tests(args.user)
    else:
        logger.error(f"未知的测试模式: {args.mode}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)