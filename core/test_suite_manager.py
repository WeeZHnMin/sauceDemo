"""
测试套件管理器 - 负责用户会话管理和浏览器复用
"""
import time
from typing import Optional, List
from core.logger_config import logger
from core.webdriver_utils import WebDriverManager
from pages.page_objects import LoginPage, InventoryPage
from config import USERNAMES, PASSWORD, BASE_URL


class TestSuiteManager:
    """测试套件管理器 - 管理用户切换和浏览器会话复用"""
    
    def __init__(self):
        self.driver = None
        self.current_user = None
        self.is_logged_in = False
        
    def start_session(self):
        """启动测试会话 - 创建浏览器实例"""
        if self.driver is None:
            try:
                self.driver = WebDriverManager.create_driver()
                logger.info("测试会话已启动 - 浏览器已创建")
                return True
            except Exception as e:
                logger.error(f"启动测试会话失败: {str(e)}")
                return False
        return True
    
    def end_session(self):
        """结束测试会话 - 关闭浏览器"""
        if self.driver:
            try:
                WebDriverManager.close_driver(self.driver)
                self.driver = None
                self.current_user = None
                self.is_logged_in = False
                logger.info("测试会话已结束 - 浏览器已关闭")
            except Exception as e:
                logger.error(f"结束测试会话失败: {str(e)}")
    
    def switch_user(self, username: str) -> bool:
        """切换用户 - 通过登出/登入实现用户切换"""
        if not self.driver:
            logger.error("浏览器会话未启动，无法切换用户")
            return False
            
        try:
            # 如果当前有用户登录，先登出
            if self.is_logged_in and self.current_user:
                logger.info(f"登出当前用户: {self.current_user}")
                self._logout_current_user()
            
            # 登录新用户
            logger.info(f"登录新用户: {username}")
            success = self._login_user(username)
            
            if success:
                self.current_user = username
                self.is_logged_in = True
                logger.info(f"用户切换成功: {username}")
                return True
            else:
                logger.error(f"用户切换失败: {username}")
                return False
                
        except Exception as e:
            logger.error(f"切换用户时发生错误: {str(e)}")
            return False
    
    def _logout_current_user(self):
        """登出当前用户"""
        try:
            # 确保在正确的页面上
            if "inventory" not in self.driver.current_url:
                self.driver.get(BASE_URL + "inventory.html")
                time.sleep(1)
            
            inventory_page = InventoryPage(self.driver)
            inventory_page.logout()
            self.is_logged_in = False
            time.sleep(0.5)  # 等待登出完成
            
        except Exception as e:
            logger.warning(f"登出用户时出现警告: {str(e)}")
            # 如果登出失败，尝试直接导航到登录页
            self.driver.get(BASE_URL)
            self.is_logged_in = False
    
    def _login_user(self, username: str) -> bool:
        """登录指定用户"""
        try:
            # 确保在登录页面
            if "inventory" in self.driver.current_url:
                self.driver.get(BASE_URL)
                time.sleep(0.5)
            
            login_page = LoginPage(self.driver)
            login_page.login(username, PASSWORD)
            
            # 验证登录是否成功
            return login_page.is_login_success()
            
        except Exception as e:
            logger.error(f"登录用户 {username} 失败: {str(e)}")
            return False
    
    def reset_session_state(self):
        """重置会话状态 - 清理购物车等状态"""
        if not self.driver or not self.is_logged_in:
            return
            
        try:
            # 导航到首页以重置状态
            self.driver.get(BASE_URL + "inventory.html")
            time.sleep(0.5)
            
            # 清理本地存储和会话存储（如果需要）
            self.driver.execute_script("localStorage.clear();")
            self.driver.execute_script("sessionStorage.clear();")
            
            logger.info("会话状态已重置")
            
        except Exception as e:
            logger.warning(f"重置会话状态时出现警告: {str(e)}")
    
    def get_driver(self):
        """获取当前的WebDriver实例"""
        return self.driver
    
    def is_session_active(self) -> bool:
        """检查会话是否活跃"""
        return self.driver is not None
    
    def get_current_user(self) -> Optional[str]:
        """获取当前登录的用户"""
        return self.current_user if self.is_logged_in else None


# 全局测试套件管理器实例
test_suite_manager = TestSuiteManager()