// background.js
chrome.runtime.onInstalled.addListener(() => {
  console.log("Shopee HTML Downloader installed.");
});

chrome.action.onClicked.addListener(() => {
  chrome.windows.getCurrent(window => {
    const left = window.left + window.width - 420;
    chrome.windows.create({
      url: chrome.runtime.getURL("panel.html"),
      type: "popup",
      width: 400,
      height: 600,
      top: window.top + 80,
      left: left > 0 ? left : 100,
      focused: true
    });
  });
});
