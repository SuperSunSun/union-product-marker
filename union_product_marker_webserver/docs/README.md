# Union Product Marker

本地化商品标准信息标注系统，具备图形界面（Web GUI），服务于 HDBMart 上架数据的整理与导出。

## 功能简介

- 上传基础商品清单（CSV）
- 上传原始爬虫数据（JSON）
- 比对已有数据，显示差异，高亮标记
- 选择并确认更新入库
- 浏览全部商品信息，实时搜索与高亮
- 导出每商品图片和 JSON 结构

## 技术栈

- Python 3.12
- Flask + Bootstrap 5
- SQLite3 本地数据库
- jQuery + DataTables

## 项目架构

### 应用架构
- **应用工厂模式**：使用 `create_app()` 函数创建应用实例，支持不同环境配置
- **MVC 模式**：清晰的分层架构，模型-视图-控制器分离
- **蓝图组织**：按功能模块组织路由，提高代码可维护性
- **配置管理**：支持开发和生产环境，通过环境变量配置

### 代码组织原则
- **模块化设计**：功能模块独立，便于维护和扩展
- **标准化结构**：符合 Flask 最佳实践
- **分层架构**：数据层、业务层、表现层清晰分离

## 项目结构

```
union_product_marker/
├── app/                    # 应用主目录
│   ├── __init__.py         # 应用工厂
│   ├── models/             # 数据模型层
│   │   ├── __init__.py
│   │   └── product.py
│   ├── views/              # 视图层
│   │   ├── __init__.py
│   │   ├── index.py
│   │   ├── import_views.py
│   │   ├── crawler_views.py
│   │   ├── annotation_views.py
│   │   └── static_views.py
│   ├── static/             # 静态资源
│   │   ├── css/
│   │   │   ├── style.css
│   │   │   └── image-components.css
│   │   ├── js/
│   │   │   ├── image-components.js
│   │   │   └── product_preview.js
│   │   └── images/
│   ├── templates/          # 模板
│   └── utils/              # 工具类
│       └── db_util.py
├── config/                 # 配置管理
│   ├── __init__.py
│   ├── development.py
│   └── production.py
├── tests/                  # 测试目录
│   ├── __init__.py
│   ├── test_db_connection.py
│   ├── test_import.py
│   ├── test_annotation.py
│   └── check_db.py
├── data/                   # 数据目录
│   ├── database.db
│   └── 产品列表.csv
├── docs/                   # 文档目录
│   ├── README.md
│   ├── PRD.md
│   ├── CRAWLER_FEATURES.md
│   └── ANNOTATION_GUIDE.md
├── requirements.txt        # 依赖文件
├── .gitignore             # Git 忽略文件
└── run.py                 # 启动文件
```

## 如何启动

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动应用

```bash
python run.py
```

### 3. 访问应用

浏览器访问：`http://127.0.0.1:5000`

## 开发指南

### 运行测试

```bash
# 测试数据库连接
python tests/test_db_connection.py

# 测试数据导入
python tests/test_import.py

# 测试数据标注
python tests/test_annotation.py

# 检查数据库状态
python tests/check_db.py
```

### 环境配置

- 开发环境：`FLASK_ENV=development`
- 生产环境：`FLASK_ENV=production`

### 数据库

- 数据库文件位置：`data/database.db`
- 自动初始化：应用启动时自动创建表结构

## 功能模块

### 1. 基础商品导入 (`/import-basic`)
- 上传CSV文件
- 比对数据库现有数据
- 显示差异并确认更新

### 2. 爬虫数据上传 (`/crawler-upload`)
- 上传JSON格式的爬虫数据
- 预览数据结构
- 批量导入到数据库

### 3. 爬虫数据管理 (`/crawler-manage`)
- 浏览所有爬虫数据
- 按商品ID查看多来源数据
- 删除特定来源数据

