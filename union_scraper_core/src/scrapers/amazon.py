from typing import Dict, List, Optional
import os
import re
from bs4 import BeautifulSoup
import json5 as json

from .base import BaseScraper
from ..models.product_data import ProductData

class AmazonScraper(BaseScraper):
    def __init__(self, site_name: str, config: dict):
        super().__init__(site_name, config)

    def parse_product_data(self, html: str, product_id: str, url: str) -> ProductData:
        """解析亚马逊页面数据"""
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 解析所有数据
        title = self._parse_title(soup)
        brand = self._parse_brand(soup)
        price_info = self._parse_price(soup) or {"current_price": None, "original_price": None}
        original_urls = self._parse_image_urls(soup)
        simplified_urls = [self._simplify_image_url(url) for url in original_urls]
        
        # 其他信息放入 infos
        infos = {
            "meta_info": self._parse_meta_info(soup),
            "about_this_item": self._parse_about_this_item(soup),
            "product_description": self._parse_product_description(soup),
            "product_infomation": self._parse_product_infomation(soup),
            "product_details": self._parse_product_details(soup),
            "important_information": self._parse_important_information(soup)
        }
        
        # 返回 ProductData 对象
        return ProductData(
            id=product_id,
            url=url,
            product_name=title or "",
            brand=brand or "",
            price_current=price_info.get("current_price", ""),
            price_original=price_info.get("original_price", ""),
            image_urls_original=original_urls,
            image_urls_simplified=simplified_urls,
            infos=infos
        )

    def _clean_text(self,text: str) -> str:
        """清理文本：去除不可见字符、多余换行、连续空格"""
        if not text:
            return text
        text = re.sub(r'[\u200e\u200f\xa0]+', '', text)  # 删除不可见字符
        text = re.sub(r'\s+', ' ', text)  # 合并换行与空格为单个空格
        return text.strip()

    def _simplify_image_url(self, url: str) -> str:
        """移除 Amazon 图片 URL 中尺寸后缀"""
        return re.sub(
            r'(.*/)([^/.]+)(\..+)(\.[^.]+)$', 
            lambda m: f"{m.group(1)}{m.group(2)}{m.group(4)}",
            url
        )

    def _extract_color_images_script(self, content: str) -> List[Dict]:
        """从脚本中安全提取 'colorImages': {'initial': [ {...}, {...} ] } 数组内容"""
        start_marker = "'colorImages': { 'initial': "
        start = content.find(start_marker)
        if start == -1:
            return []
        start = content.find('[', start)
        if start == -1:
            return []

        depth = 0
        for i in range(start, len(content)):
            if content[i] == '[':
                depth += 1
            elif content[i] == ']':
                depth -= 1
                if depth == 0:
                    json_text = content[start:i+1]
                    try:
                        return json.loads(json_text)
                    except Exception as e:
                        print("[ERROR] Failed to load extracted colorImages array:", e)
                    break
        return []


    def _parse_title(self, soup: BeautifulSoup) -> Optional[str]:
        """解析商品标题"""
        title_elem = soup.select_one('#productTitle')
        return self._clean_text(title_elem.text) if title_elem else None

    def _parse_brand(self, soup: BeautifulSoup) -> Optional[str]:
        """解析品牌信息"""
        brand_tag = soup.select_one('#bylineInfo')
        if not brand_tag:
            return None
        
        brand = self._clean_text(brand_tag.text)
        if brand and brand.lower().startswith("brand:"):
            brand = brand[6:].strip()
        elif brand and brand.startswith("Brand："):
            brand = brand[4:].strip()
        return brand

    def _parse_price(self, soup: BeautifulSoup) -> Dict:
        """解析价格信息
        
        处理以下价格结构：
        1. 现价提取策略：
           - 优先从 .priceToPay span[aria-hidden="true"] 中提取（包含 a-price-symbol, a-price-whole, a-price-fraction）
           - 如果为空，则尝试从 .priceToPay .a-offscreen 中提取
           - 最后尝试从 .aok-offscreen 中提取
           
        2. 原价提取策略：
           - 优先查找包含 "List Price:" 的容器
           - 从容器中提取 .a-price.a-text-price[data-a-strike="true"] 的价格
           - 如果未找到，直接在价格块中查找带有 data-a-strike="true" 属性的价格
        
        Returns:
            Dict: {
                "current_price": "S$22.40",  # 现价，如果未找到则为 None
                "original_price": "S$40.80"  # 原价，如果未找到则为 None
            }
        """
        price = {
            "current_price": None,
            "original_price": None
        }
        
        def clean_price(price_text: str) -> str:
            """清理价格文本，去除单价等额外信息"""
            if not price_text:
                return None
            
            # 清理并规范化价格格式
            price_text = self._clean_text(price_text)
            
            # 确保价格以 S$ 开头
            if not price_text.startswith('S$'):
                # 尝试查找价格部分
                if 'S$' in price_text:
                    price_text = price_text[price_text.find('S$'):].strip()
                else:
                    return None
                
            return price_text.strip()

        # 只从 corePriceDisplay_desktop_feature_div 中提取价格
        price_block = soup.select_one('#corePriceDisplay_desktop_feature_div')
        if not price_block:
            return price

        # 1. 获取现价
        # 首先尝试从 priceToPay 的 span[aria-hidden="true"] 中获取（最准确的方法）
        price_to_pay = price_block.select_one('.priceToPay')
        if price_to_pay:
            # 尝试从 aria-hidden="true" 的 span 中提取价格
            aria_hidden_span = price_to_pay.select_one('span[aria-hidden="true"]')
            if aria_hidden_span:
                # 组合价格符号、整数部分和小数部分
                price_symbol = aria_hidden_span.select_one('.a-price-symbol')
                price_whole = aria_hidden_span.select_one('.a-price-whole')
                price_fraction = aria_hidden_span.select_one('.a-price-fraction')
                
                if price_symbol and price_whole:
                    symbol_text = price_symbol.get_text(strip=True)
                    whole_text = price_whole.get_text(strip=True)
                    fraction_text = price_fraction.get_text(strip=True) if price_fraction else ""
                    
                    # 组合完整价格
                    combined_price = f"{symbol_text}{whole_text}{fraction_text}"
                    price["current_price"] = clean_price(combined_price)
        
        # 如果上面的方法失败，尝试从 priceToPay 的 a-offscreen 中获取
        if not price["current_price"]:
            current_price_elem = price_block.select_one('.priceToPay .a-offscreen')
            if current_price_elem and current_price_elem.get_text(strip=True):
                price_text = current_price_elem.get_text(strip=True)
                if price_text:
                    price["current_price"] = clean_price(price_text)
        
        # 如果还是失败，尝试从 aok-offscreen 中获取（需要进一步清理）
        if not price["current_price"]:
            price_container = price_block.select_one('.a-section.a-spacing-none.aok-align-center')
            if price_container:
                offscreen_price = price_container.select_one('.aok-offscreen')
                if offscreen_price:
                    price_text = offscreen_price.get_text(strip=True)
                    if price_text:
                        # 对于 aok-offscreen，需要更严格的清理
                        if 'S$' in price_text:
                            # 提取 S$ 后面的数字部分
                            import re
                            price_match = re.search(r'S\$(\d+\.?\d*)', price_text)
                            if price_match:
                                price["current_price"] = f"S${price_match.group(1)}"

        # 2. 获取原价（如果存在）
        # 首先尝试找到包含 "List Price:" 的文本
        list_price_container = price_block.find(lambda tag: tag.get_text(strip=True) and 'List Price:' in tag.get_text(strip=True))
        if list_price_container:
            # 在这个容器中查找原价
            original_price_elem = list_price_container.select_one('.a-price.a-text-price[data-a-strike="true"] .a-offscreen')
            if original_price_elem:
                price_text = original_price_elem.get_text(strip=True)
                if price_text:
                    price["original_price"] = clean_price(price_text)
        
        # 如果上面的方法没找到原价，尝试直接在价格块中查找
        if not price["original_price"]:
            original_price_elem = price_block.select_one('.a-price.a-text-price[data-a-strike="true"] .a-offscreen')
            if original_price_elem:
                price_text = original_price_elem.get_text(strip=True)
                if price_text:
                    price["original_price"] = clean_price(price_text)
        
        return price

    def _parse_meta_info(self, soup: BeautifulSoup) -> Dict:
        """解析商品元信息"""
        # Step 1: meta_info (价格下方, about this item上方) productOverview_feature_div
        meta_info = {}

        overview_div = soup.select_one('#productOverview_feature_div')
        if overview_div:
            for row in overview_div.select('table tr'):
                cells = row.find_all(['th', 'td'])
                if len(cells) >= 2:
                    k = self._clean_text(cells[0].get_text())
                    v = self._clean_text(cells[1].get_text())
                    if k and v:
                        meta_info[k] = v
        
        return meta_info
    
    def _parse_about_this_item(self, soup: BeautifulSoup) -> List[str]:
        """解析'关于此商品'部分"""
        # about this item
        about_items = []
        about_section = soup.select_one('#feature-bullets')
        if about_section:
            for item in about_section.select('li:not(.aok-hidden) span'):
                text = self._clean_text(item.text)
                if text:
                    about_items.append(text)
        return about_items

    def _parse_image_urls(self, soup: BeautifulSoup) -> List[str]:
        """解析图片URL列表"""
        image_urls = []
        # image_urls 从 colorImages.initial 中提取（兼容嵌套在 JS 中的伪 JSON）
        # 首先尝试从colorImages脚本中提取
        for script in soup.find_all('script'):
            content = script.string or script.get_text()
            if content and 'colorImages' in content:
                images = self._extract_color_images_script(content)
                image_urls = [
                    img.get('hiRes') or img.get('large') or img.get('mainUrl')
                    for img in images if any(img.get(k) for k in ('hiRes', 'large', 'mainUrl'))
                ]
                image_urls = [url for url in image_urls if url]
                if image_urls:
                    break
        
        # 如果脚本方式失败，尝试从图片展示区获取
        if not image_urls:
            for img in soup.select('#imageBlock img'):
                if 'src' in img.attrs:
                    url = img['src']
                    image_urls.append(url)
        
        return image_urls

    def _parse_product_description(self, soup: BeautifulSoup) -> Optional[str]:
        """解析商品详情"""
        detail_elem = soup.select_one('#productDescription_feature_div')
        return self._clean_text(detail_elem.text) if detail_elem else None

    def _parse_product_infomation(self, soup: BeautifulSoup) -> Dict:
        """解析商品信息"""
        product_infomation = {}
        
        def extract_table_dict(selector: str) -> Dict:
            """从表格中提取键值对"""
            result = {}
            table = soup.select_one(selector)
            if table:
                for row in table.select('tr'):
                    cells = row.select('td, th')
                    if len(cells) >= 2:
                        key = self._clean_text(cells[0].text)
                        value = self._clean_text(cells[1].text)
                        if key and value:
                            result[key] = value
            return result
        

        product_infomation['technical_details'] = extract_table_dict('#productDetails_techSpec_section_1')
        product_infomation['additional_information'] = extract_table_dict('#productDetails_detailBullets_sections1')

        return product_infomation
    
    def _parse_product_details(self, soup: BeautifulSoup) -> Dict:
        # 专门提取 product_details（来自 detailBullets_feature_div）
        product_details = {}
        detail_div = soup.select_one('#detailBullets_feature_div')
        if detail_div:
            for li in detail_div.select('li'):
                text = self._clean_text(li.get_text())
                if ':' in text:
                    k, v = map(self._clean_text, text.split(':', 1))
                    if k and v:
                        product_details[k] = v
        return product_details
    
    def _parse_important_information(self, soup: BeautifulSoup) -> Dict:
        """解析重要信息"""
        # important_information 特殊处理：查找 div 中包含关键标题
        important_data = {}
        imp_section = soup.find('div', id='important-information')
        if imp_section:
            headers = imp_section.find_all(['h3', 'h4'])
            for header in headers:
                title = self._clean_text(header.get_text())

                # 收集 header 到下一个 header 之间的所有段落、列表、div 等内容
                content_parts = []
                for sib in header.next_siblings:
                    if sib.name in ['h3', 'h4']:
                        break
                    if hasattr(sib, 'get_text'):
                        text = self._clean_text(sib.get_text())
                        if text:
                            content_parts.append(text)

                if content_parts:
                    important_data[title] = "\n".join(content_parts)
        return important_data
