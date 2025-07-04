"""
SauceDemo网站自动化测试用例 - 优化版本（浏览器会话复用）
实现浏览器会话复用，每个用户使用一个浏览器会话，大幅提升测试效率
"""
import pytest
import sys
import os
import time

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from config import USERNAMES, PASSWORD, FIRST_NAME, LAST_NAME, POSTAL_CODE
    from pages.page_objects import LoginPage, InventoryPage, CartPage, CheckoutPage, ProductDetailPage
    from core.exceptions import TestException
    from core.logger_config import logger
    from core.test_suite_manager import test_suite_manager
except ImportError as e:
    print(f"导入模块失败: {e}")
    print(f"项目根目录: {project_root}")
    raise


class TestSauceDemoOptimized:
    """SauceDemo优化测试类 - 使用浏览器会话复用"""

    def run_all_tests_for_user(self, driver, username):
        """为指定用户运行所有测试用例"""
        logger.info(f"开始为用户 {username} 运行所有测试用例")
        
        # 确保用户已切换
        if test_suite_manager.get_current_user() != username:
            success = test_suite_manager.switch_user(username)
            if not success:
                pytest.fail(f"无法切换到用户 {username}")
        
        # 运行所有测试方法
        test_methods = [
            self.test_login_success,
            self.test_logout_and_relogin,
            self.test_add_single_product_to_cart,
            self.test_add_multiple_products_to_cart,
            self.test_add_all_products_to_cart,
            self.test_sort_products_price_low_to_high,
            self.test_sort_products_price_high_to_low,
            self.test_sort_products_name_a_to_z,
            self.test_sort_products_name_z_to_a,
            self.test_view_cart,
            self.test_remove_product_from_cart,
            self.test_continue_shopping,
            self.test_view_product_details,
            self.test_back_to_products_from_details,
            self.test_complete_checkout_flow,
            self.test_cancel_checkout_flow,
            self.test_product_information_accuracy
        ]
        
        for test_method in test_methods:
            try:
                logger.info(f"执行测试: {test_method.__name__} (用户: {username})")
                test_method(driver, username)
                test_suite_manager.reset_session_state()  # 每个测试后重置状态
                logger.info(f"测试完成: {test_method.__name__}")
            except Exception as e:
                logger.error(f"测试失败: {test_method.__name__} (用户: {username}) - {str(e)}")
                # 继续执行其他测试，不中断整个流程
                test_suite_manager.reset_session_state()  # 重置状态以继续下一个测试

    # ============= 测试用例方法 =============

    def test_login_success(self, driver, username):
        """测试用户登录成功"""
        try:
            # 验证当前用户是否已经正确登录
            current_url = driver.current_url
            if "inventory" not in current_url:
                pytest.fail(f"用户 {username} 登录状态验证失败")
            logger.info(f"用户 {username} 登录验证成功")
        except Exception as e:
            logger.error(f"登录测试失败: {str(e)}")
            pytest.fail(f"登录测试失败: {str(e)}")

    def test_logout_and_relogin(self, driver, username):
        """测试用户登出和重新登录"""
        try:
            inventory_page = InventoryPage(driver)
            inventory_page.logout()
            
            # 验证登出成功
            login_page = LoginPage(driver)
            if login_page.is_login_success():
                pytest.fail(f"用户 {username} 登出失败")
            
            # 重新登录
            login_page.login(username, PASSWORD)
            if not login_page.is_login_success():
                pytest.fail(f"用户 {username} 重新登录失败")
                
            logger.info(f"用户 {username} 登出和重新登录测试成功")
        except TestException as e:
            pytest.fail(f"登出重登测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"登出重登测试意外失败: {str(e)}")
            pytest.fail(f"登出重登测试意外失败: {str(e)}")

    def test_add_single_product_to_cart(self, driver, username):
        """测试添加单个商品到购物车"""
        try:
            inventory_page = InventoryPage(driver)
            inventory_page.add_product_by_index(0)
            cart_count = inventory_page.get_cart_item_count()
            assert cart_count == 1, f"购物车商品数量应为1，实际为{cart_count}"
            logger.info(f"用户 {username} 添加单个商品测试成功")
        except TestException as e:
            pytest.fail(f"添加单个商品测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"添加单个商品测试意外失败: {str(e)}")
            pytest.fail(f"添加单个商品测试意外失败: {str(e)}")

    def test_add_multiple_products_to_cart(self, driver, username):
        """测试添加多个商品到购物车"""
        try:
            inventory_page = InventoryPage(driver)
            inventory_page.add_product_by_index(0)
            inventory_page.add_product_by_index(1)
            inventory_page.add_product_by_index(2)
            cart_count = inventory_page.get_cart_item_count()
            assert cart_count == 3, f"购物车商品数量应为3，实际为{cart_count}"
            logger.info(f"用户 {username} 添加多个商品测试成功")
        except TestException as e:
            pytest.fail(f"添加多个商品测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"添加多个商品测试意外失败: {str(e)}")
            pytest.fail(f"添加多个商品测试意外失败: {str(e)}")

    def test_add_all_products_to_cart(self, driver, username):
        """测试添加所有商品到购物车"""
        try:
            inventory_page = InventoryPage(driver)
            products = inventory_page.get_all_products()
            total_products = len(products)
            
            inventory_page.add_all_products()
            cart_count = inventory_page.get_cart_item_count()
            assert cart_count == total_products, f"购物车商品数量应为{total_products}，实际为{cart_count}"
            logger.info(f"用户 {username} 添加所有商品测试成功")
        except TestException as e:
            pytest.fail(f"添加所有商品测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"添加所有商品测试意外失败: {str(e)}")
            pytest.fail(f"添加所有商品测试意外失败: {str(e)}")

    def test_sort_products_price_low_to_high(self, driver, username):
        """测试商品按价格从低到高排序"""
        try:
            inventory_page = InventoryPage(driver)
            inventory_page.sort_products("lohi")
            
            # 验证排序结果
            products = inventory_page.get_all_products()
            prices = []
            for product in products:
                try:
                    price_text = product.find_element(*inventory_page.PRODUCT_PRICE).text
                    price = float(price_text.replace('$', ''))
                    prices.append(price)
                except Exception as e:
                    logger.warning(f"获取产品价格失败: {str(e)}")
                    continue
            
            if len(prices) > 0:
                sorted_prices = sorted(prices)
                assert prices == sorted_prices, "商品价格排序不正确"
            logger.info(f"用户 {username} 价格低到高排序测试成功")
        except TestException as e:
            pytest.fail(f"价格排序测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"价格排序测试意外失败: {str(e)}")
            pytest.fail(f"价格排序测试意外失败: {str(e)}")

    def test_sort_products_price_high_to_low(self, driver, username):
        """测试商品按价格从高到低排序"""
        try:
            inventory_page = InventoryPage(driver)
            inventory_page.sort_products("hilo")
            
            # 验证排序结果
            products = inventory_page.get_all_products()
            prices = []
            for product in products:
                try:
                    price_text = product.find_element(*inventory_page.PRODUCT_PRICE).text
                    price = float(price_text.replace('$', ''))
                    prices.append(price)
                except Exception as e:
                    logger.warning(f"获取产品价格失败: {str(e)}")
                    continue
            
            if len(prices) > 0:
                sorted_prices = sorted(prices, reverse=True)
                assert prices == sorted_prices, "商品价格排序不正确"
            logger.info(f"用户 {username} 价格高到低排序测试成功")
        except TestException as e:
            pytest.fail(f"价格排序测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"价格排序测试意外失败: {str(e)}")
            pytest.fail(f"价格排序测试意外失败: {str(e)}")

    def test_sort_products_name_a_to_z(self, driver, username):
        """测试商品按名称A-Z排序"""
        try:
            inventory_page = InventoryPage(driver)
            inventory_page.sort_products("az")
            
            # 验证排序结果
            products = inventory_page.get_all_products()
            names = []
            for product in products:
                try:
                    name = product.find_element(*inventory_page.PRODUCT_NAME).text
                    names.append(name)
                except Exception as e:
                    logger.warning(f"获取产品名称失败: {str(e)}")
                    continue
            
            if len(names) > 0:
                sorted_names = sorted(names)
                assert names == sorted_names, "商品名称排序不正确"
            logger.info(f"用户 {username} 名称A-Z排序测试成功")
        except TestException as e:
            pytest.fail(f"名称排序测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"名称排序测试意外失败: {str(e)}")
            pytest.fail(f"名称排序测试意外失败: {str(e)}")

    def test_sort_products_name_z_to_a(self, driver, username):
        """测试商品按名称Z-A排序"""
        try:
            inventory_page = InventoryPage(driver)
            inventory_page.sort_products("za")
            
            # 验证排序结果
            products = inventory_page.get_all_products()
            names = []
            for product in products:
                try:
                    name = product.find_element(*inventory_page.PRODUCT_NAME).text
                    names.append(name)
                except Exception as e:
                    logger.warning(f"获取产品名称失败: {str(e)}")
                    continue
            
            if len(names) > 0:
                sorted_names = sorted(names, reverse=True)
                assert names == sorted_names, "商品名称排序不正确"
            logger.info(f"用户 {username} 名称Z-A排序测试成功")
        except TestException as e:
            pytest.fail(f"名称排序测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"名称排序测试意外失败: {str(e)}")
            pytest.fail(f"名称排序测试意外失败: {str(e)}")

    def test_view_cart(self, driver, username):
        """测试查看购物车"""
        try:
            inventory_page = InventoryPage(driver)
            inventory_page.add_product_by_index(0)
            inventory_page.go_to_cart()
            
            cart_page = CartPage(driver)
            cart_items = cart_page.get_cart_items()
            assert len(cart_items) > 0, "购物车应该包含商品"
            assert "cart" in driver.current_url, "应该在购物车页面"
            logger.info(f"用户 {username} 查看购物车测试成功")
        except TestException as e:
            pytest.fail(f"查看购物车测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"查看购物车测试意外失败: {str(e)}")
            pytest.fail(f"查看购物车测试意外失败: {str(e)}")

    def test_remove_product_from_cart(self, driver, username):
        """测试从购物车移除商品"""
        try:
            inventory_page = InventoryPage(driver)
            inventory_page.add_product_by_index(0)
            inventory_page.go_to_cart()
            
            cart_page = CartPage(driver)
            initial_count = len(cart_page.get_cart_items())
            cart_page.remove_product_by_index(0)
            
            final_count = len(cart_page.get_cart_items())
            assert final_count == initial_count - 1, "商品应该从购物车中移除"
            logger.info(f"用户 {username} 移除购物车商品测试成功")
        except TestException as e:
            pytest.fail(f"移除购物车商品测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"移除购物车商品测试意外失败: {str(e)}")
            pytest.fail(f"移除购物车商品测试意外失败: {str(e)}")

    def test_continue_shopping(self, driver, username):
        """测试继续购物功能"""
        try:
            inventory_page = InventoryPage(driver)
            inventory_page.add_product_by_index(0)
            inventory_page.go_to_cart()
            
            cart_page = CartPage(driver)
            cart_page.continue_shopping()
            assert "inventory" in driver.current_url, "未能返回商品页面"
            logger.info(f"用户 {username} 继续购物测试成功")
        except TestException as e:
            pytest.fail(f"继续购物测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"继续购物测试意外失败: {str(e)}")
            pytest.fail(f"继续购物测试意外失败: {str(e)}")

    def test_view_product_details(self, driver, username):
        """测试查看商品详情"""
        try:
            inventory_page = InventoryPage(driver)
            inventory_page.click_product_by_index(0)
            
            assert "inventory-item" in driver.current_url, "应该在商品详情页面"
            
            product_detail_page = ProductDetailPage(driver)
            product_name = product_detail_page.get_product_name()
            assert product_name, "应该能获取商品名称"
            logger.info(f"用户 {username} 查看商品详情测试成功")
        except TestException as e:
            pytest.fail(f"查看商品详情测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"查看商品详情测试意外失败: {str(e)}")
            pytest.fail(f"查看商品详情测试意外失败: {str(e)}")

    def test_back_to_products_from_details(self, driver, username):
        """测试从商品详情页返回商品列表"""
        try:
            inventory_page = InventoryPage(driver)
            inventory_page.click_product_by_index(0)
            
            product_detail_page = ProductDetailPage(driver)
            product_detail_page.back_to_products()
            
            assert "inventory.html" in driver.current_url, "应该返回到商品列表页面"
            logger.info(f"用户 {username} 从详情页返回测试成功")
        except TestException as e:
            pytest.fail(f"从详情页返回测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"从详情页返回测试意外失败: {str(e)}")
            pytest.fail(f"从详情页返回测试意外失败: {str(e)}")

    def test_complete_checkout_flow(self, driver, username):
        """测试完整结账流程"""
        try:
            inventory_page = InventoryPage(driver)
            inventory_page.add_product_by_index(0)
            inventory_page.go_to_cart()
            
            cart_page = CartPage(driver)
            cart_page.checkout()
            
            checkout_page = CheckoutPage(driver)
            checkout_page.fill_checkout_info(FIRST_NAME, LAST_NAME, POSTAL_CODE)
            checkout_page.continue_checkout()
            checkout_page.finish_checkout()
            
            assert "checkout-complete" in driver.current_url, "结账流程应该完成"
            logger.info(f"用户 {username} 完整结账流程测试成功")
        except TestException as e:
            pytest.fail(f"完整结账流程测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"完整结账流程测试意外失败: {str(e)}")
            pytest.fail(f"完整结账流程测试意外失败: {str(e)}")

    def test_cancel_checkout_flow(self, driver, username):
        """测试取消结账流程"""
        try:
            inventory_page = InventoryPage(driver)
            inventory_page.add_product_by_index(0)
            inventory_page.go_to_cart()
            
            cart_page = CartPage(driver)
            cart_page.checkout()
            
            checkout_page = CheckoutPage(driver)
            checkout_page.cancel_checkout()
            assert "cart" in driver.current_url, "取消结账后未返回购物车"
            logger.info(f"用户 {username} 取消结账流程测试成功")
        except TestException as e:
            pytest.fail(f"取消结账流程测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"取消结账流程测试意外失败: {str(e)}")
            pytest.fail(f"取消结账流程测试意外失败: {str(e)}")

    def test_product_information_accuracy(self, driver, username):
        """测试商品信息的准确性"""
        try:
            inventory_page = InventoryPage(driver)
            products = inventory_page.get_all_products()
            
            if len(products) > 0:
                first_product = products[0]
                name = first_product.find_element(*inventory_page.PRODUCT_NAME).text
                price = first_product.find_element(*inventory_page.PRODUCT_PRICE).text
                
                assert name, "商品应该有名称"
                assert price, "商品应该有价格"
                assert "$" in price, "价格应该包含货币符号"
            logger.info(f"用户 {username} 商品信息准确性测试成功")
        except TestException as e:
            pytest.fail(f"商品信息准确性测试执行失败: {str(e)}")
        except Exception as e:
            logger.error(f"商品信息准确性测试意外失败: {str(e)}")
            pytest.fail(f"商品信息准确性测试意外失败: {str(e)}")

    # ============= 用户级别的测试用例 =============

    @pytest.mark.order(1)
    def test_user_standard_user(self, shared_driver, suite_manager):
        """执行 standard_user 的所有测试用例"""
        username = "standard_user"
        logger.info(f"=" * 60)
        logger.info(f"开始执行用户 {username} 的所有测试用例")
        logger.info(f"=" * 60)
        self.run_all_tests_for_user(shared_driver, username)
        logger.info(f"用户 {username} 的所有测试用例执行完成")

    @pytest.mark.order(2)
    def test_user_visual_user(self, shared_driver, suite_manager):
        """执行 visual_user 的所有测试用例"""
        username = "visual_user"
        logger.info(f"=" * 60)
        logger.info(f"开始执行用户 {username} 的所有测试用例")
        logger.info(f"=" * 60)
        self.run_all_tests_for_user(shared_driver, username)
        logger.info(f"用户 {username} 的所有测试用例执行完成")