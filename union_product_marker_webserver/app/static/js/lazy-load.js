/**
 * 图片懒加载组件
 * 使用 Intersection Observer API 实现高性能懒加载
 */

const LazyLoader = (function() {
  let observer = null;
  let loadedImages = new Set();

  /**
   * 初始化懒加载
   * @param {Object} options 配置选项
   */
  function init(options = {}) {
    const {
      root = null,
      rootMargin = '50px',
      threshold = 0.1,
      selector = '.lazy-image',
      placeholder = '/static/images/placeholder.svg'
    } = options;

    // 检查浏览器支持
    if (!('IntersectionObserver' in window)) {
      console.warn('IntersectionObserver not supported, falling back to scroll event');
      initScrollBasedLazyLoad(options);
      return;
    }

    // 创建观察器
    observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          loadImage(entry.target, options);
          observer.unobserve(entry.target);
        }
      });
    }, {
      root,
      rootMargin,
      threshold
    });

    // 观察所有懒加载图片
    const lazyImages = document.querySelectorAll(selector);
    lazyImages.forEach(img => {
      observer.observe(img);
    });

    console.log(`LazyLoader initialized with ${lazyImages.length} images`);
  }

  /**
   * 加载图片
   * @param {HTMLElement} img 图片元素
   * @param {Object} options 配置选项
   */
  function loadImage(img, options = {}) {
    const { placeholder = '/static/images/placeholder.svg' } = options;
    
    // 防止重复加载
    if (loadedImages.has(img)) return;
    loadedImages.add(img);

    const dataSrc = img.getAttribute('data-src');
    const dataLocalSrc = img.getAttribute('data-local-src');
    const useLocal = img.getAttribute('data-use-local') !== 'false';

    if (!dataSrc && !dataLocalSrc) {
      console.warn('No image source found for lazy loading');
      return;
    }

    // 确定图片源
    let src = '';
    if (useLocal && dataLocalSrc) {
      src = dataLocalSrc.startsWith('/') ? dataLocalSrc : '/images/' + dataLocalSrc.replace(/^\/+|\/+/g, '/');
    } else if (dataSrc) {
      src = dataSrc;
    } else {
      src = placeholder;
    }

    // 添加加载状态
    img.classList.add('lazy-loading');
    
    // 创建新图片对象进行预加载
    const tempImg = new Image();
    
    tempImg.onload = function() {
      img.src = src;
      img.classList.remove('lazy-loading');
      img.classList.add('lazy-loaded');
      img.classList.remove('lazy-error');
      // 新增：显示尺寸
      const dim = img.parentNode && img.parentNode.querySelector('.image-dimensions');
      if (dim) {
        dim.textContent = this.naturalWidth + '×' + this.naturalHeight;
      }
      // 触发加载完成事件
      img.dispatchEvent(new CustomEvent('lazyLoaded', { detail: { src } }));
    };

    tempImg.onerror = function() {
      img.src = placeholder;
      img.classList.remove('lazy-loading');
      img.classList.add('lazy-error');
      // 新增：显示加载失败
      const dim = img.parentNode && img.parentNode.querySelector('.image-dimensions');
      if (dim) {
        dim.textContent = '加载失败';
      }
      // 触发加载失败事件
      img.dispatchEvent(new CustomEvent('lazyError', { detail: { src } }));
    };

    tempImg.src = src;
  }

  /**
   * 回退方案：基于滚动事件的懒加载
   * @param {Object} options 配置选项
   */
  function initScrollBasedLazyLoad(options = {}) {
    const { selector = '.lazy-image', placeholder = '/static/images/placeholder.svg' } = options;
    
    let ticking = false;

    function updateLazyImages() {
      const lazyImages = document.querySelectorAll(selector);
      
      lazyImages.forEach(img => {
        if (isInViewport(img)) {
          loadImage(img, options);
        }
      });
      
      ticking = false;
    }

    function requestTick() {
      if (!ticking) {
        requestAnimationFrame(updateLazyImages);
        ticking = true;
      }
    }

    // 监听滚动事件
    window.addEventListener('scroll', requestTick, { passive: true });
    window.addEventListener('resize', requestTick, { passive: true });
    
    // 初始检查
    updateLazyImages();
  }

  /**
   * 检查元素是否在视口中
   * @param {HTMLElement} element 元素
   * @returns {boolean} 是否在视口中
   */
  function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
      rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
  }

  /**
   * 添加新的懒加载图片
   * @param {HTMLElement|NodeList|Array} elements 图片元素
   */
  function add(elements) {
    if (!observer) return;

    const elementArray = Array.isArray(elements) ? elements : 
                        elements instanceof NodeList ? Array.from(elements) : 
                        [elements];

    elementArray.forEach(element => {
      if (element.matches && element.matches('.lazy-image')) {
        observer.observe(element);
      }
    });
  }

  /**
   * 销毁懒加载器
   */
  function destroy() {
    if (observer) {
      observer.disconnect();
      observer = null;
    }
    loadedImages.clear();
  }

  /**
   * 手动触发图片加载
   * @param {HTMLElement} img 图片元素
   */
  function forceLoad(img) {
    loadImage(img);
  }

  return {
    init,
    add,
    destroy,
    forceLoad,
    isInViewport
  };
})();

// 兼容全局
window.LazyLoader = LazyLoader; 