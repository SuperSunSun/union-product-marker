"""
数据模型包

这个包包含应用的数据模型定义，用于：
1. 定义数据库表结构
2. 提供数据访问接口
3. 实现业务逻辑层

当前包含的模型：
- Product: 产品数据模型，处理产品相关的数据库操作
- AutoChecker: 自动检查器，用于检查产品标注数据的质量问题

作者: Union Product Marker Team
版本: 1.0.0
"""

# 导入主要模型类，方便其他模块使用
from .product import Product
from .auto_checker import AutoChecker, auto_checker

# Models package 