"""
Product data model
"""

from dataclasses import dataclass, field
from typing import List, Dict
from ..utils.time_utils import get_iso_timestamp

@dataclass
class ProductData:
    """标准商品数据结构"""
    id: str = ""  # 商品ID
    url: str = ""  # 商品URL
    url_tag: str = "main"  # 商品URL标签
    crawled_at: str = field(default_factory=get_iso_timestamp)  # 爬取时间
    product_name: str = ""  # 商品名称
    brand: str = ""  # 品牌    
    price_original: str = ""  # 原价
    price_current: str = ""  # 当前价格    
    image_urls_original: List[str] = field(default_factory=list)  # 原始图片URL
    image_urls_simplified: List[str] = field(default_factory=list)  # 简化后的图片URL
    infos: dict = field(default_factory=dict)  # 其他信息
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "url": self.url,
            "url_tag": self.url_tag,
            "crawled_at": self.crawled_at,
            "product_name": self.product_name,
            "brand": self.brand,
            "price_current": self.price_current,
            "price_original": self.price_original,
            "image_urls_original": self.image_urls_original,
            "image_urls_simplified": self.image_urls_simplified,
            "infos": self.infos
        }
    
    def is_empty(self) -> bool:
        """判断是否为空"""
        return not self.product_name

    @classmethod
    def create_empty(cls, product_id: str = "", url: str = "") -> 'ProductData':
        """创建空的数据结构"""
        return cls(
            id=product_id,
            url=url,
            url_tag="main",
            product_name="",
            brand="",
            price_original="",
            price_current="",
            image_urls_original=[],
            image_urls_simplified=[],
            infos={}
        ) 