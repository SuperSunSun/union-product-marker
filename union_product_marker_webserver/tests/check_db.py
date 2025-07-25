"""
数据库检查工具模块

这个模块提供了一个简单的数据库检查工具，用于：
1. 检查数据库文件是否存在
2. 查看数据库表结构
3. 统计各表的记录数
4. 验证数据库完整性

主要功能：
- 快速检查数据库状态
- 显示表结构和记录统计
- 帮助诊断数据库问题
- 提供数据库概览信息

作者: Union Product Marker Team
版本: 1.0.0
"""

import sqlite3
import os

def check_database():
    """
    检查数据库状态和结构
    
    这个函数执行以下检查：
    - 验证数据库文件是否存在
    - 列出所有数据库表
    - 统计每个表的记录数
    - 显示关键表的结构信息
    
    输出格式化的检查结果，便于快速了解数据库状态。
    """
    # 数据库文件路径（相对于当前工作目录）
    db_path = "database.db"
    
    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在")
        return
    
    print(f"✅ 数据库文件存在: {db_path}")
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        # 查询所有用户表（排除系统表）
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\n📋 数据库中的表:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 检查每个表的记录数
        # 统计每个表的数据量，帮助了解数据分布
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  📊 {table_name}: {count} 条记录")
        
        # 检查sources表的结构
        # sources表存储爬虫数据，是系统的核心表之一
        if ('sources',) in tables:
            cursor.execute("PRAGMA table_info(sources)")
            columns = cursor.fetchall()
            print(f"\n🔍 sources表结构:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        
        # 检查products表的结构
        # products表存储产品信息，是系统的基础表
        if ('products',) in tables:
            cursor.execute("PRAGMA table_info(products)")
            columns = cursor.fetchall()
            print(f"\n🔍 products表结构:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        
        # 关闭数据库连接
        conn.close()
        
    except Exception as e:
        # 如果检查过程中出现异常，输出错误信息
        print(f"❌ 检查数据库时出错: {e}")

if __name__ == "__main__":
    # 当直接运行此文件时执行数据库检查
    check_database() 