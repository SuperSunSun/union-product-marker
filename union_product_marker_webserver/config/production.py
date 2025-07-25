"""
生产环境配置模块

这个模块定义了生产环境的配置参数，包括：
1. 生产模式设置
2. 安全密钥管理
3. 数据库和文件路径配置
4. 性能优化设置

生产环境特点：
- 禁用调试模式，提高性能和安全性
- 使用环境变量管理敏感信息
- 与开发环境相同的文件大小限制

作者: Union Product Marker Team
版本: 1.0.0
"""

import os

class ProductionConfig:
    """
    生产环境配置类
    
    包含生产环境下的所有配置参数，用于Flask应用的初始化。
    这些配置注重安全性和性能，适合部署到生产服务器。
    """
    
    # 调试模式：生产环境中应该禁用，提高性能和安全性
    DEBUG = False
    
    # 安全密钥：从环境变量获取，如果没有则使用默认值
    # 在生产环境中应该设置一个强密钥作为环境变量
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    # 数据库路径：SQLite数据库文件的存储位置
    # 使用相对路径，确保在不同环境下都能正确找到
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'database.db')
    
    # 上传文件夹：用户上传文件的存储目录
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    
    # 导出文件夹：导出文件的存储目录
    EXPORT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')
    
    # 最大文件大小：限制上传文件的大小为16MB
    # 这个限制可以防止过大的文件影响系统性能
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size 