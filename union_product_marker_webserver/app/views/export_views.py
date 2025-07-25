"""
导出数据视图模块

这个模块处理数据导出相关的功能，包括：
1. 导出页面显示
2. 商品数据导出
3. 图片处理和保存
4. 文件浏览器功能
5. 导出目录管理

主要功能：
- 选择商品进行导出
- 图片resize和压缩处理
- 创建标准化的导出目录结构
- 提供文件浏览功能
- 清空导出目录

作者: Union Product Marker Team
版本: 1.0.0
"""

import os
import json
import re
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory, abort
from app.utils.db_util import get_db_connection, BASE_DIR
from app.utils.image_util import ImageProcessor
import threading
import uuid
import time

# 创建导出数据蓝图
export_bp = Blueprint('export', __name__, url_prefix='/export-data')

# 全局导出任务进度存储
export_tasks = {}
export_tasks_lock = threading.Lock()

@export_bp.route('/')
def export_data():
    """
    导出数据页面
    
    显示商品选择界面和文件浏览器。
    
    Returns:
        str: 渲染后的导出页面HTML
    """
    return render_template('export_data.html')

@export_bp.route('/products')
def get_products_for_export():
    """
    获取可用于导出的商品列表
    
    返回所有已标注的商品，用于在导出页面中选择。
    
    Returns:
        JSON: 包含商品列表的数据
    """
    try:
        db = get_db_connection()
        # 获取所有已标注的商品（有annotation_data的商品）
        products = db.execute("""
            SELECT id, name, brand, annotation_data, notes, auto_notes, updated_at 
            FROM products 
            WHERE annotation_data IS NOT NULL AND annotation_data != ''
            ORDER BY CAST(id AS INTEGER) ASC
        """).fetchall()
        db.close()
        
        product_list = []
        for row in products:
            # 解析标注数据
            annotation_data = {}
            if row['annotation_data']:
                try:
                    annotation_data = json.loads(row['annotation_data'])
                except (json.JSONDecodeError, TypeError):
                    pass
            
            # 获取品牌信息：优先使用标注数据中的品牌，其次使用数据库中的品牌
            brand = annotation_data.get('brand', '') if annotation_data else row['brand'] or ''
            
            # 构建与数据标注页面相同的数据结构
            product_item = {
                'id': row['id'],
                'base_name': row['name'] or '',
                'brand': brand,
                'unified_name': annotation_data.get('unified_name', ''),
                'price_listed': annotation_data.get('price_listed'),
                'price_cost': annotation_data.get('price_cost'),
                'notes': row['notes'] or '',
                'auto_notes': row['auto_notes'] or '',
                'updated_at': row['updated_at'],
                'image_local_paths': annotation_data.get('image_local_paths', {}),
                'status': 'annotated'  # 导出页面只显示已标注的商品
            }
            
            product_list.append(product_item)
        
        return jsonify({
            'success': True,
            'products': product_list
        })
    except Exception as e:
        return jsonify({'error': f'获取商品列表失败: {str(e)}'}), 500

@export_bp.route('/export', methods=['POST'])
def execute_export():
    """
    异步执行导出任务，立即返回任务ID，后台线程处理导出。
    """
    try:
        data = request.get_json()
        product_ids = data.get('product_ids', [])
        if not product_ids:
            return jsonify({'error': '未选择商品'}), 400

        # 生成任务ID
        task_id = str(uuid.uuid4())
        with export_tasks_lock:
            export_tasks[task_id] = {
                'status': 'pending',
                'progress': 0,
                'total': len(product_ids),
                'processed': 0,
                'results': [],
                'errors': [],
                'start_time': time.time(),
                'end_time': None
            }

        from flask import current_app
        app = current_app._get_current_object()
        # 启动后台线程处理导出，传递app参数
        thread = threading.Thread(target=run_export_task, args=(app, task_id, product_ids))
        thread.daemon = True
        thread.start()

        return jsonify({'success': True, 'task_id': task_id})
    except Exception as e:
        return jsonify({'error': f'导出任务启动失败: {str(e)}'}), 500

