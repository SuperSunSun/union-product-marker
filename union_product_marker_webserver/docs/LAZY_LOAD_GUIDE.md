# 图片懒加载功能使用指南

## 概述

本项目已集成高性能的图片懒加载功能，使用 Intersection Observer API 实现，当图片滚动到可视区域时才会开始加载，大大提升页面性能。

## 功能特性

- ✅ **高性能**: 使用 Intersection Observer API，比滚动事件更高效
- ✅ **兼容性**: 自动回退到滚动事件方案，支持旧版浏览器
- ✅ **可配置**: 支持自定义触发距离、阈值等参数
- ✅ **状态管理**: 提供加载中、加载完成、加载失败等状态
- ✅ **事件支持**: 支持自定义事件回调
- ✅ **内存优化**: 防止重复加载，自动清理观察器

## 文件结构

```
app/static/
├── js/
│   └── lazy-load.js          # 懒加载核心脚本
├── css/
│   └── lazy-load.css         # 懒加载样式文件
└── images/
    └── placeholder.svg       # 占位符图片
```

## 使用方法

### 1. 基本用法

在HTML中为图片添加懒加载支持：

```html
<!-- 本地图片懒加载 -->
<img class="lazy-image" 
     data-local-src="path/to/image.jpg" 
     data-use-local="true"
     alt="图片描述">

<!-- 远程图片懒加载 -->
<img class="lazy-image" 
     data-src="https://example.com/image.jpg" 
     data-use-local="false"
     alt="图片描述">
```

### 2. JavaScript 初始化

```javascript
// 页面加载完成后初始化懒加载
document.addEventListener('DOMContentLoaded', function() {
    LazyLoader.init({
        rootMargin: '100px',    // 提前100px开始加载
        threshold: 0.1,         // 触发阈值
        selector: '.lazy-image', // 选择器
        placeholder: '/static/images/placeholder.svg' // 占位符图片
    });
});
```

### 3. 配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `rootMargin` | string | '50px' | 触发距离，支持CSS margin格式 |
| `threshold` | number | 0.1 | 触发阈值，0-1之间 |
| `selector` | string | '.lazy-image' | 懒加载图片的选择器 |
| `placeholder` | string | '/static/images/placeholder.svg' | 加载失败时的占位符 |

### 4. 动态添加图片

```javascript
// 动态添加新的懒加载图片
const newImage = document.createElement('img');
newImage.className = 'lazy-image';
newImage.setAttribute('data-local-src', 'new-image.jpg');
newImage.setAttribute('data-use-local', 'true');

document.querySelector('.container').appendChild(newImage);

// 添加到懒加载观察器
LazyLoader.add(newImage);
```

## 状态类名

懒加载过程中会自动添加以下CSS类名：

- `.lazy-loading`: 加载中状态
- `.lazy-loaded`: 加载完成状态  
- `.lazy-error`: 加载失败状态

## 事件监听

```javascript
// 监听图片加载完成事件
document.addEventListener('lazyLoaded', function(e) {
    console.log('图片加载完成:', e.detail.src);
});

// 监听图片加载失败事件
document.addEventListener('lazyError', function(e) {
    console.log('图片加载失败:', e.detail.src);
});
```

## 在标注列表页的使用

标注列表页已集成懒加载功能：

1. **图片HTML结构**:
```html
<img class="lazy-image" 
     data-local-src="{{ local_path }}"
     data-use-local="true"
     alt="{{ img_label }}" 
     onclick="window.open(this.src, '_blank')">
```

2. **初始化代码**:
```javascript
LazyLoader.init({
    rootMargin: '100px',
    threshold: 0.1,
    selector: '.lazy-image',
    placeholder: '/static/images/placeholder.svg'
});
```

3. **开关控制**:
```javascript
// 当用户切换"加载本地图片"开关时
loadImagesCheck.addEventListener("change", function() {
    const shouldLoadImages = this.checked;
    // 设置或移除懒加载属性
    // 如果图片在视口中，立即加载
});
```

## 性能优化建议

1. **合理设置 rootMargin**: 根据图片大小和网络情况调整
2. **使用合适的占位符**: 提供与最终图片尺寸相近的占位符
3. **避免过度使用**: 只对需要懒加载的图片使用此功能
4. **监控加载状态**: 通过事件监听了解加载情况

## 浏览器兼容性

- ✅ Chrome 51+
- ✅ Firefox 55+
- ✅ Safari 12.1+
- ✅ Edge 15+
- ✅ 自动回退到滚动事件方案

## 故障排除

### 图片不加载
1. 检查 `data-local-src` 或 `data-src` 属性是否正确
2. 确认图片路径是否存在
3. 查看浏览器控制台是否有错误信息

### 加载动画不显示
1. 确认 `lazy-load.css` 文件已正确引入
2. 检查CSS类名是否正确应用

### 性能问题
1. 调整 `rootMargin` 参数
2. 减少同时观察的图片数量
3. 使用更小的占位符图片

## 测试

可以使用项目根目录的 `test_lazy_load.html` 文件进行测试：

```bash
# 直接在浏览器中打开测试文件
open test_lazy_load.html
```

滚动页面查看懒加载效果，打开浏览器开发者工具观察网络请求。 