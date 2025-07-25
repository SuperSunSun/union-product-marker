// panel.js

// 初始化变量和 UI 元素引用
let fileHandle = null;
let folderId = null;
let prefix = "";
const urlList = document.getElementById("urlList");
const fileInput = document.getElementById("fileInput");
const prefixInput = document.getElementById("prefixInput");
const folderStatus = document.getElementById("folderStatus");
let idMap = {}; // url -> id 映射表
let urlQueue = []; // 所有可用的 URL 队列
let autoNext = false; // 是否启用“保存后自动打开下一个 URL”模式

// 创建并插入“自动跳转”复选框
const checkbox = document.createElement("label");
checkbox.innerHTML = '<input type="checkbox" id="autoNextCheckbox"> 保存后自动跳转下一个 URL';
document.body.insertBefore(checkbox, urlList);

const autoNextCheckbox = document.getElementById("autoNextCheckbox");

// Toast 弹出提示函数（替代 alert）
const showToast = (msg, ok = true) => {
  const toast = document.createElement("div");
  toast.textContent = msg;
  toast.style.position = "fixed";
  toast.style.bottom = "20px";
  toast.style.left = "50%";
  toast.style.transform = "translateX(-50%)";
  toast.style.background = ok ? "#4caf50" : "#f44336";
  toast.style.color = "white";
  toast.style.padding = "8px 14px";
  toast.style.borderRadius = "5px";
  toast.style.boxShadow = "0 2px 6px rgba(0,0,0,0.3)";
  toast.style.zIndex = 1000;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
};

// 加载用户上次填写的前缀、自动跳转状态
window.addEventListener("DOMContentLoaded", () => {
  const savedPrefix = localStorage.getItem("savedPrefix");
  if (savedPrefix) {
    prefixInput.value = savedPrefix;
  }
  const savedAutoNext = localStorage.getItem("savedAutoNext");
  if (savedAutoNext === "true") {
    autoNextCheckbox.checked = true;
    autoNext = true;
  }
});

// 切换“自动跳转”开关
autoNextCheckbox.addEventListener("change", (e) => {
  autoNext = e.target.checked;
  localStorage.setItem("savedAutoNext", autoNext);
});

// 用户点击“选择文件夹”按钮，调起文件夹选择器
// 成功则保存 folderId，失败降级为默认下载

document.getElementById("chooseFolder").addEventListener("click", async () => {
  try {
    folderId = await window.showDirectoryPicker({ mode: "readwrite" });
    folderStatus.textContent = "📁 目录已选择";
  } catch (err) {
    console.warn("目录选择取消或失败", err);
    showToast("⚠️ 未能选择目录，已使用默认下载", false);
  }
});

// 👇 文件上传：读取 CSV 或 XLSX 内容并展示 URL 列表
fileInput.addEventListener("change", async () => {
  const file = fileInput.files[0];
  if (!file) return;
  localStorage.setItem("savedFilename", file.name);
  const urls = await parseFile(file);
  urlList.innerHTML = "";
  idMap = {};
  urlQueue = urls.filter(x => x.url.startsWith("http"));
  const header = document.createElement("li");
  header.innerHTML = "<strong>ID</strong> | <strong>URL</strong>";
  urlList.appendChild(header);

  chrome.tabs.query({}, (tabs) => {
    const openUrls = tabs.map(t => t.url);
    urls.forEach(({ id, url }) => {
      idMap[url] = id;
      if (!url.startsWith("http")) return;
      const li = document.createElement("li");
      li.style.cursor = "pointer";
      if (openUrls.includes(url)) li.style.background = "#c0f0c0";
      li.textContent = `${id} | ${url}`;
      li.addEventListener("click", async () => {
        const tab = await chrome.tabs.create({ url, active: true });
        localStorage.setItem("lastShopeeTabId", tab.id);
        localStorage.setItem("lastShopeeUrl", url);
      });
      urlList.appendChild(li);
    });
  });
  localStorage.setItem("urlData", JSON.stringify(urls));
});

// 监听前缀输入变化并保存
prefixInput.addEventListener("input", () => {
  localStorage.setItem("savedPrefix", prefixInput.value);
});

// 文件解析逻辑：支持 CSV 和 Excel 文件
function parseFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    const ext = file.name.split(".").pop().toLowerCase();

    reader.onload = async (e) => {
      try {
        if (ext === "csv") {
          const text = e.target.result;
          const lines = text.split(/\r?\n/);
          const data = lines.map((line) => line.split(","));
          const output = data.map(([id, url]) => ({ id, url })).filter(x => x.url);
          resolve(output);
        } else if (["xlsx", "xls"].includes(ext)) {
          const data = new Uint8Array(e.target.result);
          const workbook = XLSX.read(data, { type: "array" });
          const sheet = workbook.Sheets[workbook.SheetNames[0]];
          const json = XLSX.utils.sheet_to_json(sheet, { header: 1 });
          const output = json.map(([id, url]) => ({ id, url })).filter(x => x.url);
          resolve(output);
        }
      } catch (err) {
        reject(err);
      }
    };

    if (ext === "csv") reader.readAsText(file);
    else reader.readAsArrayBuffer(file);
  });
}

// 保存当前页面为 HTML 文件并下载或写入目录
document.getElementById("saveCurrent").addEventListener("click", async () => {
  const rawPrefix = prefixInput.value || "";
  prefix = rawPrefix && !rawPrefix.endsWith("_") ? rawPrefix + "_" : rawPrefix;
  let tabId = null;
  const lastId = parseInt(localStorage.getItem("lastShopeeTabId"));
  const lastUrl = localStorage.getItem("lastShopeeUrl");

  if (!isNaN(lastId)) {
    try {
      const tab = await chrome.tabs.get(lastId);
      if (tab && tab.url.includes("shopee")) {
        tabId = tab.id;
      }
    } catch (e) {
      console.warn("上次打开的 Shopee 标签页不可用，使用当前 tab");
    }
  }

  if (!tabId) {
    const [current] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (current.url.startsWith("chrome-extension://")) {
      showToast("⚠️ 当前标签页是插件页面，无法保存！请先访问商品页。", false);
      return;
    }
    tabId = current.id;
  }

  try {
    const [result] = await chrome.scripting.executeScript({
      target: { tabId },
      func: () => document.documentElement.outerHTML
    });
    const html = result.result;

    let filenameId = Date.now();
    if (lastUrl && idMap[lastUrl]) {
      filenameId = idMap[lastUrl];
    }

    const filename = `${prefix}${filenameId}.html`;

    if (folderId) {
      const fileHandle = await folderId.getFileHandle(filename, { create: true });
      const writable = await fileHandle.createWritable();
      await writable.write(html);
      await writable.close();
      showToast(`✅ 已保存：${filename}`);
    } else {
      const blob = new Blob([html], { type: "text/html" });
      const url = URL.createObjectURL(blob);
      chrome.downloads.download({ url, filename });
      showToast(`✅ 已下载：${filename}`);
    }

    if (autoNext && lastUrl) {
      chrome.tabs.remove(tabId);
      const currentIndex = urlQueue.findIndex(u => u.url === lastUrl);
      const next = urlQueue[currentIndex + 1];
      if (next) {
        const tab = await chrome.tabs.create({ url: next.url, active: true });
        localStorage.setItem("lastShopeeTabId", tab.id);
        localStorage.setItem("lastShopeeUrl", next.url);
      }
    }
  } catch (err) {
    showToast("❌ 保存失败: " + err.message, false);
    console.error(err);
  }
});