def run_export_task(app, task_id, product_ids):
    """
    实际执行导出任务的后台线程函数
    """
    with app.app_context():
        try:
            # 获取导出目录
            export_dir = app.config['EXPORT_FOLDER']
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            
            # 初始化图片处理器
            image_processor = ImageProcessor()
            
            # 获取商品数据
            db = get_db_connection()
            products = db.execute("""
                SELECT id, name, brand, annotation_data 
                FROM products 
                WHERE id IN ({})
            """.format(','.join(['?' for _ in product_ids])), product_ids).fetchall()
            db.close()
            
            export_results = []
            errors = []
            
            for idx, product in enumerate(products):
                try:
                    product_id = product['id']
                    product_name = product['name'] or ''
                    brand = product['brand'] or ''
                    
                    # 解析标注数据
                    annotation_data = {}
                    if product['annotation_data']:
                        try:
                            annotation_data = json.loads(product['annotation_data'])
                        except (json.JSONDecodeError, TypeError):
                            errors.append(f"商品 {product_id} 标注数据解析失败")
                            continue
                    
                    # 获取统一名称
                    unified_name = annotation_data.get('unified_name', product_name)
                    
                    # 创建文件夹名称（去除特殊字符）
                    folder_name = f"{product_id} - {unified_name}"
                    folder_name = re.sub(r'[<>:"/\\|?*]', '', folder_name)  # 去除Windows不允许的字符
                    folder_name = re.sub(r'\s+', ' ', folder_name).strip()  # 规范化空格
                    
                    # 检查是否需要重命名现有文件夹
                    old_folder_path = None
                    for existing_folder in os.listdir(export_dir):
                        if existing_folder.startswith(f"{product_id} - "):
                            old_folder_path = os.path.join(export_dir, existing_folder)
                            if existing_folder != folder_name:
                                # 重命名文件夹
                                new_folder_path = os.path.join(export_dir, folder_name)
                                if os.path.exists(new_folder_path):
                                    # 如果新名称已存在，删除旧文件夹
                                    import shutil
                                    shutil.rmtree(old_folder_path)
                                else:
                                    os.rename(old_folder_path, new_folder_path)
                            break
                    
                    # 创建商品文件夹
                    product_folder = os.path.join(export_dir, folder_name)
                    if not os.path.exists(product_folder):
                        os.makedirs(product_folder)
                    
                    # 处理图片
                    image_local_paths = annotation_data.get('image_local_paths', {})
                    processed_images = []
                    
                    image_root = os.path.abspath(os.path.join(BASE_DIR, "..", "union_scraper", "output"))
                    for img_type, local_path in image_local_paths.items():
                        abs_input_path = os.path.join(image_root, local_path) if local_path else ""
                        print(f"[DEBUG] 商品ID={product_id}, 图片类型={img_type}, 相对路径={local_path}, 绝对路径={abs_input_path}")
                        if local_path and os.path.exists(abs_input_path):
                            try:
                                output_filename = f"{product_id}_{img_type}.jpg"
                                output_path = os.path.join(product_folder, output_filename)
                                print(f"[DEBUG] 即将处理图片: {abs_input_path} -> {output_path}")
                                success = image_processor.process_image(
                                    input_path=abs_input_path,
                                    output_path=output_path,
                                    target_size=(800, 800)
                                )
                                print(f"[DEBUG] 处理结果: {success}")
                                if success:
                                    processed_images.append({
                                        'type': img_type,
                                        'filename': output_filename,
                                        'path': output_path
                                    })
                                else:
                                    print(f"[ERROR] 商品 {product_id} 图片 {img_type} 处理失败")
                                    errors.append(f"商品 {product_id} 图片 {img_type} 处理失败")
                            except Exception as e:
                                print(f"[ERROR] 商品 {product_id} 图片 {img_type} 处理异常: {str(e)}")
                                errors.append(f"商品 {product_id} 图片 {img_type} 处理异常: {str(e)}")
                        else:
                            print(f"[WARN] 商品 {product_id} 图片 {img_type} 路径无效或文件不存在: {abs_input_path}")
                    
                    export_results.append({
                        'product_id': product_id,
                        'folder_name': folder_name,
                        'processed_images': len(processed_images),
                        'total_images': len([p for p in image_local_paths.values() if p])
                    })
                    
                except Exception as e:
                    errors.append(f"商品 {product['id']} 导出失败: {str(e)}")
                # === 实时更新进度 ===
                with export_tasks_lock:
                    task = export_tasks[task_id]
                    task['processed'] = idx + 1
                    task['progress'] = int((idx + 1) / task['total'] * 100)
                    task['results'] = export_results[:]
                    task['errors'] = errors[:]
            
            with export_tasks_lock:
                task = export_tasks[task_id]
                task['status'] = 'finished'
                task['end_time'] = time.time()
                task['results'] = export_results
                task['errors'] = errors
                task['processed'] = len(export_results)
                task['progress'] = 100
            
            return jsonify({
                'success': True,
                'results': export_results,
                'errors': errors,
                'total_processed': len(export_results),
                'total_errors': len(errors)
            })
        except Exception as e:
            with export_tasks_lock:
                task = export_tasks[task_id]
                task['status'] = 'error'
                task['errors'] = [str(e)]
                task['end_time'] = time.time()
            return jsonify({'error': f'导出失败: {str(e)}'}), 500

