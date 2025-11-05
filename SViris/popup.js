// Tab switching functionality
document.querySelectorAll('.tab-button').forEach(button => {
  button.addEventListener('click', () => {
    const tabName = button.dataset.tab;
    
    // Remove active class from all tabs and contents
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Add active class to clicked tab and corresponding content
    button.classList.add('active');
    document.getElementById(tabName).classList.add('active');
  });
});

// File scanning functionality
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const selectFileBtn = document.getElementById('selectFileBtn');
const fileScanResult = document.getElementById('fileScanResult');
const fileResultContent = document.getElementById('fileResultContent');
const newFileScanBtn = document.getElementById('newFileScan');

selectFileBtn.addEventListener('click', () => fileInput.click());

// Drag and drop functionality
uploadArea.addEventListener('dragover', (e) => {
  e.preventDefault();
  uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
  uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
  e.preventDefault();
  uploadArea.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) scanFile(file);
});

fileInput.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) scanFile(file);
});

newFileScanBtn.addEventListener('click', () => {
  fileScanResult.classList.add('hidden');
  fileInput.value = '';
});

async function scanFile(file) {
  if (file.size > CONFIG.MAX_FILE_SIZE) {
    showError('Файл слишком большой. Максимальный размер: 32 МБ');
    return;
  }

  showLoading(fileResultContent);
  fileScanResult.classList.remove('hidden');

  try {
    // Calculate file hash
    const hash = await calculateFileHash(file);
    
    // Check if file is already scanned in VirusTotal
    let result = await checkFileHash(hash);
    
    if (!result) {
      // Upload file for scanning
      result = await uploadFileForScanning(file);
    }

    displayFileScanResult(result, file.name);
    saveToHistory('file', file.name, result);
  } catch (error) {
    console.error('Scan error:', error);
    showError('Ошибка при сканировании файла: ' + error.message);
  }
}

async function calculateFileHash(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        const buffer = e.target.result;
        const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
        resolve(hashHex);
      } catch (error) {
        reject(error);
      }
    };
    reader.onerror = reject;
    reader.readAsArrayBuffer(file);
  });
}

async function checkFileHash(hash) {
  try {
    const response = await fetch(`${CONFIG.VIRUSTOTAL_API_URL}/files/${hash}`, {
      method: 'GET',
      headers: {
        'x-apikey': CONFIG.VIRUSTOTAL_API_KEY
      }
    });

    if (response.status === 404) {
      return null; // File not found, needs to be uploaded
    }

    if (!response.ok) {
      throw new Error('API request failed');
    }

    const data = await response.json();
    return data.data.attributes;
  } catch (error) {
    console.error('Error checking hash:', error);
    return null;
  }
}

