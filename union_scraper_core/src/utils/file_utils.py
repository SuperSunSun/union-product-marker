# -*- coding: utf-8 -*-
# union_scraper/utils/file_utils.py

import os
import json
import time

def ensure_dir_exists(dir_path):
    """确保目录存在，如果不存在则创建"""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def ensure_path_exists(*paths):
    """
    确保一个或多个路径存在
    
    参数：
        *paths: 一个或多个路径，可以是目录或文件路径
               如果是文件路径，会创建其父目录
    """
    for path in paths:
        if path:
            if os.path.splitext(path)[1]:  # 如果有扩展名，说明是文件路径
                dir_path = os.path.dirname(path)
            else:
                dir_path = path
            ensure_dir_exists(dir_path)

def save_file(filepath: str, content, mode='w', encoding="utf-8"):
    """
    保存文件并更新时间戳
    
    参数：
        filepath: 文件路径
        content: 文件内容
        mode: 写入模式 ('w' 或 'wb')
        encoding: 编码方式（文本模式时使用）
    """
    # 确保目录存在
    ensure_path_exists(filepath)
    
    # 获取当前时间戳
    current_time = time.time()
    
    # 保存文件
    kwargs = {'encoding': encoding} if 'b' not in mode else {}
    with open(filepath, mode, **kwargs) as f: # type: ignore
        f.write(content)
    
    # 更新文件时间戳
    os.utime(filepath, (current_time, current_time))

def write_json(filepath: str, data: dict):
    """保存JSON文件并更新时间戳"""
    content = json.dumps(data, ensure_ascii=False, indent=2)
    save_file(filepath, content, mode='w', encoding='utf-8')
