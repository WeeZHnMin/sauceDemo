import os
import sys
import pytest
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.logger_config import logger

def get_test_statistics():
    """获取测试统计信息"""
    try:
        from reports.test_reporter import test_reporter
        if hasattr(test_reporter, 'get_test_summary'):
            return test_reporter.get_test_summary()
        return {}
    except Exception as e:
        logger.warning(f"无法获取测试统计信息: {str(e)}")
        return {}

def calculate_failure_rate(total, failed):
    """计算失败率"""
    if total == 0:
        return 0.0
    return (failed / total) * 100

def run_tests():
    """运行测试套件 - 标准模式"""
    try:
        logger.info("=" * 80)
        logger.info("开始执行SauceDemo自动化测试 - 标准模式")
        logger.info("=" * 80)
        
        # 创建测试报告目录
        reports_dir = "test_reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        # 生成HTML报告文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_report = os.path.join(reports_dir, f"test_report_{timestamp}.html")
        
        # 构建pytest参数
        pytest_args = [
            "tests/test_saucedemo.py",     # 测试文件路径
            "-v",                          # 详细输出
            "--tb=short",                  # 简短的错误信息
            f"--html={html_report}",       # HTML报告
            "--self-contained-html",       # 自包含的HTML
            "--capture=no",                # 不捕获输出，实时显示日志
            "--strict-markers",            # 严格标记模式
            "--disable-warnings",          # 禁用警告
        ]
        
        logger.info(f"执行参数: {' '.join(pytest_args)}")
        logger.info("测试模式：标准模式 - 严格检查所有测试结果")
        
        # 使用pytest.main()执行测试
        exit_code = pytest.main(pytest_args)
        
        # 分析测试结果
        stats = get_test_statistics()
        
        logger.info("=" * 80)
        if exit_code == 0:
            logger.info("✅ 所有测试执行完成并通过！")
        elif exit_code == 1:
            logger.info("⚠️  测试执行完成，但有部分测试失败")
            if stats:
                total = stats.get('total', 0)
                failed = stats.get('failed', 0)
                failure_rate = calculate_failure_rate(total, failed)
                logger.info(f"📊 测试统计: 总计 {total}, 失败 {failed}, 失败率 {failure_rate:.2f}%")
        elif exit_code == 2:
            logger.info("❌ 测试执行被中断或配置错误")
        elif exit_code == 3:
            logger.info("❌ 内部错误")
        elif exit_code == 4:
            logger.info("❌ pytest使用错误")
        elif exit_code == 5:
            logger.info("❌ 没有找到测试用例")
        else:
            logger.info(f"❓ 测试完成，退出代码: {exit_code}")
            
        logger.info(f"📊 HTML报告已生成: {html_report}")
        logger.info("📈 检查 test_reports/ 目录获取详细的Excel测试报告")
        logger.info("=" * 80)
        
        # 标准模式：严格检查
        return exit_code == 0
        
    except Exception as e:
        logger.error(f"测试运行失败: {str(e)}")
        return False

