# 爬虫数据管理功能

## 功能概述

新增了两个爬虫数据管理页面，用于处理和管理从不同来源（Amazon、Shopee、FairPrice等）爬取的商品数据。

## 页面功能

### 1. 爬虫数据上传页面 (`/crawler-upload`)

**功能特点：**
- 📤 JSON文件上传和验证
- 📊 数据预览和统计信息
- ✅ 确认导入功能
- 🔍 支持多来源数据结构
- 🖼️ **完整内容预览** - 展示所有商品的所有内容
- 🎯 **来源筛选** - 可选择查看特定来源的数据
- 📁 **本地图片预览** - 支持base_path+相对路径的图片显示

**使用流程：**
1. 选择爬虫生成的JSON文件
2. 系统自动解析并显示统计信息
3. **完整预览所有商品内容**（包括图片、详细信息等）
4. 可选择特定来源进行筛选
5. 确认无误后点击"确认导入"

**预览功能增强：**
- **完整展示：** 不再限制只显示前3个商品，而是展示所有商品
- **图片支持：** 支持本地图片路径，可点击放大查看
- **来源筛选：** 可选择查看"所有来源"或特定来源（amazon/shopee/fairprice）
- **路径切换：** 可选择使用绝对路径（base_path+URL）或相对路径
- **详细信息：** 完整展示商品的所有爬虫数据，包括规格、描述、营养成分等

**支持的数据格式：**
```json
{
  "base_path": "图片基础路径",
  "merged_at": "合并时间",
  "products": {
    "amazon": [...],
    "shopee": [...],
    "fairprice": [...]
  }
}
```

### 2. 爬虫数据管理页面 (`/crawler-manage`)

**功能特点：**
- 📋 左侧商品ID列表（显示来源数量）
- 📊 右侧详细数据展示
- 🖼️ 图片预览功能
- 🗑️ 来源数据删除功能
- 🔍 多来源数据对比

**界面布局：**
- **左侧面板：** 商品列表，显示ID、名称、状态、来源数量
- **右侧面板：** 选中商品的详细爬虫数据
  - 基本信息（名称、品牌、价格等）
  - 商品图片（可点击放大）
  - 详细信息（表格形式展示）

**数据展示：**
- 支持Amazon、Shopee、FairPrice等不同来源的数据格式
- 自动解析和展示商品规格、描述等信息
- 图片支持本地路径显示

## 用户体验优化

### 统一布局系统

系统采用统一的布局架构，提供一致的用户体验：

#### 布局文件结构
- **基础布局**: `app/templates/layout.html` - 统一的基础模板
- **块结构**: 支持 `common_css`、`page_css`、`common_js`、`page_js` 块
- **响应式设计**: 支持桌面和移动设备

#### 统一库引入
```html
<!-- 常用第三方库样式 -->
{% block common_css %}
  <!-- DataTables 样式 -->
  <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/dataTables.bootstrap5.min.css">
  <!-- Font Awesome 图标 -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
{% endblock %}

<!-- 常用第三方库脚本 -->
{% block common_js %}
  <!-- jQuery -->
  <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
  <!-- DataTables -->
  <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
  <script src="https://cdn.datatables.net/1.13.6/js/dataTables.bootstrap5.min.js"></script>
{% endblock %}
```

### 通用工具函数

系统提供 `AppUtils` 全局工具对象，统一处理常用功能：

```javascript
window.AppUtils = {
  // 显示加载状态
  showLoading: function(element, text = '加载中...') { ... },
  
  // 隐藏加载状态
  hideLoading: function(element, originalText) { ... },
  
  // 显示消息提示
  showMessage: function(message, type = 'info') { ... },
  
  // 格式化日期
  formatDate: function(date) { ... }
};
```

### 消息提示系统

#### 优化前的问题
- 提示消息被固定顶栏遮挡
- 消息插入到页面内容中导致页面布局位移
- 消息显示位置不固定

#### 优化后的解决方案
```javascript
showMessage: function(message, type = 'info') {
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
  alertDiv.style.cssText = `
    position: fixed;
    top: 80px;
    right: 20px;
    z-index: 9999;
    max-width: 400px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    border-radius: 8px;
  `;
  alertDiv.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  
  // 插入到body中，而不是content-wrapper
  document.body.appendChild(alertDiv);
  
  // 3秒后自动消失
  setTimeout(() => {
    if (alertDiv.parentNode) {
      alertDiv.remove();
    }
  }, 3000);
}
```

#### 改进效果
- ✅ 消息显示在固定位置（右上角）
- ✅ 不会被顶栏遮挡
- ✅ 不会影响页面布局
- ✅ 添加阴影和圆角，更美观
- ✅ 自动消失功能正常

### 图标系统优化

