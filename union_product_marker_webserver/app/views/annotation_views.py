"""
产品标注视图模块

这个模块处理产品标注相关的功能，包括：
1. 产品标注列表显示
2. 单个产品标注详情页
3. 标注数据保存
4. 标注状态管理

主要功能：
- 显示待标注和已标注的产品列表
- 提供产品标注界面，支持统一名称、品牌、价格等标注
- 保存标注数据到数据库
- 支持标注数据的JSON格式存储

作者: Union Product Marker Team
版本: 1.0.0
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from app.utils.db_util import get_db_connection
from app.models.auto_checker import auto_checker
import json

# 创建产品标注蓝图，设置URL前缀
annotation_bp = Blueprint('annotation', __name__, url_prefix='/annotation')

@annotation_bp.route('/')
def annotation_list():
    """
    显示待标注商品列表。
    
    从数据库获取所有产品信息，解析标注数据，显示产品列表。
    包括标注状态、产品信息、价格等。
    支持分页和每页显示数量选择。
    
    Returns:
        str: 渲染后的产品列表页面HTML
    """
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=str)
    status_filter = request.args.get('status', 'all')  # 状态筛选参数
    notes_filter = request.args.get('notes', 'all')  # 备注筛选参数
    search_keyword = request.args.get('search', '').strip()  # 搜索关键词
    
    # 处理"显示全部"选项
    if per_page == 'all':
        per_page = None
    else:
        per_page = int(per_page)
        # 限制每页显示数量范围
        if per_page < 10:
            per_page = 10
        elif per_page > 200:
            per_page = 200
    
    db = get_db_connection()
    
    # 构建WHERE条件
    where_conditions = []
    where_params = []
    
    # 状态筛选
    if status_filter == 'annotated':
        where_conditions.append("annotation_data IS NOT NULL AND annotation_data != ''")
    elif status_filter == 'pending':
        where_conditions.append("(annotation_data IS NULL OR annotation_data = '')")
    
    # 备注筛选
    if notes_filter == 'has_notes':
        where_conditions.append("(notes IS NOT NULL AND notes != '' OR auto_notes IS NOT NULL AND auto_notes != '')")
    elif notes_filter == 'no_notes':
        where_conditions.append("(notes IS NULL OR notes = '') AND (auto_notes IS NULL OR auto_notes = '')")
    elif notes_filter == 'has_manual_notes':
        where_conditions.append("notes IS NOT NULL AND notes != ''")
    elif notes_filter == 'has_auto_notes':
        where_conditions.append("auto_notes IS NOT NULL AND auto_notes != ''")
    
    # 搜索筛选（全局搜索）
    if search_keyword:
        search_condition = """(
            id LIKE ? OR 
            name LIKE ? OR 
            brand LIKE ? OR
            notes LIKE ? OR
            auto_notes LIKE ?
        )"""
        where_conditions.append(search_condition)
        search_param = f"%{search_keyword}%"
        where_params.extend([search_param] * 5)
    
    where_clause = ""
    if where_conditions:
        where_clause = "WHERE " + " AND ".join(where_conditions)
    
    # 获取总记录数
    count_query = f"SELECT COUNT(*) FROM products {where_clause}"
    total_count = db.execute(count_query, where_params).fetchone()[0]
    
    # 计算分页信息
    if per_page is None:
        # 显示全部
        total_pages = 1
        page = 1
        offset = 0
        limit_clause = ""
        limit_params = []
    else:
        total_pages = (total_count + per_page - 1) // per_page
        if page < 1:
            page = 1
        elif page > total_pages and total_pages > 0:
            page = total_pages
        
        offset = (page - 1) * per_page
        limit_clause = "LIMIT ? OFFSET ?"
        limit_params = [per_page, offset]
    
    # 查询分页数据
    query = f"""SELECT id, name, brand, price_orig, price_curr, annotation_data, notes, auto_notes, updated_at 
               FROM products {where_clause} ORDER BY CAST(id AS INTEGER) ASC {limit_clause}"""
    all_params = where_params + limit_params
    products = db.execute(query, all_params).fetchall()
    db.close()
    
    # 处理状态和图片数据
    product_list = []
    for row in products:
        # 解析标注数据获取统一名称和图片信息
        unified_name = ''
        base_name = ''
        images = {}
        image_local_paths = {}
        
        if row['annotation_data']:
            try:
                annotation_data = json.loads(row['annotation_data'])
                unified_name = annotation_data.get('unified_name', '')
                images = annotation_data.get('images', {})
                image_local_paths = annotation_data.get('image_local_paths', {})
            except (json.JSONDecodeError, TypeError):
                # 如果JSON解析失败，保持默认值
                pass
        
        # 如果没有统一名称，使用原始名称作为基础名称
        if not unified_name:
            base_name = row['name'] or ''
        else:
            base_name = row['name'] or ''
        
        # 根据是否有标注数据判断状态
        status = 'annotated' if row['annotation_data'] else 'pending'
        
        # 获取品牌和价格信息
        brand = annotation_data.get('brand', '') if row['annotation_data'] else row['brand'] or ''
        price_listed = annotation_data.get('price_listed', None) if row['annotation_data'] else None
        price_cost = annotation_data.get('price_cost', None) if row['annotation_data'] else None

        # 处理价格显示逻辑
        # 优先显示标注的价格，其次显示数据库中的价格
        if price_listed:
            price_display = f"${price_listed:.2f}"
        elif price_cost:
            price_display = f"${price_cost:.2f}"
        elif row['price_curr']:
            price_display = f"${row['price_curr']:.2f}"
        elif row['price_orig']:
            price_display = f"${row['price_orig']:.2f}"
        else:
            price_display = ''
        
        # 构建产品信息字典
        product_list.append({
            'id': row['id'],
            'name': row['name'],
            'unified_name': unified_name,
            'base_name': base_name,
            'brand': brand,
            'price': price_display,
            'price_listed': price_listed,
            'price_cost': price_cost,
            'images': images,
            'image_local_paths': image_local_paths,
            'status': status,
            'updated_at': row['updated_at'],
            'notes': row['notes'] or '',
            'auto_notes': row['auto_notes'] or ''
        })
    
    # 分页信息
    pagination = {
        'page': page,
        'per_page': per_page,
        'total_count': total_count,
        'total_pages': total_pages,
        'has_prev': page > 1 and per_page is not None,
        'has_next': page < total_pages and per_page is not None,
        'prev_page': page - 1 if page > 1 and per_page is not None else None,
        'next_page': page + 1 if page < total_pages and per_page is not None else None,
        'status_filter': status_filter,
        'notes_filter': notes_filter,
        'search_keyword': search_keyword
    }
    
    return render_template('annotation_list.html', products=product_list, pagination=pagination)

@annotation_bp.route('/<product_id>')
def annotation_detail(product_id):
    """
    显示单个商品的标注详情页。
    
    左侧是标注表单，右侧是该商品的所有爬虫数据源。
    用户可以查看和编辑产品的标注信息。
    
    Args:
        product_id (str): 产品ID
        
    Returns:
        str: 渲染后的产品标注详情页面HTML
    """
    db = get_db_connection()
    
    # 获取产品基本信息
    product = db.execute(
        'SELECT * FROM products WHERE id = ?', (product_id,)
    ).fetchone()

    # 获取已保存的标注数据
    saved_annotation = {}
    if product and product['annotation_data']:
        try:
            saved_annotation = json.loads(product['annotation_data'])
        except (json.JSONDecodeError, TypeError):
            # 如果解析失败，保持为空字典
            saved_annotation = {}
            
    # 为模板提供一个安全的、包含默认结构的字典
    # 这样即使没有已保存的标注，模板也不会出错
    default_structure = {
        'unified_name': '',
        'brand': '',
        'price_listed': None,
        'price_cost': None,
        'images': {
            'main': '',
            'front': '',
            'back': '',
            'box': '',
            'extra': ''
        },
        'image_local_paths': {
            'main': '',
            'front': '',
            'back': '',
            'box': '',
            'extra': ''
        }
    }
    
    # 使用已保存的数据（如果存在且有效）来更新默认结构
    if isinstance(saved_annotation, dict):
        # 递归更新，以确保内部的字典也被正确合并
        for key, value in default_structure.items():
            if key in saved_annotation:
                if isinstance(value, dict) and isinstance(saved_annotation[key], dict):
                    value.update(saved_annotation[key])
                else:
                    default_structure[key] = saved_annotation[key]
    
    saved_annotation = default_structure

    # 获取与此产品ID相关的所有爬虫数据，使用正确的表名和列名
    current_app.logger.info(f"Fetching crawler data for product_id: {product_id}")
    crawler_data_rows = db.execute(
        'SELECT id, source_name, raw_json FROM sources WHERE product_id = ?', (product_id,)
    ).fetchall()
    current_app.logger.info(f"Found {len(crawler_data_rows)} rows of crawler data.")
    db.close()

    # 准备给JS用的数据结构
    crawler_data_for_js = {
        'products': {},
        'sources': []
    }
    for row in crawler_data_rows:
        source_name = row['source_name'] # 使用正确的列名
        if source_name not in crawler_data_for_js['products']:
            crawler_data_for_js['products'][source_name] = []
            crawler_data_for_js['sources'].append({'id': source_name, 'name': source_name})
        
        try:
            # 使用正确的列名
            data_dict = json.loads(row['raw_json'])
            crawler_data_for_js['products'][source_name].append(data_dict)
        except (json.JSONDecodeError, TypeError):
            # 如果解析失败，可以跳过或记录日志
            current_app.logger.error(f"Failed to parse crawler_data id {row['id']}")
            continue

    return render_template('annotation_detail.html',
                           product=product,
                           crawler_data=crawler_data_for_js,
                           saved_annotation=saved_annotation,
                           notes=product['notes'] if product and product['notes'] else '',
                           auto_notes=product['auto_notes'] if product and product['auto_notes'] else '')


@annotation_bp.route('/save/<product_id>', methods=['POST'])
def save_annotation(product_id):
    """
    接收前端发送的标注数据，并将其以JSON格式存入数据库。
    
    这个接口接收前端发送的标注数据，验证数据格式，
    然后保存到数据库的annotation_data字段中。
    支持保存前自动检查功能。
    
    Args:
        product_id (str): 产品ID
        
    Returns:
        JSON: 保存结果
            {
                "success": true/false,
                "message": "操作结果消息",
                "next_product_id": "下一个产品ID（如果存在）",
                "auto_notes": "自动检查结果（如果执行了检查）"
            }
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided.'}), 400

    try:
        # 验证数据结构
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'Invalid data format.'}), 400
        
        # 提取备注字段和自动检查标志，从JSON数据中分离出来
        notes = data.pop('notes', '')
        auto_check_before_save = data.pop('auto_check_before_save', False)
        
        # 确保图片数据结构完整
        if 'images' not in data:
            data['images'] = {}
        if 'image_local_paths' not in data:
            data['image_local_paths'] = {}
        
        # 确保所有图片类型都有对应的字段
        image_types = ['main', 'front', 'back', 'box', 'extra']
        for img_type in image_types:
            if img_type not in data['images']:
                data['images'][img_type] = ''
            if img_type not in data['image_local_paths']:
                data['image_local_paths'][img_type] = ''
        
        # 将数据转换为JSON字符串（不包含备注）
        annotation_json = json.dumps(data, ensure_ascii=False, indent=2)
        
        # 保存到数据库
        db = get_db_connection()
        
        # 如果需要自动检查，先执行检查
        auto_notes = ""
        if auto_check_before_save:
            issues = auto_checker.check_product(annotation_json)
            auto_notes = "; ".join(issues) if issues else ""
            db.execute(
                'UPDATE products SET annotation_data = ?, notes = ?, auto_notes = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (annotation_json, notes, auto_notes, product_id)
            )
        else:
            db.execute(
                'UPDATE products SET annotation_data = ?, notes = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (annotation_json, notes, product_id)
            )
        
        # 获取下一个产品ID，用于自动跳转
        next_product = db.execute(
            'SELECT id FROM products WHERE CAST(id AS INTEGER) > CAST(? AS INTEGER) ORDER BY CAST(id AS INTEGER) ASC LIMIT 1',
            (product_id,)
        ).fetchone()
        
        db.commit()
        db.close()
        
        # 构建响应数据
        response_data = {
            'success': True, 
            'message': 'Annotation saved successfully.',
            'next_product_id': next_product['id'] if next_product else None
        }
        
        # 如果执行了自动检查，在响应中包含检查结果
        if auto_check_before_save:
            response_data['auto_notes'] = auto_notes
        
        return jsonify(response_data)

    except Exception as e:
        # 记录错误日志
        current_app.logger.error(f"Error saving annotation for product {product_id}: {e}")
        return jsonify({'success': False, 'message': 'An error occurred on the server.'}), 500


