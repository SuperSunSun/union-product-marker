"""
批量标注视图模块

这个模块处理批量标注相关的功能，包括：
1. 批量标注页面显示
2. CSV数据导出
3. CSV数据上传和比对
4. 批量标注数据保存

主要功能：
- 导出当前标注数据为CSV
- 上传修改后的CSV进行比对
- 预览变更内容
- 批量保存标注数据

作者: Union Product Marker Team
版本: 1.0.0
"""

import io
import csv
import json
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, send_file
from app.utils.db_util import get_db_connection

# 创建批量标注蓝图
batch_annotation_bp = Blueprint('batch_annotation', __name__, url_prefix='/batch-annotation')

@batch_annotation_bp.route('/')
def batch_annotation():
    """
    批量标注页面
    """
    return render_template('batch_annotation.html')

@batch_annotation_bp.route('/export-csv')
def export_annotation_csv():
    """
    导出标注数据为CSV文件
    """
    try:
        db = get_db_connection()
        products = db.execute("""
            SELECT id, name, brand, price_orig, price_curr, annotation_data, notes, auto_notes 
            FROM products 
            ORDER BY CAST(id AS INTEGER) ASC
        """).fetchall()
        db.close()
        csv_data = []
        for row in products:
            # 解析标注数据
            unified_name = ''
            brand = ''
            price_listed = ''
            price_cost = ''
            
            if row['annotation_data']:
                try:
                    annotation_data = json.loads(row['annotation_data'])
                    unified_name = annotation_data.get('unified_name', '')
                    brand = annotation_data.get('brand', '')
                    price_listed = annotation_data.get('price_listed', '')
                    price_cost = annotation_data.get('price_cost', '')
                except (json.JSONDecodeError, TypeError):
                    pass
            
            csv_data.append({
                'id': row['id'],
                'name': row['name'] or '',
                'unified_name': unified_name,
                'brand': brand,
                'price_listed': price_listed,
                'price_cost': price_cost,
                'notes': row['notes'] or ''
            })
        
        output = io.StringIO()
        fieldnames = [
            'id', 'name', 'unified_name', 'brand', 
            'price_listed', 'price_cost', 'notes'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'annotation_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        
    except Exception as e:
        return jsonify({"error": f"导出失败: {str(e)}"}), 500

@batch_annotation_bp.route('/upload-csv', methods=['POST'])
def upload_annotation_csv():
    """
    上传修改后的CSV文件并比对差异
    """
    try:
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "未上传文件"}), 400
        
        stream = io.StringIO(file.stream.read().decode("utf-8-sig"))
        reader = csv.DictReader(stream)
        uploaded_data = list(reader)
        
        db = get_db_connection()
        existing_products = {}
        for row in db.execute("SELECT id, name, brand, price_orig, price_curr, annotation_data, notes, auto_notes FROM products").fetchall():
            existing_products[row['id']] = {
                'name': row['name'],
                'brand': row['brand'],
                'price_orig': row['price_orig'],
                'price_curr': row['price_curr'],
                'annotation_data': row['annotation_data'],
                'notes': row['notes'],
                'auto_notes': row['auto_notes']
            }
        db.close()
        records = []
        changed_count = 0
        for row in uploaded_data:
            product_id = row.get('id', '').strip()
            if not product_id:
                continue
            existing = existing_products.get(product_id, {})
            changes = {}
            existing_annotation = {}
            if existing.get('annotation_data'):
                try:
                    existing_annotation = json.loads(existing['annotation_data'])
                except (json.JSONDecodeError, TypeError):
                    pass
            # 定义所有需要比对的字段（只包含可修改的字段）
            fields_to_check = [
                ('unified_name', 'unified_name'),
                ('brand', 'brand'),
                ('price_listed', 'price_listed'),
                ('price_cost', 'price_cost'),
                ('notes', 'notes')
            ]
            for csv_field, annotation_field in fields_to_check:
                new_value = row.get(csv_field, '').strip()
                if annotation_field == 'notes':
                    # notes字段直接存储在products表中
                    old_value = existing.get('notes', '')
                else:
                    # 其他字段存储在annotation_data中
                    old_value = existing_annotation.get(annotation_field, '')
                
                if annotation_field in ['price_listed', 'price_cost']:
                    try:
                        new_value = float(new_value) if new_value else None
                        old_value = float(old_value) if old_value else None
                    except ValueError:
                        new_value = None
                        old_value = None
                new_str = str(new_value) if new_value is not None else ''
                old_str = str(old_value) if old_value is not None else ''
                if new_str != old_str:
                    changes[annotation_field] = {
                        'old': old_value,
                        'new': new_value
                    }
            has_changes = len(changes) > 0
            if has_changes:
                changed_count += 1
            # 构建完整的数据记录，包含CSV中的新值
            records.append({
                'id': product_id,
                'name': existing.get('name', ''),
                'unified_name': row.get('unified_name', '').strip(),
                'brand_annotated': row.get('brand', '').strip(),
                'price_listed': row.get('price_listed', '').strip(),
                'price_cost': row.get('price_cost', '').strip(),
                'image_local_paths': existing_annotation.get('image_local_paths', {}),
                'notes': row.get('notes', '').strip(),
                'auto_notes': existing.get('auto_notes', ''),
                'changes': changes,
                'has_changes': has_changes
            })
        summary = {
            'total': len(records),
            'changed': changed_count,
            'unchanged': len(records) - changed_count
        }
        return jsonify({
            'records': records,
            'summary': summary
        })
    except Exception as e:
        return jsonify({"error": f"处理失败: {str(e)}"}), 500

