# -*- coding: utf-8 -*-
# amazon_scraper/main.py

import sys
import time
import random
import json
from loguru import logger
from src.core.input_loader import load_input_files
from src.models.scraper_factory import ScraperFactory
from tools.tool_merge_json import main as merge_json_main

def setup_logger(log_file='log.txt'):
    """
    配置logger，同时输出到控制台和文件
    """
    # 移除默认的控制台输出
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"
    )
    
    # 添加文件输出，设置 mode='w' 使其每次运行时覆盖文件
    logger.add(
        log_file,
        rotation="500 MB",  # 文件大小超过500MB时轮转
        retention="10 days",  # 保留10天的日志
        compression="zip",  # 压缩旧日志
        encoding='utf-8',
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        mode='w'  # 使用写入模式，而不是追加模式
    )

def main():
    try:
        # 1. 加载配置
        config = json.load(open('config.json', 'r', encoding='utf-8'))
        
        # 2. 设置日志
        setup_logger()
        
        # 3. 加载输入文件
        logger.info("Loading input files...")
        product_list = load_input_files(config)
        logger.info(f"Loaded {len(product_list)} products in total.\n")

        # 4. 处理每个商品
        for idx, product in enumerate(product_list, 1):
            product_id = product["id"]
            url = product["url"]
            logger.info(f"\n({idx}/{len(product_list)}) Processing ID={product_id}, URL={url}")

            # 检查 URL 是否有效
            if url == '--' or not url.startswith(('http://', 'https://')):
                logger.info(f"Skipping invalid URL for ID={product_id}")
                continue

            try:
                # 5. 创建爬虫实例
                scraper = ScraperFactory.create_scraper(url, product_id, config)
                
                # 6. 获取HTML内容
                if config['debug']['use_local_html']:
                    logger.info("Using local HTML file...")
                    html = scraper.get_local_html()
                else:
                    logger.info("Fetching page...")
                    html = scraper.fetch_page()

                if not html:
                    logger.error(f"Failed to get HTML(NO HTML) for ID={product_id}")
                    continue

                # 7. 解析HTML
                logger.info("Parsing HTML...")
                try:
                    data = scraper.parse_data(html)
                except Exception as e:
                    logger.error(f"Failed to parse HTML for ID={product_id}: {e}")
                    logger.exception(e)  # 这会输出完整的异常堆栈
                    continue

                # 8. 保存数据
                logger.info("Saving data...")
                scraper.save_product_data(data, config['output']['data_dir'])

                # 9. 下载图片（如果不是调试模式）
                if not config['debug'].get('skip_image_download', False):
                    logger.info("Downloading images...")
                    local_images = scraper.download_images()
                    data['local_images'] = local_images
                else:
                    logger.info("Skipping image download (debug mode)...")

                # 10. 延时控制
                if config['crawler']['enable_random_delay']:
                    delay = random.uniform(1, config['crawler']['max_sleep_seconds'])
                    logger.info(f"Sleeping for {delay:.2f} seconds...")
                    time.sleep(delay)

            except Exception as e:
                logger.error(f"Failed to process ID={product_id}: {e}")
                logger.exception(e)  # 输出完整的异常堆栈
                continue

        # 11. 如果配置了自动合并JSON，则执行合并
        if config.get('crawler', {}).get('enable_merge_json', False):
            merge_json_main(add_timestamp_suffix=False)

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        logger.exception(e)  # 输出完整的异常堆栈
        return 1

if __name__ == "__main__":
    sys.exit(main())
