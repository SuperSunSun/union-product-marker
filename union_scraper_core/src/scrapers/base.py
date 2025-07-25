from abc import ABC, abstractmethod
import os
from typing import List, Dict, Optional
from ..models.site_type import SiteType
from ..models.file_manager import FileManager
from ..utils.file_utils import save_file, write_json
from ..core.page_fetcher import fetch_page
from ..core.image_downloader import download_images
from loguru import logger
from ..models.product_data import ProductData
import re

class BaseScraper(ABC):
    def __init__(self, site_name: str, config: dict):
        """
        初始化爬虫
        
        参数：
            site_name (str): 网站名称（如 'amazon' 或 'fairprice'）
            config (dict): 配置字典
        """
        # 从配置中获取站点配置
        site_config = next((site for site in config['sites'] if site['name'] == site_name), None)
        if site_config is None:
            raise ValueError(f"Site configuration not found for: {site_name}")
            
        # 处理 base_url
        base_url = site_config['base_url'].replace('https://', '').replace('http://', '')
        self.site_type = SiteType.from_url(base_url, config)
        self.config = config
        
        # 初始化配置
        self.site_config = site_config
        self.file_manager = None
        self.output_config = config['output']
        self.debug_config = config.get('debug', {})
        self.crawler_config = config.get('crawler', {})
        
        
        # 初始化当前处理的商品信息
        self._current_product_id: Optional[str] = None
        self._current_url: Optional[str] = None
        self._current_url_tag: Optional[str] = "main"
        self._current_data: Optional[ProductData] = None

    def _check_if_initialized(self):
        """检查产品ID和URL是否都已设置"""
        if not self._current_product_id or not self._current_url:
            raise ValueError("Product ID or URL not set")

    def set_current_product_info(self, product_id: str, url: str, url_tag: str = "main"):
        """
        设置当前处理的商品信息
        
        参数：
            product_id (str): 商品ID
            url (str): 商品URL
            url_tag (str): URL标签，默认为 "main"
        """
        self._current_product_id = product_id
        self._current_url = url
        self._current_url_tag = url_tag

        self.file_manager = FileManager(
            self.site_config.get('prefix', self.site_config['name'][0] + '_'), 
            self._current_product_id, 
            self._current_url_tag
        )

    def format_price(self, price_str: str) -> str:
        """
        格式化价格字符串，移除货币符号并确保保留两位小数
        
        参数：
            price_str (str): 原始价格字符串，可能包含货币符号如 $、S$ 等
            
        返回：
            str: 格式化后的价格字符串，保留两位小数，无货币符号
        """
        if not price_str or not isinstance(price_str, str):
            return ""
        
        # 移除所有货币符号和空格
        cleaned_price = re.sub(r'[S$,$,\s]', '', price_str.strip())
        
        # 尝试提取数字部分
        try:
            # 匹配数字（包括小数点和逗号分隔符）
            price_match = re.search(r'[\d,]+\.?\d*', cleaned_price)
            if price_match:
                price_value = price_match.group()
                # 移除逗号分隔符
                price_value = price_value.replace(',', '')
                # 转换为浮点数并格式化为两位小数
                formatted_price = f"{float(price_value):.2f}"
                return formatted_price
            else:
                return ""
        except (ValueError, TypeError):
            return ""

    def get_local_html(self) -> str:
        """
        从本地文件获取HTML内容
            
        返回：
            str: HTML内容
        """
        self._check_if_initialized()
            
        html_path = os.path.join(
            self.output_config['html_dir'],
            self.file_manager.get_html_filename()
        )
        
        if not os.path.exists(html_path):
            raise FileNotFoundError(f"Local HTML file not found: {html_path}")
            
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()

    def fetch_page(self) -> str:
        """
        获取页面内容
        
        返回：
            str: HTML内容
        """
        self._check_if_initialized()
        
        # 生成HTML文件名
        filename = self.file_manager.get_html_filename(self._current_product_id)
        return fetch_page(self._current_url, save_path=self.output_config['html_dir'], filename=filename)

    def parse_data(self, html: str) -> dict:
        """
        解析页面数据
        
        参数：
            html (str): 页面HTML内容
            
        返回：
            dict: 解析后的数据
        """
        self._check_if_initialized()
            
        # 如果HTML为空，返回空的数据结构
        if not html: 
            self._current_data = ProductData.create_empty(self._current_product_id, self._current_url)
            return self._current_data.to_dict()
        
        try:
            # 获取具体爬虫的解析结果
            self._current_data = self.parse_product_data(html, self._current_product_id, self._current_url)
            
            # 格式化价格字段
            if self._current_data:
                self._current_data.price_original = self.format_price(self._current_data.price_original)
                self._current_data.price_current = self.format_price(self._current_data.price_current)
            
            # 如果解析失败，返回空的数据结构
            if self._current_data.is_empty():
                logger.warning(f"Failed to parse HTML(EMPTY) for ID={self._current_product_id}")

        except Exception as e:
            logger.error(f"Failed to parse HTML(ERROR) for ID={self._current_product_id}: {str(e)}")
            logger.error(str(e))
            self._current_data = ProductData.create_empty(self._current_product_id, self._current_url)
        
                    
        return self._current_data.to_dict()

    @abstractmethod
    def parse_product_data(self, html: str, product_id: str, url: str) -> ProductData:
        """
        解析页面数据的抽象方法，需要由具体爬虫实现
        
        参数：
            html (str): 页面HTML内容
            product_id (str): 商品ID
            url (str): 商品URL
            
        返回：
            ProductData: 解析后的数据对象
        """
        raise NotImplementedError("Subclasses must implement parse_product_data()")

    def download_images(self) -> List[str]:
        """
        下载商品图片
            
        返回：
            List[str]: 下载的图片文件路径列表
        """
        self._check_if_initialized()
            
        if not self._current_data:
            return []

        image_urls = self._current_data.image_urls_simplified
        if not image_urls:
            return []
            
        folder_path = os.path.join(self.output_config['image_dir'], str(self._current_product_id))
        # 使用file_manager的方法生成文件名模式
        filename_pattern = lambda idx: self.file_manager.get_image_filename(idx)
        # 使用简化后的URL进行下载
        return download_images(
            image_urls,
            folder_path,
            filename_pattern
        )

    def save_html(self, html: str, output_dir: str):
        """保存HTML文件"""
        self._check_if_initialized()
            
        filename = self.file_manager.get_html_filename()
        filepath = os.path.join(output_dir, filename)
        save_file(filepath, html, mode='w', encoding='utf-8')

    def save_product_data(self, data: dict, output_dir: str):
        """保存商品数据"""
        self._check_if_initialized()
            
        # 创建商品目录
        product_folder = self.file_manager.get_product_folder()
        product_path = os.path.join(output_dir, product_folder)
        os.makedirs(product_path, exist_ok=True)

        # 保存JSON文件
        json_filename = self.file_manager.get_json_filename()
        json_path = os.path.join(product_path, json_filename)
        
        try:
            write_json(json_path, data)
        except Exception as e:
            print(f"[ERROR] Failed to save JSON: {str(e)}")
            raise 