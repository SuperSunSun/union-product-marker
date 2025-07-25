from typing import Dict, List, Optional
import os
import re
from bs4 import BeautifulSoup
import json5 as json
from loguru import logger

from .base import BaseScraper
from ..models.product_data import ProductData

class FairpriceScraper(BaseScraper):
    def __init__(self, site_name: str, config: dict):
        super().__init__(site_name, config)

    def _simplify_image_url(self, url: str) -> str:
        """
        简化图片链接：将最后一个下划线之后的部分（含扩展名）去除
        
        参数：
            url (str): 原始图片URL
            
        返回：
            str: 简化后的图片URL
            
        示例：
            输入: https://.../10020187_RXL1_20250513.jpg
            输出: https://.../10020187_RXL1.jpg
        """
        if not url:
            return url
        url = url.split('?')[0]  # 去掉查询参数
        parts = url.rsplit('/', 1)
        if len(parts) == 2:
            filename = parts[1]
            simplified_filename = re.sub(r'_(?!.*_).*?(\.\w+)$', r'\1', filename)
            return parts[0] + '/' + simplified_filename
        return url

    def parse_product_data(self, html: str, product_id: str, url: str) -> ProductData:
        """解析 Fairprice 页面数据"""
        soup = BeautifulSoup(html, 'html.parser')
        json_ld = self._extract_json_ld(soup)
        
        # 如果没有获取到 JSON-LD 数据，返回空的 ProductData
        if not json_ld:
            logger.warning("No JSON-LD data found, return empty ProductData")
            return ProductData.create_empty(product_id, url)
        
        # 有数据时正常解析
        meta = self._parse_meta(soup)
        
        # 解析所有数据
        title = json_ld['name'] or self._parse_title(soup)
        brand = json_ld['brand']['name'] or self._parse_brand(soup)
        original_urls = self._parse_image_urls(soup)
        simplified_urls = [self._simplify_image_url(url) for url in original_urls]
        
        # 其他信息放入 infos
        infos = {
            "meta": meta,
            "script": json_ld,
            "description": self._parse_product_blocks(soup)
        }
        
        # 返回 ProductData 对象
        return ProductData(
            id=product_id,
            url=url,
            product_name=title or "",
            brand=brand or "",
            price_current=json_ld['offers']['price'] or meta.get("price", ""),
            price_original=meta.get("original_price", ""),
            image_urls_original=original_urls,
            image_urls_simplified=simplified_urls,
            infos=infos
        )

    def _parse_title(self, soup: BeautifulSoup) -> Optional[str]:
        """解析商品标题"""
        # 尝试从页面元素中获取标题
        title_elem = soup.find('h1', class_='product-name')
        if title_elem:
            return self._clean_text(title_elem.text)
            
        # 尝试从 meta 标签获取
        meta_title = soup.find('meta', property='og:title')
        if meta_title:
            return self._clean_text(meta_title.get('content', ''))
            
        return None

    def _parse_brand(self, soup: BeautifulSoup) -> Optional[str]:
        """解析品牌信息"""
        # 尝试从页面元素中获取品牌
        brand_elem = soup.find('span', string=re.compile(r'Brand:', re.I))
        if brand_elem:
            brand_link = brand_elem.find_next('a')
            if brand_link:
                return self._clean_text(brand_link.text.replace('Brand:', ''))
                
        return None


    def _parse_image_urls(self, soup: BeautifulSoup) -> List[str]:
        """解析图片URL列表"""
        image_urls = []
        
        # 尝试从 JSON-LD 中获取图片
        json_ld = self._extract_json_ld(soup)
        if json_ld and 'image' in json_ld:
            if isinstance(json_ld['image'], list):
                image_urls.extend(json_ld['image'])
            elif isinstance(json_ld['image'], str):
                image_urls.append(json_ld['image'])
        
        # 如果 JSON-LD 中没有图片，尝试从页面元素中获取
        if not image_urls:
            # 尝试从商品图片区域获取
            image_container = soup.find('div', class_='product-image-container')
            if image_container:
                for img in image_container.find_all('img'):
                    if 'src' in img.attrs:
                        image_urls.append(img['src'])
            
            # 尝试从缩略图区域获取
            thumbnail_container = soup.find('div', class_='thumbnail-container')
            if thumbnail_container:
                for img in thumbnail_container.find_all('img'):
                    if 'src' in img.attrs:
                        image_urls.append(img['src'])
        
        # 确保返回的是唯一的URL列表
        return list(dict.fromkeys(image_urls))

    def _clean_text(self, text: str) -> str:
        """清理文本内容"""
        if not text:
            return ""
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        # 替换特殊字符
        text = text.replace('\xa0', ' ')
        return text

    def _extract_json_ld(self, soup: BeautifulSoup) -> dict:
        """
        提取页面中的 JSON-LD 结构化数据
        
        参数：
            soup (BeautifulSoup): 页面的 BeautifulSoup 对象
            
        返回：
            dict: 解析后的 JSON-LD 数据，如果解析失败则返回空字典
            
        说明：
            1. 查找并提取 application/ld+json 类型的脚本内容
            2. 使用 json 进行解析
            3. 处理缩进和换行问题
            4. 移除最后一个右花括号（FairPrice 页面特殊处理）
        """
        script_tag = soup.find("script", {"type": "application/ld+json", "data-next-head": True})

        if script_tag:
            try:
                # 获取原始 JSON 文本
                raw_text = script_tag.string or script_tag.get_text()
                # 移除缩进和换行
                raw_text = ' '.join(line.strip() for line in raw_text.splitlines())
                # 移除最后一个右花括号
                if raw_text.rstrip().endswith('}'):
                    raw_text = raw_text.rstrip()[:-1]
                # 使用 json 解析
                return json.loads(raw_text)
            except Exception as e:
                print(f"JSON-LD 解析失败: {e}")
                print(f"原始文本: {raw_text}")
                return {}
        return {}

    def _parse_meta(self, soup: BeautifulSoup) -> dict:
        """
        解析商品元数据信息
        
        参数：
            soup (BeautifulSoup): 页面的 BeautifulSoup 对象
            
        返回：
            dict: 包含以下字段的元数据字典：
                - product_name: 商品名称
                - brand: 品牌名称
                - size_quantity: 规格信息
                - price: 当前价格
                - original_price: 原价
                
        说明：
            从页面的 tagWrapper 区域提取商品的基本信息，包括：
            1. 价格信息（当前价格和原价）
            2. 商品名称
            3. 规格信息
            4. 品牌信息
        """
        product_name = brand = price = original_price = size_quantity = ""
        tag_wrapper = soup.find(class_="tagWrapper")
        
        if tag_wrapper:
            target_div = tag_wrapper.find_next_sibling("div")
            if target_div:
                # 当前价格
                price_elem = target_div.find("span", attrs={"weight": "black"})
                if price_elem:
                    price = price_elem.text.strip()
                
                    # 找当前价的父 <span>，然后找它的下一个兄弟 <div>
                    parent_span = price_elem.find_parent("span")
                    if parent_span:
                        next_div = parent_span.find_next_sibling("div")
                        if next_div:
                            text = next_div.get_text(strip=True)
                            if text.startswith("$"):
                                original_price = text

                # 产品名
                name_elem = target_div.find("span", attrs={"weight": "regular"})
                if name_elem:
                    product_name = name_elem.text.strip().replace('\xa0', ' ')
                
                # 规格
                quantity_elem = target_div.find("span", class_="quantity")
                if quantity_elem:
                    size_quantity = quantity_elem.text.strip()
                
                # 品牌
                brand_elem = target_div.find("span", string="Brand:")
                if brand_elem:
                    brand_link = brand_elem.find_next("a")
                    if brand_link:
                        brand = brand_link.text.strip().replace("Brand: ", "")

        return {
            "product_name": product_name,
            "brand": brand,
            "size_quantity": size_quantity,
            "price": price,
            "original_price": original_price
        }

    def _parse_product_blocks(self, soup: BeautifulSoup) -> dict:
        """
        解析商品详情区域内容
        
        参数：
            soup (BeautifulSoup): 页面的 BeautifulSoup 对象
            
        返回：
            dict: 包含各个详情块内容的字典，其中：
                - PRODUCT DETAILS / NUTRITIONAL DATA: 以字典形式存储
                - 其他块: 以多行文本形式存储（如 INGREDIENTS）
                
        说明：
            1. 查找 productDescription 区域
            2. 遍历所有 productComplextAttribute 块
            3. 根据块的类型选择不同的解析方式：
               - 详情/营养信息：解析为字典
               - 列表内容：转换为多行文本
               - 普通段落：保留为纯文本
        """
        blocks = {}

        def extract_ul_dict(ul_tag: BeautifulSoup) -> dict:
            """
            将 <ul> 中的 <li> 项目提取为字典
            
            参数：
                ul_tag (BeautifulSoup): 包含列表项的 ul 标签
                
            返回：
                dict: 键值对形式的列表内容
            """
            result = {}
            for li in ul_tag.find_all("li"):
                spans = li.find_all("span")
                if len(spans) >= 2:
                    key = spans[0].get_text(strip=True)
                    value = spans[1].get_text(strip=True)
                    result[key] = value
            return result

        desc_container = soup.find("div", attrs={"data-testid": "productDescription"})
        if not desc_container:
            return blocks

        sections = desc_container.find_all("div", attrs={"data-testid": "productComplextAttribute"})

        for section in sections:
            # 标题
            title_elem = section.find("h2")
            if not title_elem:
                continue

            title_text = title_elem.get_text(strip=True)

            # 内容容器（可能是 <div> 或 <ul>）
            content_elem = title_elem.find_next_sibling()
            while content_elem and content_elem.name not in ["div", "ul"]:
                content_elem = content_elem.find_next_sibling()

            if not content_elem:
                continue

            # dict 类型处理
            if title_text in ["PRODUCT DETAILS", "NUTRITIONAL DATA"] and content_elem.name == "ul":
                blocks[title_text] = extract_ul_dict(content_elem)
            # <ul> 列表转多段文本（保留换行）
            elif content_elem.name == "ul":
                lines = [li.get_text(strip=True) for li in content_elem.find_all("li")]
                blocks[title_text] = "\n".join(lines)
            # 普通段落 <div> 转纯文本
            else:
                blocks[title_text] = content_elem.get_text(strip=True)

        return blocks
    

