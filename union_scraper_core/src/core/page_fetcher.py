# -*- coding: utf-8 -*-
# union_scraper/page_fetcher.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import os
import platform

def fetch_page(url, save_path=None, filename=None, wait_time=5):
    """
    使用 Selenium 加载商品页面，返回完整 HTML，可选保存到本地。

    参数：
        url (str): 商品页面 URL
        save_path (str): 保存 HTML 的目录（可选）
        filename (str): HTML 文件名（如 f_1.html）
        wait_time (int): 页面加载等待秒数

    返回：
        str: 页面 HTML 字符串
    """
    # 配置Chrome选项
    options = Options()
    
    # 基本配置
    options.add_argument("--headless=new")  # 使用新版无头模式
    options.add_argument("--no-sandbox")  # 禁用沙箱
    options.add_argument("--disable-dev-shm-usage")  # 禁用/dev/shm使用
    
    # 禁用不必要的功能
    options.add_argument("--disable-extensions")  # 禁用扩展
    options.add_argument("--disable-notifications")  # 禁用通知
    options.add_argument("--disable-popup-blocking")  # 禁用弹窗阻止
    
    # GPU相关（保持基本渲染功能）
    options.add_argument("--disable-gpu")  # 禁用GPU加速
    
    # 内存相关
    options.add_argument("--disable-dev-shm-usage")  # 禁用共享内存
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")  # 禁用站点隔离
    
    # 安全相关
    options.add_argument("--ignore-certificate-errors")  # 忽略证书错误
    options.add_argument("--allow-insecure-localhost")  # 允许不安全的本地连接
    
    # 窗口设置
    options.add_argument("--window-size=1280,800")
    options.add_argument("--force-device-scale-factor=1")
    
    # 用户代理
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

    # 实验性选项
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)

    try:
        # 创建Chrome服务
        service = ChromeService(ChromeDriverManager().install())
        
        # Windows特定配置
        if platform.system() == "Windows":
            # 在Windows上禁用日志
            service.creation_flags = 0x08000000  # CREATE_NO_WINDOW
        
        # 创建Chrome实例
        driver = webdriver.Chrome(service=service, options=options)
        
        try:
            # 设置页面加载超时
            driver.set_page_load_timeout(wait_time * 2)
            
            # 加载页面
            driver.get(url)
            
            # 等待页面渲染
            time.sleep(wait_time)

            # 获取页面源码
            html = driver.page_source

            # 保存HTML（如果需要）
            if save_path and filename is not None:
                os.makedirs(save_path, exist_ok=True)
                html_file = os.path.join(save_path, filename)
                with open(html_file, "w", encoding="utf-8") as f:
                    f.write(html)

            return html

        except TimeoutException as e:
            print(f"[ERROR] Timeout when loading: {url}")
            return None
        except Exception as e:
            print(f"[ERROR] Failed to fetch page {url}: {str(e)}")
            return None
        finally:
            try:
                if driver:
                    driver.quit()
            except Exception as e:
                print(f"[WARNING] Error while closing Chrome driver: {str(e)}")
                # 不抛出异常，让程序继续运行
                
    except Exception as e:
        print(f"[ERROR] Failed to initialize Chrome: {str(e)}")
        return None
