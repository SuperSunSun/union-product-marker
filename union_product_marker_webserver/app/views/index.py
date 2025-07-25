"""
首页视图模块

这个模块定义了应用的主页路由，负责：
1. 显示产品列表
2. 产品数据排序
3. 产品状态展示

主要功能：
- 从数据库获取所有产品信息
- 按产品ID进行排序显示
- 提供产品概览页面

作者: Union Product Marker Team
版本: 1.0.0
"""

from flask import Blueprint, render_template, request
from app.utils.db_util import get_db_connection

# 创建首页蓝图
# 蓝图用于组织相关的路由和视图函数
index_bp = Blueprint('index', __name__)

@index_bp.route('/')
def index():
    """
    首页路由处理函数
    
    显示所有产品的列表页面，包括：
    - 产品基本信息（ID、名称、状态、更新时间）
    - 按产品ID排序显示
    - 产品状态概览
    
    Returns:
        str: 渲染后的HTML页面
    """
    # 获取数据库连接
    conn = get_db_connection()
    
    # 查询所有产品的基本信息
    # 按ID排序，使用COLLATE NOCASE确保大小写不敏感
    cursor = conn.execute("""
        SELECT id, name, status, updated_at FROM products
        ORDER BY id COLLATE NOCASE
    """)
    products = cursor.fetchall()
    conn.close()

    # 按 ID 的数值排序（假设 id 为数字字符串）
    # 如果ID不是纯数字，则将其排在最后
    products.sort(key=lambda x: int(x["id"]) if str(x["id"]).isdigit() else float("inf"))
        
    # 渲染首页模板，传递产品数据
    return render_template('index.html', products=products)