### 4. 数据标注 (`/annotation`)
- 商品标准化标注
- 图片选择和分配
- 多来源数据整合

### 5. 商品列表 (`/`)
- 显示所有商品
- 实时搜索和筛选
- 状态管理

## 技术特性

### 前端组件系统
- **统一图片组件**：可复用的图片展示、选择、预览组件
- **响应式设计**：支持桌面和移动设备
- **交互体验**：统一的悬停效果、加载状态、消息提示
- **图标系统**：使用 Font Awesome 图标，提供一致的视觉体验

### 后端架构
- **应用工厂模式**：更好的模块化和测试支持
- **数据模型**：清晰的数据结构定义
- **视图组织**：按功能模块组织路由
- **工具函数**：通用的数据库操作和业务逻辑

### 用户体验优化
- **消息提示系统**：美观的 Bootstrap 提示，固定位置显示
- **加载状态管理**：统一的按钮加载状态显示
- **错误处理**：完善的错误提示和处理机制
- **数据验证**：前端和后端双重验证

## 注意事项

- 确保 `data/` 目录有写入权限
- 上传文件大小限制：16MB
- 支持的文件格式：CSV、JSON
- 图片文件支持本地路径和远程URL
- 数据库自动备份建议定期进行

## 开发规范

### 代码组织
- 遵循 Flask 最佳实践
- 使用应用工厂模式
- 按功能模块组织代码
- 保持代码简洁和可读性

### 测试要求
- 新功能需要添加对应测试
- 数据库操作需要测试覆盖
- 前端交互需要功能测试

### 文档维护
- 重要功能需要更新文档
- API 变更需要同步更新
- 部署流程需要文档化

# 前端图片插件（ImageComponents）使用说明

本项目集成了统一的图片显示插件 `ImageComponents`，用于各页面的图片容器、缩略图、懒加载、显示模式切换等功能。

## 功能简介
- 支持"本地图片/原始图片/不显示"三种显示模式
- 支持图片懒加载，提升页面性能
- 提供统一的图片显示模式选择器（下拉框）
- 支持图片说明文字、尺寸信息、点击放大等
- 可灵活集成到任意页面

## 主要API
- `ImageComponents.init(options)`：初始化插件（全局配置）
- `ImageComponents.createImageContainer(options)`：创建图片容器（含尺寸信息）
- `ImageComponents.createImageThumbnail(options)`：创建图片缩略图（常用于表格、卡片）
- `ImageComponents.createImageModeSelector(options)`：创建图片显示模式选择器（下拉框）
- `ImageComponents.setImageDisplayMode(mode, selector)`：切换所有图片的显示模式
- `ImageComponents.addLazyImages(elements)`：为新图片补全懒加载监听

## 页面集成方式
1. 页面JS初始化时调用：
   ```js
   ImageComponents.init({
     defaultMode: 'local',
     lazyLoad: true,
     placeholder: '/static/images/placeholder.svg'
   });
   ```
2. 挂载图片显示模式选择器：
   ```js
   const modeSelector = ImageComponents.createImageModeSelector({
     id: 'imageDisplayMode',
     defaultMode: 'local',
     onModeChange: function(mode) {
       ImageComponents.setImageDisplayMode(mode, '.image-thumbnail');
     }
   });
   document.querySelector('.image-controls').appendChild(modeSelector);
   ```
3. 渲染图片缩略图：
   ```js
   const thumb = ImageComponents.createImageThumbnail({
     localSrc: 'images/xxx.jpg',
     alt: '主图',
     label: '主图'
   });
   container.appendChild(thumb);
   ```
4. 切换显示模式时自动同步所有图片：
   ```js
   ImageComponents.setImageDisplayMode('local', '.image-thumbnail');
   ```

## 典型用法示例
- 见 `app/templates/annotation_list.html`、`batch_annotation.html`、`crawler_upload.html` 等页面
- 详细API见 `app/static/js/image-components.js` 文件头注释