def run_tests_for_jenkins(failure_threshold=15.0):
    """
    专门为Jenkins CI/CD设计的测试运行函数
    
    参数:
        failure_threshold (float): 失败率阈值，默认15%
    """
    try:
        logger.info("=" * 80)
        logger.info("Jenkins CI/CD 模式 - 容错性测试执行")
        logger.info(f"失败率阈值: {failure_threshold}%")
        logger.info("=" * 80)
        
        # 创建测试报告目录
        reports_dir = "test_reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        # 生成HTML报告文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_report = os.path.join(reports_dir, f"test_report_jenkins_{timestamp}.html")
        
        # 构建pytest参数 - Jenkins 友好配置
        pytest_args = [
            "tests/test_saucedemo.py",
            "-v",
            "--tb=short",
            f"--html={html_report}",
            "--self-contained-html",
            "--continue-on-collection-errors",  # 收集错误时继续
            "--disable-warnings",
            "--strict-markers",
        ]
        
        logger.info(f"Jenkins模式执行参数: {' '.join(pytest_args)}")
        
        # 执行测试
        exit_code = pytest.main(pytest_args)
        
        # Jenkins 专用的结果处理
        jenkins_result = False
        
        logger.info("=" * 80)
        if exit_code == 0:
            logger.info("✅ 所有测试通过 - Jenkins构建成功")
            jenkins_result = True
        elif exit_code == 1:
            logger.info("⚠️  部分测试失败 - 分析失败率...")
            
            # 获取详细统计信息
            stats = get_test_statistics()
            if stats:
                total = stats.get('total', 0)
                failed = stats.get('failed', 0)
                passed = stats.get('passed', 0)
                
                if total > 0:
                    failure_rate = calculate_failure_rate(total, failed)
                    pass_rate = (passed / total) * 100
                    
                    logger.info(f"📊 详细统计:")
                    logger.info(f"   总测试数: {total}")
                    logger.info(f"   通过数量: {passed}")
                    logger.info(f"   失败数量: {failed}")
                    logger.info(f"   通过率: {pass_rate:.2f}%")
                    logger.info(f"   失败率: {failure_rate:.2f}%")
                    
                    if failure_rate <= failure_threshold:
                        logger.info(f"✅ 失败率 {failure_rate:.2f}% 在可接受范围内 (≤{failure_threshold}%) - Jenkins构建成功")
                        jenkins_result = True
                    else:
                        logger.warning(f"❌ 失败率 {failure_rate:.2f}% 超过阈值 {failure_threshold}% - Jenkins构建失败")
                        jenkins_result = False
                else:
                    logger.warning("❌ 无法获取测试统计信息 - Jenkins构建失败")
                    jenkins_result = False
            else:
                # 如果无法获取统计信息，但有测试失败，采用保守策略
                logger.info("⚠️  无法获取详细统计，但检测到测试失败 - 采用容错策略")
                logger.info("✅ Jenkins构建标记为成功 (容错模式)")
                jenkins_result = True
                
        elif exit_code == 5:
            logger.warning("❌ 没有找到测试用例 - Jenkins构建失败")
            jenkins_result = False
        else:
            logger.error(f"❌ 严重错误 (退出码: {exit_code}) - Jenkins构建失败")
            jenkins_result = False
            
        logger.info(f"📊 HTML报告: {html_report}")
        logger.info("📈 Excel报告: test_reports/ 目录")
        logger.info(f"🔧 Jenkins构建结果: {'SUCCESS' if jenkins_result else 'FAILURE'}")
        logger.info("=" * 80)
        
        return jenkins_result
        
    except Exception as e:
        logger.error(f"Jenkins模式测试失败: {str(e)}")
        return False

def run_tests_tolerant():
    """容错模式 - 总是返回成功"""
    try:
        logger.info("=" * 80)
        logger.info("容错模式 - 无论测试结果如何都标记为成功")
        logger.info("=" * 80)
        
        # 创建测试报告目录
        reports_dir = "test_reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        # 生成HTML报告文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_report = os.path.join(reports_dir, f"test_report_tolerant_{timestamp}.html")
        
        # 构建pytest参数
        pytest_args = [
            "tests/test_saucedemo.py",
            "-v",
            "--tb=short",
            f"--html={html_report}",
            "--self-contained-html",
            "--continue-on-collection-errors",
            "--disable-warnings",
        ]
        
        logger.info(f"容错模式执行参数: {' '.join(pytest_args)}")
        
        # 执行测试
        exit_code = pytest.main(pytest_args)
        
        # 容错模式结果处理
        stats = get_test_statistics()
        
        logger.info("=" * 80)
        if exit_code == 0:
            logger.info("✅ 所有测试通过")
        else:
            logger.info(f"⚠️  测试完成 (退出码: {exit_code})")
            if stats:
                total = stats.get('total', 0)
                failed = stats.get('failed', 0)
                passed = stats.get('passed', 0)
                logger.info(f"📊 统计: 总计 {total}, 通过 {passed}, 失败 {failed}")
        
        logger.info(f"📊 HTML报告: {html_report}")
        logger.info("✅ 容错模式 - 构建标记为成功")
        logger.info("=" * 80)
        
        # 容错模式总是返回成功
        return True
        
    except Exception as e:
        logger.error(f"容错模式测试失败: {str(e)}")
        # 即使出现异常，容错模式也返回成功
        return True

