"""
产品URL管理视图模块

这个模块处理产品URL管理相关的功能，包括：
1. URL管理列表页面
2. URL的增删改操作
3. URL状态管理
4. 批量操作接口

主要功能：
- 显示所有产品及其URL统计
- 支持展开查看每个产品的URL详情
- 支持inline编辑和删除URL
- 支持为产品添加新URL

作者: Union Product Marker Team
版本: 1.0.0
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from app.utils.db_util import get_db_connection
from app.models.product_url import ProductUrl
import json
from datetime import datetime

# 创建URL管理蓝图，设置URL前缀
url_manage_bp = Blueprint('url_manage', __name__, url_prefix='/url-manage')

def convert_display_to_db_value(display_value, value_dict):
    """
    将显示值转换为数据库存储值
    
    Args:
        display_value: 显示值（中文）
        value_dict: 值映射字典（数据库值->显示值）
        
    Returns:
        str: 数据库存储值，如果找不到对应值则返回原值
    """
    if not display_value:
        return display_value
    
    # 反向查找：从显示值找到数据库值
    for db_value, display in value_dict.items():
        if display == display_value:
            return db_value
    
    # 如果找不到映射，返回原值（支持用户自定义值）
    return display_value

@url_manage_bp.route('/')
def url_manage_list():
    """
    显示URL管理列表页面
    
    展示所有产品及其URL统计信息，支持展开查看详情。
    
    Returns:
        str: 渲染后的URL管理列表页面HTML
    """
    try:
        # 获取数据库路径
        from app.utils.db_util import get_db_path
        db_path = get_db_path()
        
        # 创建URL模型实例
        url_model = ProductUrl(db_path)
        
        # 获取所有产品及URL统计
        products = url_model.get_all_products_with_urls()
        
        # 获取统计信息
        statistics = url_model.get_url_statistics()
        
        # 获取选项数据
        url_tags = url_model.URL_TAGS
        source_options = url_model.SOURCE_OPTIONS
        status_options = url_model.STATUS_OPTIONS
        
        return render_template('url_manage_list.html', 
                             products=products,
                             statistics=statistics,
                             url_tags=url_tags,
                             source_options=source_options,
                             status_options=status_options)
    
    except Exception as e:
        current_app.logger.error(f"URL管理列表页面错误: {e}")
        return render_template('url_manage_list.html', 
                             products=[],
                             statistics={},
                             url_tags={},
                             source_options={},
                             status_options={},
                             error=str(e))

@url_manage_bp.route('/api/product/<product_id>/urls')
def get_product_urls(product_id):
    """
    获取指定产品的所有URL
    
    Args:
        product_id (str): 产品ID
        
    Returns:
        JSON: URL列表数据
    """
    try:
        from app.utils.db_util import get_db_path
        db_path = get_db_path()
        url_model = ProductUrl(db_path)
        
        urls = url_model.get_urls_by_product_id(product_id)
        
        return jsonify({
            'success': True,
            'data': urls
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取URL列表失败: {str(e)}'
        })

@url_manage_bp.route('/api/url/add', methods=['POST'])
def add_url():
    """
    添加新URL
    
    接收POST请求，添加新的产品URL。
    
    Returns:
        JSON: 操作结果
    """
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['product_id', 'url', 'source_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'缺少必需字段: {field}'
                })
        
        from app.utils.db_util import get_db_path
        db_path = get_db_path()
        url_model = ProductUrl(db_path)
        
        # 转换显示值为数据库值
        url_tag_db = convert_display_to_db_value(data['url_tag'], url_model.URL_TAGS)
        source_name_db = convert_display_to_db_value(data['source_name'], url_model.SOURCE_OPTIONS)
        
        # 添加URL
        success = url_model.add_url(
            product_id=data['product_id'],
            url=data['url'],
            url_tag=url_tag_db,
            source_name=source_name_db,
            status=data.get('status', 'active'),
            collected_at=data.get('collected_at')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'URL添加成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'URL添加失败'
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'添加URL时发生错误: {str(e)}'
        })

@url_manage_bp.route('/api/url/<int:url_id>/update', methods=['PUT'])
def update_url(url_id):
    """
    更新URL信息
    
    Args:
        url_id (int): URL ID
        
    Returns:
        JSON: 操作结果
    """
    try:
        data = request.get_json()
        
        from app.utils.db_util import get_db_path
        db_path = get_db_path()
        url_model = ProductUrl(db_path)
        
        # 转换显示值为数据库值
        url_tag_db = convert_display_to_db_value(data.get('url_tag'), url_model.URL_TAGS) if data.get('url_tag') else None
        source_name_db = convert_display_to_db_value(data.get('source_name'), url_model.SOURCE_OPTIONS) if data.get('source_name') else None
        
        # 更新URL
        success = url_model.update_url(
            url_id=url_id,
            url=data.get('url'),
            url_tag=url_tag_db,
            source_name=source_name_db,
            status=data.get('status')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'URL更新成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'URL更新失败'
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新URL时发生错误: {str(e)}'
        })

@url_manage_bp.route('/api/url/<int:url_id>/delete', methods=['DELETE'])
def delete_url(url_id):
    """
    删除URL
    
    Args:
        url_id (int): URL ID
        
    Returns:
        JSON: 操作结果
    """
    try:
        from app.utils.db_util import get_db_path
        db_path = get_db_path()
        url_model = ProductUrl(db_path)
        
        success = url_model.delete_url(url_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'URL删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'URL删除失败'
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除URL时发生错误: {str(e)}'
        })

@url_manage_bp.route('/api/url/<int:url_id>/toggle-status', methods=['POST'])
def toggle_url_status(url_id):
    """
    切换URL状态（启用/禁用）
    
    Args:
        url_id (int): URL ID
        
    Returns:
        JSON: 操作结果
    """
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['active', 'inactive']:
            return jsonify({
                'success': False,
                'message': '无效的状态值'
            })
        
        from app.utils.db_util import get_db_path
        db_path = get_db_path()
        url_model = ProductUrl(db_path)
        
        success = url_model.update_url(url_id=url_id, status=new_status)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'URL状态已切换为{"启用" if new_status == "active" else "禁用"}'
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'URL状态切换失败'
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'切换URL状态时发生错误: {str(e)}'
        })

@url_manage_bp.route('/api/statistics')
def get_statistics():
    """
    获取URL统计信息
    
    Returns:
        JSON: 统计数据
    """
    try:
        from app.utils.db_util import get_db_path
        db_path = get_db_path()
        url_model = ProductUrl(db_path)
        
        statistics = url_model.get_url_statistics()
        
        return jsonify({
            'success': True,
            'data': statistics
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取统计信息失败: {str(e)}'
        })