async function uploadFileForScanning(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${CONFIG.VIRUSTOTAL_API_URL}/files`, {
    method: 'POST',
    headers: {
      'x-apikey': CONFIG.VIRUSTOTAL_API_KEY
    },
    body: formData
  });

  if (!response.ok) {
    throw new Error('Failed to upload file');
  }

  const data = await response.json();
  const analysisId = data.data.id;

  // Wait for analysis to complete
  return await pollAnalysisResult(analysisId);
}

async function pollAnalysisResult(analysisId) {
  let attempts = 0;
  const maxAttempts = 30;

  while (attempts < maxAttempts) {
    await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds

    const response = await fetch(`${CONFIG.VIRUSTOTAL_API_URL}/analyses/${analysisId}`, {
      headers: {
        'x-apikey': CONFIG.VIRUSTOTAL_API_KEY
      }
    });

    const data = await response.json();
    const status = data.data.attributes.status;

    if (status === 'completed') {
      // Get file report
      const fileId = data.data.meta.file_info.sha256;
      return await checkFileHash(fileId);
    }

    attempts++;
  }

  throw new Error('Analysis timeout');
}

function displayFileScanResult(result, fileName) {
  const stats = result.last_analysis_stats || {};
  const malicious = stats.malicious || 0;
  const suspicious = stats.suspicious || 0;
  const undetected = stats.undetected || 0;
  const total = malicious + suspicious + undetected + (stats.harmless || 0);

  let statusClass = 'safe';
  let statusText = 'Чисто';
  
  if (malicious > 0) {
    statusClass = 'danger';
    statusText = 'Обнаружена угроза';
  } else if (suspicious > 0) {
    statusClass = 'warning';
    statusText = 'Подозрительно';
  }

  fileResultContent.innerHTML = `
    <div class="result-item">
      <span class="result-label">Файл:</span>
      <span class="result-value">${fileName}</span>
    </div>
    <div class="result-item">
      <span class="result-label">Статус:</span>
      <span class="result-value ${statusClass}">${statusText}</span>
    </div>
    <div class="result-item">
      <span class="result-label">Вредоносных:</span>
      <span class="result-value ${malicious > 0 ? 'danger' : ''}">${malicious} из ${total}</span>
    </div>
    <div class="result-item">
      <span class="result-label">Подозрительных:</span>
      <span class="result-value ${suspicious > 0 ? 'warning' : ''}">${suspicious} из ${total}</span>
    </div>
    <div class="result-item">
      <span class="result-label">Размер:</span>
      <span class="result-value">${formatFileSize(result.size || 0)}</span>
    </div>
    ${result.type_description ? `
    <div class="result-item">
      <span class="result-label">Тип:</span>
      <span class="result-value">${result.type_description}</span>
    </div>
    ` : ''}
  `;
}

// URL scanning functionality
const urlInput = document.getElementById('urlInput');
const scanUrlBtn = document.getElementById('scanUrlBtn');
const scanCurrentPageBtn = document.getElementById('scanCurrentPageBtn');
const urlScanResult = document.getElementById('urlScanResult');
const urlResultContent = document.getElementById('urlResultContent');

scanUrlBtn.addEventListener('click', () => {
  const url = urlInput.value.trim();
  if (url) scanUrl(url);
});

scanCurrentPageBtn.addEventListener('click', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (tab?.url) {
    urlInput.value = tab.url;
    scanUrl(tab.url);
  }
});

async function scanUrl(url) {
  if (!isValidUrl(url)) {
    showError('Введите корректный URL');
    return;
  }

  showLoading(urlResultContent);
  urlScanResult.classList.remove('hidden');

  try {
    // Get URL ID
    const urlId = btoa(url).replace(/=/g, '');
    
    // Check if URL is already scanned
    let result = await checkUrlReport(urlId);
    
    if (!result) {
      // Submit URL for scanning
      result = await submitUrlForScanning(url);
    }

    displayUrlScanResult(result, url);
    saveToHistory('url', url, result);
  } catch (error) {
    console.error('URL scan error:', error);
    showError('Ошибка при проверке URL: ' + error.message);
  }
}

async function checkUrlReport(urlId) {
  try {
    const response = await fetch(`${CONFIG.VIRUSTOTAL_API_URL}/urls/${urlId}`, {
      headers: {
        'x-apikey': CONFIG.VIRUSTOTAL_API_KEY
      }
    });

    if (response.status === 404) {
      return null;
    }

    if (!response.ok) {
      throw new Error('API request failed');
    }

    const data = await response.json();
    return data.data.attributes;
  } catch (error) {
    console.error('Error checking URL:', error);
    return null;
  }
}

async function submitUrlForScanning(url) {
  const formData = new FormData();
  formData.append('url', url);

  const response = await fetch(`${CONFIG.VIRUSTOTAL_API_URL}/urls`, {
    method: 'POST',
    headers: {
      'x-apikey': CONFIG.VIRUSTOTAL_API_KEY
    },
    body: formData
  });

  if (!response.ok) {
    throw new Error('Failed to submit URL');
  }

  const data = await response.json();
  const analysisId = data.data.id;

  // Wait for analysis
  return await pollAnalysisResult(analysisId);
}

function displayUrlScanResult(result, url) {
  const stats = result.last_analysis_stats || {};
  const malicious = stats.malicious || 0;
  const suspicious = stats.suspicious || 0;
  const total = malicious + suspicious + (stats.undetected || 0) + (stats.harmless || 0);

  let statusClass = 'safe';
  let statusText = 'Безопасно';
  
  if (malicious > 0) {
    statusClass = 'danger';
    statusText = 'Опасный сайт';
  } else if (suspicious > 0) {
    statusClass = 'warning';
    statusText = 'Подозрительный';
  }

  urlResultContent.innerHTML = `
    <div class="result-item">
      <span class="result-label">URL:</span>
      <span class="result-value" style="word-break: break-all;">${url}</span>
    </div>
    <div class="result-item">
      <span class="result-label">Статус:</span>
      <span class="result-value ${statusClass}">${statusText}</span>
    </div>
    <div class="result-item">
      <span class="result-label">Вредоносных:</span>
      <span class="result-value ${malicious > 0 ? 'danger' : ''}">${malicious} из ${total}</span>
    </div>
    <div class="result-item">
      <span class="result-label">Подозрительных:</span>
      <span class="result-value ${suspicious > 0 ? 'warning' : ''}">${suspicious} из ${total}</span>
    </div>
    ${result.last_final_url && result.last_final_url !== url ? `
    <div class="result-item">
      <span class="result-label">Перенаправление:</span>
      <span class="result-value">${result.last_final_url}</span>
    </div>
    ` : ''}
  `;
}

// Behavior monitoring
const monitorScripts = document.getElementById('monitorScripts');
const monitorNetwork = document.getElementById('monitorNetwork');
const monitorCookies = document.getElementById('monitorCookies');
const monitorDownloads = document.getElementById('monitorDownloads');
const logEntries = document.getElementById('logEntries');

// Load monitoring settings
chrome.storage.local.get(['monitoring'], (result) => {
  const settings = result.monitoring || {};
  monitorScripts.checked = settings.scripts !== false;
  monitorNetwork.checked = settings.network !== false;
  monitorCookies.checked = settings.cookies !== false;
  monitorDownloads.checked = settings.downloads !== false;
});

// Save monitoring settings
[monitorScripts, monitorNetwork, monitorCookies, monitorDownloads].forEach(checkbox => {
  checkbox.addEventListener('change', () => {
    const settings = {
      scripts: monitorScripts.checked,
      network: monitorNetwork.checked,
      cookies: monitorCookies.checked,
      downloads: monitorDownloads.checked
    };
    chrome.storage.local.set({ monitoring: settings });
    chrome.runtime.sendMessage({ action: 'updateMonitoring', settings });
  });
});

// Load behavior stats
function loadBehaviorStats() {
  chrome.storage.local.get(['behaviorStats', 'activityLog'], (result) => {
    const stats = result.behaviorStats || { scripts: 0, requests: 0, warnings: 0 };
    document.getElementById('scriptCount').textContent = stats.scripts;
    document.getElementById('requestCount').textContent = stats.requests;
    document.getElementById('warningCount').textContent = stats.warnings;

    const logs = result.activityLog || [];
    displayActivityLog(logs);
  });
}

function displayActivityLog(logs) {
  if (logs.length === 0) {
    logEntries.innerHTML = '<p class="empty-state">Нет записей</p>';
    return;
  }

  logEntries.innerHTML = logs.slice(-20).reverse().map(log => `
    <div class="log-entry ${log.type || ''}">
      <span class="log-entry-time">${formatTime(log.timestamp)}</span>
      <span class="log-entry-message">${log.message}</span>
    </div>
  `).join('');
}

// History functionality
const historyList = document.getElementById('historyList');
const clearHistoryBtn = document.getElementById('clearHistoryBtn');
let currentFilter = 'all';

document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentFilter = btn.dataset.filter;
    loadHistory();
  });
});

clearHistoryBtn.addEventListener('click', () => {
  if (confirm('Вы уверены, что хотите очистить историю?')) {
    chrome.storage.local.set({ scanHistory: [] });
    loadHistory();
  }
});

function loadHistory() {
  chrome.storage.local.get(['scanHistory'], (result) => {
    let history = result.scanHistory || [];
    
    if (currentFilter !== 'all') {
      history = history.filter(item => {
        if (currentFilter === 'files') return item.type === 'file';
        if (currentFilter === 'urls') return item.type === 'url';
        if (currentFilter === 'threats') return item.malicious > 0;
        return true;
      });
    }

    displayHistory(history);
  });
}

function displayHistory(history) {
  if (history.length === 0) {
    historyList.innerHTML = '<p class="empty-state">История пуста</p>';
    return;
  }

  historyList.innerHTML = history.slice(-50).reverse().map(item => {
    const isClean = item.malicious === 0 && item.suspicious === 0;
    return `
      <div class="history-item">
        <div class="history-item-header">
          <span class="history-item-name">${truncate(item.name, 40)}</span>
          <span class="history-item-status ${isClean ? 'clean' : 'threat'}">
            ${isClean ? 'Чисто' : 'Угроза'}
          </span>
        </div>
        <div class="history-item-time">${formatDateTime(item.timestamp)}</div>
      </div>
    `;
  }).join('');
}

function saveToHistory(type, name, result) {
  const stats = result.last_analysis_stats || {};
  const historyItem = {
    type,
    name,
    malicious: stats.malicious || 0,
    suspicious: stats.suspicious || 0,
    timestamp: Date.now()
  };

  chrome.storage.local.get(['scanHistory'], (data) => {
    const history = data.scanHistory || [];
    history.push(historyItem);
    chrome.storage.local.set({ scanHistory: history.slice(-100) }); // Keep last 100 items
  });
}

// Utility functions
function isValidUrl(string) {
  try {
    new URL(string);
    return true;
  } catch (_) {
    return false;
  }
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

function formatTime(timestamp) {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
}

function formatDateTime(timestamp) {
  const date = new Date(timestamp);
  return date.toLocaleString('ru-RU', { 
    day: '2-digit', 
    month: '2-digit', 
    year: 'numeric',
    hour: '2-digit', 
    minute: '2-digit' 
  });
}

function truncate(str, maxLength) {
  if (str.length <= maxLength) return str;
  return str.substr(0, maxLength - 3) + '...';
}

function showLoading(container) {
  container.innerHTML = `
    <div class="loading">
      <div class="spinner"></div>
      <p class="loading-text">Сканирование...</p>
    </div>
  `;
}

function showError(message) {
  alert(message);
}

// Initialize
loadBehaviorStats();
loadHistory();

// Update stats every 5 seconds when on behavior tab
setInterval(() => {
  if (document.getElementById('behavior').classList.contains('active')) {
    loadBehaviorStats();
  }
}, 5000);
