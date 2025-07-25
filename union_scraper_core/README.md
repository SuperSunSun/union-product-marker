# Union Scraper

一个用于抓取多个电商网站商品数据的爬虫框架。

## 项目结构

```
union_scraper/
├── src/                   # 源代码目录
│   ├── scrapers/         # 爬虫实现
│   │   ├── base.py      # 基础爬虫类
│   │   ├── amazon.py    # 亚马逊爬虫实现
│   │   └── fairprice.py # FairPrice爬虫实现
│   ├── models/          # 数据模型
│   │   ├── product_data.py    # 商品数据模型
│   │   ├── scraper_factory.py # 爬虫工厂类
│   │   ├── site_type.py      # 网站类型管理
│   │   └── file_manager.py   # 文件名管理
│   ├── utils/           # 工具类
│   └── core/           # 核心功能
├── input/              # 输入文件目录
├── output/             # 输出目录
│   ├── html/          # HTML文件
│   └── data/          # 解析后的数据
├── tools/             # 辅助工具
└── config.json        # 配置文件
```

## 主要组件

### 1. 数据模型 (models/)
- `ProductData`: 统一的商品数据模型
- `SiteType`: 网站类型管理
- `FileManager`: 文件名管理
- `ScraperFactory`: 爬虫工厂

### 2. 爬虫实现 (scrapers/)
- `BaseScraper`: 定义爬虫基本接口
- `AmazonScraper`: 亚马逊专用爬虫实现
  - 支持多种价格提取场景：
    1. 现价提取：
       - 优先从`.priceToPay .a-offscreen`中提取
       - 如果为空，则从`.aok-offscreen`中提取
    2. 原价提取：
       - 优先查找包含"List Price:"的容器
       - 从容器中提取`.a-price.a-text-price[data-a-strike="true"]`的价格
       - 如果未找到，直接在价格块中查找带有`data-a-strike="true"`属性的价格
- `FairpriceScraper`: FairPrice专用爬虫实现

### 3. 工具类 (utils/)
- 提供通用的工具函数和辅助类

### 4. 核心功能 (core/)
- 实现框架的核心功能
- 处理页面获取、数据解析等基础操作

## 配置文件结构

```json
{
    "input": [
        {
            "path": "input_fairprice_test.xlsx",
            "enabled": true
        },
        {
            "path": "input_amazon_test.xlsx",
            "enabled": true
        }
    ],
    "output": {
        "html_dir": "output/html",
        "data_dir": "output/data",
        "image_dir": "output/images"
    },
    "debug": {
        "use_local_html": false,
        "skip_image_download": false
    },
    "crawler": {
        "enable_random_delay": true,
        "max_sleep_seconds": 5
    },
    "sites": {
        "amazon": {
            "prefix": "a",
            "base_url": "https://www.amazon.sg"
        },
        "fairprice": {
            "prefix": "f",
            "base_url": "https://www.fairprice.com.sg"
        }
    }
}
```

## 使用方法

1. 准备输入文件
   - Excel或CSV格式
   - 必须包含 'id' 和 'url' 两列
   - 在配置文件中设置文件路径和启用状态

2. 配置文件设置
   - 配置支持的网站（前缀和基础URL）
   - 设置输出目录
   - 配置调试选项
   - 设置爬虫行为（如延迟时间）

3. 运行爬虫
   ```python
   from src.models.scraper_factory import ScraperFactory
   from src.models.product_data import ProductData
   
   # 加载配置
   config = load_config()
   
   # 加载输入文件
   product_list = load_input_files(config)
   
   # 处理每个商品
   for product in product_list:
       # 自动创建对应的爬虫
       scraper = ScraperFactory.create_scraper(product["url"], config)
       
       # 获取页面
       html = scraper.fetch_page(product["url"], product["id"])
       
       # 解析数据
       data = scraper.parse_data(html)
       
       # 保存数据和图片
       scraper.save_product_data(data, product["id"])
       scraper.download_images(data.image_urls_original, product["id"])
   ```

## 输出格式

每个商品的数据将被保存为以下格式：

```
output/
├── data/                 # 商品数据目录
│   └── {prefix}_{id}.json # 商品数据
├── images/              # 图片目录
│   └── {prefix}_{id}/   # 商品图片
└── html/               # HTML缓存
    └── {prefix}_{id}.html # 原始页面
```

商品数据JSON包含以下字段：
- `id`: 商品ID
- `url`: 商品URL
- `product_name`: 商品名称
- `brand`: 品牌
- `price_current`: 当前价格
- `price_original`: 原价（如果有）
- `image_urls_original`: 原始图片URL列表
- `image_urls_simplified`: 简化后的图片URL列表
- `infos`: 其他商品信息（因网站而异）
  - `meta_info`: 基本信息
  - `about_this_item`: 商品特点
  - `product_description`: 商品描述
  - `product_infomation`: 商品信息
  - `product_details`: 商品详情
  - `important_information`: 重要信息 