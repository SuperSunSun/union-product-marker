# Union Product Marker 项目集合

这是一个统一管理的电商数据采集和标注项目集合，包含三个主要组件：

## 📁 项目结构

```
union-product-marker/
├── union_product_marker_webserver/        # 产品标注Web服务
├── union_scraper_core/                    # 核心爬虫框架
├── union_scraper_htmlsaver_chrome_plugin/ # Chrome浏览器插件
└── README.md                             # 项目说明文档
```

## 🚀 项目组件

### 1. Union Scraper Core (`union_scraper_core/`)

**功能描述：** 一个用于抓取多个电商网站商品数据的爬虫框架

**主要特性：**
- 🕷️ 支持多电商平台（亚马逊、FairPrice等）
- 📊 统一的数据模型和输出格式
- 🖼️ 自动图片下载和保存
- ⚙️ 可配置的爬虫行为（延迟、重试等）
- 🔧 模块化设计，易于扩展

**技术栈：**
- Python 3.x
- BeautifulSoup4 (HTML解析)
- Requests (HTTP请求)
- LXML (XML/HTML处理)

**主要文件：**
- `main.py` - 主程序入口
- `config.json` - 配置文件
- `src/` - 源代码目录
- `input/` - 输入文件目录
- `output/` - 输出目录（已加入.gitignore）

**使用方法：**
```bash
cd union_scraper_core
python main.py
```

### 2. Union Product Marker Web Server (`union_product_marker_webserver/`)

**功能描述：** 基于Flask的Web应用，用于产品数据标注和管理

**主要特性：**
- 🌐 Web界面进行产品标注
- 📝 支持批量数据处理
- 💾 数据库存储和管理
- 📤 数据导出功能
- 🎨 现代化UI界面

**技术栈：**
- Flask 3.0.0 (Web框架)
- SQLite (数据库)
- Pandas (数据处理)
- Jinja2 (模板引擎)
- Pillow (图像处理)

**主要文件：**
- `run.py` - 应用启动文件
- `app/` - Flask应用代码
- `data/` - 数据文件目录
- `exports/` - 导出文件目录（已加入.gitignore）

**使用方法：**
```bash
cd union_product_marker_webserver
pip install -r requirements.txt
python run.py
```

### 3. Union Scraper HTML Saver Chrome Plugin (`union_scraper_htmlsaver_chrome_plugin/`)

**功能描述：** Chrome浏览器插件，用于保存网页HTML内容

**主要特性：**
- 🔌 Chrome扩展程序
- 📄 一键保存网页HTML
- 🎯 特别针对Shopee页面优化
- 💾 本地存储功能

**技术栈：**
- JavaScript (Chrome Extension API)
- Manifest V3
- HTML/CSS

**主要文件：**
- `manifest.json` - 插件配置文件
- `background.js` - 后台脚本
- `panel.html/js` - 弹出面板
- `output/` - 保存的HTML文件（已加入.gitignore）

**使用方法：**
1. 在Chrome中加载插件
2. 访问目标网页
3. 点击插件图标保存HTML
项目使用独立的虚拟环境
3. **浏览器兼容性**：Chrome插件仅支持Chrome浏览器
4. **网络请求**：爬虫功能需要稳定的网络连接


**Union Product Marker Team** - 让电商数据采集和标注更简单高效！ 