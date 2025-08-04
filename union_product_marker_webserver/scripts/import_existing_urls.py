#!/usr/bin/env python3
"""
导入现有爬虫数据中的URL信息到URL管理系统

这个脚本会从sources表中读取现有的爬虫数据，
提取URL信息并导入到product_urls表中。

作者: Union Product Marker Team
版本: 1.0.0
"""

import sys
import os
import json
import sqlite3
from datetime import datetime
from urllib.parse import urlparse

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.utils.db_util import get_db_path
from app.models.product_url import ProductUrl

def clear_existing_urls():
    """
    清空现有的URL数据
    """
    print("🗑️  开始清空现有的URL数据...")
    
    # 获取数据库路径
    db_path = get_db_path()
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 查询当前URL数量
        cursor.execute("SELECT COUNT(*) FROM product_urls")
        count_before = cursor.fetchone()[0]
        print(f"📊 清空前URL数量: {count_before}")
        
        # 清空product_urls表
        cursor.execute("DELETE FROM product_urls")
        
        # 重置自增ID
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='product_urls'")
        
        conn.commit()
        
        # 确认清空结果
        cursor.execute("SELECT COUNT(*) FROM product_urls")
        count_after = cursor.fetchone()[0]
        
        print(f"✅ 清空完成! 删除了 {count_before} 条URL记录")
        print(f"📊 清空后URL数量: {count_after}")
        
    except Exception as e:
        print(f"❌ 清空过程中发生错误: {e}")
        conn.rollback()
        
    finally:
        conn.close()

def get_source_from_url(url):
    """
    根据URL判断来源站点
    
    Args:
        url (str): 产品URL
        
    Returns:
        str: 来源站点标识
    """
    if not url:
        return 'other'
    
    domain = urlparse(url).netloc.lower()
    
    if 'shopee' in domain:
        return 'shopee'
    elif 'lazada' in domain:
        return 'lazada' 
    elif 'amazon' in domain:
        return 'amazon'
    elif 'fairprice' in domain:
        return 'fairprice'
    else:
        return 'other'

def clean_url_parameters(url):
    """
    清理URL中的查询参数，移除?后面的所有参数和#后面的片段标识符
    
    Args:
        url (str): 原始URL
        
    Returns:
        tuple: (清理后的URL, 是否进行了清理)
    
    Examples:
        原始: https://shopee.sg/product/123?ref=abc&utm_source=google#reviews
        清理: https://shopee.sg/product/123
        
        原始: https://www.amazon.sg/product/456?tag=tracking&source=fb
        清理: https://www.amazon.sg/product/456
    """
    if not url:
        return url, False
    
    try:
        parsed = urlparse(url)
        # 重新构建URL，去除查询参数和片段标识符
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        # 检查是否有参数被清理
        was_cleaned = bool(parsed.query or parsed.fragment)
        
        return clean_url, was_cleaned
    except Exception as e:
        print(f"⚠️  清理URL参数时发生错误: {e}, 原URL: {url}")
        return url, False

def extract_url_from_json_data(raw_json_str):
    """
    从JSON数据中提取产品URL，并自动清理查询参数
    
    Args:
        raw_json_str (str): 原始JSON字符串
        
    Returns:
        tuple: (清理后的URL, 是否进行了清理), 如果未找到URL则返回(None, False)
    """
    try:
        data = json.loads(raw_json_str)
        
        # 尝试多种可能的URL字段名
        url_fields = ['url', 'product_url', 'link', 'href', 'page_url']
        
        for field in url_fields:
            if field in data and data[field]:
                return clean_url_parameters(data[field])
        
        # 如果直接字段没找到，尝试在嵌套对象中查找
        if 'meta_info' in data and isinstance(data['meta_info'], dict):
            meta_info = data['meta_info']
            for field in url_fields:
                if field in meta_info and meta_info[field]:
                    return clean_url_parameters(meta_info[field])
        
        return None, False
        
    except (json.JSONDecodeError, TypeError) as e:
        print(f"解析JSON数据失败: {e}")
        return None, False