@export_bp.route('/files')
def get_export_files():
    """
    获取导出目录的文件列表
    
    用于文件浏览器功能，返回exports目录的结构。
    
    Returns:
        JSON: 包含文件树结构的数据
    """
    try:
        export_dir = current_app.config['EXPORT_FOLDER']
        if not os.path.exists(export_dir):
            return jsonify({'files': []})
        
        def build_file_tree(path, relative_path=''):
            """递归构建文件树"""
            tree = []
            try:
                items = os.listdir(path)
                items.sort()  # 排序
                
                for item in items:
                    item_path = os.path.join(path, item)
                    item_relative = os.path.join(relative_path, item) if relative_path else item
                    
                    if os.path.isdir(item_path):
                        # 文件夹
                        children = build_file_tree(item_path, item_relative)
                        tree.append({
                            'name': item,
                            'path': item_relative,
                            'type': 'folder',
                            'children': children
                        })
                    else:
                        # 文件
                        file_size = os.path.getsize(item_path)
                        file_ext = os.path.splitext(item)[1].lower()
                        
                        tree.append({
                            'name': item,
                            'path': item_relative,
                            'type': 'file',
                            'size': file_size,
                            'extension': file_ext,
                            'is_image': file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
                        })
            except PermissionError:
                pass  # 忽略权限错误
            
            return tree
        
        file_tree = build_file_tree(export_dir)
        
        return jsonify({
            'success': True,
            'files': file_tree
        })
        
    except Exception as e:
        return jsonify({'error': f'获取文件列表失败: {str(e)}'}), 500

@export_bp.route('/clear', methods=['POST'])
def clear_export_directory():
    """
    清空导出目录
    
    删除exports目录下的所有内容。
    
    Returns:
        JSON: 清空结果
    """
    try:
        export_dir = current_app.config['EXPORT_FOLDER']
        if not os.path.exists(export_dir):
            return jsonify({'success': True, 'message': '导出目录不存在'})
        
        # 删除目录下的所有内容
        import shutil
        for item in os.listdir(export_dir):
            item_path = os.path.join(export_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        
        return jsonify({
            'success': True,
            'message': '导出目录已清空'
        })
        
    except Exception as e:
        return jsonify({'error': f'清空导出目录失败: {str(e)}'}), 500

@export_bp.route('/image/<path:filename>')
def serve_export_image(filename):
    """
    提供导出图片文件服务
    
    用于在文件浏览器中显示导出的图片。
    
    Args:
        filename (str): 图片文件名，支持包含路径的文件名
        
    Returns:
        Response: 图片文件内容，如果文件不存在则返回404
    """
    try:
        export_dir = current_app.config['EXPORT_FOLDER']
        file_path = os.path.join(export_dir, filename)
        
        # 检查文件是否存在
        if os.path.exists(file_path) and os.path.isfile(file_path):
            # 使用Flask的send_from_directory安全地发送文件
            return send_from_directory(export_dir, filename)
        
        # 文件不存在，返回404错误
        abort(404)
        
    except Exception as e:
        # 记录错误日志并返回404
        print(f"导出图片服务错误: {e}")
        abort(404)

@export_bp.route('/progress/<task_id>')
def export_progress(task_id):
    """
    查询导出任务进度
    """
    with export_tasks_lock:
        task = export_tasks.get(task_id)
        if not task:
            return jsonify({'error': '任务不存在'}), 404
        return jsonify({
            'status': task['status'],
            'progress': task['progress'],
            'total': task['total'],
            'processed': task['processed'],
            'results': task['results'],
            'errors': task['errors'],
            'start_time': task['start_time'],
            'end_time': task['end_time']
        }) 