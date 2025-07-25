"""
Scrapers for different e-commerce sites
"""

from .base import BaseScraper
from .amazon import AmazonScraper
from .fairprice import FairpriceScraper

__all__ = ['BaseScraper', 'AmazonScraper', 'FairpriceScraper'] 