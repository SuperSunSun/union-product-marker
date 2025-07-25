"""
Site type model
"""

from typing import Dict

class SiteType:
    """网站类型类，从配置文件动态生成支持的网站类型"""
    
    _types: Dict[str, 'SiteType'] = {}
    
    def __init__(self, site_name: str):
        self.site_name = site_name
    
    @classmethod
    def load_from_config(cls, config: dict) -> None:
        """从配置文件加载支持的网站类型"""
        cls._types.clear()
        for site in config['sites']:
            cls._types[site['name']] = cls(site['name'])
    
    @classmethod
    def from_url(cls, url: str, config: dict) -> 'SiteType':
        """从URL识别网站类型"""
        if not cls._types:
            cls.load_from_config(config)
            
        url = url.lower()
        for site_name, site_type in cls._types.items():
            if site_name in url:
                return site_type
        raise ValueError(f"Unsupported site type for url: {url}") 