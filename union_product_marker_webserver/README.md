# Union Product Marker WebServer

一个基于Flask的商品数据标准化管理Web应用，专为电商平台产品数据整理、标注和导出而设计。

## 🚀 项目简介

Union Product Marker WebServer 是一个本地化的商品标准信息标注系统，具备图形化Web界面，主要用于：

- 📥 商品数据的批量导入和管理
- 🏷️ 产品信息的标准化标注
- 🔍 多来源数据的比对和整合
- 📤 标准化数据的导出和分发
- ✅ 数据质量自动检查和验证

## ✨ 核心功能

### 📥 数据导入模块
- **基础数据导入**: 支持CSV格式的产品基础信息导入
- **爬虫数据导入**: 支持JSON格式的爬虫数据批量导入
- **数据预览**: 上传前预览数据结构和统计信息
- **差异比对**: 自动检测数据差异并高亮显示

### 🏷️ 产品标注模块
- **单个产品标注**: 支持统一名称、品牌、价格等标准化标注
- **批量标注**: 支持CSV导出/导入进行批量操作
- **图片管理**: 支持多张图片的选择、分配和预览
- **自动检查**: 内置数据质量检查规则，自动发现问题

### 📊 数据管理模块
- **产品列表**: 显示所有产品的基本信息和状态
- **实时搜索**: 支持ID/名称搜索，实时高亮匹配结果
- **状态筛选**: 按标注状态、备注状态等条件筛选
- **数据统计**: 提供详细的数据统计和概览

### 📤 数据导出模块
- **选择性导出**: 支持选择特定产品进行导出
- **图片处理**: 自动resize和压缩处理
- **标准化输出**: 生成标准化的目录结构和JSON文件
- **文件管理**: 提供导出文件浏览和清理功能

## 🛠️ 技术栈

### 后端技术
- **Python 3.12+**: 主要开发语言
- **Flask 3.0.0**: Web框架
- **SQLite3**: 本地数据库
- **Pandas**: 数据处理
- **Pillow**: 图片处理

### 前端技术
- **Bootstrap 5**: UI框架
- **jQuery**: JavaScript库
- **DataTables**: 表格组件
- **Font Awesome**: 图标库

### 开发工具
- **应用工厂模式**: Flask最佳实践
- **蓝图架构**: 模块化路由管理
- **配置管理**: 开发/生产环境配置
- **自动测试**: 完整的测试覆盖

## 📁 项目结构

```
union_product_marker_webserver/
├── app/                    # 主应用目录
│   ├── __init__.py         # 应用工厂
│   ├── models/             # 数据模型
│   │   ├── product.py      # 产品数据模型
│   │   └── auto_checker.py # 自动检查器
│   ├── views/              # 视图控制器
│   │   ├── index.py        # 首页视图
│   │   ├── import_views.py # 导入视图
│   │   ├── crawler_views.py # 爬虫数据视图
│   │   ├── annotation_views.py # 标注视图
│   │   ├── batch_annotation_views.py # 批量标注视图
│   │   ├── export_views.py # 导出视图
│   │   └── static_views.py # 静态资源视图
│   ├── templates/          # HTML模板
│   ├── static/             # 静态资源
│   │   ├── css/            # 样式文件
│   │   ├── js/             # JavaScript文件
│   │   └── images/         # 图片资源
│   └── utils/              # 工具函数
│       ├── db_util.py      # 数据库工具
│       └── image_util.py   # 图片处理工具
├── config/                 # 配置文件
│   ├── development.py      # 开发环境配置
│   └── production.py       # 生产环境配置
├── data/                   # 数据目录
├── docs/                   # 文档目录
├── exports/                # 导出文件目录
├── uploads/                # 上传文件目录
├── tests/                  # 测试目录
├── requirements.txt        # 依赖文件
└── run.py                  # 启动文件
```

## 🚀 快速开始

