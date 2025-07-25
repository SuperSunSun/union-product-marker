/*
 * ImageComponents 统一图片组件系统（增强版）
 * --------------------------------------------------
 * 功能：
 *   - 支持"本地图片/原始图片/不显示"三种显示模式
 *   - 集成懒加载，提升性能
 *   - 提供图片显示模式选择器（下拉框）
 *   - 支持图片容器、缩略图、说明文字、尺寸信息、点击放大等
 *   - 可灵活集成到任意页面，API高度解耦
 *   - 兼容多页面、表格、卡片、弹窗等多种场景
 * 
 * 典型用法：
 *   ImageComponents.init({ defaultMode: 'local', lazyLoad: true });
 *   const thumb = ImageComponents.createImageThumbnail({ localSrc: 'xxx.jpg', label: '主图' });
 *   const selector = ImageComponents.createImageModeSelector({ onModeChange: ... });
 *   ImageComponents.setImageDisplayMode('local', '.image-thumbnail');
 *
 * 详见 docs/README.md
 */

const ImageComponents = (function() {
  
  // 显示模式枚举
  const DisplayModes = {
    LOCAL: 'local',    // 本地优先
    REMOTE: 'remote',  // 原始图片
    HIDDEN: 'hidden'   // 不显示
  };

  // 全局配置
  let globalConfig = {
    defaultMode: DisplayModes.LOCAL, // 默认显示模式
    lazyLoad: true,                  // 是否启用懒加载
    placeholder: '/static/images/placeholder.svg', // 占位图
    localImageBaseUrl: '/images/'    // 本地图片基础路径
  };

  // 懒加载观察器
  let lazyObserver = null;

  /**
   * 初始化图片组件系统（全局只需调用一次）
   * @param {Object} options 配置项：defaultMode, lazyLoad, placeholder, localImageBaseUrl
   * @example
   *   ImageComponents.init({ defaultMode: 'local', lazyLoad: true });
   */
  function init(options = {}) {
    globalConfig = { ...globalConfig, ...options };
    
    // 初始化懒加载
    if (globalConfig.lazyLoad) {
      initLazyLoading();
    }
    
    console.log('ImageComponents initialized with config:', globalConfig);
  }

  /**
   * 创建图片容器（含尺寸信息、说明文字、点击放大等）
   * @param {Object} options
   *   - localSrc: 本地图片路径
   *   - remoteSrc: 原始图片URL
   *   - alt: 图片alt文字
   *   - mode: 显示模式（local/remote/hidden）
   *   - dimensions: 是否显示尺寸信息
   *   - clickable: 是否可点击放大
   *   - size: normal/small/large
   *   - onLoad/onError/onClick: 事件回调
   * @returns {HTMLElement} 图片容器div
   */
  function createImageContainer(options = {}) {
    const {
      src = '',
      alt = '商品图片',
      localSrc = '',
      remoteSrc = '',
      mode = globalConfig.defaultMode,
      dimensions = true,
      clickable = true,
      size = 'normal', // normal, small, large
      onLoad = null,
      onError = null,
      onClick = null
    } = options;

    const container = document.createElement('div');
    container.className = 'image-container';
    container.setAttribute('data-display-mode', mode);
    
    // 设置尺寸类
    if (size !== 'normal') {
      container.classList.add(`image-${size}`);
    }

    // 隐藏模式直接返回
    if (mode === DisplayModes.HIDDEN) {
      // 只隐藏图片，不隐藏容器和说明文字
    }

    // 确定显示的图片源
    let displaySrc = src;
    if (mode === DisplayModes.LOCAL && localSrc) {
      displaySrc = localSrc.startsWith('/') ? localSrc : globalConfig.localImageBaseUrl + localSrc;
    } else if (mode === DisplayModes.REMOTE && remoteSrc) {
      displaySrc = remoteSrc;
    } else if (mode === DisplayModes.LOCAL && remoteSrc) {
      // 本地模式但无本地图片时，回退到远程图片
      displaySrc = remoteSrc;
    }

    // 创建图片元素
    const img = document.createElement('img');
    img.alt = alt;
    img.setAttribute('data-local-src', localSrc);
    img.setAttribute('data-remote-src', remoteSrc);
    img.setAttribute('data-display-mode', mode);

    // 应用懒加载
    if (globalConfig.lazyLoad && displaySrc) {
      img.classList.add('lazy-image');
      img.setAttribute('data-src', displaySrc);
      img.src = globalConfig.placeholder;
    } else {
      img.src = displaySrc || globalConfig.placeholder;
    }

    // 绑定事件
    if (onLoad) {
      img.addEventListener('load', onLoad);
    }
    if (onError) {
      img.addEventListener('error', onError);
    }
    if (clickable) {
      img.style.cursor = 'pointer';
      img.addEventListener('click', (e) => {
        if (onClick) {
          onClick(e);
        } else {
          window.open(displaySrc, '_blank');
        }
      });
    }

    // 添加尺寸信息
    if (dimensions) {
      const dimensionsDiv = document.createElement('div');
      dimensionsDiv.className = 'image-dimensions';
      dimensionsDiv.textContent = '加载中...';
      
      img.addEventListener('load', function() {
        dimensionsDiv.textContent = `${this.naturalWidth}×${this.naturalHeight}`;
      });
      
      img.addEventListener('error', function() {
        dimensionsDiv.textContent = '加载失败';
      });
      
      container.appendChild(img);
      container.appendChild(dimensionsDiv);
    } else {
      container.appendChild(img);
    }

    return container;
  }

  /**
   * 创建图片缩略图（常用于表格、卡片、批量渲染）
   * @param {Object} options
   *   - localSrc: 本地图片路径
   *   - remoteSrc: 原始图片URL
   *   - mode: 显示模式
   *   - alt: alt文字
   *   - label: 说明文字
   * @returns {HTMLElement} 缩略图div
   * @example
   *   const thumb = ImageComponents.createImageThumbnail({ localSrc: 'xxx.jpg', label: '主图' });
   */
  function createImageThumbnail(options = {}) {
    const {
      localSrc = '',
      remoteSrc = '',
      mode = globalConfig.defaultMode,
      alt = '图片缩略图',
      label = ''
    } = options;

    const thumbnail = document.createElement('div');
    thumbnail.className = 'image-thumbnail';
    
    if (mode === DisplayModes.HIDDEN) {
      // 只隐藏图片，不隐藏容器和说明文字
    }

    const hasImage = (mode === DisplayModes.LOCAL && localSrc) || 
                    (mode === DisplayModes.REMOTE && remoteSrc);
    
    thumbnail.classList.add(hasImage ? 'has-image' : 'no-image');

    if (hasImage) {
      const img = document.createElement('img');
      const displaySrc = mode === DisplayModes.LOCAL && localSrc ? 
                        (localSrc.startsWith('/') ? localSrc : globalConfig.localImageBaseUrl + localSrc) : 
                        remoteSrc;
      
      img.alt = alt;
      img.setAttribute('data-local-src', localSrc);
      img.setAttribute('data-remote-src', remoteSrc);
      img.setAttribute('data-display-mode', mode);
      
      if (globalConfig.lazyLoad) {
        img.classList.add('lazy-image');
        img.setAttribute('data-src', displaySrc);
        img.src = globalConfig.placeholder;
      } else {
        img.src = displaySrc;
      }
      
      thumbnail.appendChild(img);
    }

    if (label) {
      const labelDiv = document.createElement('div');
      labelDiv.className = 'image-alt-text';
      labelDiv.textContent = label;
      // 有图片时初始隐藏，无图片时显示
      if (hasImage) {
        labelDiv.style.display = 'none';
      }
      thumbnail.appendChild(labelDiv);
    }

    return thumbnail;
  }

  /**
   * 批量切换所有图片的显示模式（本地/原始/不显示）
   * @param {string} mode - 'local' | 'remote' | 'hidden'
   * @param {string|Element|NodeList} selector - 目标图片容器选择器
   * @example
   *   ImageComponents.setImageDisplayMode('local', '.image-thumbnail');
   */
  function setImageDisplayMode(mode, selector = '.image-container, .image-thumbnail') {
    let containers;
    if (typeof selector === 'string') {
      containers = document.querySelectorAll(selector);
    } else if (selector instanceof Element) {
      containers = [selector];
    } else if (selector instanceof NodeList || Array.isArray(selector)) {
      containers = selector;
    } else {
      containers = [];
    }
    
    containers.forEach(container => {
      container.setAttribute('data-display-mode', mode);
      
      const img = container.querySelector('img');
      const altText = container.querySelector('.image-alt-text');
      if (!img) return;
      if (mode === DisplayModes.HIDDEN) {
        img.style.display = 'none';
        if (altText) altText.style.display = 'flex';
        return;
      } else {
        // 判断有无图片内容
        const hasImageContent = !!(img.getAttribute('data-local-src') || img.getAttribute('data-remote-src'));
        if (hasImageContent) {
          img.style.display = '';
          if (altText) altText.style.display = 'none';
          container.classList.add('has-image');
          container.classList.remove('no-image');
        } else {
          img.style.display = 'none';
          if (altText) altText.style.display = 'flex';
          container.classList.add('no-image');
          container.classList.remove('has-image');
        }
      }
      const localSrc = img.getAttribute('data-local-src');
      const remoteSrc = img.getAttribute('data-remote-src');
      let displaySrc = '';
      if (mode === DisplayModes.LOCAL && localSrc) {
        displaySrc = localSrc.startsWith('/') ? localSrc : globalConfig.localImageBaseUrl + localSrc;
      } else if (mode === DisplayModes.REMOTE && remoteSrc) {
        displaySrc = remoteSrc;
      } else if (mode === DisplayModes.LOCAL && remoteSrc) {
        // 本地模式但无本地图片时，回退到远程图片
        displaySrc = remoteSrc;
      }
      if (displaySrc) {
        img.setAttribute('data-display-mode', mode);
        if (globalConfig.lazyLoad) {
          img.setAttribute('data-src', displaySrc);
          if (img.classList.contains('lazy-loaded')) {
            img.src = displaySrc;
          }
        } else {
          img.src = displaySrc;
        }
      }
    });
  }

  /**
   * 创建图片显示模式选择器（下拉框）
   * @param {Object} options
   *   - id: 元素id
   *   - defaultMode: 默认模式
   *   - onModeChange: 切换回调
   *   - modes: 自定义选项数组（如只显示本地/原始）
   * @returns {HTMLSelectElement}
   * @example
   *   const sel = ImageComponents.createImageModeSelector({ onModeChange: ... });
   */
  function createImageModeSelector(options = {}) {
    const {
      id = 'imageDisplayMode',
      defaultMode = globalConfig.defaultMode,
      onModeChange = null,
      className = 'image-mode-selector',
      modes = null // 新增：指定要显示的模式选项
    } = options;

    const selector = document.createElement('select');
    selector.id = id;
    selector.className = className;
    selector.value = defaultMode;
    
    // 根据modes参数决定显示哪些选项
    let availableModes = modes;
    if (!availableModes) {
      // 默认显示全部三种模式
      availableModes = [
        { value: DisplayModes.LOCAL, label: '本地图片' },
        { value: DisplayModes.REMOTE, label: '原始图片' },
        { value: DisplayModes.HIDDEN, label: '不显示' }
      ];
    }
    
    // 生成选项HTML
    const optionsHtml = availableModes.map(mode => 
      `<option value="${mode.value}">${mode.label}</option>`
    ).join('');
    
    selector.innerHTML = optionsHtml;

    if (onModeChange) {
      selector.addEventListener('change', function() {
        const mode = this.value;
        setImageDisplayMode(mode);
        onModeChange(mode);
      });
    }

    return selector;
  }

  /**
   * 渲染图片选择器网格（用于弹窗批量分配）
   * @param {HTMLElement} container
   * @param {Array} images
   * @param {Object} options
   */
  function renderImagePickerGrid(container, images = [], options = {}) {
    const {
      mode = globalConfig.defaultMode,
      onImageSelect = null,
      imageTypes = [],
      imageLabels = {}
    } = options;

    container.innerHTML = '';

    if (images.length === 0) {
      container.innerHTML = '<div class="text-center text-muted w-100"><i class="fas fa-info-circle me-2"></i>暂无可用图片</div>';
      return;
    }

    images.forEach((image, index) => {
      const imageItem = document.createElement('div');
      imageItem.className = 'image-picker-item';
      
      // 创建图片容器
      const imageContainer = createImageContainer({
        localSrc: image.localUrl || image.localSrc,
        remoteSrc: image.url || image.remoteSrc,
        mode: mode,
        clickable: false
      });
      imageItem.appendChild(imageContainer);

      // 创建分配标签
      if (imageTypes.length > 0) {
        const tagsContainer = document.createElement('div');
        tagsContainer.className = 'image-assignment-tags';
        
        imageTypes.forEach(type => {
          const tag = document.createElement('button');
          tag.className = 'image-assign-tag';
          tag.textContent = imageLabels[type] || type;
          tag.setAttribute('data-type', type);
          
          // 点亮已分配按钮
          if (window.imageAssignments && window.imageAssignments[type]) {
            const assigned = window.imageAssignments[type];
            if (
              (assigned.localUrl && assigned.localUrl === (image.localUrl || image.localSrc)) ||
              (assigned.remoteUrl && assigned.remoteUrl === (image.url || image.remoteSrc))
            ) {
              tag.classList.add('active');
            }
          }
          
          if (onImageSelect) {
            tag.addEventListener('click', function() {
              onImageSelect(this, image.url || '', image.localUrl || '', type);
            });
          }
          
          tagsContainer.appendChild(tag);
        });
        
        imageItem.appendChild(tagsContainer);
      }
      
      container.appendChild(imageItem);
    });
  }

  /**
   * 初始化懒加载（内部自动调用）
   * 兼容IntersectionObserver
   */
  function initLazyLoading() {
    if (!('IntersectionObserver' in window)) {
      console.warn('IntersectionObserver not supported');
      return;
    }

    lazyObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          const dataSrc = img.getAttribute('data-src');
          
          if (dataSrc) {
            img.classList.add('lazy-loading');
            
            const tempImg = new Image();
            tempImg.onload = function() {
              img.src = dataSrc;
              img.classList.remove('lazy-loading');
              img.classList.add('lazy-loaded');
              lazyObserver.unobserve(img);
            };
            tempImg.onerror = function() {
              img.classList.remove('lazy-loading');
              img.classList.add('lazy-error');
              lazyObserver.unobserve(img);
            };
            tempImg.src = dataSrc;
          }
        }
      });
    }, {
      rootMargin: '50px',
      threshold: 0.1
    });

    // 观察所有懒加载图片
    document.querySelectorAll('.lazy-image').forEach(img => {
      lazyObserver.observe(img);
    });
  }

  /**
   * 为新图片元素补全懒加载监听
   * @param {HTMLElement|NodeList|Array} elements
   */
  function addLazyImages(elements) {
    if (!lazyObserver) return;

    const elementArray = Array.isArray(elements) ? elements : 
                        elements instanceof NodeList ? Array.from(elements) : 
                        [elements];

    elementArray.forEach(element => {
      if (element.matches && element.matches('.lazy-image')) {
        lazyObserver.observe(element);
      }
    });
  }

  /**
   * 创建图片预览（兼容老API，等价于createImageContainer但不显示尺寸）
   * @param {Object} options
   * @returns {HTMLElement}
   */
  function createImagePreview(options = {}) {
    return createImageContainer({ ...options, dimensions: false });
  }

  /**
   * 切换单个图片容器的显示模式（兼容老API）
   * @param {HTMLElement} container
   * @param {boolean} useLocal
   */
  function toggleImageSource(container, useLocal) {
    const mode = useLocal ? DisplayModes.LOCAL : DisplayModes.REMOTE;
    setImageDisplayMode(mode, container);
  }

  /**
   * 批量切换所有图片容器的显示模式（兼容老API）
   * @param {string} selector
   * @param {boolean} useLocal
   */
  function toggleAllImageSources(selector, useLocal) {
    const mode = useLocal ? DisplayModes.LOCAL : DisplayModes.REMOTE;
    setImageDisplayMode(mode, selector);
  }

  return {
    // 新增API
    init,
    DisplayModes,
    createImageContainer,
    createImageThumbnail,
    setImageDisplayMode,
    createImageModeSelector,
    renderImagePickerGrid,
    addLazyImages,
    
    // 保持兼容的API
    createImagePreview,
    toggleImageSource,
    toggleAllImageSources
  };
})();

// 兼容全局
window.ImageComponents = ImageComponents; 