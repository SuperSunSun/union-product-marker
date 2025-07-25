"""
静态文件服务视图模块

这个模块提供静态文件（主要是图片）的服务功能，包括：
1. 本地图片文件访问
2. 多级路径支持
3. 错误处理和404响应

主要功能：
- 为爬虫下载的图片提供HTTP访问服务
- 支持嵌套目录结构的图片访问
- 安全的文件访问控制

作者: Union Product Marker Team
版本: 1.0.0
"""

import os
from flask import Blueprint, send_from_directory, request, abort
from app.utils.db_util import BASE_DIR

# 创建静态图片服务蓝图
static_images_bp = Blueprint("static_images", __name__)

@static_images_bp.route("/images/<path:filename>")
def serve_image(filename):
    """
    提供本地图片文件服务，支持多级路径
    
    这个路由用于访问爬虫下载的图片文件。图片文件存储在
    union_scraper/output目录下，通过HTTP请求可以访问这些图片。
    
    Args:
        filename (str): 图片文件名，支持包含路径的文件名
        
    Returns:
        Response: 图片文件内容，如果文件不存在则返回404
        
    Raises:
        404: 当请求的图片文件不存在时
    """
    try:
        # 构建图片目录路径
        # 图片存储在union_scraper/output目录下
        image_dir = os.path.join(BASE_DIR, "..", "union_scraper", "output")
        file_path = os.path.join(image_dir, filename)
        
        # 检查文件是否存在
        if os.path.exists(file_path):
            # 使用Flask的send_from_directory安全地发送文件
            # 这可以防止路径遍历攻击
            return send_from_directory(image_dir, filename)
        
        # 文件不存在，返回404错误
        abort(404)
        
    except Exception as e:
        # 记录错误日志并返回404
        print(f"图片服务错误: {e}")
        abort(404) 