### 环境要求
- Python 3.12 或更高版本
- 支持的操作系统：Windows、macOS、Linux

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd union_product_marker_webserver
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **启动应用**
```bash
python run.py
```

4. **访问应用**
打开浏览器访问：`http://127.0.0.1:5000`

### 环境配置

- **开发环境**: 默认配置，支持热重载和详细错误信息
- **生产环境**: 设置环境变量 `FLASK_ENV=production`

## 📖 使用指南

### 1. 基础数据导入
1. 访问 `/import-basic` 页面
2. 上传包含产品ID和名称的CSV文件
3. 系统自动比对数据库差异
4. 确认并导入数据

### 2. 爬虫数据导入
1. 访问 `/crawler-upload` 页面
2. 上传JSON格式的爬虫数据
3. 预览数据结构和统计信息
4. 执行批量导入

### 3. 产品标注
1. 访问 `/annotation` 页面
2. 选择待标注的产品
3. 填写统一名称、品牌、价格等信息
4. 选择和管理产品图片
5. 保存标注数据

### 4. 数据导出
1. 访问 `/export-data` 页面
2. 选择要导出的产品
3. 配置导出选项
4. 执行导出操作
5. 下载标准化数据文件

## 🧪 测试

运行测试套件：

```bash
# 测试数据库连接
python tests/test_db_connection.py

# 测试数据导入功能
python tests/test_import.py

# 测试标注功能
python tests/test_annotation.py

# 测试自动检查器
python tests/test_auto_checker.py

# 检查数据库状态
python tests/check_db.py
```

## ⚙️ 配置说明

### 数据库配置
- 数据库文件：`data/database.db`
- 自动初始化：应用启动时自动创建表结构
- 备份建议：定期备份数据库文件

### 文件上传配置
- 最大文件大小：16MB
- 支持格式：CSV、JSON、图片文件
- 上传目录：`uploads/`

### 导出配置
- 导出目录：`exports/`
- 图片处理：自动resize和压缩
- 文件命名：按产品ID命名

## 🎨 前端组件

### 图片组件系统
项目集成了统一的图片显示组件，支持：
- 三种显示模式：本地图片/原始图片/不显示
- 图片懒加载，提升性能
- 统一的图片选择器
- 响应式设计

### 使用示例
```javascript
// 初始化图片组件
ImageComponents.init({
    defaultMode: 'local',
    lazyLoad: true,
    placeholder: '/static/images/placeholder.svg'
});

// 创建图片缩略图
const thumb = ImageComponents.createImageThumbnail({
    localSrc: 'images/product.jpg',
    alt: '产品图片',
    label: '主图'
});
```

## 📊 数据模型

### 产品数据结构
```json
{
    "id": "产品唯一标识",
    "name": "产品名称",
    "brand": "品牌信息",
    "annotation_data": {
        "unified_name": "统一名称",
        "brand": "标准品牌",
        "price_listed": "上架价格",
        "price_cost": "成本价格",
        "images": {
            "main": "主图URL",
            "front": "正面图URL",
            "back": "背面图URL"
        }
    },
    "notes": "手动备注",
    "auto_notes": "自动检查备注",
    "created_at": "创建时间",
    "updated_at": "更新时间"
}
```

## 🔍 自动检查规则

系统内置多种数据质量检查规则：

- **图片检查**: 主图存在性、图片数量、本地路径完整性
- **价格检查**: 价格合理性、价格格式
- **品牌检查**: 品牌信息完整性
- **名称检查**: 统一名称完整性

## ⚠️ 注意事项

1. **文件权限**: 确保 `data/`、`uploads/`、`exports/` 目录有写入权限
2. **文件大小**: 上传文件限制为16MB
3. **数据备份**: 建议定期备份数据库文件
4. **图片处理**: 大量图片处理可能需要较长时间
5. **浏览器兼容**: 建议使用现代浏览器（Chrome、Firefox、Safari、Edge）

---

**Union Product Marker WebServer** - 让商品数据管理更简单、更高效！ 