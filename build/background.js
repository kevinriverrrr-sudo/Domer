const SETTINGS_KEY = "tabMute.settings";
const MUTED_TABS_KEY = "tabMute.mutedTabs";

const DEFAULT_SETTINGS = {
  autoMuteEnabled: true,
  showBanner: true,
  muteDelay: 3000,
  exclusions: []
};

const state = {
  settings: { ...DEFAULT_SETTINGS },
  mutedTabs: new Map(),
  pendingTimers: new Map(),
  manualBypass: new Map()
};

const BADGE_COLOR = "#E53E3E";
const BADGE_TEXT_MUTED = "•";

async function ensureDefaultSettings() {
  const stored = await chrome.storage.local.get(SETTINGS_KEY);
  if (!stored[SETTINGS_KEY]) {
    await chrome.storage.local.set({
      [SETTINGS_KEY]: { ...DEFAULT_SETTINGS }
    });
  }
}

async function loadState() {
  const [settingsEntry, mutedEntry] = await Promise.all([
    chrome.storage.local.get(SETTINGS_KEY),
    chrome.storage.local.get(MUTED_TABS_KEY)
  ]);

  state.settings = {
    ...DEFAULT_SETTINGS,
    ...(settingsEntry[SETTINGS_KEY] || {})
  };

  const mutedItems = mutedEntry[MUTED_TABS_KEY] || [];
  state.mutedTabs = new Map(
    mutedItems
      .filter((item) => item && typeof item.id === "number")
      .map((item) => [item.id, { ...item, id: item.id }])
  );

  await cleanMutedTabState();
  updateBadge();
}

async function cleanMutedTabState() {
  if (state.mutedTabs.size === 0) {
    return;
  }

  const removals = [];
  for (const tabId of state.mutedTabs.keys()) {
    try {
      const tab = await chrome.tabs.get(tabId);
      if (!tab || !tab.mutedInfo || !tab.mutedInfo.muted) {
        removals.push(tabId);
      }
    } catch (error) {
      removals.push(tabId);
    }
  }

  if (removals.length > 0) {
    for (const tabId of removals) {
      state.mutedTabs.delete(tabId);
    }
    await persistMutedTabs();
  }
}

async function persistMutedTabs() {
  const serialized = Array.from(state.mutedTabs.values()).map((item) => ({
    id: item.id,
    title: item.title || "",
    url: item.url || "",
    mutedAt: item.mutedAt || Date.now()
  }));
  await chrome.storage.local.set({
    [MUTED_TABS_KEY]: serialized
  });
}

function updateBadge() {
  const text = state.mutedTabs.size > 0 ? BADGE_TEXT_MUTED : "";
  chrome.action.setBadgeText({ text });
  if (text) {
    chrome.action.setBadgeBackgroundColor({ color: BADGE_COLOR });
  }
}

function cancelPendingMute(tabId) {
  const timeoutId = state.pendingTimers.get(tabId);
  if (timeoutId) {
    clearTimeout(timeoutId);
    state.pendingTimers.delete(tabId);
  }
}

function cancelAllPendingMutes() {
  for (const timeoutId of state.pendingTimers.values()) {
    clearTimeout(timeoutId);
  }
  state.pendingTimers.clear();
}

function registerBypass(tabId, durationMs = 8000) {
  const expiresAt = Date.now() + durationMs;
  state.manualBypass.set(tabId, expiresAt);
}

function isBypassed(tabId) {
  const expiresAt = state.manualBypass.get(tabId);
  if (typeof expiresAt !== "number") {
    return false;
  }
  if (Date.now() > expiresAt) {
    state.manualBypass.delete(tabId);
    return false;
  }
  return true;
}

