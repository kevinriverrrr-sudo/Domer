const SETTINGS_KEY = "tabMute.settings";
const DEFAULT_SETTINGS = {
  autoMuteEnabled: true,
  showBanner: true,
  muteDelay: 3000,
  exclusions: []
};

const autoMuteToggle = document.getElementById("auto-mute-toggle");
const bannerToggle = document.getElementById("banner-toggle");
const delaySelect = document.getElementById("delay-select");
const exclusionForm = document.getElementById("exclusion-form");
const exclusionInput = document.getElementById("exclusion-input");
const exclusionsList = document.getElementById("exclusions-list");

let currentSettings = { ...DEFAULT_SETTINGS };

function normalizePattern(value) {
  if (!value) {
    return "";
  }
  let pattern = value.trim();
  pattern = pattern.replace(/^https?:\/\//i, "");
  pattern = pattern.replace(/\s+/g, "");
  const slashIndex = pattern.indexOf("/");
  if (slashIndex !== -1) {
    pattern = pattern.slice(0, slashIndex);
  }
  pattern = pattern.replace(/\.$/, "");
  return pattern.toLowerCase();
}

async function loadSettings() {
  const stored = await chrome.storage.local.get(SETTINGS_KEY);
  currentSettings = {
    ...DEFAULT_SETTINGS,
    ...(stored[SETTINGS_KEY] || {})
  };
  syncUi();
}

function saveSettings(nextSettings) {
  currentSettings = { ...nextSettings };
  return chrome.storage.local.set({
    [SETTINGS_KEY]: currentSettings
  });
}

function syncUi() {
  autoMuteToggle.checked = Boolean(currentSettings.autoMuteEnabled);
  bannerToggle.checked = Boolean(currentSettings.showBanner);
  delaySelect.value = String(currentSettings.muteDelay || DEFAULT_SETTINGS.muteDelay);
  renderExclusions(currentSettings.exclusions || []);
}

function renderExclusions(list) {
  exclusionsList.textContent = "";
  if (!list || list.length === 0) {
    return;
  }

  list.forEach((pattern, index) => {
    const item = document.createElement("li");
    item.className = "exclusion-item";

    const label = document.createElement("span");
    label.textContent = pattern;
    item.appendChild(label);

    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.textContent = "Удалить";
    removeButton.addEventListener("click", () => {
      const updated = [...(currentSettings.exclusions || [])];
      updated.splice(index, 1);
      saveSettings({ ...currentSettings, exclusions: updated }).then(() => {
        renderExclusions(updated);
      });
    });

    item.appendChild(removeButton);
    exclusionsList.appendChild(item);
  });
}

autoMuteToggle.addEventListener("change", () => {
  saveSettings({
    ...currentSettings,
    autoMuteEnabled: autoMuteToggle.checked
  });
});

bannerToggle.addEventListener("change", () => {
  saveSettings({
    ...currentSettings,
    showBanner: bannerToggle.checked
  });
});

delaySelect.addEventListener("change", () => {
  const value = Number(delaySelect.value);
  saveSettings({
    ...currentSettings,
    muteDelay: Number.isFinite(value) ? value : DEFAULT_SETTINGS.muteDelay
  });
});

exclusionForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const normalized = normalizePattern(exclusionInput.value);
  if (!normalized) {
    exclusionInput.value = "";
    return;
  }

  const existing = currentSettings.exclusions || [];
  if (existing.some((pattern) => pattern.toLowerCase() === normalized)) {
    exclusionInput.value = "";
    return;
  }

  const updated = [...existing, normalized];
  saveSettings({
    ...currentSettings,
    exclusions: updated
  }).then(() => {
    exclusionInput.value = "";
    renderExclusions(updated);
  });
});

chrome.storage.onChanged.addListener((changes, area) => {
  if (area !== "local" || !changes[SETTINGS_KEY]) {
    return;
  }
  currentSettings = {
    ...DEFAULT_SETTINGS,
    ...(changes[SETTINGS_KEY].newValue || {})
  };
  syncUi();
});

loadSettings();
