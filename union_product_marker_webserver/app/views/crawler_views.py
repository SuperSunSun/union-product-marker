"""
爬虫数据管理视图模块

这个模块处理爬虫数据的上传、管理和统计功能，包括：
1. 爬虫数据文件上传和预览
2. 数据导入到数据库
3. 数据统计和概览
4. 数据源管理

主要功能：
- 支持JSON格式的爬虫数据上传
- 数据预览和验证
- 批量导入爬虫数据
- 数据统计和来源分析
- 数据源删除和管理

作者: Union Product Marker Team
版本: 1.0.0
"""

import json
import os
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app
from app.utils.db_util import get_db_connection

# 爬虫数据上传蓝图
crawler_upload_bp = Blueprint("crawler_upload", __name__)

@crawler_upload_bp.route("/crawler-upload")
def crawler_upload():
    """
    爬虫数据上传页面
    
    显示爬虫数据上传的界面，用户可以：
    - 上传JSON格式的爬虫数据文件
    - 预览数据内容
    - 执行数据导入
    
    Returns:
        str: 渲染后的上传页面HTML
    """
    return render_template("crawler_upload.html")

@crawler_upload_bp.route("/crawler-upload/preview", methods=["POST"])
def preview_crawler_data():
    """
    预览爬虫数据
    
    接收上传的JSON文件，解析并返回数据统计信息，
    供用户确认后执行导入。
    
    Returns:
        JSON: 包含数据统计和预览信息
            {
                "success": true,
                "stats": {
                    "total_sources": 数据源总数,
                    "total_products": 产品总数,
                    "sources": [{"name": "来源名", "count": 产品数量}]
                },
                "data": 原始数据,
                "filename": 文件名
            }
    """
    try:
        # 获取上传的文件
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "未上传文件"}), 400

        # 读取JSON文件内容
        content = file.read().decode("utf-8")
        data = json.loads(content)
        
        # 验证数据结构
        if not isinstance(data, dict) or "products" not in data:
            return jsonify({"error": "无效的JSON结构：缺少products字段"}), 400
        
        # 统计信息
        stats = {
            "total_sources": len(data.get("products", {})),
            "total_products": 0,
            "sources": []
        }
        
        # 计算每个来源的产品数量
        for source_name, products in data.get("products", {}).items():
            if isinstance(products, list):
                stats["total_products"] += len(products)
                stats["sources"].append({
                    "name": source_name,
                    "count": len(products)
                })
        
        # 返回预览数据
        return jsonify({
            "success": True,
            "stats": stats,
            "data": data,
            "filename": file.filename
        })
        
    except json.JSONDecodeError as e:
        return jsonify({"error": f"JSON解析错误: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"处理失败: {str(e)}"}), 500

@crawler_upload_bp.route("/crawler-upload/import", methods=["POST"])
def import_crawler_data():
    """
    导入爬虫数据到数据库
    
    接收前端发送的爬虫数据，将其导入到sources表中。
    支持新增和更新操作，同时确保products表中存在对应的产品记录。
    
    Returns:
        JSON: 导入结果信息
            {
                "success": true,
                "message": "导入完成：新增 X 条，更新 Y 条。"
            }
    """
    try:
        # 获取前端发送的数据
        data = request.get_json()
        if not data or "data" not in data:
            return jsonify({"error": "无效的请求数据"}), 400
        
        crawler_data = data["data"]  # 这里直接是products对象，不是包含products字段的对象
        source_name = data.get("source_name", "unknown")
        
        # 添加调试信息
        print(f"🔍 调试信息:")
        print(f"  - 接收到的数据类型: {type(crawler_data)}")
        print(f"  - 数据键: {list(crawler_data.keys()) if isinstance(crawler_data, dict) else 'N/A'}")
        
        # 获取数据库连接
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 统计导入结果
        inserted = 0
        updated = 0
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 处理每个来源的数据 - crawler_data直接是products对象
        for source_key, products in crawler_data.items():
            if not isinstance(products, list):
                print(f"  - 跳过非列表数据: {source_key} (类型: {type(products)})")
                continue
                
            print(f"  - 处理来源: {source_key}, 商品数量: {len(products)}")
            
            # 处理每个产品
            for product in products:
                product_id = str(product.get("id", ""))
                if not product_id:
                    print(f"    - 跳过无ID商品: {product.get('product_name', 'N/A')}")
                    continue
                
                # 检查是否已存在该来源的数据
                cursor.execute(
                    "SELECT id FROM sources WHERE product_id = ? AND source_name = ?",
                    (product_id, source_key)
                )
                exists = cursor.fetchone()
                
                if exists:
                    # 更新现有数据
                    cursor.execute(
                        "UPDATE sources SET raw_json = ?, uploaded_at = ? WHERE product_id = ? AND source_name = ?",
                        (json.dumps(product), now, product_id, source_key)
                    )
                    updated += 1
                else:
                    # 插入新数据
                    cursor.execute(
                        "INSERT INTO sources (product_id, source_name, raw_json, uploaded_at) VALUES (?, ?, ?, ?)",
                        (product_id, source_key, json.dumps(product), now)
                    )
                    inserted += 1
                
                # 确保products表中存在该商品
                cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO products (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
                        (product_id, product.get("product_name", "未命名"), now, now)
                    )
        
        # 提交事务并关闭连接
        conn.commit()
        conn.close()
        
        print(f"  - 导入结果: 新增 {inserted} 条，更新 {updated} 条")
        
        return jsonify({
            "success": True,
            "message": f"✅ 导入完成：新增 {inserted} 条，更新 {updated} 条。"
        })
        
    except Exception as e:
        print(f"❌ 导入失败: {str(e)}")
        return jsonify({"error": f"导入失败: {str(e)}"}), 500

# 爬虫数据管理蓝图
crawler_manage_bp = Blueprint("crawler_manage", __name__)

@crawler_manage_bp.route("/crawler-manage")
def crawler_manage():
    """
    爬虫数据管理页面
    
    显示爬虫数据管理的界面，用户可以：
    - 查看数据统计信息
    - 浏览所有产品数据
    - 管理数据源
    - 删除特定数据源
    
    Returns:
        str: 渲染后的管理页面HTML
    """
    return render_template("crawler_manage.html")

@crawler_manage_bp.route("/crawler-manage/statistics")
def get_statistics():
    """
    获取数据统计信息
    
    计算并返回数据库中的数据统计信息，包括：
    - 产品总数
    - 有数据的产品数量
    - 数据源统计
    - 覆盖率分析
    
    Returns:
        JSON: 包含详细统计信息
            {
                "success": true,
                "stats": {
                    "total_products": 产品总数,
                    "products_with_data": 有数据的产品数,
                    "total_sources": 数据源总数,
                    "data_ratio": 数据覆盖率,
                    "sources": [{"source_name": "来源名", "source_data_count": 数据量, "products_with_this_source": 产品数, "source_ratio": 覆盖率}]
                }
            }
    """
    try:
        conn = get_db_connection()
        
        # 1. 商品总数：库内所有有ID的数量
        cursor = conn.execute("SELECT COUNT(*) as total_products FROM products")
        total_products = cursor.fetchone()[0]
        
        # 2. 有数据商品：有至少1个来源数据的商品数量
        cursor.execute("SELECT COUNT(DISTINCT product_id) as products_with_data FROM sources")
        products_with_data = cursor.fetchone()[0]
        
        # 3. 来源数据总量：所有来源的爬虫数据总量
        cursor.execute("SELECT COUNT(*) as total_sources FROM sources")
        total_sources = cursor.fetchone()[0]
        
        # 4. 有数据比率：有数据商品数/商品总数
        data_ratio = (products_with_data / total_products * 100) if total_products > 0 else 0
        
        # 5. 每个来源的统计信息
        cursor.execute("""
            SELECT 
                source_name,
                COUNT(*) as source_data_count,
                COUNT(DISTINCT product_id) as products_with_this_source
            FROM sources
            GROUP BY source_name
            ORDER BY source_data_count DESC
        """)
        source_stats = cursor.fetchall()
        
        # 计算每个来源的有数据比率
        sources_with_ratio = []
        for source in source_stats:
            source_dict = dict(source)
            source_ratio = (source_dict['products_with_this_source'] / total_products * 100) if total_products > 0 else 0
            source_dict['source_ratio'] = round(source_ratio, 1)
            sources_with_ratio.append(source_dict)
        
        conn.close()
        
        return jsonify({
            "success": True,
            "stats": {
                "total_products": total_products,
                "products_with_data": products_with_data,
                "total_sources": total_sources,
                "data_ratio": round(data_ratio, 1),
                "sources": sources_with_ratio
            }
        })
    except Exception as e:
        return jsonify({"error": f"获取统计信息失败: {str(e)}"}), 500

@crawler_manage_bp.route("/crawler-manage/all-data")
def get_all_data():
    """
    获取所有商品数据，格式与crawler_upload上传的JSON一致
    
    从数据库检索所有爬虫数据，按来源分组，返回与上传格式一致的数据结构。
    这可以用于数据导出或备份。
    
    Returns:
        JSON: 包含所有爬虫数据，按来源分组
            {
                "success": true,
                "products": {
                    "来源名1": [产品数据列表],
                    "来源名2": [产品数据列表]
                }
            }
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT s.product_id, s.source_name, s.raw_json, s.uploaded_at
            FROM sources s
            ORDER BY s.product_id, s.source_name
        """)
        sources = cursor.fetchall()
        conn.close()
        
        # 按来源分组数据
        products_by_source = {}
        
        for source in sources:
            try:
                raw_data = json.loads(source["raw_json"])
                source_name = source["source_name"]
                
                if source_name not in products_by_source:
                    products_by_source[source_name] = []
                
                products_by_source[source_name].append(raw_data)
                
            except json.JSONDecodeError:
                print(f"JSON解析失败: product_id={source['product_id']}, source_name={source['source_name']}")
                continue
        
        return jsonify({
            "success": True,
            "products": products_by_source
        })
    except Exception as e:
        return jsonify({"error": f"获取数据失败: {str(e)}"}), 500

@crawler_manage_bp.route("/crawler-manage/products")
def get_products():
    """
    获取所有有爬虫数据的商品列表
    
    查询所有有爬虫数据的产品，包括每个产品的数据源数量。
    
    Returns:
        JSON: 包含产品列表和统计信息
            {
                "success": true,
                "products": [
                    {
                        "id": "产品ID",
                        "name": "产品名称",
                        "status": "状态",
                        "updated_at": "更新时间",
                        "source_count": 数据源数量
                    }
                ]
            }
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT DISTINCT p.id, p.name, p.status, p.updated_at,
                   COUNT(s.id) as source_count
            FROM products p
            INNER JOIN sources s ON p.id = s.product_id
            GROUP BY p.id, p.name, p.status, p.updated_at
            ORDER BY CAST(p.id AS INTEGER)
        """)
        products = cursor.fetchall()
        conn.close()
        
        return jsonify({
            "success": True,
            "products": [dict(p) for p in products]
        })
    except Exception as e:
        return jsonify({"error": f"获取商品列表失败: {str(e)}"}), 500

