"""
数据导入视图模块

这个模块处理基础数据的导入功能，包括：
1. CSV文件上传和解析
2. 数据差异比较
3. 数据导入到数据库
4. JSON格式数据导入

主要功能：
- 支持CSV格式的产品数据导入
- 自动检测数据差异
- 批量更新产品信息
- 数据验证和错误处理

作者: Union Product Marker Team
版本: 1.0.0
"""

import io
import csv
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from app.utils.db_util import get_db_connection

# 创建基础数据导入蓝图
import_basic_bp = Blueprint("import_basic", __name__)

@import_basic_bp.route("/import-basic")
def import_basic():
    """
    基础数据导入页面
    
    显示数据导入的界面，用户可以：
    - 上传CSV文件
    - 预览数据差异
    - 执行数据导入
    
    Returns:
        str: 渲染后的导入页面HTML
    """
    return render_template("import_basic.html")

@import_basic_bp.route("/import-basic/upload-csv", methods=["POST"])
def import_basic_upload_csv():
    """
    处理CSV文件上传和预览
    
    接收上传的CSV文件，解析内容并与数据库中的现有数据进行比较，
    返回差异分析结果供用户确认。
    
    Returns:
        JSON: 包含数据差异分析的结果
            {
                "records": [
                    {
                        "id": "产品ID",
                        "name_csv": "CSV中的名称",
                        "name_db": "数据库中的名称",
                        "diff": true/false,
                        "debug_reason": "差异原因"
                    }
                ]
            }
    """
    try:
        # 获取上传的文件
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "未上传文件"}), 400

        # 关键点：使用 utf-8-sig 自动剥离 BOM
        # 这解决了Excel导出的CSV文件可能包含BOM字符的问题
        stream = io.StringIO(file.stream.read().decode("utf-8-sig"))
        reader = csv.DictReader(stream)
        uploaded = list(reader)

        #print("📄 CSV 字段名：", reader.fieldnames)

        # 获取数据库中现有的产品数据
        conn = get_db_connection()
        existing_data = {
            row["id"]: row["name"]
            for row in conn.execute("SELECT id, name FROM products").fetchall()
        }
        conn.close()

        # 分析每个上传的记录
        records = []
        for row in uploaded:
            # 标准化字段名（转小写并去除空格）
            row_lower = {k.strip().lower(): v for k, v in row.items()}
            pid = row_lower.get("id", "").strip()
            name_csv = row_lower.get("fullname", "").strip()
            name_db = existing_data.get(pid)

            # 标准化名称比较（转小写并去除空格）
            name_csv_norm = (name_csv or "").lower().strip()
            name_db_norm = (name_db or "").lower().strip()

            # 判断是否存在差异
            if name_db is None:
                diff = True
                reason = "ID 不存在于数据库"
            elif name_csv_norm != name_db_norm:
                diff = True
                reason = f"名称不一致：CSV='{name_csv}' vs DB='{name_db}'"
            else:
                diff = False
                reason = "无差异"

            # 构建记录信息
            records.append({
                "id": pid,
                "name_csv": name_csv,
                "name_db": name_db,
                "diff": diff,
                "debug_reason": reason
            })

        return jsonify({ "records": records })

    except Exception as e:
        return jsonify({ "error": f"导入失败: {str(e)}" }), 500

@import_basic_bp.route("/import-basic/upload-json", methods=["POST"])
def import_basic_upload_json():
    """
    处理JSON格式的数据导入
    
    接收前端发送的JSON数据，将其导入到数据库中。
    支持新增和更新操作。
    
    Returns:
        JSON: 导入结果信息
            {
                "message": "导入完成：新增 X 条，更新 Y 条。"
            }
    """
    # 获取前端发送的JSON数据
    data = request.get_json()
    records = data.get("records", [])

    # 获取数据库连接
    conn = get_db_connection()
    cursor = conn.cursor()

    # 统计导入结果
    inserted = 0
    updated = 0
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 处理每条记录
    for row in records:
        pid = row.get("id")
        name = row.get("name_csv")

        # 检查产品是否已存在
        cursor.execute("SELECT COUNT(*) FROM products WHERE id = ?", (pid,))
        exists = cursor.fetchone()[0]

        if exists:
            # 更新现有产品信息
            cursor.execute(
                "UPDATE products SET name = ?, updated_at = ? WHERE id = ?",
                (name, now, pid)
            )
            updated += 1
        else:
            # 插入新产品
            cursor.execute(
                "INSERT INTO products (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (pid, name, now, now)
            )
            inserted += 1

    # 提交事务并关闭连接
    conn.commit()
    conn.close()

    # 返回导入结果
    return jsonify({
        "message": f"✅ 导入完成：新增 {inserted} 条，更新 {updated} 条。"
    })