def import_existing_urls():
    """
    导入现有爬虫数据中的URL信息
    """
    print("🚀 开始导入现有爬虫数据中的URL信息...")
    
    # 获取数据库路径
    db_path = get_db_path()
    print(f"📁 数据库路径: {db_path}")
    
    # 创建URL模型实例
    url_model = ProductUrl(db_path)
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 查询所有爬虫数据源
        cursor.execute("""
            SELECT product_id, source_name, raw_json, uploaded_at
            FROM sources
            WHERE raw_json IS NOT NULL AND raw_json != ''
        """)
        
        sources = cursor.fetchall()
        print(f"📊 找到 {len(sources)} 条爬虫数据记录")
        
        if len(sources) == 0:
            print("❌ 没有找到爬虫数据，请先导入爬虫数据")
            return
        
        # 统计信息
        imported_count = 0
        skipped_count = 0
        error_count = 0
        cleaned_count = 0  # 清理了参数的URL数量
        
        # 获取今天的日期
        today = datetime.now().isoformat()
        
        # 处理每条记录
        for product_id, source_name, raw_json, uploaded_at in sources:
            try:
                # 从JSON数据中提取URL（已自动清理参数）
                url, was_cleaned = extract_url_from_json_data(raw_json)
                
                if not url:
                    print(f"⚠️  产品 {product_id} 的数据中未找到URL")
                    skipped_count += 1
                    continue
                
                # 显示是否清理了查询参数
                if was_cleaned:
                    print(f"🧹 产品 {product_id} 的URL已清理查询参数")
                    cleaned_count += 1
                
                # 根据URL判断来源站点
                detected_source = get_source_from_url(url)
                
                # 如果source_name存在且能匹配，使用source_name，否则使用检测到的来源
                final_source = source_name.lower() if source_name else detected_source
                if final_source not in ['shopee', 'lazada', 'amazon', 'fairprice']:
                    final_source = detected_source
                
                # 检查URL是否已存在
                existing_urls = url_model.get_urls_by_product_id(product_id)
                url_exists = any(existing_url['url'] == url for existing_url in existing_urls)
                
                if url_exists:
                    print(f"⏭️  产品 {product_id} 的URL已存在，跳过")
                    skipped_count += 1
                    continue
                
                # 添加URL到数据库
                success = url_model.add_url(
                    product_id=product_id,
                    url=url,
                    url_tag='package',  # 默认为整箱
                    source_name=final_source,
                    status='active',
                    collected_at=today
                )
                
                if success:
                    print(f"✅ 成功导入: {product_id} -> {final_source} -> {url[:50]}...")
                    imported_count += 1
                else:
                    print(f"❌ 导入失败: {product_id}")
                    error_count += 1
                    
            except Exception as e:
                print(f"❌ 处理产品 {product_id} 时发生错误: {e}")
                error_count += 1
        
        # 打印统计结果
        print("\n" + "="*50)
        print("📈 导入统计结果:")
        print(f"✅ 成功导入: {imported_count} 条")
        print(f"⏭️  跳过记录: {skipped_count} 条")
        print(f"❌ 错误记录: {error_count} 条")
        print(f"🧹 清理参数: {cleaned_count} 条")
        print(f"📊 总计处理: {len(sources)} 条")
        print("="*50)
        
        if imported_count > 0:
            print("🎉 URL数据导入完成！")
        else:
            print("⚠️  没有新的URL数据被导入")
    
    except Exception as e:
        print(f"❌ 导入过程中发生错误: {e}")
    
    finally:
        conn.close()
        print("🔒 数据库连接已关闭")

def show_import_preview():
    """
    显示导入预览，不执行实际导入
    """
    print("🔍 预览模式 - 分析现有爬虫数据...")
    
    # 获取数据库路径
    db_path = get_db_path()
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 查询所有爬虫数据源
        cursor.execute("""
            SELECT product_id, source_name, raw_json
            FROM sources
            WHERE raw_json IS NOT NULL AND raw_json != ''
            LIMIT 10
        """)
        
        sources = cursor.fetchall()
        
        print(f"📊 数据库中共有爬虫数据记录（前10条预览）:")
        print("-" * 80)
        
        for i, (product_id, source_name, raw_json) in enumerate(sources, 1):
            url, was_cleaned = extract_url_from_json_data(raw_json)
            detected_source = get_source_from_url(url) if url else 'unknown'
            
            print(f"{i:2d}. 产品ID: {product_id}")
            print(f"    来源: {source_name or 'N/A'} -> 检测: {detected_source}")
            print(f"    URL: {url[:60] if url else 'N/A'}{'...' if url and len(url) > 60 else ''}")
            if was_cleaned:
                print(f"    🧹 此URL已清理查询参数")
            print()
        
        # 统计总数
        cursor.execute("SELECT COUNT(*) FROM sources WHERE raw_json IS NOT NULL AND raw_json != ''")
        total_count = cursor.fetchone()[0]
        
        print(f"📈 总计: {total_count} 条爬虫数据记录")
        
    except Exception as e:
        print(f"❌ 预览过程中发生错误: {e}")
    
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("🔗 URL管理系统 - 爬虫数据导入工具")
    print("=" * 60)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == '--preview':
            show_import_preview()
        elif sys.argv[1] == '--clear':
            print("⚠️  即将清空所有现有的URL数据！")
            confirm = input("确认清空所有URL数据吗？(y/n): ").lower().strip()
            if confirm in ['y', 'yes', '是']:
                clear_existing_urls()
            else:
                print("❌ 用户取消清空操作")
        elif sys.argv[1] == '--clear-and-import':
            print("⚠️  即将清空所有现有的URL数据并重新导入！")
            confirm = input("确认清空并重新导入吗？(y/n): ").lower().strip()
            if confirm in ['y', 'yes', '是']:
                clear_existing_urls()
                print("\n" + "="*50)
                import_existing_urls()
            else:
                print("❌ 用户取消操作")
    else:
        print("可用参数:")
        print("  --preview           预览将要导入的数据")
        print("  --clear             清空现有URL数据")
        print("  --clear-and-import  清空并重新导入")
        print("")
        
        # 确认是否继续普通导入
        while True:
            confirm = input("确认开始导入吗？(仅导入新的URL，跳过重复的)(y/n): ").lower().strip()
            if confirm in ['y', 'yes', '是']:
                import_existing_urls()
                break
            elif confirm in ['n', 'no', '否']:
                print("❌ 用户取消导入")
                break
            else:
                print("请输入 y 或 n")