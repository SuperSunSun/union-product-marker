# 数据标注功能使用指南

## 功能概述

数据标注功能允许用户对商品进行标准化标注，将来自不同平台的爬虫数据整合成统一的商品信息格式。

## 主要功能

### 1. 标注列表页面 (`/annotation`)
- 显示所有需要标注的商品
- 显示标注状态（未标注、已标注、待标注）
- 支持搜索和筛选
- 点击"开始标注"或"重新标注"进入标注页面

### 2. 单个商品标注页面 (`/annotation/<product_id>`)
- 左右分栏布局
- 左侧：标注表单
- 右侧：爬虫数据源（按crawler_manage模式展示）

## 图片组件系统

### 统一图片组件架构

系统采用统一的图片组件系统，提供可复用的图片展示、选择、预览功能：

#### 核心组件文件
- **CSS文件**: `app/static/css/image-components.css` - 统一图片样式
- **JS文件**: `app/static/js/image-components.js` - 图片功能组件

#### 主要组件类型
- `.image-container` - 基础图片容器
- `.image-preview` - 图片预览组件
- `.image-grid` - 图片网格布局
- `.image-picker-item` - 图片选择器项目
- `.image-assign-tag` - 图片分配标签
- `.image-actions` - 图片操作按钮

#### 核心功能函数
- `createImageContainer()` - 创建图片容器
- `createImagePreview()` - 创建图片预览
- `createImageSelector()` - 创建图片选择器
- `createImageAssignmentTags()` - 创建分配标签
- `createImagePickerModal()` - 创建选择模态框
- `toggleImageSource()` - 切换图片源
- `toggleAllImageSources()` - 批量切换图片源

### 图片组件特性

#### 响应式设计
```css
@media (max-width: 768px) {
  .image-grid-container {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 480px) {
  .image-container img {
    height: 100px;
    width: 100px;
  }
}
```

#### 交互效果
- 悬停时边框颜色变化
- 图片缩放动画
- 尺寸信息显示/隐藏
- 加载状态指示

#### 使用示例
```javascript
// 创建图片容器
const container = ImageComponents.createImageContainer({
  src: 'image.jpg',
  alt: '商品图片',
  localSrc: '/images/local.jpg',
  remoteSrc: 'https://example.com/image.jpg',
  useLocal: true,
  dimensions: true,
  clickable: true
});

// 切换图片源
ImageComponents.toggleImageSource(container, true);
```

## 标注数据结构

每个商品的标注数据包含以下字段：

```json
{
  "id": "唯一商品ID",
  "base_name": "数据库基础名称",
  "display_name": "前台显示名称",
  "brand": "品牌",
  "cost_price": 0.0,
  "list_price": 0.0,
  "source_prices": [
    {
      "platform": "Amazon",
      "price": 16.81,
      "url": "https://example.com/product-url"
    }
  ],
  "images": {
    "main": "主图 URL",
    "front": "单品正面图 URL",
    "back": "单品背面图 URL",
    "box": "整箱图 URL",
    "extra": "其他图 URL",
    "nutrition": "营养表图 URL"
  },
  "image_local_paths": {
    "main": "本地路径/main.jpg",
    "front": "本地路径/front.jpg",
    "back": "本地路径/back.jpg",
    "box": "本地路径/box.jpg",
    "extra": "本地路径/extra.jpg",
    "nutrition": "本地路径/nutrition.jpg"
  },
  "description": "统一商品描述",
  "highlights": [
    "简洁卖点1",
    "简洁卖点2"
  ]
}
```

## 使用方法

### 1. 访问标注列表
1. 在导航栏点击"🏷️ 数据标注"
2. 或直接访问 `http://localhost:5000/annotation`

### 2. 开始标注
1. 在标注列表中找到要标注的商品
2. 点击"开始标注"按钮
3. 进入标注页面

### 3. 标注操作
1. **商品ID**：
   - 显示商品ID，不可修改
   - 只读字段，背景色为灰色

2. **文字标注**：
   - 点击右侧爬虫数据中的文字内容
   - 或点击"复制"按钮
   - 内容会自动填充到左侧对应字段

3. **图片标注**：
   - 点击左侧的图片缩略图框
   - 在弹出的图片选择器中选择合适的图片
   - 支持从所有爬虫来源的图片中选择
   - 可选择使用本地图片或原始URL
   - 支持重新选择，会替换现有图片
   - 鼠标悬停可显示移除按钮

4. **手动输入**：
   - 直接在左侧表单中输入或修改内容
   - 支持所有标准HTML表单控件

### 4. 保存标注
1. 填写需要标注的字段（所有字段都是可选的）
2. 点击"保存标注"按钮
3. 系统会保存数据到数据库
4. 保存成功后自动返回标注列表

## 字段说明

### 基本信息
- **商品ID**：只读字段，显示商品唯一标识
- **数据库基础名称**：用于数据库存储的名称
- **前台显示名称**：用户界面显示的名称
- **品牌**：商品品牌信息

### 价格信息
- **成本价**：商品成本价格
- **标价**：商品标价
- **来源价格**：可添加多个来源的价格信息

### 图片信息
- **主图**：商品主图
- **单品正面图**：商品正面图
- **单品背面图**：商品背面图
- **整箱图**：整箱包装图
- **其他图**：其他相关图片
- **营养表图**：营养信息表图

### 描述信息
- **统一商品描述**：标准化的商品描述
- **简洁卖点**：每行一个卖点

## 图片标注功能详解

### 缩略图显示
- 每个图片类型都有一个120x120像素的缩略图框
- 已选择的图片会显示在缩略图中
- 未选择的图片显示"点击选择XX图"提示
- 鼠标悬停时显示红色移除按钮

