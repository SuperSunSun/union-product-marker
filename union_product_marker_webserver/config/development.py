"""
开发环境配置模块

这个模块定义了开发环境的配置参数，包括：
1. 调试模式设置
2. 数据库路径配置
3. 文件上传配置
4. 安全密钥设置

开发环境特点：
- 启用调试模式，提供详细的错误信息
- 使用简单的密钥（生产环境需要更改）
- 文件大小限制为16MB

作者: Union Product Marker Team
版本: 1.0.0
"""

import os

class DevelopmentConfig:
    """
    开发环境配置类
    
    包含开发环境下的所有配置参数，用于Flask应用的初始化。
    这些配置在开发过程中提供更好的调试体验。
    """
    
    # 调试模式：启用后会显示详细的错误信息和自动重载
    DEBUG = True
    
    # 安全密钥：用于会话加密等安全功能
    # 注意：在生产环境中应该使用环境变量或更复杂的密钥
    SECRET_KEY = 'dev-secret-key-change-in-production'
    
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