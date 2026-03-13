// NeuroRoute Background Service Worker
// Handles extension lifecycle and communication

chrome.runtime.onInstalled.addListener(() => {
  console.log("NeuroRoute AI extension installed.");
  chrome.storage.local.set({
    neuroroute_stats: {
      total_queries: 0,
      total_energy: 0,
      total_carbon: 0,
      total_water: 0,
    },
  });
});

// Listen for messages from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "UPDATE_STATS") {
    chrome.storage.local.get("neuroroute_stats", (data) => {
      const stats = data.neuroroute_stats || {};
      stats.total_queries = (stats.total_queries || 0) + 1;
      stats.total_energy = (stats.total_energy || 0) + (message.energy || 0);
      stats.total_carbon = (stats.total_carbon || 0) + (message.carbon || 0);
      stats.total_water = (stats.total_water || 0) + (message.water || 0);
      chrome.storage.local.set({ neuroroute_stats: stats });
      sendResponse({ success: true, stats });
    });
    return true;
  }

  if (message.type === "GET_STATS") {
    chrome.storage.local.get("neuroroute_stats", (data) => {
      sendResponse(data.neuroroute_stats || {});
    });
    return true;
  }
});
