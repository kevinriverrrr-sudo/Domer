// Content script for cursor.com
// Injects button and manages UI feedback

let autofillButton = null;
let toastContainer = null;

// Create and inject the autofill button
function createButton() {
  if (autofillButton) return;
  
  autofillButton = document.createElement('button');
  autofillButton.id = 'stripe-autofill-button';
  autofillButton.innerHTML = `
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="2" y="4" width="16" height="10" rx="2" stroke="currentColor" stroke-width="2"/>
      <rect x="2" y="7" width="16" height="3" fill="currentColor"/>
    </svg>
    <span>Fill Stripe Test</span>
  `;
  autofillButton.title = 'Autofill Stripe test payment (Ctrl+Shift+A)';
  
  autofillButton.addEventListener('click', handleButtonClick);
  
  document.body.appendChild(autofillButton);
}

// Handle button click
async function handleButtonClick() {
  showToast('Initiating Stripe test autofill...', 'info');
  
  try {
    const response = await chrome.runtime.sendMessage({ type: 'START_AUTOFILL' });
    
    if (response.success) {
      showToast('Looking for Stripe payment forms...', 'info');
    } else {
      showToast(`Error: ${response.error}`, 'error');
    }
  } catch (error) {
    showToast(`Failed to start autofill: ${error.message}`, 'error');
  }
}

// Create toast container
function createToastContainer() {
  if (toastContainer) return;
  
  toastContainer = document.createElement('div');
  toastContainer.id = 'stripe-autofill-toast-container';
  document.body.appendChild(toastContainer);
}

// Show toast notification
function showToast(message, type = 'info', duration = 5000) {
  createToastContainer();
  
  const toast = document.createElement('div');
  toast.className = `stripe-autofill-toast toast-${type}`;
  toast.textContent = message;
  
  toastContainer.appendChild(toast);
  
  setTimeout(() => toast.classList.add('show'), 10);
  
  if (duration > 0) {
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }
  
  return toast;
}

// Listen for messages from background
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'TRIGGER_BUTTON_CLICK') {
    handleButtonClick();
    sendResponse({ success: true });
  }
  
  if (message.type === 'AUTOFILL_UPDATE') {
    handleAutofillUpdate(message.status, message.details);
    sendResponse({ success: true });
  }
  
  return true;
});

// Handle autofill status updates
function handleAutofillUpdate(status, details) {
  switch (status) {
    case 'detecting':
      showToast('Detecting Stripe test mode...', 'info');
      break;
    case 'test_mode_confirmed':
      showToast('✓ Test mode confirmed, filling fields...', 'success', 3000);
      break;
    case 'live_mode_blocked':
      showToast('⚠ BLOCKED: Live mode detected. This extension only works in TEST mode.', 'error', 10000);
      break;
    case 'filling':
      showToast(`Filling ${details}...`, 'info', 2000);
      break;
    case 'success':
      showToast(`✓ ${details}`, 'success', 5000);
      break;
    case 'error':
      showToast(`✗ Error: ${details}`, 'error', 7000);
      break;
    case 'warning':
      showToast(`⚠ ${details}`, 'warning', 5000);
      break;
  }
}

// Initialize
function init() {
  createButton();
  createToastContainer();
  console.log('Stripe Test Autofill: Button injected on cursor.com');
}

// Wait for DOM to be ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