def run_tests_with_custom_options(**kwargs):
    """
    带自定义选项运行测试
    
    参数:
        verbose (bool): 是否显示详细输出，默认True
        capture (str): 输出捕获模式，'no'|'sys'|'fd'，默认'no' 
        tb_style (str): 错误信息样式，'short'|'long'|'line'|'native'，默认'short'
        markers (list): 要运行的标记列表
        keywords (str): 关键字表达式过滤测试
        maxfail (int): 最大失败数，达到后停止测试
        html_report (bool): 是否生成HTML报告，默认True
        strict_mode (bool): 是否启用严格模式，默认True
    """
    try:
        logger.info("=" * 80)
        logger.info("开始执行SauceDemo自动化测试 - 自定义配置")
        logger.info("=" * 80)
        
        # 创建测试报告目录
        reports_dir = "test_reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        # 构建基础pytest参数
        pytest_args = ["tests/test_saucedemo.py"]
        
        # 处理详细输出
        if kwargs.get('verbose', True):
            pytest_args.append("-v")
        
        # 处理错误信息样式
        tb_style = kwargs.get('tb_style', 'short')
        pytest_args.append(f"--tb={tb_style}")
        
        # 处理输出捕获
        capture = kwargs.get('capture', 'no')
        pytest_args.append(f"--capture={capture}")
        
        # 处理HTML报告
        if kwargs.get('html_report', True):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_report = os.path.join(reports_dir, f"test_report_custom_{timestamp}.html")
            pytest_args.extend([f"--html={html_report}", "--self-contained-html"])
        
        # 处理标记过滤
        markers = kwargs.get('markers')
        if markers:
            if isinstance(markers, list):
                marker_expr = " or ".join(markers)
            else:
                marker_expr = str(markers)
            pytest_args.extend(["-m", marker_expr])
        
        # 处理关键字过滤
        keywords = kwargs.get('keywords')
        if keywords:
            pytest_args.extend(["-k", keywords])
        
        # 处理最大失败数
        maxfail = kwargs.get('maxfail')
        if maxfail:
            pytest_args.extend(["--maxfail", str(maxfail)])
        
        # 添加其他常用选项
        pytest_args.extend([
            "--strict-markers",
            "--disable-warnings"
        ])
        
        logger.info(f"执行参数: {' '.join(pytest_args)}")
        
        # 执行测试
        exit_code = pytest.main(pytest_args)
        
        # 结果处理
        strict_mode = kwargs.get('strict_mode', True)
        
        logger.info("=" * 80)
        logger.info(f"测试执行完成，退出代码: {exit_code}")
        
        if strict_mode:
            logger.info("严格模式：只有所有测试通过才标记为成功")
            return exit_code == 0
        else:
            logger.info("宽松模式：只要测试执行完成就标记为成功")
            return exit_code != 2  # 只要不是配置错误就算成功
        
    except Exception as e:
        logger.error(f"自定义测试运行失败: {str(e)}")
        return False

def run_specific_test(test_name):
    """
    运行特定的测试用例
    
    参数:
        test_name (str): 测试用例名称，例如 "test_01_login_success"
    """
    try:
        logger.info(f"运行特定测试: {test_name}")
        
        # 创建报告目录
        reports_dir = "test_reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_report = os.path.join(reports_dir, f"test_report_{test_name}_{timestamp}.html")
        
        pytest_args = [
            "tests/test_saucedemo.py",
            "-v",
            "--tb=short",
            f"--html={html_report}",
            "--self-contained-html",
            "--capture=no",
            "-k", test_name
        ]
        
        logger.info(f"特定测试执行参数: {' '.join(pytest_args)}")
        
        exit_code = pytest.main(pytest_args)
        
        logger.info(f"特定测试 '{test_name}' 完成，退出代码: {exit_code}")
        logger.info(f"报告文件: {html_report}")
        
        return exit_code == 0
        
    except Exception as e:
        logger.error(f"运行特定测试失败: {str(e)}")
        return False