@annotation_bp.route('/check/<product_id>', methods=['POST'])
def check_single_product(product_id):
    """
    检查单个产品的标注数据
    
    接收前端表单数据，调用自动检查器检查指定产品的标注数据，并将检查结果更新到auto_notes字段。
    
    Args:
        product_id (str): 产品ID
        
    Returns:
        JSON: 检查结果
            {
                "success": true/false,
                "message": "操作结果消息",
                "result": "检查结果字符串"
            }
    """
    try:
        # 获取前端发送的表单数据
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '未提供表单数据'}), 400
        
        # 构建标注数据
        annotation_data = {
            'unified_name': data.get('unified_name', ''),
            'brand': data.get('brand', ''),
            'price_listed': data.get('price_listed'),
            'price_cost': data.get('price_cost'),
            'images': {
                'main': data.get('main_image_url', ''),
                'front': data.get('front_image_url', ''),
                'back': data.get('back_image_url', ''),
                'box': data.get('box_image_url', ''),
                'extra': data.get('extra_image_url', ''),
            },
            'image_local_paths': {
                'main': data.get('main_image_local_url', ''),
                'front': data.get('front_image_local_url', ''),
                'back': data.get('back_image_local_url', ''),
                'box': data.get('box_image_local_url', ''),
                'extra': data.get('extra_image_local_url', ''),
            }
        }
        
        # 转换为JSON字符串
        annotation_json = json.dumps(annotation_data, ensure_ascii=False)
        
        # 执行检查
        issues = auto_checker.check_product(annotation_json)
        result = "; ".join(issues) if issues else "暂无问题"
        
        return jsonify({
            'success': True,
            'message': '检查完成',
            'result': result
        })
    except Exception as e:
        current_app.logger.error(f"检查产品 {product_id} 时出错: {e}")
        return jsonify({
            'success': False,
            'message': f'检查失败: {str(e)}'
        }), 500


@annotation_bp.route('/check-all', methods=['POST'])
def check_all_products():
    """
    批量检查所有已标注的产品
    
    调用自动检查器批量检查所有已标注的产品，并将检查结果更新到各自的auto_notes字段。
    
    Returns:
        JSON: 检查统计结果
            {
                "success": true/false,
                "message": "操作结果消息",
                "stats": {
                    "total": 总产品数,
                    "checked": 成功检查数,
                    "errors": 检查出错数
                }
            }
    """
    try:
        stats = auto_checker.check_all_products()
        return jsonify({
            'success': True,
            'message': '批量检查完成',
            'stats': stats
        })
    except Exception as e:
        current_app.logger.error(f"批量检查时出错: {e}")
        return jsonify({
            'success': False,
            'message': f'批量检查失败: {str(e)}'
        }), 500