### 图片选择器
- 点击缩略图打开图片选择器模态框
- 显示该产品所有爬虫来源的所有图片
- 支持网格布局，每张图片显示来源和产品信息
- 可选择优先使用本地图片或原始URL
- 点击图片进行选择，选中的图片会有绿色边框
- 确认选择后自动关闭模态框并更新缩略图

### 图片存储
- **实际URL**：存储原始爬虫图片的完整URL
- **本地URL**：存储本地图片服务的路径（如`/images/xxx.jpg`）
- 两种URL都会保存，便于后续使用

## 数据源支持

目前支持以下爬虫数据源的自动解析：
- Amazon
- FairPrice
- 其他通用格式

### 爬虫数据展示
右侧爬虫数据按以下模式展示：
- **来源分组**：每个数据源独立显示
- **基本信息**：标题、品牌、价格、描述
- **图片展示**：网格布局显示所有图片
- **详细信息**：表格形式展示所有附加信息

## 技术特性

- **响应式设计**：支持桌面和移动设备
- **图片可视化**：图片直接显示，无需输入URL
- **智能选择**：从所有爬虫来源中选择最佳图片
- **双URL存储**：同时保存本地和原始URL
- **数据持久化**：标注数据保存到SQLite数据库
- **状态管理**：自动更新商品标注状态
- **无必填字段**：所有字段都是可选的
- **爬虫数据展示**：按crawler_manage模式展示数据源
- **统一组件系统**：可复用的图片组件，提高开发效率

## 数据库结构

### products 表新增字段
- `annotation_data`: TEXT - 存储JSON格式的标注数据
- `status`: TEXT - 标注状态（pending/annotated）

### sources 表
- 存储爬虫原始数据，用于右侧数据源显示

## 开发说明

### 添加新的数据源解析器
1. 在 `annotation_views.py` 中添加新的解析函数
2. 在 `get_crawler_data()` 函数中添加对应的处理逻辑

### 修改标注数据结构
1. 更新 `annotation_detail.html` 模板中的表单字段
2. 更新 `saveAnnotation()` JavaScript函数
3. 更新 `validate_annotation_data()` 验证函数

### 自定义样式
- 主要样式在 `annotation_detail.html` 的 `<style>` 块中
- 可以修改CSS来自定义界面外观

### 图片组件扩展
- 添加图片懒加载功能
- 支持图片压缩和优化
- 添加图片轮播组件
- 支持拖拽排序功能

## 测试

运行测试脚本添加示例数据：
```bash
python tests/test_annotation.py
```

这将添加两个测试产品和对应的爬虫数据，可以用于测试标注功能。

## 故障排除

### 常见错误

1. **AttributeError: 'sqlite3.Row' object has no attribute 'get'**
   - 原因：sqlite3.Row对象不支持get方法
   - 解决：使用字典访问方式 `row['column_name']` 而不是 `row.get('column_name')`

2. **数据库连接错误**
   - 确保 `data` 目录存在
   - 检查数据库文件权限

3. **模板渲染错误**
   - 检查模板文件路径是否正确
   - 确保所有必需的变量都已传递给模板

4. **图片显示问题**
   - 检查图片URL是否有效
   - 确保图片服务器可访问
   - 本地图片路径需要确保文件存在

5. **图片选择器问题**
   - 确保爬虫数据包含图片信息
   - 检查图片URL格式是否正确
   - 本地图片服务需要正确配置

6. **图片组件问题**
   - 确保 `image-components.css` 和 `image-components.js` 文件存在
   - 检查组件函数调用是否正确
   - 验证图片路径和URL格式

## 更新日志

### v3.0 (最新)
- ✅ 图片URL输入框改为缩略图显示
- ✅ 新增图片选择器模态框
- ✅ 支持从所有爬虫来源选择图片
- ✅ 双URL存储（本地URL和实际URL）
- ✅ 图片移除功能
- ✅ 本地图片优先显示选项
- ✅ 响应式图片网格布局
- ✅ 统一图片组件系统
- ✅ 可复用的图片展示和选择组件

### v2.0
- ✅ 显示商品ID且禁止修改
- ✅ 移除所有必填字段要求
- ✅ 图片直接显示，无需输入URL
- ✅ 删除Meta信息和附加信息字段
- ✅ 爬虫数据按crawler_manage模式展示
- ✅ 支持图片重新选择
- ✅ 优化数据展示结构

## 图片插件在标注功能中的用法

标注相关页面（如标注列表、详情、批量标注等）均集成了统一的图片显示插件 ImageComponents，实现如下功能：

- 支持"本地图片/原始图片/不显示"三种显示模式，用户可通过下拉框切换
- 图片缩略图、容器、说明文字、尺寸信息等结构和样式完全统一
- 懒加载自动生效，提升页面性能
- 切换显示模式时，图片和说明文字自动同步显示/隐藏，UI一致
- 图片显示模式记忆，翻页/筛选/切换后自动恢复

### 主要集成方式

1. 页面JS初始化：
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
   - 标注列表页用Jinja2宏生成HTML，详情/批量标注页用JS动态生成
   - 有图片时说明文字默认隐藏，无图片时显示

### 典型交互说明
- 切换显示模式时，所有图片和说明文字同步切换，无需手动处理
- 懒加载自动补全，无需手动注册
- 说明文字、容器、尺寸信息等UI风格与标注列表页完全一致

### 参考文件
- `app/static/js/image-components.js`（插件主文件）
- `app/static/css/image-components.css`（统一样式）
- `app/templates/annotation_list.html`、`batch_annotation.html` 等页面 