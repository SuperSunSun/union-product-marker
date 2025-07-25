"""
Factory model for creating scrapers
"""

from typing import Dict, Type
from .site_type import SiteType
from ..scrapers.base import BaseScraper
from ..scrapers.amazon import AmazonScraper
from ..scrapers.fairprice import FairpriceScraper
from ..scrapers.shopee import ShopeeScraper

class ScraperFactory:
    """爬虫工厂类"""
    
    _scrapers: Dict[str, Type[BaseScraper]] = {
        'amazon': AmazonScraper,
        'fairprice': FairpriceScraper,
        'shopee': ShopeeScraper,        # 添加 Shopee 爬虫
        # 'lazada': LazadaScraper,        # 未实现
    }
    
    @classmethod
    def create_scraper(cls, url: str, product_id: str, config: dict) -> BaseScraper:
        """
        根据URL创建对应的爬虫实例
        
        参数：
            url: str - 商品URL
            product_id: str - 商品ID
            config: dict - 配置字典
            
        返回：
            BaseScraper - 爬虫实例
        """
        site_type = SiteType.from_url(url, config)
        
        if site_type.site_name not in cls._scrapers:
            raise ValueError(f"No scraper implemented for site: {site_type.site_name}")
            
        scraper_class = cls._scrapers[site_type.site_name]
        scraper = scraper_class(site_type.site_name, config)  # type: ignore
        scraper.set_current_product_info(product_id, url)
        return scraper 