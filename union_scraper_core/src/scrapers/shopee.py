from typing import Dict, List, Optional
import re
from bs4 import BeautifulSoup
import json
from .base import BaseScraper
from ..models.product_data import ProductData
from loguru import logger

class ShopeeScraper(BaseScraper):
    def __init__(self, site_name: str, config: dict):
        super().__init__(site_name, config)

    def fetch_page(self) -> str:
        logger.warning(f"fetch_page is banned by shopee, use local html instead")
        return self.get_local_html()


    def parse_product_data(self, html: str, product_id: str, url: str) -> ProductData:
        """解析 Shopee 页面数据"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 解析标题和品牌，若无则设为 ""
        title = self._parse_title(soup) or ""
        brand = self._parse_brand(soup) or ""

        # 解析价格，兼容返回 None 的情况
        price_info = self._parse_price(soup) or [None, None]

        # 解析图片 URL，默认空列表
        original_urls = self._parse_image_urls(soup) or []
        simplified_urls = self._simplify_image_urls(original_urls)

        # 解析结构化信息
        infos = {
            "Product Specifications": self._parse_product_specifications(soup),
            "Product Description": self._parse_product_description(soup) or ""
        }

        
        return ProductData(
            id=product_id,
            url=url,
            product_name=title or "",
            brand=brand or "",
            price_current=price_info[0],
            price_original=price_info[1],
            image_urls_original=original_urls,
            image_urls_simplified=simplified_urls,
            infos=infos
        )

    def _parse_title(self, soup: BeautifulSoup) -> Optional[str]:
        """解析 Shopee 商品标题，从 <section class='flex card'> 中的第二个 <section> 下的 <h1> 获取"""
        card_sections = soup.select('section.flex.card > section')
        if len(card_sections) >= 2:
            target_section = card_sections[1]
            h1 = target_section.find('h1')
            if h1:
                return self._clean_text(h1.get_text())
        return None

    def _parse_brand(self, soup: BeautifulSoup) -> Optional[str]:
        """仅从 Product Specifications 中提取品牌名称"""
        sections = soup.find_all('section')
        for section in sections:
            h2 = section.find('h2')
            if h2 and 'Product Specifications' in h2.get_text():
                for h3 in section.find_all('h3'):
                    if 'Brand' in h3.get_text():
                        parent = h3.find_parent()
                        if parent:
                            brand_tag = parent.find('a')
                            if brand_tag:
                                return self._clean_text(brand_tag.get_text())
                            else:
                                # fallback: 找该块下的纯文本内容
                                divs = parent.find_all('div')
                                for div in divs:
                                    text = div.get_text(strip=True)
                                    if text:
                                        return self._clean_text(text)
        return None


    def _parse_price(self, soup: BeautifulSoup) -> Optional[List[Optional[str]]]:
        """Shopee 商品价格提取，仅解析价格区域中第一个价格块的直接子项"""
        
        # 方法1: 直接查找包含 aria-live="polite" 的 section
        polite_sections = soup.find_all('section', attrs={'aria-live': 'polite'})
        for section in polite_sections:
            price_div = section.find('div', class_='jRlVo0')
            if price_div:
                price_elem = price_div.find('div', class_='IZPeQz B67UQ0')
                if price_elem:
                    current_price = self._clean_text(price_elem.get_text())
                    
                    # 查找最低价格信息 - 在同一个父容器中查找
                    original_price = None
                    parent_container = section.find_parent('div')
                    if parent_container:
                        lowest_price_div = parent_container.find('div', class_='yJfHJc')
                        if lowest_price_div:
                            price_spans = lowest_price_div.find_all('span')
                            for span in price_spans:
                                text = span.get_text(strip=True)
                                if text.startswith('$') and text != 'LOWEST PRICE: ':
                                    original_price = self._clean_text(text)
                                    break
                    
                    return [current_price, original_price]
        
        # 方法2: 如果方法1失败，尝试原有的逻辑
        h1 = soup.find('h1')
        if not h1:
            return None

        # 查找价格区块（包含 $ 的块中，class 随机但结构固定）
        for sibling in h1.find_all_next():
            if sibling.name == 'div' and '$' in sibling.get_text():
                # 尝试找到只包含价格的直接块（如 .jRlVo0）
                price_inner_block = sibling.find('div', string=lambda text: text and '$' in text)
                if price_inner_block:
                    price_block = price_inner_block.find_parent('div')
                else:
                    price_block = sibling
                break
        else:
            return None

        # 只提取 .jRlVo0 的直接子 div 内容
        result = []
        for div in price_block.find_all('div', recursive=False):
            text = div.get_text(strip=True)
            if text.startswith('$'):
                result.append(self._clean_text(text))

        if not result:
            return None

        current_price = result[0]
        original_price = result[1] if len(result) > 1 else None
        return [current_price, original_price]



    def _parse_product_specifications(self, soup: BeautifulSoup) -> Dict[str, str]:
        """解析 'Product Specifications'，一对一提取每个 h3 及其下一个值节点"""
        result = {}
        section = None
        for sec in soup.select('div.product-detail section'):
            header = sec.find('h2')
            if header and 'Product Specifications' in header.get_text(strip=True):
                section = sec
                break
        if not section:
            return result

        # 查找所有 h3，逐个提取其后的值
        for h3 in section.find_all('h3'):
            key = self._clean_text(h3.get_text())
            value = ""
            next_elem = h3.find_next_sibling()
            while next_elem and next_elem.name not in ['h3', 'h2']:
                text = next_elem.get_text(" ", strip=True)
                if text:
                    value += self._clean_text(text) + "\n"
                next_elem = next_elem.find_next_sibling()
            result[key] = value.strip()
        return result

    def _parse_product_description(self, soup: BeautifulSoup) -> Optional[str]:
        """解析 'Product Description'，结构定位，逐段换行，去重并清洗"""
        section = None
        for sec in soup.select('div.product-detail section'):
            header = sec.find('h2')
            if header and 'Product Description' in header.get_text(strip=True):
                section = sec
                break
        if not section:
            return None

        seen = set()
        paragraphs = []

        # 优先处理所有 <p> 标签
        for p in section.find_all('p'):
            text = self._clean_text(p.get_text(strip=True))
            if text and text not in seen:
                seen.add(text)
                paragraphs.append(text)

        return "\n".join(paragraphs) if paragraphs else None


    def _parse_image_urls(self, soup: BeautifulSoup) -> list[str]:
        """
        提取图片缩略图的 webp 地址（带后缀），用于 image_urls_original。
        """
        image_urls = []
        # 找到图片缩略图容器的父 section
        section = soup.select_one('section.card section')
        if not section:
            return image_urls

        # 选择包含所有 thumbnail 的块
        thumbnail_divs = section.select('div:has(div.thumbnail-selected-mask)')
        for thumb in thumbnail_divs:
            target = thumb.find_previous_sibling('div')
            if target:
                source = target.find('source')
                if source and source.has_attr('srcset'):
                    srcset = source['srcset']
                    # 拿第一个（1x）图片地址
                    url = srcset.split()[0]
                    image_urls.append(url)
        return image_urls


    def _simplify_image_urls(self, urls: list[str]) -> list[str]:
        """
        批量简化并去重图片链接，保留顺序。
        示例：
        ['...abc@resize.webp', '...abc@resize.webp', '...xyz@resize.webp']
        -> ['...abc', '...xyz']
        """
        seen = set()
        simplified = []
        for url in urls:
            base_url = url.split('@')[0]
            if base_url not in seen:
                seen.add(base_url)
                simplified.append(base_url)
        return simplified



    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        # 移除多余空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        return text 