function normalizePattern(pattern) {
  return (pattern || "")
    .trim()
    .replace(/^https?:\/\//i, "")
    .replace(/\/$/, "")
    .toLowerCase();
}

function wildcardToRegExp(pattern) {
  const escaped = pattern.replace(/[.+?^${}()|[\]\\]/g, "\\$&");
  const regexString = `^${escaped.replace(/\\\*/g, ".*")}$`;
  return new RegExp(regexString, "i");
}

function isExcluded(url, patterns) {
  if (!url || !patterns || patterns.length === 0) {
    return false;
  }
  let host;
  try {
    host = new URL(url).hostname.toLowerCase();
  } catch (error) {
    return false;
  }

  return patterns.some((pattern) => {
    const trimmed = normalizePattern(pattern);
    if (!trimmed) {
      return false;
    }

    // Allow hostnames without wildcards to match subdomains as well.
    if (!trimmed.includes("*")) {
      return host === trimmed || host.endsWith(`.${trimmed}`);
    }

    try {
      const regex = wildcardToRegExp(trimmed);
      return regex.test(host);
    } catch (error) {
      return false;
    }
  });
}

async function handleAudioStarted(tabId) {
  if (!state.settings.autoMuteEnabled) {
    return;
  }
  if (state.pendingTimers.has(tabId) || state.mutedTabs.has(tabId) || isBypassed(tabId)) {
    return;
  }

  let tab;
  try {
    tab = await chrome.tabs.get(tabId);
  } catch (error) {
    return;
  }

  if (!tab || tab.active || isExcluded(tab.url, state.settings.exclusions)) {
    return;
  }

  const delay = Math.max(0, Number(state.settings.muteDelay) || DEFAULT_SETTINGS.muteDelay);

  const timeoutId = setTimeout(() => {
    state.pendingTimers.delete(tabId);
    muteTab(tabId).catch(() => {
      /* no-op */
    });
  }, delay);

  state.pendingTimers.set(tabId, timeoutId);
}

async function muteTab(tabId) {
  let tab;
  try {
    tab = await chrome.tabs.get(tabId);
  } catch (error) {
    return;
  }

  if (!tab || tab.active || isExcluded(tab.url, state.settings.exclusions)) {
    return;
  }

  if (isBypassed(tabId)) {
    return;
  }

  try {
    await chrome.tabs.update(tabId, { muted: true });
  } catch (error) {
    return;
  }

  const updatedEntry = {
    id: tabId,
    title: tab.title || tab.url || "",
    url: tab.url || "",
    mutedAt: Date.now()
  };
  state.mutedTabs.set(tabId, updatedEntry);
  await persistMutedTabs();
  updateBadge();

  chrome.tabs.sendMessage(tabId, {
    action: "mute_tab",
    showBanner: Boolean(state.settings.showBanner)
  }).catch(() => {
    /* Ignore messaging failures (e.g., chrome:// pages). */
  });
}

async function unmuteTab(tabId, { registerManualBypass = true } = {}) {
  cancelPendingMute(tabId);

  try {
    await chrome.tabs.update(tabId, { muted: false });
  } catch (error) {
    // Tab may no longer exist; still continue cleanup.
  }

  const removed = state.mutedTabs.delete(tabId);
  if (removed) {
    await persistMutedTabs();
    updateBadge();
  }

  if (registerManualBypass) {
    registerBypass(tabId);
  }

  chrome.tabs.sendMessage(tabId, { action: "unmute_tab" }).catch(() => {
    /* Ignore messaging failures */
  });
}

async function unmuteAllTabs() {
  const tabIds = Array.from(state.mutedTabs.keys());
  await Promise.all(tabIds.map((tabId) => unmuteTab(tabId)));
}

function applyExclusionsToState() {
  const exclusions = state.settings.exclusions;
  if (!exclusions || exclusions.length === 0) {
    return;
  }

  for (const [tabId, info] of state.mutedTabs.entries()) {
    if (isExcluded(info.url, exclusions)) {
      unmuteTab(tabId).catch(() => {
        /* ignore */
      });
    }
  }

  for (const tabId of state.pendingTimers.keys()) {
    chrome.tabs
      .get(tabId)
      .then((tab) => {
        if (tab && isExcluded(tab.url, exclusions)) {
          cancelPendingMute(tabId);
        }
      })
      .catch(() => {
        cancelPendingMute(tabId);
      });
  }
}

function handleTabActivated(activeInfo) {
  const tabId = activeInfo.tabId;
  cancelPendingMute(tabId);
  if (state.mutedTabs.has(tabId)) {
    unmuteTab(tabId).catch(() => {
      /* ignore */
    });
  } else {
    registerBypass(tabId);
  }
}

async function handleTabUpdated(tabId, changeInfo, tab) {
  if (changeInfo.audible === true) {
    await handleAudioStarted(tabId);
  }

  if (changeInfo.mutedInfo && changeInfo.mutedInfo.muted === false && state.mutedTabs.has(tabId)) {
    await unmuteTab(tabId, { registerManualBypass: true });
  }

  if (state.mutedTabs.has(tabId)) {
    const existing = state.mutedTabs.get(tabId);
    const updated = {
      ...existing,
      title: tab?.title || existing.title,
      url: changeInfo.url || tab?.url || existing.url
    };
    state.mutedTabs.set(tabId, updated);
    await persistMutedTabs();
  }
}

function handleTabRemoved(tabId) {
  cancelPendingMute(tabId);
  state.manualBypass.delete(tabId);
  if (state.mutedTabs.has(tabId)) {
    state.mutedTabs.delete(tabId);
    persistMutedTabs().then(updateBadge);
  }
}

chrome.runtime.onInstalled.addListener(() => {
  ensureDefaultSettings().catch(() => {
    /* ignore */
  });
});

chrome.runtime.onStartup.addListener(() => {
  loadState().catch(() => {
    /* ignore */
  });
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (!message) {
    return false;
  }

  if (message.type === "audio_started" && sender.tab && typeof sender.tab.id === "number") {
    handleAudioStarted(sender.tab.id);
    return false;
  }

  if (message.type === "user_unmute_request" && sender.tab && typeof sender.tab.id === "number") {
    unmuteTab(sender.tab.id, { registerManualBypass: true }).catch(() => {
      /* ignore */
    });
    return false;
  }

  if (message.type === "unmute_tab" && typeof message.tabId === "number") {
    unmuteTab(message.tabId).catch(() => {
      /* ignore */
    });
    return false;
  }

  if (message.type === "unmute_all") {
    unmuteAllTabs().catch(() => {
      /* ignore */
    });
    return false;
  }

  if (message.type === "get_popup_state") {
    (async () => {
      const entries = [];
      for (const [tabId, cached] of state.mutedTabs.entries()) {
        try {
          const tab = await chrome.tabs.get(tabId);
          entries.push({
            id: tabId,
            title: tab.title || cached.title || "",
            url: tab.url || cached.url || ""
          });
        } catch (error) {
          entries.push({
            id: tabId,
            title: cached.title || "",
            url: cached.url || ""
          });
        }
      }

      sendResponse({
        mutedTabs: entries,
        autoMuteEnabled: state.settings.autoMuteEnabled
      });
    })();
    return true;
  }

  return false;
});

chrome.storage.onChanged.addListener((changes, area) => {
  if (area !== "local") {
    return;
  }

  if (changes[MUTED_TABS_KEY]) {
    const newValue = changes[MUTED_TABS_KEY].newValue || [];
    state.mutedTabs = new Map(
      newValue
        .filter((item) => item && typeof item.id === "number")
        .map((item) => [item.id, { ...item, id: item.id }])
    );
    updateBadge();
  }

  if (changes[SETTINGS_KEY]) {
    const previousSettings = state.settings;
    state.settings = {
      ...DEFAULT_SETTINGS,
      ...(changes[SETTINGS_KEY].newValue || {})
    };

    if (!state.settings.autoMuteEnabled) {
      cancelAllPendingMutes();
    }

    const exclusionsChanged =
      JSON.stringify((changes[SETTINGS_KEY].oldValue || {}).exclusions || []) !==
      JSON.stringify((changes[SETTINGS_KEY].newValue || {}).exclusions || []);

    if (exclusionsChanged) {
      applyExclusionsToState();
    }

    if (previousSettings.autoMuteEnabled && !state.settings.autoMuteEnabled) {
      unmuteAllTabs().catch(() => {
        /* ignore */
      });
    }
  }
});

chrome.tabs.onActivated.addListener(handleTabActivated);
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  handleTabUpdated(tabId, changeInfo, tab).catch(() => {
    /* ignore */
  });
});
chrome.tabs.onRemoved.addListener(handleTabRemoved);
chrome.tabs.onCreated.addListener((tab) => {
  if (tab && tab.id != null && tab.audible) {
    handleAudioStarted(tab.id).catch(() => {
      /* ignore */
    });
  }
});

(async function init() {
  chrome.action.setBadgeText({ text: "" });
  chrome.action.setBadgeBackgroundColor({ color: BADGE_COLOR });
  await ensureDefaultSettings();
  await loadState();
})();
