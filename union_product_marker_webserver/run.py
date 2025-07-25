#!/usr/bin/env python3
"""
Union Product Marker 应用启动文件

这个文件是Union Product Marker应用的主入口点，负责：
1. 创建Flask应用实例
2. 配置应用环境
3. 启动开发服务器

作者: Union Product Marker Team
版本: 1.0.0
"""

import os
from app import create_app

# 创建Flask应用实例
# create_app()函数会根据环境变量选择合适的配置
app = create_app()

if __name__ == '__main__':
    # 启动 Flask 应用
    # debug=True 可以在代码更改时自动重载，并提供详细的错误页面
    # 在生产环境中应该设置为False以提高性能和安全性
    app.run(debug=True) 