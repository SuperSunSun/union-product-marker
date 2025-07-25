# -*- coding: utf-8 -*-
# union_scraper/image_downloader.py

import os
import requests
from urllib.parse import urlparse
from ..utils.file_utils import save_file, ensure_dir_exists

def download_images(image_urls, folder_path, filename_generator):
    """
    下载图片列表中的所有图片到指定文件夹。

    参数：
        image_urls (list): 图片 URL 列表
        folder_path (str): 保存图片的本地目录
        filename_generator (callable): 文件名生成函数，接收索引参数，返回完整的文件名

    返回：
        list[str]: 所有下载后图片的本地路径
    """
    if not image_urls:
        return []

    ensure_dir_exists(folder_path)
    saved_paths = []
    total_images = len(image_urls)

    print(f"[INFO] Found {total_images} images to download")
    
    for idx, url in enumerate(image_urls, start=1):
        try:
            print(f"[INFO] Downloading image {idx}/{total_images}: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # 使用生成器函数获取文件名
            filename = filename_generator(idx)
            filepath = os.path.join(folder_path, filename)

            save_file(filepath, response.content, mode='wb')

            print(f"[INFO] Successfully saved image to: {filepath}")
            saved_paths.append(filepath)

        except Exception as e:
            print(f"[WARN] Failed to download image {url}: {e}")
            continue

    print(f"[INFO] Downloaded {len(saved_paths)}/{total_images} images successfully")
    return saved_paths