@batch_annotation_bp.route('/save-changes', methods=['POST'])
def save_annotation_changes():
    """
    保存批量标注变更
    """
    try:
        data = request.get_json()
        records = data.get('records', [])
        if not records:
            return jsonify({"error": "没有要保存的数据"}), 400
        db = get_db_connection()
        cursor = db.cursor()
        updated_count = 0
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for record in records:
            if not record.get('has_changes'):
                continue
            product_id = record['id']
            changes = record['changes']
            
            # 分别处理annotation_data和notes字段
            annotation_updates = {}
            notes_update = None
            
            for field, change in changes.items():
                if field == 'notes':
                    notes_update = change['new']
                else:
                    annotation_updates[field] = change['new']
            
            # 更新annotation_data
            if annotation_updates:
                cursor.execute("SELECT annotation_data FROM products WHERE id = ?", (product_id,))
                result = cursor.fetchone()
                if result:
                    annotation_data = {}
                    if result[0]:
                        try:
                            annotation_data = json.loads(result[0])
                        except (json.JSONDecodeError, TypeError):
                            pass
                    
                    # 更新annotation_data中的字段
                    for field, value in annotation_updates.items():
                        annotation_data[field] = value
                    
                    cursor.execute(
                        "UPDATE products SET annotation_data = ?, updated_at = ? WHERE id = ?",
                        (json.dumps(annotation_data), now, product_id)
                    )
                    updated_count += 1
            
            # 更新notes字段
            if notes_update is not None:
                cursor.execute(
                    "UPDATE products SET notes = ?, updated_at = ? WHERE id = ?",
                    (notes_update, now, product_id)
                )
                if not annotation_updates:  # 如果只更新了notes，也要计数
                    updated_count += 1
        
        db.commit()
        db.close()
        return jsonify({
            "success": True,
            "message": f"✅ 保存完成：更新 {updated_count} 条记录。"
        })
    except Exception as e:
        return jsonify({"error": f"保存失败: {str(e)}"}), 500

@batch_annotation_bp.route('/get-current-data')
def get_current_data():
    """
    获取当前标注数据
    
    从数据库获取所有产品的标注数据，用于前端显示。
    
    Returns:
        JSON: 包含所有产品标注数据
            {
                "records": [
                    {
                        "id": "产品ID",
                        "name": "基础名称",
                        "unified_name": "统一名称",
                        "brand_annotated": "品牌",
                        "price_listed": "价格（上架）",
                        "price_cost": "价格（成本）",
                        "image_local_paths": "本地图片路径",
                        "notes": "人工备注",
                        "auto_notes": "自动备注"
                    }
                ]
            }
    """
    try:
        db = get_db_connection()
        products = db.execute("""
            SELECT id, name, brand, price_orig, price_curr, annotation_data, notes, auto_notes
            FROM products 
            ORDER BY CAST(id AS INTEGER) ASC
        """).fetchall()
        db.close()
        
        records = []
        for row in products:
            # 解析标注数据
            unified_name = ''
            brand_annotated = ''
            price_listed = ''
            price_cost = ''
            image_local_paths = {}
            
            if row['annotation_data']:
                try:
                    annotation_data = json.loads(row['annotation_data'])
                    unified_name = annotation_data.get('unified_name', '')
                    brand_annotated = annotation_data.get('brand', '')
                    price_listed = annotation_data.get('price_listed', '')
                    price_cost = annotation_data.get('price_cost', '')
                    image_local_paths = annotation_data.get('image_local_paths', {})
                except (json.JSONDecodeError, TypeError):
                    pass
            
            records.append({
                'id': row['id'],
                'name': row['name'] or '',
                'unified_name': unified_name,
                'brand_annotated': brand_annotated,
                'price_listed': price_listed,
                'price_cost': price_cost,
                'image_local_paths': image_local_paths,
                'notes': row['notes'] or '',
                'auto_notes': row['auto_notes'] or ''
            })
        
        return jsonify({
            'records': records
        })
        
    except Exception as e:
        return jsonify({"error": f"获取数据失败: {str(e)}"}), 500 