# -*- coding: utf-8 -*-
# union_scraper/input_loader.py

import os
import pandas as pd
from typing import List, Dict

def load_single_file(filepath: str) -> List[Dict]:
    """
    加载单个输入文件

    参数：
        filepath (str): 输入文件路径

    返回：
        list[dict]: 形如 [{'id': '1', 'url': 'https://...'}, ...] 的列表
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"输入文件未找到：{filepath}")

    # 从文件扩展名推断类型
    ext = os.path.splitext(filepath)[-1].lower()
    
    # 读取文件，指定 ID 列为字符串类型
    dtype = {'id': str}
    
    try:
        if ext == '.csv':
            df = pd.read_csv(filepath, dtype=dtype)
        elif ext in ['.xls', '.xlsx']:
            df = pd.read_excel(filepath, dtype=dtype)
        else:
            raise ValueError(f"不支持的文件格式：{ext}")
    except Exception as e:
        raise ValueError(f"读取文件 {filepath} 失败: {str(e)}")

    # 检查字段是否包含 'id' 和 'url'
    if not {'id', 'url'}.issubset(df.columns):
        raise ValueError(f"文件 {filepath} 必须包含 'id' 和 'url' 两列")

    # 清洗缺失数据，仅保留完整行
    df = df.dropna(subset=['id', 'url'])
    
    # 确保 ID 是字符串类型
    df['id'] = df['id'].astype(str).str.replace('.0', '', regex=False)

    # 转换为字典列表
    return df[['id', 'url']].to_dict(orient='records')

def load_input_files(config: Dict) -> List[Dict]:
    """
    加载所有启用的输入文件

    参数：
        config (dict): 包含输入文件配置的字典

    返回：
        list[dict]: 所有启用文件的数据合并后的列表
    """
    all_products = []

    for file_config in config['input']:
        if not file_config.get('enabled', False):
            print(f"[INFO] 跳过禁用的文件：{file_config['path']}")
            continue
            
        filepath = file_config['path']
        print(f"[INFO] 正在处理文件：{filepath}")
        try:
            products = load_single_file(filepath)
            print(f"[INFO] 从 {filepath} 加载了 {len(products)} 条数据")
            all_products.extend(products)
        except Exception as e:
            print(f"[ERROR] 加载文件 {filepath} 失败: {str(e)}")
            continue

    if not all_products:
        raise ValueError("没有成功加载任何商品数据")

    print(f"[INFO] 总共加载了 {len(all_products)} 条数据")
    return all_products
