"""
产品数据模型模块

这个模块定义了Product类，用于管理产品数据的数据库操作。
包括产品的增删改查、数据验证等功能。

主要功能：
1. 创建产品数据表
2. 插入/更新产品数据
3. 查询产品信息
4. 数据格式化和验证

作者: Union Product Marker Team
版本: 1.0.0
"""

import sqlite3
from typing import List, Dict, Optional
import json

class Product:
    """
    产品数据模型类
    
    负责处理产品相关的数据库操作，包括：
    - 产品数据的存储和检索
    - 数据库表结构管理
    - 数据格式化和验证
    """
    
    def __init__(self, db_path: str):
        """
        初始化产品模型
        
        Args:
            db_path (str): 数据库文件路径
        """
        self.db_path = db_path
    
    def create_table(self):
        """
        创建产品数据表
        
        如果表不存在，则创建一个包含以下字段的产品表：
        - id: 主键，自增整数
        - product_id: 产品唯一标识符
        - name: 产品名称
        - category: 产品类别
        - price: 产品价格
        - description: 产品描述
        - images: 产品图片（JSON格式存储）
        - source: 数据来源
        - created_at: 创建时间
        - updated_at: 更新时间
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT UNIQUE NOT NULL,
                name TEXT,
                category TEXT,
                price REAL,
                description TEXT,
                images TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_product(self, product_data: Dict) -> bool:
        """
        插入产品数据
        
        将产品数据插入到数据库中。如果产品ID已存在，则更新现有记录。
        
        Args:
            product_data (Dict): 包含产品信息的字典，必须包含以下字段：
                - product_id: 产品唯一标识符
                - name: 产品名称（可选）
                - category: 产品类别（可选）
                - price: 产品价格（可选）
                - description: 产品描述（可选）
                - images: 产品图片列表（可选）
                - source: 数据来源（可选）
        
        Returns:
            bool: 操作是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 使用INSERT OR REPLACE确保数据唯一性
            cursor.execute('''
                INSERT OR REPLACE INTO products 
                (product_id, name, category, price, description, images, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                product_data.get('product_id'),
                product_data.get('name'),
                product_data.get('category'),
                product_data.get('price'),
                product_data.get('description'),
                json.dumps(product_data.get('images', [])),  # 将图片列表转换为JSON字符串
                product_data.get('source')
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"插入产品数据失败: {e}")
            return False
    
    def get_all_products(self) -> List[Dict]:
        """
        获取所有产品数据
        
        从数据库中检索所有产品记录，按创建时间倒序排列。
        
        Returns:
            List[Dict]: 包含所有产品信息的字典列表，每个字典包含：
                - id: 数据库主键
                - product_id: 产品唯一标识符
                - name: 产品名称
                - category: 产品类别
                - price: 产品价格
                - description: 产品描述
                - images: 产品图片列表（从JSON字符串解析）
                - source: 数据来源
                - created_at: 创建时间
                - updated_at: 更新时间
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM products ORDER BY created_at DESC')
        rows = cursor.fetchall()
        
        products = []
        for row in rows:
            products.append({
                'id': row[0],
                'product_id': row[1],
                'name': row[2],
                'category': row[3],
                'price': row[4],
                'description': row[5],
                'images': json.loads(row[6]) if row[6] else [],  # 解析JSON字符串为列表
                'source': row[7],
                'created_at': row[8],
                'updated_at': row[9]
            })
        
        conn.close()
        return products
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """
        根据产品ID获取产品信息
        
        Args:
            product_id (str): 产品唯一标识符
        
        Returns:
            Optional[Dict]: 产品信息字典，如果未找到则返回None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM products WHERE product_id = ?', (product_id,))
        row = cursor.fetchone()
        
        if row:
            product = {
                'id': row[0],
                'product_id': row[1],
                'name': row[2],
                'category': row[3],
                'price': row[4],
                'description': row[5],
                'images': json.loads(row[6]) if row[6] else [],
                'source': row[7],
                'created_at': row[8],
                'updated_at': row[9]
            }
        else:
            product = None
        
        conn.close()
        return product 