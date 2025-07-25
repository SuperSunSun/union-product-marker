// 商品预览插件
// 用法：ProductPreview.init({
//   container: '#previewSection',
//   data: {products: {...}},
//   onImport: function() {...} // 可选，显示导入按钮时的回调
// })

const ProductPreview = (function() {
  let currentData = null;
  let useAbsolute = true;
  let navViewMode = 'id';
  let navState = {};
  let lastActiveAnchor = null;
  let containerSelector = null;
  let contentSelector = null;
  let onImport = null;
  let showDeleteButton = false;

  function renderSidebarNav() {
    if (!currentData) return;
    const nav = document.querySelector(containerSelector + ' #sidebarNav');
    const search = document.querySelector(containerSelector + ' #sidebarSearch').value.trim().toLowerCase();
    let html = '';

    if (navViewMode === 'source') {
      const productsBySource = currentData.products || {};
      const sortedSources = Object.keys(productsBySource).sort();
      
      sortedSources.forEach(source => {
        const groupId = 'nav-group-' + source;
        if (!(source in navState)) navState[source] = true;
        const collapsed = !navState[source];
        const products = (productsBySource[source] || []).sort((a, b) => (parseInt(a.id) || 0) - (parseInt(b.id) || 0));
        let productLinks = '';
        let hasVisibleProducts = false;
        products.forEach(p => {
          const idStr = String(p.id || '');
          const nameStr = (p.product_name || '').toLowerCase();
          const brandStr = (p.brand || '').toLowerCase();
          const isVisible = !search || idStr.includes(search) || nameStr.includes(search) || brandStr.includes(search);
          if (!isVisible) return;
          hasVisibleProducts = true;
          const fullName = p.product_name || '未命名';
          productLinks += `<li onclick="ProductPreview.jumpToProduct('${source}','${idStr}')" id="nav-li-${source}-${idStr}" title="${fullName}">
            <span class="badge bg-light text-dark border me-1">${idStr}</span>
            <span>${fullName}</span>
          </li>`;
        });
        if (hasVisibleProducts) {
          const arrow = `<span class="arrow" style="transform:rotate(${collapsed ? '0' : '90'}deg)">&#9654;</span>`;
          const sourceColor = getSourceColor(source);
          const sourceTag = `<span class="badge ${sourceColor} small">${source}</span>`;
          html += `<div class="source-group">
            <div class="source-header" onclick="ProductPreview.toggleNavGroup('${source}')">${arrow}${sourceTag}</div>
            <ul class="source-list" id="${groupId}" style="display:${collapsed ? 'none' : 'block'};">${productLinks}</ul>
          </div>`;
        }
      });
    } else {
      let allProducts = [];
      Object.entries(currentData.products || {}).forEach(([source, products]) => {
        products.forEach(p => allProducts.push({ ...p, source: source }));
      });
      allProducts.sort((a, b) => (parseInt(a.id) || 0) - (parseInt(b.id) || 0));
      html = '<ul class="source-list" style="margin-left: 0;">';
      let hasVisibleProducts = false;
      allProducts.forEach(p => {
        const idStr = String(p.id || '');
        const nameStr = (p.product_name || '').toLowerCase();
        const brandStr = (p.brand || '').toLowerCase();
        const isVisible = !search || idStr.includes(search) || nameStr.includes(search) || brandStr.includes(search);
        if (!isVisible) return;
        hasVisibleProducts = true;
        const fullName = p.product_name || '未命名';
        const sourceColor = getSourceColor(p.source);
        html += `<li onclick="ProductPreview.jumpToProduct('${p.source}','${idStr}')" id="nav-li-${p.source}-${idStr}" title="${fullName}">
            <span class="badge bg-light text-dark border me-1">${idStr}</span>
            <span class="badge ${sourceColor} me-1 small">${p.source}</span>
            <span>${fullName}</span>
        </li>`;
      });
      html += '</ul>';
      if (!hasVisibleProducts && search) {
        html = '<div class="text-center text-muted small p-3">无匹配结果</div>';
      }
    }
    nav.innerHTML = html;
  }

  function renderProducts() {
    if (!currentData) return;
    const container = document.querySelector(contentSelector);
    let displayedProducts = [];
    Object.entries(currentData.products || {}).forEach(([source, products]) => {
      products.forEach(p => displayedProducts.push({...p, source}));
    });
    
    // 根据导航视图模式进行排序
    if (navViewMode === 'source') {
      // 按来源分组排序，然后按ID排序
      displayedProducts.sort((a, b) => {
        // 首先按来源名称排序
        const sourceCompare = a.source.localeCompare(b.source);
        if (sourceCompare !== 0) return sourceCompare;
        // 然后按ID排序
        return Number(a.id) - Number(b.id);
      });
    } else {
      // 按ID排序
      displayedProducts.sort((a, b) => Number(a.id) - Number(b.id));
    }
    
    const summaryEl = document.querySelector(containerSelector + ' #summary');
    if (summaryEl) {
      summaryEl.innerText = `共 ${displayedProducts.length} 件商品`;
    }
    container.innerHTML = "";
    
    let currentSource = null;
    for (const p of displayedProducts) {
      // 如果是按来源排序且来源发生变化，添加分隔标题
      if (navViewMode === 'source' && currentSource !== p.source) {
        currentSource = p.source;
        const sourceHeader = document.createElement("div");
        sourceHeader.className = "source-section-header";
        const sourceColor = getSourceColor(p.source);
        sourceHeader.innerHTML = `
          <div class="source-divider">
            <span class="badge ${sourceColor}">${p.source}</span>
            <span class="source-title">来源数据</span>
          </div>
        `;
        container.appendChild(sourceHeader);
      }
      
      const anchorId = `product-${p.source}-${p.id}`;
      const div = document.createElement("div");
      div.className = "product";
      div.id = anchorId;
      let images = (p.image_urls_simplified || p.image_urls_original || []).map((img, index) => {
        if (!img) return '';
        
        // 获取对应的本地图片路径
        const localImages = p.local_images || [];
        const localPath = localImages[index];
        const localUrl = localPath ? `/images/${localPath}` : '';
        
        // 确定初始显示的图片URL
        let initialSrc = img;
        if (useAbsolute && localPath) {
          initialSrc = localUrl;
        } else if (/^https?:\/\//i.test(img)) {
          initialSrc = img;
        } else if (useAbsolute) {
          initialSrc = `/images/${img}`;
        }
        
        return `<div class="image-container" 
                     data-remote-url="${img}" 
                     data-local-path="${localPath || ''}"
                     data-source="${p.source}"
                     data-index="${index}">
          <img class="lazy-image"
               data-local-src="${localUrl}"
               data-remote-src="${img}"
               data-use-local="${useAbsolute && localPath ? 'true' : 'false'}"
               alt="商品图片"
               onclick="window.open(this.src, '_blank')">
          <div class="image-dimensions">加载中...</div>
        </div>`;
      }).join("");
      
      // 处理本地图片（如果远程图片数量少于本地图片）
      const localImages = p.local_images || [];
      if (localImages.length > (p.image_urls_simplified || p.image_urls_original || []).length) {
        const remoteCount = (p.image_urls_simplified || p.image_urls_original || []).length;
        for (let i = remoteCount; i < localImages.length; i++) {
          const localPath = localImages[i];
          if (localPath) {
            const localUrl = `/images/${localPath}`;
            const initialSrc = useAbsolute ? localUrl : '';
            
            images += `<div class="image-container" 
                             data-remote-url="" 
                             data-local-path="${localPath}"
                             data-source="${p.source}"
                             data-index="${i}">
              <img class="lazy-image"
                   data-local-src="${localUrl}"
                   data-remote-src=""
                   data-use-local="${useAbsolute ? 'true' : 'false'}"
                   alt="本地图片 ${i + 1}"
                   onclick="window.open(this.src, '_blank')">
              <div class="image-dimensions">加载中...</div>
            </div>`;
          }
        }
      }
      const description = renderDescription(p.infos, p.source);
      const sourceColor = getSourceColor(p.source);
      const deleteButtonHTML = showDeleteButton ? `
        <button class="btn btn-sm btn-outline-danger delete-btn" onclick="ProductPreview.deleteSource('${p.source}', '${p.id}')" title="删除此来源数据">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
            <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
          </svg>
        </button>
      ` : '';

      div.innerHTML = `
        <div class="d-flex justify-content-between align-items-start mb-2">
          <h3 class="product-title">
            <span class="badge ${sourceColor}">${p.source}</span>
            #${p.id} - ${p.product_name || p.brand || "无标题"}
          </h3>
          ${deleteButtonHTML}
        </div>
        <div class="product-info">
          <p>
            <strong>品牌:</strong> ${p.brand || "N/A"} |
            <span class="price-current"><strong>价格:</strong> ${p.price_current || "N/A"}</span> |
            <span class="price-original"><strong>原价:</strong> ${p.price_original || "N/A"}</span>
          </p>
          <p><strong>商品链接:</strong> ${p.url ? `<a href="${p.url}" target="_blank">商品页面</a>` : 'N/A'}</p>
          <p><strong>抓取时间:</strong> ${p.crawled_at || "N/A"}</p>
        </div>
        <div class="images">${images}</div>
        <div class="product-details">
          <div class="detail-column">${description.leftColumn}</div>
          <div class="detail-column">${description.rightColumn}</div>
        </div>
      `;
      container.appendChild(div);
    }
    // 渲染后补全所有.lazy-image的data-src并触发懒加载
    document.querySelectorAll('.lazy-image').forEach(img => {
      const localSrc = img.getAttribute('data-local-src');
      if (localSrc && !img.getAttribute('data-src')) {
        const baseUrl = window.ImageComponents && ImageComponents['localImageBaseUrl']
          ? ImageComponents['localImageBaseUrl']
          : '/images/';
        img.setAttribute('data-src', localSrc.startsWith('/') ? localSrc : baseUrl + localSrc);
        img.src = '/static/images/placeholder.svg';
      }
    });
    if (window.ImageComponents && ImageComponents.addLazyImages) {
      ImageComponents.addLazyImages(document.querySelectorAll('.lazy-image'));
    }
    // 渲染完所有商品后，补全懒加载监听
    if (window.LazyLoader && typeof window.LazyLoader.add === 'function') {
      window.LazyLoader.add(container.querySelectorAll('.lazy-image'));
    } else if (window.LazyLoader && typeof window.LazyLoader.init === 'function') {
      window.LazyLoader.init({
        rootMargin: '100px',
        threshold: 0.1,
        selector: '.lazy-image',
        placeholder: '/static/images/placeholder.svg'
      });
    }
  }

  function renderTable(title, obj) {
    if (!obj || Object.keys(obj).length === 0) return "";
    const rows = Object.entries(obj).map(([k, v]) => {
      if (typeof v === 'object' && v !== null && !Array.isArray(v)) {
        return Object.entries(v).map(([subK, subV]) => `<tr><td>${subK}</td><td>${subV}</td></tr>`).join('');
      }
      return `<tr><td>${k}</td><td>${Array.isArray(v) ? `<ul>${v.map(i => `<li>${i}</li>`).join('')}</ul>` : v}</td></tr>`;
    }).join("");
    return `<h4>${title}</h4><table>${rows}</table>`;
  }

  function renderDescription(infos, source) {
    if (!infos) return {leftColumn: "", rightColumn: ""};
    let leftColumn = "", rightColumn = "";
    const sourceRules = {
      fairprice: {
        leftKeys: ['meta'],
        rightKeys: ['description', 'country of origin', 'storage']
      },
      shopee: {
        leftKeys: ['Product Specifications'],
        rightKeys: ['Product Description', 'price_info']
      },
      amazon: {
        leftKeys: ['meta_info', 'about_this_item'],
        rightKeys: ['product_infomation', 'important_information', 'description']
      }
    };
    const rules = sourceRules[source] || { leftKeys: [], rightKeys: [] };
    for (const [key, value] of Object.entries(infos)) {
      if (!value || key.toLowerCase() === 'script') continue;
      let content = '';
      if (Array.isArray(value)) {
        content = `<h4>${key}</h4><ul>${value.map(i => `<li>${i}</li>`).join('')}</ul>`;
      } else if (typeof value === 'object') {
        content = renderTable(key, value);
      } else {
        const paragraphs = String(value).split('\n').filter(p => p.trim());
        content = `<h4>${key}</h4><div>${paragraphs.map(p => `<p>${p}</p>`).join('')}</div>`;
      }
      if (rules.leftKeys.includes(key)) {
        leftColumn += content;
      } else {
        rightColumn += content;
      }
    }
    return {leftColumn, rightColumn};
  }

  function getSourceColor(sourceName) {
    const s = (sourceName || '').toLowerCase();
    if (s.includes('amazon')) return 'bg-warning text-dark';
    if (s.includes('shopee')) return 'bg-danger text-white';
    if (s.includes('fairprice')) return 'bg-primary text-white';
    return 'bg-secondary text-white';
  }

  function jumpToProduct(source, id) {
    const anchor = document.getElementById(`product-${source}-${id}`);
    if (anchor) {
      anchor.scrollIntoView({behavior: 'smooth', block: 'start'});
      if (lastActiveAnchor) lastActiveAnchor.classList.remove('active');
      const navLi = document.getElementById(`nav-li-${source}-${id}`);
      if (navLi) { navLi.classList.add('active'); lastActiveAnchor = navLi; }
    }
  }

  function toggleNavGroup(source) {
    navState[source] = !navState[source];
    renderProducts();
    renderSidebarNav();
  }

  function deleteSource(source, id) {
    if (!confirm(`确认删除来源 "${source}" 的商品 #${id} 数据吗？此操作不可恢复。`)) {
      return;
    }
    
    fetch('/crawler-manage/delete-source', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        product_id: id,
        source_name: source
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        alert('删除失败: ' + data.error);
      } else {
        alert('删除成功！');
        // 重新加载数据
        if (window.loadAllData) {
          window.loadAllData();
        }
        if (window.loadStatistics) {
          window.loadStatistics();
        }
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('删除失败: ' + error.message);
    });
  }

  function updateUseAbsolute(value) {
    useAbsolute = value;
    // 使用高性能的切换方式，直接修改DOM属性
    toggleAllImages(value);
  }

  function toggleAllImages(useLocal) {
    const images = document.querySelectorAll(contentSelector + ' img[data-local-src]');
    images.forEach(img => {
      const localSrc = img.getAttribute('data-local-src');
      const remoteSrc = img.getAttribute('data-remote-src');
      
      if (useLocal && localSrc && localSrc !== '') {
        // 切换到本地图片
        if (img.src !== localSrc) {
          img.src = localSrc;
          img.setAttribute('data-use-local', 'true');
        }
      } else if (remoteSrc && remoteSrc !== '') {
        // 切换到远程图片
        if (img.src !== remoteSrc) {
          img.src = remoteSrc;
          img.setAttribute('data-use-local', 'false');
        }
      }
    });
  }

  function init(opts) {
    if (!opts || !opts.data || (!opts.container && !opts.content)) {
      console.error('ProductPreview init error: container/content and data are required.');
      return;
    }
    currentData = opts.data;
    useAbsolute = opts.hasOwnProperty('useAbsoluteImages') ? opts.useAbsoluteImages : true;
    containerSelector = opts.container || opts.content.replace(/#previewContent$/, '');
    contentSelector = opts.content || containerSelector + ' #previewContent';
    onImport = opts.onImport;
    showDeleteButton = opts.showDeleteButton === true;
    const renderNav = opts.renderNav !== false; // Default to true

    navViewMode = 'id';
    navState = {};
    lastActiveAnchor = null;

    // 渲染
    if (renderNav) {
      renderSidebarNav();
    }
    renderProducts();

    // 事件绑定
    if (renderNav) {
      document.querySelector(containerSelector + ' #sidebarSearch').addEventListener('input', renderSidebarNav);
      document.querySelectorAll(containerSelector + ' input[name="navView"]').forEach(radio => {
        radio.addEventListener('change', function() {
          navViewMode = this.value;
          renderSidebarNav();
          renderProducts();
        });
      });
      
      // 查找本地图片服务复选框（支持多种ID）
      const localImageCheckbox = document.querySelector(containerSelector + ' #useAbsolutePath') || 
                                document.querySelector('#useLocalImageService') ||
                                document.querySelector(containerSelector + ' #useLocalImageService');
      
      if (localImageCheckbox) {
        // 更新useAbsolute变量以匹配复选框的初始状态
        useAbsolute = localImageCheckbox.checked;
        
        localImageCheckbox.addEventListener('change', function() {
          useAbsolute = this.checked;
          // 使用高性能切换而不是重新渲染
          toggleAllImages(this.checked);
        });
      }
    }
    
    // 导入按钮
    if (onImport) {
      document.querySelector(containerSelector + ' #confirmImport').addEventListener('click', function() {
        onImport(currentData);
      });
    }

    // 页面渲染后初始化懒加载
    setTimeout(function() {
      if (window.LazyLoader) {
        LazyLoader.init({
          rootMargin: '100px',
          threshold: 0.1,
          selector: '.lazy-image',
          placeholder: '/static/images/placeholder.svg'
        });
      }
    }, 100);
  }

  return {
    init,
    jumpToProduct,
    toggleNavGroup,
    deleteSource,
    updateUseAbsolute,
    toggleAllImages
  };
})();

// 兼容全局
window.ProductPreview = ProductPreview;
window.deleteSource = ProductPreview.deleteSource; 