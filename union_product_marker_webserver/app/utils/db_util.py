"""
数据库工具模块

这个模块提供了数据库操作的工具函数，包括：
1. 数据库连接管理
2. 数据库初始化
3. 目录结构创建
4. 数据库路径配置

主要功能：
- 统一的数据库连接接口
- 自动创建必要的数据库表
- 确保项目目录结构完整

作者: Union Product Marker Team
版本: 1.0.0
"""

import os
import sqlite3

# 获取当前项目的根目录
# 通过相对路径计算，确保在不同环境下都能正确找到项目根目录
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

# 数据库文件路径
# 数据库文件存储在data目录下，文件名为database.db
DB_PATH = os.path.join(BASE_DIR, "data", "database.db")

# 项目中所需的文件夹列表
# 这些文件夹用于存储不同类型的数据
REQUIRED_DIRS = ['uploads', 'exports', 'media']

def get_db_path():
    """
    获取数据库文件路径
    
    Returns:
        str: 数据库文件的绝对路径
    """
    return DB_PATH

def get_db_connection():
    """
    获取数据库连接
    
    创建一个SQLite数据库连接，并配置行工厂为sqlite3.Row，
    这样查询结果可以通过列名访问。
    
    Returns:
        sqlite3.Connection: 配置好的数据库连接对象
    """
    print("🔍 当前使用的数据库路径为：", DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    # 设置行工厂，使查询结果可以通过列名访问
    conn.row_factory = sqlite3.Row
    return conn

def ensure_directories():
    """
    确保必要的目录存在
    
    创建项目中需要的所有目录，如果目录已存在则不会报错。
    这些目录用于存储上传的文件、导出的数据等。
    """
    for sub in REQUIRED_DIRS:
        path = os.path.join(BASE_DIR, sub)
        os.makedirs(path, exist_ok=True)

def init_db():
    """
    初始化数据库
    
    这个函数负责：
    1. 创建必要的目录结构
    2. 创建数据库表（如果不存在）
    3. 确保数据库结构完整
    
    数据库表结构：
    - products: 产品信息表
    - sources: 爬虫数据源表
    - images: 图片信息表
    """
    # 首先确保所有必要的目录都存在
    ensure_directories()

    # 获取数据库连接
    conn = get_db_connection()
    cursor = conn.cursor()

    # 创建产品表
    # 存储产品的基本信息，包括标注数据
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,                    -- 产品ID（主键）
            name TEXT,                              -- 产品名称
            brand TEXT,                             -- 品牌
            price_orig REAL,                        -- 原始价格
            price_curr REAL,                        -- 当前价格
            description TEXT,                       -- 产品描述
            meta_info TEXT,                         -- 元信息（JSON格式）
            specs TEXT,                             -- 规格信息（JSON格式）
            extra_sections TEXT,                    -- 额外信息（JSON格式）
            status TEXT,                            -- 状态
            completeness INTEGER,                   -- 完整度评分
            annotation_data TEXT,                   -- 标注数据（JSON格式）
            created_at TEXT,                        -- 创建时间
            updated_at TEXT                         -- 更新时间
        )
    """)

    # 创建数据源表
    # 存储来自不同爬虫的数据源信息
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,   -- 自增主键
            product_id TEXT,                        -- 产品ID（外键）
            source_name TEXT,                       -- 数据源名称
            raw_json TEXT,                          -- 原始JSON数据
            uploaded_at TEXT                        -- 上传时间
        )
    """)

    # 创建图片表
    # 存储产品相关的图片信息
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,   -- 自增主键
            product_id TEXT,                        -- 产品ID（外键）
            url TEXT,                               -- 图片URL
            local_path TEXT,                        -- 本地存储路径
            source TEXT                             -- 图片来源
        )
    """)

    # 创建产品URL管理表
    # 存储每个产品的URL信息，支持多种URL类型和来源
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,   -- 自增主键
            product_id TEXT NOT NULL,               -- 产品ID（外键）
            url TEXT NOT NULL,                      -- URL地址
            url_tag TEXT,                           -- URL标签（single/package/subpack/other），可选  
            source_name TEXT NOT NULL,              -- 来源（lazada/shopee/amazon/fairprice/other）
            status TEXT DEFAULT 'active',           -- 状态（active/inactive）
            collected_at TEXT DEFAULT CURRENT_TIMESTAMP,  -- 收集时间
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,    -- 创建时间
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,    -- 更新时间
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # 检查是否需要添加 annotation_data 字段
    # 这是一个向后兼容的检查，确保旧版本的数据库也能正常工作
    cursor.execute("PRAGMA table_info(products)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'annotation_data' not in columns:
        cursor.execute("ALTER TABLE products ADD COLUMN annotation_data TEXT")
        print("✅ 已添加 annotation_data 字段到 products 表")

    # 检查是否需要添加 notes 字段（人工备注）
    if 'notes' not in columns:
        cursor.execute("ALTER TABLE products ADD COLUMN notes TEXT")
        print("✅ 已添加 notes 字段到 products 表")

    # 检查是否需要添加 auto_notes 字段（自动备注）
    if 'auto_notes' not in columns:
        cursor.execute("ALTER TABLE products ADD COLUMN auto_notes TEXT")
        print("✅ 已添加 auto_notes 字段到 products 表")

    # 提交更改并关闭连接
    conn.commit()
    conn.close()
