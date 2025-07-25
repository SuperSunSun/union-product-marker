# -*- coding: utf-8 -*-
# union_scraper/utils/time_utils.py

from datetime import datetime

def get_iso_timestamp():
    """
    返回当前时间的 ISO 8601 格式字符串，例如：2025-05-19T15:04:05.123456

    返回：
        str: 当前时间戳（精确到微秒）
    """
    return datetime.now().isoformat()
