"""
数据库连接测试模块

这个模块用于测试数据库连接和表结构，包括：
1. 数据库初始化测试
2. 连接功能测试
3. 表结构验证
4. 基本CRUD操作测试

主要功能：
- 验证数据库工具函数是否正常工作
- 检查数据库表结构是否正确
- 测试基本的数据库操作
- 提供详细的测试结果输出

作者: Union Product Marker Team
版本: 1.0.0
"""

import sqlite3
import os
import sys

# 添加项目根目录到Python路径
# 这确保可以正确导入项目中的模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.db_util import get_db_connection, init_db

def test_database():
    """
    测试数据库连接和表结构
    
    这个函数执行一系列数据库测试，包括：
    - 数据库初始化
    - 连接测试
    - 表结构检查
    - 基本操作测试
    - 数据清理
    
    测试过程会输出详细的日志信息，帮助诊断问题。
    """
    
    print("🔍 测试数据库连接和表结构:")
    
    try:
        # 确保数据库初始化
        print("  - 初始化数据库...")
        init_db()
        print("  ✅ 数据库初始化完成")
        
        # 测试连接
        # 验证get_db_connection函数是否正常工作
        conn = get_db_connection()
        cursor = conn.cursor()
        print("  ✅ 数据库连接成功")
        
        # 检查表结构
        # 查询所有表名，验证表是否已创建
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"  📋 数据库表: {[table[0] for table in tables]}")
        
        # 检查sources表结构
        # 详细查看sources表的列定义
        if ('sources',) in tables:
            cursor.execute("PRAGMA table_info(sources)")
            columns = cursor.fetchall()
            print(f"  🔍 sources表结构:")
            for col in columns:
                print(f"    - {col[1]} ({col[2]})")
        
        # 测试插入一条记录
        # 验证基本的插入操作是否正常
        print("  - 测试插入记录...")
        cursor.execute(
            "INSERT INTO sources (product_id, source_name, raw_json, uploaded_at) VALUES (?, ?, ?, ?)",
            ("test_001", "test_source", '{"test": "data"}', "2024-01-01 00:00:00")
        )
        conn.commit()
        print("  ✅ 测试插入成功")
        
        # 检查记录数
        # 验证插入操作是否真的增加了记录
        cursor.execute("SELECT COUNT(*) FROM sources")
        count = cursor.fetchone()[0]
        print(f"  📊 sources表记录数: {count}")
        
        # 清理测试数据
        # 删除测试记录，保持数据库清洁
        cursor.execute("DELETE FROM sources WHERE product_id = 'test_001'")
        conn.commit()
        print("  ✅ 测试数据清理完成")
        
        # 关闭连接
        conn.close()
        print("  ✅ 数据库测试完成")
        
    except Exception as e:
        # 如果测试过程中出现异常，输出详细的错误信息
        print(f"  ❌ 数据库测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 当直接运行此文件时执行测试
    test_database() 