#### 图标使用规范
- **保留的图标**: 按钮上的图标（如上传、保存、返回等）、加载状态图标、错误状态图标
- **删除的图标**: 页面标题中的图标、表单字段标签中的图标、导航标签中的图标、统计数据显示中的图标、模态框标题中的图标

#### 图标系统升级
- 替换 emoji 为 Font Awesome 图标
- 提供更好的视觉一致性和可扩展性

```html
<!-- 之前 -->
<a href="...">🏠 首页</a>

<!-- 现在 -->
<a href="..."><i class="fas fa-home me-2"></i>首页</a>
```

### 交互体验改进

#### 加载状态管理
```javascript
// 之前
btn.disabled = true;
btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> 加载中...';

// 现在
AppUtils.showLoading(btn, '加载中...');
// 完成后
AppUtils.hideLoading(btn, originalText);
```

#### 消息提示使用
```javascript
// 之前
alert('操作成功');

// 现在
AppUtils.showMessage('操作成功', 'success');
```

## 数据库结构

### sources表
```sql
CREATE TABLE sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT,           -- 商品ID
    source_name TEXT,          -- 来源名称（amazon/shopee/fairprice）
    raw_json TEXT,             -- 原始JSON数据
    uploaded_at TEXT           -- 上传时间
);
```

### 关联关系
- `sources.product_id` ↔ `products.id`
- 一个商品可以有多个来源的数据
- 支持同一来源的数据更新

## API接口

### 上传相关
- `POST /crawler-upload/preview` - 预览上传的JSON数据
- `POST /crawler-upload/import` - 确认导入数据

### 管理相关
- `GET /crawler-manage/products` - 获取有爬虫数据的商品列表
- `GET /crawler-manage/product/<id>` - 获取指定商品的爬虫数据
- `POST /crawler-manage/delete-source` - 删除指定来源的数据

## 使用示例

### 1. 上传爬虫数据
1. 访问 `/crawler-upload`
2. 选择JSON文件（如 `test_crawler_data_full.json`）
3. 查看完整预览信息（所有商品、图片、详细信息）
4. 可选择特定来源进行筛选
5. 点击"确认导入"

### 2. 管理爬虫数据
1. 访问 `/crawler-manage`
2. 左侧选择商品ID
3. 右侧查看该商品的所有来源数据
4. 可以删除不需要的来源数据

## 技术特点

- **响应式设计：** 支持不同屏幕尺寸
- **完整预览：** 上传前可预览所有数据内容
- **图片支持：** 本地图片路径解析和预览
- **数据验证：** 自动验证JSON格式和结构
- **错误处理：** 完善的错误提示和处理
- **性能优化：** 分页加载和懒加载图片
- **用户体验：** 来源筛选、路径切换、图片放大
- **统一布局：** 一致的界面风格和交互体验
- **工具函数：** 可复用的前端功能组件

## 预览界面特色

### 参考viewer.html的设计理念：
- **完整展示：** 不再限制商品数量，展示所有内容
- **图片预览：** 支持本地图片路径，显示图片尺寸
- **来源标签：** 每个商品显示来源标识
- **详细信息：** 左右分栏展示商品规格和描述
- **交互功能：** 图片点击放大、来源筛选、路径切换

### 预览控制功能：
- **来源选择器：** 可选择查看所有来源或特定来源
- **路径切换：** 可选择使用绝对路径或相对路径
- **统计信息：** 实时显示当前显示的商品数量
- **滚动预览：** 支持长列表的滚动浏览

## 优化效果统计

### 代码优化
- **CSS代码减少**: 约300行 → 约100行
- **重复定义消除**: 4个页面中的重复样式
- **维护成本降低**: 集中管理，统一修改

### 功能增强
- **响应式支持**: 更好的移动端适配
- **交互体验**: 统一的悬停效果和动画
- **错误处理**: 统一的加载失败显示
- **可扩展性**: 易于添加新的图片组件

### 性能提升
- **文件大小**: 减少重复代码，降低加载时间
- **缓存效率**: 统一的CSS/JS文件，更好的缓存效果
- **渲染性能**: 统一的样式，减少重绘

## 注意事项

1. **文件格式：** 仅支持UTF-8编码的JSON文件
2. **数据结构：** 必须包含`products`字段
3. **图片路径：** 支持相对路径和绝对路径（base_path+相对路径）
4. **数据更新：** 相同商品ID和来源的数据会被更新
5. **删除操作：** 删除来源数据不可恢复，请谨慎操作
6. **图片显示：** 确保base_path路径正确，图片文件存在
7. **布局兼容：** 确保所有页面都使用统一的布局模板
8. **工具函数：** 使用AppUtils进行消息提示和加载状态管理 