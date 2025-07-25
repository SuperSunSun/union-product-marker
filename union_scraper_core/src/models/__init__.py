"""
Data models for the scraper
"""

from .product_data import ProductData
from .site_type import SiteType
from .file_manager import FileManager
from .scraper_factory import ScraperFactory

__all__ = ['ProductData', 'SiteType', 'FileManager', 'ScraperFactory'] 