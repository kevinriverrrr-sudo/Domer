const TABMUTE_BANNER_ID = "tabmute-banner";
const MEDIA_EVENTS = [
  "play",
  "playing",
  "canplay",
  "canplaythrough",
  "volumechange",
  "ratechange",
  "loadstart"
];

let lastNotificationAt = 0;
let suppressNotificationsUntil = 0;
const observedElements = new WeakSet();

function now() {
  return Date.now();
}

function suppressNotifications(duration = 600) {
  suppressNotificationsUntil = Math.max(suppressNotificationsUntil, now() + duration);
}

function notifyAudioStarted() {
  if (now() < suppressNotificationsUntil) {
    return;
  }

  const throttleMs = 500;
  const current = now();
  if (current - lastNotificationAt < throttleMs) {
    return;
  }

  lastNotificationAt = current;
  try {
    chrome.runtime.sendMessage({ type: "audio_started" });
  } catch (error) {
    // Ignored: messaging can fail on restricted pages.
  }
}

function handleMediaEvent(event) {
  const target = event.target;
  if (!(target instanceof HTMLMediaElement)) {
    return;
  }

  if (target.muted || target.volume === 0) {
    return;
  }

  if (target.dataset.tabMuteMutedByExtension === "true") {
    return;
  }

  notifyAudioStarted();
}

function bindMediaElement(element) {
  if (!(element instanceof HTMLMediaElement)) {
    return;
  }

  if (observedElements.has(element)) {
    return;
  }

  observedElements.add(element);
  MEDIA_EVENTS.forEach((eventName) => {
    element.addEventListener(eventName, handleMediaEvent, true);
  });

  if (!element.paused && !element.muted && element.volume > 0) {
    notifyAudioStarted();
  }
}

function scanForMedia(root = document) {
  if (!root) {
    return;
  }

  if (root instanceof HTMLMediaElement) {
    bindMediaElement(root);
  }

  const elements = root.querySelectorAll ? root.querySelectorAll("audio, video") : [];
  elements.forEach((el) => bindMediaElement(el));
}

function muteTrackedMedia() {
  suppressNotifications(800);
  const elements = document.querySelectorAll("audio, video");
  elements.forEach((element) => {
    if (!(element instanceof HTMLMediaElement)) {
      return;
    }
    if (!element.muted) {
      try {
        element.muted = true;
        element.dataset.tabMuteMutedByExtension = "true";
      } catch (error) {
        // Ignore assignment errors.
      }
    } else if (!element.dataset.tabMuteMutedByExtension) {
      element.dataset.tabMuteMutedByExtension = "inherited";
    }
  });
}

function unmuteTrackedMedia() {
  suppressNotifications(800);
  const elements = document.querySelectorAll("audio, video");
  elements.forEach((element) => {
    if (!(element instanceof HTMLMediaElement)) {
      return;
    }
    if (element.dataset.tabMuteMutedByExtension === "true") {
      try {
        element.muted = false;
      } catch (error) {
        // Ignore assignment errors.
      }
    }
    delete element.dataset.tabMuteMutedByExtension;
  });
}

function ensureBannerContainer() {
  if (document.getElementById(TABMUTE_BANNER_ID)) {
    return document.getElementById(TABMUTE_BANNER_ID);
  }

  const banner = document.createElement("div");
  banner.id = TABMUTE_BANNER_ID;
  banner.style.position = "fixed";
  banner.style.zIndex = "2147483647";
  banner.style.top = "16px";
  banner.style.right = "16px";
  banner.style.maxWidth = "280px";
  banner.style.padding = "12px 16px";
  banner.style.borderRadius = "12px";
  banner.style.boxShadow = "0 10px 30px rgba(45, 55, 72, 0.2)";
  banner.style.background = "#ffffff";
  banner.style.color = "#2d3748";
  banner.style.fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
  banner.style.fontSize = "14px";
  banner.style.lineHeight = "1.4";
  banner.style.display = "flex";
  banner.style.flexDirection = "column";
  banner.style.gap = "8px";
  banner.style.border = "1px solid rgba(49, 130, 206, 0.16)";

  const text = document.createElement("div");
  text.textContent = "Звук отключён TabMute";
  banner.appendChild(text);

  const button = document.createElement("button");
  button.type = "button";
  button.textContent = "Включить";
  button.style.alignSelf = "flex-end";
  button.style.background = "#3182ce";
  button.style.color = "#ffffff";
  button.style.border = "none";
  button.style.borderRadius = "8px";
  button.style.padding = "6px 12px";
  button.style.cursor = "pointer";
  button.style.fontFamily = 'inherit';
  button.style.fontSize = "13px";

  button.addEventListener("click", () => {
    unmuteTrackedMedia();
    hideBanner();
    try {
      chrome.runtime.sendMessage({ type: "user_unmute_request" });
    } catch (error) {
      // Ignore messaging errors.
    }
  });

  banner.appendChild(button);

  if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
    banner.style.background = "#1a202c";
    banner.style.color = "#edf2f7";
    banner.style.border = "1px solid rgba(49, 130, 206, 0.35)";
  }

  return banner;
}

function showBanner() {
  if (document.getElementById(TABMUTE_BANNER_ID)) {
    return;
  }

  const mount = () => {
    const banner = ensureBannerContainer();
    document.body.appendChild(banner);
  };

  if (document.body) {
    mount();
  } else {
    const observer = new MutationObserver(() => {
      if (document.body) {
        observer.disconnect();
        mount();
      }
    });
    observer.observe(document.documentElement || document, { childList: true, subtree: true });
  }
}

function hideBanner() {
  const banner = document.getElementById(TABMUTE_BANNER_ID);
  if (banner) {
    banner.remove();
  }
}

scanForMedia();

const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    mutation.addedNodes.forEach((node) => {
      if (node instanceof HTMLMediaElement) {
        bindMediaElement(node);
      } else if (node && node.querySelectorAll) {
        scanForMedia(node);
      }
    });
  });
});

observer.observe(document.documentElement || document, {
  childList: true,
  subtree: true
});

chrome.runtime.onMessage.addListener((message) => {
  if (!message || !message.action) {
    return;
  }

  if (message.action === "mute_tab") {
    muteTrackedMedia();
    if (message.showBanner) {
      showBanner();
    }
  }

  if (message.action === "unmute_tab") {
    unmuteTrackedMedia();
    hideBanner();
  }
});