@crawler_manage_bp.route("/crawler-manage/product/<product_id>")
def get_product_sources(product_id):
    """
    获取指定商品的所有来源数据
    
    查询指定产品的所有爬虫数据源，包括原始JSON数据。
    
    Args:
        product_id (str): 产品ID
        
    Returns:
        JSON: 包含产品信息和所有数据源
            {
                "success": true,
                "product": 产品基本信息,
                "sources": [
                    {
                        "source_name": "来源名",
                        "data": 原始数据,
                        "uploaded_at": "上传时间"
                    }
                ]
            }
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT s.source_name, s.raw_json, s.uploaded_at
            FROM sources s
            WHERE s.product_id = ?
            ORDER BY s.uploaded_at DESC
        """, (product_id,))
        sources = cursor.fetchall()
        
        # 获取商品基本信息
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        conn.close()
        
        # 解析JSON数据
        parsed_sources = []
        for source in sources:
            try:
                raw_data = json.loads(source["raw_json"])
                parsed_sources.append({
                    "source_name": source["source_name"],
                    "data": raw_data,
                    "uploaded_at": source["uploaded_at"]
                })
            except json.JSONDecodeError:
                parsed_sources.append({
                    "source_name": source["source_name"],
                    "data": {"error": "JSON解析失败"},
                    "uploaded_at": source["uploaded_at"]
                })
        
        return jsonify({
            "success": True,
            "product": dict(product) if product else None,
            "sources": parsed_sources
        })
    except Exception as e:
        return jsonify({"error": f"获取商品数据失败: {str(e)}"}), 500

@crawler_manage_bp.route("/crawler-manage/delete-source", methods=["POST"])
def delete_source():
    """
    删除指定来源的数据
    
    删除指定产品的特定数据源。如果删除后该产品没有任何数据源，
    可以选择是否同时删除产品记录。
    
    Returns:
        JSON: 删除操作结果
            {
                "success": true,
                "message": "删除成功",
                "remaining_sources": 剩余数据源数量
            }
    """
    try:
        data = request.get_json()
        product_id = data.get("product_id")
        source_name = data.get("source_name")
        
        if not product_id or not source_name:
            return jsonify({"error": "缺少必要参数"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 删除指定的数据源
        cursor.execute(
            "DELETE FROM sources WHERE product_id = ? AND source_name = ?",
            (product_id, source_name)
        )
        
        # 检查是否还有其他来源数据
        cursor.execute(
            "SELECT COUNT(*) FROM sources WHERE product_id = ?",
            (product_id,)
        )
        remaining_sources = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"成功删除 {source_name} 的数据",
            "remaining_sources": remaining_sources
        })
        
    except Exception as e:
        return jsonify({"error": f"删除失败: {str(e)}"}), 500 