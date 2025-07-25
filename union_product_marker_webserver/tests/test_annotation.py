#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
产品标注功能测试模块

这个模块用于测试产品标注功能，包括：
1. 创建测试产品数据
2. 添加模拟爬虫数据源
3. 验证标注页面功能
4. 提供测试环境准备

主要功能：
- 在数据库中插入测试产品
- 添加多个来源的爬虫数据
- 模拟真实的产品标注场景
- 为标注功能测试提供数据基础

测试数据包括：
- 两个测试产品（蜂蜜柠檬茶、绿茶）
- 多个数据源（Amazon、FairPrice）
- 完整的图片和描述信息

作者: Union Product Marker Team
版本: 1.0.0
"""

import sqlite3
import json
from datetime import datetime
import os

# 获取项目根目录
# 确保在不同环境下都能正确找到数据库文件
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
DB_PATH = os.path.join(BASE_DIR, "data", "database.db")

def add_test_data():
    """
    添加测试数据
    
    这个函数在数据库中创建测试产品数据和爬虫数据源，
    用于测试产品标注功能。包括：
    - 在products表中插入测试产品
    - 在sources表中插入模拟的爬虫数据
    - 提供完整的测试环境
    
    测试数据特点：
    - 包含多个产品类型
    - 多个数据源（Amazon、FairPrice）
    - 完整的图片URL和描述信息
    - 真实的价格和品牌信息
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 添加测试产品
    # 这些产品将用于测试标注功能
    test_products = [
        {
            'id': 'TEST001',
            'name': '测试产品1 - 蜂蜜柠檬茶',
            'brand': 'TestBrand',
            'price_orig': 15.99,
            'price_curr': 12.99,
            'description': '这是一个测试产品',
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        },
        {
            'id': 'TEST002',
            'name': '测试产品2 - 绿茶',
            'brand': 'TestBrand',
            'price_orig': 18.50,
            'price_curr': 16.81,
            'description': '另一个测试产品',
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    ]
    
    # 插入测试产品到数据库
    for product in test_products:
        cursor.execute("""
            INSERT OR REPLACE INTO products 
            (id, name, brand, price_orig, price_curr, description, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product['id'], product['name'], product['brand'], 
            product['price_orig'], product['price_curr'], product['description'],
            product['status'], product['created_at'], product['updated_at']
        ))
    
    # 添加测试爬虫数据
    # 模拟来自不同来源的爬虫数据，用于测试标注功能
    test_sources = [
        {
            'product_id': 'TEST001',
            'source_name': 'amazon',
            'raw_json': json.dumps({
                'title': 'Amazon 蜂蜜柠檬茶 24罐装',
                'brand': 'TestBrand',
                'price': 16.81,
                'images': [
                    'https://via.placeholder.com/300x300/FF6B6B/FFFFFF?text=Amazon+Main',
                    'https://via.placeholder.com/300x300/4ECDC4/FFFFFF?text=Amazon+Front',
                    'https://via.placeholder.com/300x300/45B7D1/FFFFFF?text=Amazon+Back'
                ],
                'description': '来自Amazon的优质蜂蜜柠檬茶，24罐装，口感清爽，营养丰富。'
            }),
            'uploaded_at': datetime.now().isoformat()
        },
        {
            'product_id': 'TEST001',
            'source_name': 'fairprice',
            'raw_json': json.dumps({
                'title': 'FairPrice 蜂蜜柠檬茶 24罐',
                'brand': 'TestBrand',
                'price': 15.99,
                'images': [
                    'https://via.placeholder.com/300x300/96CEB4/FFFFFF?text=FairPrice+Main',
                    'https://via.placeholder.com/300x300/FFEAA7/FFFFFF?text=FairPrice+Box'
                ],
                'description': 'FairPrice精选蜂蜜柠檬茶，24罐装，价格实惠，品质保证。'
            }),
            'uploaded_at': datetime.now().isoformat()
        },
        {
            'product_id': 'TEST002',
            'source_name': 'amazon',
            'raw_json': json.dumps({
                'title': 'Amazon 绿茶 24罐装',
                'brand': 'TestBrand',
                'price': 18.50,
                'images': [
                    'https://via.placeholder.com/300x300/55A3FF/FFFFFF?text=Amazon+Green+Tea',
                    'https://via.placeholder.com/300x300/FFB347/FFFFFF?text=Amazon+Green+Tea+Box'
                ],
                'description': 'Amazon优质绿茶，24罐装，清香怡人，健康饮品。'
            }),
            'uploaded_at': datetime.now().isoformat()
        }
    ]
    
    # 插入测试爬虫数据到数据库
    for source in test_sources:
        cursor.execute("""
            INSERT OR REPLACE INTO sources 
            (product_id, source_name, raw_json, uploaded_at)
            VALUES (?, ?, ?, ?)
        """, (
            source['product_id'], source['source_name'], 
            source['raw_json'], source['uploaded_at']
        ))
    
    # 提交事务并关闭连接
    conn.commit()
    conn.close()
    
    # 输出测试结果
    print("✅ 测试数据添加成功！")
    print("📝 添加了以下测试产品：")
    for product in test_products:
        print(f"   - {product['id']}: {product['name']}")
    print("\n🌐 现在可以访问 http://localhost:5000/annotation 查看标注页面")

if __name__ == "__main__":
    # 当直接运行此文件时添加测试数据
    add_test_data() 