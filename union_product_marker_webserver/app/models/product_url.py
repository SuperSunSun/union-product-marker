"""
产品URL数据模型模块

这个模块定义了ProductUrl类，用于管理产品URL数据的数据库操作。
包括URL的增删改查、状态管理等功能。

主要功能：
1. URL数据的存储和检索
2. URL状态管理（启用/禁用）
3. URL分类和来源管理
4. 数据格式化和验证

作者: Union Product Marker Team
版本: 1.0.0
"""

import sqlite3
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json

class ProductUrl:
    """
    产品URL数据模型类
    
    负责处理产品URL相关的数据库操作，包括：
    - URL数据的存储和检索
    - URL状态和分类管理
    - 数据统计和查询
    """
    
    def __init__(self, db_path: str):
        """
        初始化产品URL模型
        
        Args:
            db_path (str): 数据库文件路径
        """
        self.db_path = db_path
        
        # URL标签选项
        self.URL_TAGS = {
            'single': '单品', 
            'package': '整箱', 
            'subpack': '子箱', 
            'other': '其他'
        }
        
        # 来源选项
        self.SOURCE_OPTIONS = {
            'lazada': 'Lazada',
            'shopee': 'Shopee',
            'amazon': 'Amazon',
            'fairprice': 'FairPrice',
            'other': '其他'
        }
        
        # 状态选项
        self.STATUS_OPTIONS = {
            'active': '启用',
            'inactive': '禁用'
        }
    
    def add_url(self, product_id: str, url: str, url_tag: str, source_name: str, 
                status: str = 'active', collected_at: str = None) -> bool:
        """
        添加产品URL
        
        Args:
            product_id (str): 产品ID
            url (str): URL地址
            url_tag (str): URL标签
            source_name (str): 来源名称
            status (str): 状态，默认为'active'
            collected_at (str): 收集时间，默认为当前时间
            
        Returns:
            bool: 操作是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if collected_at is None:
                collected_at = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO product_urls 
                (product_id, url, url_tag, source_name, status, collected_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (product_id, url, url_tag, source_name, status, collected_at))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"添加URL失败: {e}")
            return False
    
    def get_urls_by_product_id(self, product_id: str) -> List[Dict]:
        """
        根据产品ID获取所有URL
        
        Args:
            product_id (str): 产品ID
            
        Returns:
            List[Dict]: URL信息列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, product_id, url, url_tag, source_name, status, 
                   collected_at, created_at, updated_at
            FROM product_urls 
            WHERE product_id = ?
            ORDER BY created_at DESC
        """, (product_id,))
        
        rows = cursor.fetchall()
        urls = []
        
        for row in rows:
            urls.append({
                'id': row[0],
                'product_id': row[1],
                'url': row[2],
                'url_tag': row[3],
                'url_tag_display': self.URL_TAGS.get(row[3], row[3]),
                'source_name': row[4],
                'source_display': self.SOURCE_OPTIONS.get(row[4], row[4]),
                'status': row[5],
                'status_display': self.STATUS_OPTIONS.get(row[5], row[5]),
                'collected_at': row[6],
                'created_at': row[7],
                'updated_at': row[8]
            })
        
        conn.close()
        return urls
    
    def get_all_products_with_urls(self) -> List[Dict]:
        """
        获取所有产品及其URL统计信息
        
        Returns:
            List[Dict]: 产品信息列表，包含URL统计
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取所有产品信息
        cursor.execute("""
            SELECT p.id, p.name, p.brand,
                   COUNT(pu.id) as url_count,
                   COUNT(CASE WHEN pu.status = 'active' THEN 1 END) as active_url_count,
                   COUNT(CASE WHEN pu.status = 'inactive' THEN 1 END) as inactive_url_count
            FROM products p
            LEFT JOIN product_urls pu ON p.id = pu.product_id
            GROUP BY p.id, p.name, p.brand
            ORDER BY CAST(p.id AS INTEGER)
        """)
        
        rows = cursor.fetchall()
        products = []
        
        for row in rows:
            products.append({
                'id': row[0],
                'name': row[1] or '',
                'brand': row[2] or '',
                'url_count': row[3],
                'active_url_count': row[4],
                'inactive_url_count': row[5]
            })
        
        conn.close()
        return products
    
    def update_url(self, url_id: int, url: str = None, url_tag: str = None, 
                   source_name: str = None, status: str = None) -> bool:
        """
        更新URL信息
        
        Args:
            url_id (int): URL ID
            url (str): URL地址
            url_tag (str): URL标签
            source_name (str): 来源名称
            status (str): 状态
            
        Returns:
            bool: 操作是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 构建更新字段
            updates = []
            values = []
            
            if url is not None:
                updates.append("url = ?")
                values.append(url)
            if url_tag is not None:
                updates.append("url_tag = ?")
                values.append(url_tag)
            if source_name is not None:
                updates.append("source_name = ?")
                values.append(source_name)
            if status is not None:
                updates.append("status = ?")
                values.append(status)
            
            if not updates:
                return True
            
            updates.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            values.append(url_id)
            
            cursor.execute(f"""
                UPDATE product_urls 
                SET {', '.join(updates)}
                WHERE id = ?
            """, values)
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"更新URL失败: {e}")
            return False
    
    def delete_url(self, url_id: int) -> bool:
        """
        删除URL
        
        Args:
            url_id (int): URL ID
            
        Returns:
            bool: 操作是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM product_urls WHERE id = ?", (url_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"删除URL失败: {e}")
            return False
    
    def get_url_statistics(self) -> Dict:
        """
        获取URL统计信息
        
        Returns:
            Dict: 统计信息
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总URL数量
        cursor.execute("SELECT COUNT(*) FROM product_urls")
        total_urls = cursor.fetchone()[0]
        
        # 按状态统计
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM product_urls 
            GROUP BY status
        """)
        status_stats = dict(cursor.fetchall())
        
        # 按来源统计
        cursor.execute("""
            SELECT source_name, COUNT(*) 
            FROM product_urls 
            GROUP BY source_name
        """)
        source_stats = dict(cursor.fetchall())
        
        # 按标签统计
        cursor.execute("""
            SELECT url_tag, COUNT(*) 
            FROM product_urls 
            GROUP BY url_tag
        """)
        tag_stats = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_urls': total_urls,
            'status_stats': status_stats,
            'source_stats': source_stats,
            'tag_stats': tag_stats
        }