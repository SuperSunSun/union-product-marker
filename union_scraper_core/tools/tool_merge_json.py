# -*- coding: utf-8 -*-
"""
商品数据合并工具

此工具用于合并output目录下所有的商品JSON文件，主要功能包括：
1. 按照不同网站来源对商品数据进行分类
2. 为每个商品数据添加本地图片路径信息（local_images字段）
3. 生成一个包含所有商品数据的合并JSON文件

使用方法：
    直接运行此脚本：python tools/tool_merge_json.py
"""

import os
import json
from loguru import logger
from src.utils.file_utils import write_json
from src.utils.time_utils import get_iso_timestamp

# ===== 配置常量 =====
# output目录的绝对路径，用于存放商品数据和图片
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../output"))
# 配置文件路径，包含各网站的配置信息
CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config.json"))
# ====================

def load_config():
    """
    加载配置文件
    
    Returns:
        dict: 包含网站配置信息的字典
    """
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"无法加载配置文件 {CONFIG_PATH}: {e}")
        raise

def get_prefix_from_filename(filename):
    """
    从文件名中提取网站前缀
    
    Args:
        filename (str): 文件名，格式为 "prefix_其他内容"
        
    Returns:
        str: 提取出的网站前缀，如果无法提取则返回None
    """
    parts = filename.split('_')
    return parts[0] if parts else None

def merge_all_jsons(output_dir, sites_config):
    """
    遍历output目录下所有子目录，合并商品JSON数据并添加本地图片信息
    
    Args:
        output_dir (str): 输出目录路径
        sites_config (list): 包含所有网站配置的列表，每个配置包含name和prefix字段
        
    Returns:
        dict: 按网站分类的商品数据字典，格式为：
            {
                "网站名称1": [商品数据1, 商品数据2, ...],
                "网站名称2": [商品数据1, 商品数据2, ...]
            }
    """
    # 初始化结果字典，使用网站名称作为key
    merged = {site['name']: [] for site in sites_config}
    # 支持的图片文件扩展名
    valid_img_ext = {'.jpg', '.jpeg', '.png', '.webp'}
    
    # 创建前缀到网站名称的映射字典，用于快速查找
    prefix_to_name = {site['prefix']: site['name'] for site in sites_config}

    # 遍历输出目录
    for subdir in os.listdir(output_dir):
        sub_path = os.path.join(output_dir, subdir)
        if not os.path.isdir(sub_path) or subdir == 'html':  # 排除html目录
            continue

        # 遍历目录中的所有JSON文件
        for filename in os.listdir(sub_path):
            if not filename.endswith('.json'):
                continue

            # 从JSON文件名获取前缀
            prefix = get_prefix_from_filename(filename)
            if not prefix or prefix not in prefix_to_name:
                logger.warning(f"跳过无效文件名: {filename}")
                continue

            json_file = os.path.join(sub_path, filename)
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    # 获取 local_images 列表（只包含与当前网站前缀匹配的图片）
                    local_images = []
                    for fname in sorted(os.listdir(sub_path)):
                        ext = os.path.splitext(fname)[1].lower()
                        if ext in valid_img_ext:
                            # 检查图片文件名是否与当前网站前缀匹配
                            img_prefix = get_prefix_from_filename(fname)
                            if img_prefix == prefix:
                                local_images.append(f"{subdir}/{fname}")

                    data["local_images"] = local_images
                    
                    # 将数据添加到对应网站的列表中
                    site_name = prefix_to_name[prefix]
                    merged[site_name].append(data)
                    #logger.debug(f"已处理: {filename}")

            except Exception as e:
                logger.error(f"无法读取 {json_file}: {e}")
                continue

    # 移除空列表
    merged = {k: v for k, v in merged.items() if v}
    return merged

def main(add_timestamp_suffix=True):
    """
    主函数：执行数据合并和输出操作
    
    Args:
        add_timestamp_suffix (bool): 是否在输出文件名中添加时间戳
            True: 输出文件名格式为 merge_YYYYMMDDHHMMSS.json
            False: 输出文件名为 merge.json
    """
    logger.info(f"正在合并目录：{OUTPUT_DIR}")
    
    try:
        # 加载配置
        config = load_config()
        
        # 按网站分类合并数据
        merged_data = merge_all_jsons(OUTPUT_DIR, config['sites'])
        
        # 统计每个网站的数据量
        total_count = sum(len(products) for products in merged_data.values())
        logger.info(f"共合并 {total_count} 个 JSON 文件")
        for site_name, products in merged_data.items():
            logger.info(f"- {site_name}: {len(products)} 个商品")

        # 生成输出文件名
        if add_timestamp_suffix:
            timestamp = get_iso_timestamp().replace(":", "").replace("-", "").replace(".", "")
            output_filename = f"merge_{timestamp}.json"
        else:
            output_filename = "merge.json"

        merged_json = {
            "merged_at": get_iso_timestamp(),
            "base_path": OUTPUT_DIR,
            "products": merged_data
        }

        json_path = os.path.join(OUTPUT_DIR, output_filename)
        write_json(json_path, merged_json)
        logger.info(f"JSON 文件已保存：{json_path}")
        logger.info("合并任务完成")

    except Exception as e:
        logger.error(f"合并过程中发生错误: {e}")
        logger.exception(e)  # 输出完整的异常堆栈
        raise

if __name__ == "__main__":
    main()
