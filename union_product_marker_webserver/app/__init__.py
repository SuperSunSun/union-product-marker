"""
Union Product Marker Flask应用初始化模块

这个模块负责：
1. 创建Flask应用实例
2. 配置应用环境（开发/生产）
3. 注册所有蓝图
4. 初始化数据库
5. 创建必要的目录结构

作者: Union Product Marker Team
版本: 1.0.0
"""

from flask import Flask
from config.development import DevelopmentConfig
from config.production import ProductionConfig
import os

def create_app(config_name=None):
    """
    应用工厂函数
    
    根据环境变量或传入的参数创建并配置Flask应用实例。
    这是Flask应用的标准初始化模式，支持不同环境的配置。
    
    Args:
        config_name (str, optional): 配置名称，可以是'development'或'production'
                                    如果为None，则从环境变量FLASK_ENV获取
    
    Returns:
        Flask: 配置完成的Flask应用实例
    """
    app = Flask(__name__)
    
    # 根据环境变量选择配置
    # 如果没有指定config_name，则从环境变量FLASK_ENV获取
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # 根据配置名称加载相应的配置类
    if config_name == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)
    
    # 确保必要的目录存在
    # 这些目录用于存储上传的文件、导出的数据等
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['EXPORT_FOLDER'], exist_ok=True)
    
    # 注册蓝图
    # 蓝图是Flask中组织路由和视图的方式，每个功能模块使用一个蓝图
    from app.views.index import index_bp                    # 首页相关路由
    from app.views.import_views import import_basic_bp      # 基础数据导入路由
    from app.views.crawler_views import crawler_upload_bp, crawler_manage_bp  # 爬虫数据管理路由
    from app.views.static_views import static_images_bp     # 静态图片服务路由
    from app.views.annotation_views import annotation_bp    # 产品标注路由
    from app.views.batch_annotation_views import batch_annotation_bp  # 批量标注路由
    from app.views.export_views import export_bp            # 导出数据路由
    from app.views.url_manage_views import url_manage_bp    # URL管理路由
    
    app.register_blueprint(index_bp)
    app.register_blueprint(import_basic_bp)
    app.register_blueprint(crawler_upload_bp)
    app.register_blueprint(crawler_manage_bp)
    app.register_blueprint(static_images_bp)
    app.register_blueprint(annotation_bp)
    app.register_blueprint(batch_annotation_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(url_manage_bp)
    
    # 初始化数据库
    # 确保数据库表结构存在，如果不存在则创建
    from app.utils.db_util import init_db
    init_db()
    
    return app 