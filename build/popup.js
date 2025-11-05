const statusEl = document.getElementById("status");
const listEl = document.getElementById("muted-list");
const containerEl = document.getElementById("muted-container");
const unmuteAllButton = document.getElementById("unmute-all");
const optionsButton = document.getElementById("open-options");

function applyTheme() {
  if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
    document.body.classList.add("dark");
  } else {
    document.body.classList.remove("dark");
  }
}

applyTheme();
if (window.matchMedia) {
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", applyTheme);
}

function pluralizeTabs(count) {
  const abs = Math.abs(count) % 100;
  const remainder = abs % 10;
  if (abs > 10 && abs < 20) {
    return "вкладок";
  }
  if (remainder > 1 && remainder < 5) {
    return "вкладки";
  }
  if (remainder === 1) {
    return "вкладка";
  }
  return "вкладок";
}

function extractDomain(url) {
  if (!url) {
    return "";
  }
  try {
    const { hostname } = new URL(url);
    return hostname || url;
  } catch (error) {
    return url;
  }
}

function trimTitle(title, maxLength = 60) {
  if (!title) {
    return "Без названия";
  }
  if (title.length <= maxLength) {
    return title;
  }
  return `${title.slice(0, maxLength - 1)}…`;
}

function renderMutedList(tabs) {
  listEl.textContent = "";

  tabs.forEach((tab) => {
    const item = document.createElement("li");
    item.className = "muted-item";

    const info = document.createElement("div");
    info.className = "tab-details";

    const title = document.createElement("p");
    title.className = "tab-title";
    title.textContent = trimTitle(tab.title);

    const domain = document.createElement("p");
    domain.className = "tab-domain";
    domain.textContent = extractDomain(tab.url);

    info.appendChild(title);
    info.appendChild(domain);

    const button = document.createElement("button");
    button.className = "inline";
    button.type = "button";
    button.textContent = "Размутить";
    button.addEventListener("click", () => {
      chrome.runtime.sendMessage({ type: "unmute_tab", tabId: tab.id }, () => {
        window.setTimeout(refreshState, 150);
      });
    });

    item.appendChild(info);
    item.appendChild(button);
    listEl.appendChild(item);
  });
}

function updateView(state) {
  const mutedTabs = state.mutedTabs || [];
  const mutedCount = mutedTabs.length;

  if (!state.autoMuteEnabled) {
    statusEl.textContent = "Автоматическое отключение звука выключено";
  } else if (mutedCount > 0) {
    statusEl.textContent = `🔇 Заглушены ${mutedCount} ${pluralizeTabs(mutedCount)}`;
  } else {
    statusEl.textContent = "✅ Все вкладки в норме";
  }

  if (mutedCount > 0) {
    containerEl.classList.remove("hidden");
    renderMutedList(mutedTabs);
  } else {
    containerEl.classList.add("hidden");
    listEl.textContent = "";
  }

  unmuteAllButton.disabled = mutedCount === 0;
}

function refreshState() {
  chrome.runtime.sendMessage({ type: "get_popup_state" }, (response) => {
    if (chrome.runtime.lastError) {
      statusEl.textContent = "Не удалось получить состояние";
      return;
    }
    updateView(response || { mutedTabs: [], autoMuteEnabled: true });
  });
}

unmuteAllButton.addEventListener("click", () => {
  chrome.runtime.sendMessage({ type: "unmute_all" }, () => {
    window.setTimeout(refreshState, 150);
  });
});

optionsButton.addEventListener("click", () => {
  chrome.runtime.openOptionsPage();
});

document.addEventListener("DOMContentLoaded", () => {
  refreshState();
});