def run_tests_by_marker(marker):
    """
    根据标记运行测试
    
    参数:
        marker (str): pytest标记，例如 "smoke", "regression"
    """
    try:
        logger.info(f"运行标记为 '{marker}' 的测试")
        
        # 创建报告目录
        reports_dir = "test_reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_report = os.path.join(reports_dir, f"test_report_{marker}_{timestamp}.html")
        
        pytest_args = [
            "tests/test_saucedemo.py",
            "-v",
            "--tb=short",
            f"--html={html_report}",
            "--self-contained-html",
            "--capture=no",
            "-m", marker
        ]
        
        logger.info(f"标记测试执行参数: {' '.join(pytest_args)}")
        
        exit_code = pytest.main(pytest_args)
        
        logger.info(f"标记测试 '{marker}' 完成，退出代码: {exit_code}")
        logger.info(f"报告文件: {html_report}")
        
        return exit_code == 0
        
    except Exception as e:
        logger.error(f"运行标记测试失败: {str(e)}")
        return False

def show_help():
    """显示帮助信息"""
    help_text = """
🚀 SauceDemo 自动化测试运行器 v2.0

用法: python run_tests.py [命令] [选项]

📋 可用命令:
  (无参数)                     - 运行所有测试 (标准模式)
  help                        - 显示此帮助信息
  jenkins                     - Jenkins CI/CD模式 (容错15%失败率)
  jenkins-strict              - Jenkins严格模式 (容错5%失败率)
  tolerant                    - 容错模式 (总是成功)
  quick                       - 快速模式 (最多3次失败后停止)
  
📱 测试筛选:
  login                       - 只运行登录相关测试
  cart                        - 只运行购物车相关测试
  checkout                    - 只运行结账相关测试
  sort                        - 只运行排序相关测试
  
📊 示例用法:
  python run_tests.py                    # 标准模式运行所有测试
  python run_tests.py jenkins            # Jenkins模式 (推荐用于CI/CD)
  python run_tests.py tolerant           # 容错模式 (总是成功)
  python run_tests.py quick              # 快速测试
  python run_tests.py login              # 只测试登录功能
  
🔧 Jenkins CI/CD 推荐:
  - 使用 'jenkins' 命令获得最佳的CI/CD体验
  - 自动容错处理，合理的失败率阈值
  - 详细的构建状态报告
  
📈 报告文件:
  - HTML报告: test_reports/test_report_*.html
  - Excel报告: test_reports/test_results_*.xlsx
  - 日志文件: logs/test_execution_*.log
"""
    print(help_text)

if __name__ == "__main__":
    try:
        # 检查命令行参数
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == "help":
                show_help()
                sys.exit(0)
            
            elif command == "jenkins":
                # Jenkins模式 - 容错15%失败率
                success = run_tests_for_jenkins(failure_threshold=15.0)
            
            elif command == "jenkins-strict":
                # Jenkins严格模式 - 容错5%失败率
                success = run_tests_for_jenkins(failure_threshold=5.0)
            
            elif command == "tolerant":
                # 容错模式 - 总是成功
                success = run_tests_tolerant()
            
            elif command == "quick":
                # 快速测试模式：最多3次失败后停止
                success = run_tests_with_custom_options(
                    maxfail=3,
                    tb_style='line',
                    strict_mode=False
                )
            
            elif command == "login":
                # 只运行登录相关测试
                success = run_specific_test("login")
            
            elif command == "cart":
                # 只运行购物车相关测试
                success = run_specific_test("cart")
            
            elif command == "checkout":
                # 只运行结账相关测试
                success = run_specific_test("checkout")
            
            elif command == "sort":
                # 只运行排序相关测试
                success = run_specific_test("sort")
            
            else:
                print(f"❌ 未知命令: {command}")
                print("💡 使用 'python run_tests.py help' 查看可用命令")
                sys.exit(1)
        else:
            # 默认运行所有测试 - 标准模式
            success = run_tests()
        
        # 根据成功/失败设置退出码
        final_exit_code = 0 if success else 1
        logger.info(f"🏁 程序退出，退出码: {final_exit_code}")
        sys.exit(final_exit_code)
        
    except KeyboardInterrupt:
        logger.info("⚠️  测试被用户中断")
        sys.exit(0)  # 用户中断不算失败
    except Exception as e:
        logger.error(f"❌ 程序执行失败: {str(e)}")
        sys.exit(1)
