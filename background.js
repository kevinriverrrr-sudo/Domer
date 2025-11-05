// Background service worker for Stripe Test Autofill
// Manages test card profiles and orchestrates autofill flow

// Official Stripe test card numbers
const STRIPE_TEST_CARDS = {
  success: {
    number: '4242424242424242',
    brand: 'Visa',
    description: 'Succeeds and does not require authentication'
  },
  success_3ds: {
    number: '4000002500003155',
    brand: 'Visa',
    description: 'Requires authentication (3DS2)'
  },
  decline_generic: {
    number: '4000000000000002',
    brand: 'Visa',
    description: 'Always declined (generic decline)'
  },
  decline_insufficient: {
    number: '4000000000009995',
    brand: 'Visa',
    description: 'Declined (insufficient funds)'
  },
  decline_fraud: {
    number: '4100000000000019',
    brand: 'Visa',
    description: 'Declined (suspected fraud)'
  }
};

// Default billing profiles
const DEFAULT_PROFILES = [
  {
    name: 'John Doe',
    email: 'john.doe@example.com',
    phone: '+1 (555) 123-4567',
    country: 'US',
    line1: '123 Main Street',
    line2: 'Apt 4B',
    city: 'San Francisco',
    state: 'CA',
    postal_code: '94102'
  },
  {
    name: 'Jane Smith',
    email: 'jane.smith@example.com',
    phone: '+1 (555) 987-6543',
    country: 'US',
    line1: '456 Oak Avenue',
    line2: 'Suite 200',
    city: 'New York',
    state: 'NY',
    postal_code: '10001'
  },
  {
    name: 'Alice Johnson',
    email: 'alice.johnson@example.com',
    phone: '+44 20 7123 4567',
    country: 'GB',
    line1: '10 Downing Street',
    line2: '',
    city: 'London',
    state: '',
    postal_code: 'SW1A 2AA'
  },
  {
    name: 'Bob Wilson',
    email: 'bob.wilson@example.com',
    phone: '+1 (555) 555-5555',
    country: 'CA',
    line1: '789 Maple Drive',
    line2: '',
    city: 'Toronto',
    state: 'ON',
    postal_code: 'M5H 2N2'
  }
];

// Generate expiry date (always valid, 2+ years in future)
function generateExpiry() {
  const now = new Date();
  const year = now.getFullYear() + 2;
  const month = Math.floor(Math.random() * 12) + 1;
  return {
    mm: String(month).padStart(2, '0'),
    yy: String(year).slice(-2),
    full: `${String(month).padStart(2, '0')}/${String(year).slice(-2)}`
  };
}

// Generate CVC
function generateCVC() {
  return String(Math.floor(Math.random() * 900) + 100);
}

// Get settings from storage
async function getSettings() {
  const defaults = {
    cardScenario: 'success',
    billingProfile: DEFAULT_PROFILES[0],
    randomizeProfile: false,
    autoSubmit: false
  };
  const result = await chrome.storage.sync.get(defaults);
  return result;
}

// Get billing profile based on settings
async function getBillingProfile() {
  const settings = await getSettings();
  
  if (settings.randomizeProfile) {
    const randomIndex = Math.floor(Math.random() * DEFAULT_PROFILES.length);
    return DEFAULT_PROFILES[randomIndex];
  }
  
  return settings.billingProfile || DEFAULT_PROFILES[0];
}

// Prepare autofill data
async function prepareAutofillData() {
  const settings = await getSettings();
  const cardInfo = STRIPE_TEST_CARDS[settings.cardScenario] || STRIPE_TEST_CARDS.success;
  const expiry = generateExpiry();
  const cvc = generateCVC();
  const billingProfile = await getBillingProfile();
  
  return {
    card: {
      number: cardInfo.number,
      expiry: expiry.full,
      expiryMM: expiry.mm,
      expiryYY: expiry.yy,
      cvc: cvc,
      name: billingProfile.name
    },
    billing: billingProfile,
    autoSubmit: settings.autoSubmit,
    scenario: settings.cardScenario
  };
}

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'START_AUTOFILL') {
    handleStartAutofill(sender.tab.id)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep channel open for async response
  }
  
  if (message.type === 'GET_AUTOFILL_DATA') {
    prepareAutofillData()
      .then(data => sendResponse({ success: true, data }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
  
  if (message.type === 'AUTOFILL_STATUS') {
    // Forward status updates to cursor.com tab
    forwardStatusToCursor(sender.tab.id, message.status, message.details);
    sendResponse({ success: true });
    return true;
  }
});

// Handle start autofill request
async function handleStartAutofill(tabId) {
  try {
    const data = await prepareAutofillData();
    
    // Send message to all frames in the tab to start autofill
    await chrome.tabs.sendMessage(tabId, {
      type: 'EXECUTE_AUTOFILL',
      data: data
    });
    
    return { success: true, message: 'Autofill initiated' };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// Forward status to cursor.com content script
async function forwardStatusToCursor(tabId, status, details) {
  try {
    await chrome.tabs.sendMessage(tabId, {
      type: 'AUTOFILL_UPDATE',
      status: status,
      details: details
    });
  } catch (error) {
    console.error('Failed to forward status:', error);
  }
}

// Handle keyboard command
chrome.commands.onCommand.addListener((command) => {
  if (command === 'trigger-autofill') {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0] && tabs[0].url && tabs[0].url.includes('cursor.com')) {
        chrome.tabs.sendMessage(tabs[0].id, { type: 'TRIGGER_BUTTON_CLICK' });
      }
    });
  }
});

// Initialize default settings on install
chrome.runtime.onInstalled.addListener(async () => {
  const current = await chrome.storage.sync.get(['cardScenario', 'billingProfile', 'randomizeProfile', 'autoSubmit']);
  
  if (!current.cardScenario) {
    await chrome.storage.sync.set({
      cardScenario: 'success',
      billingProfile: DEFAULT_PROFILES[0],
      randomizeProfile: false,
      autoSubmit: false
    });
  }
});

console.log('Stripe Test Autofill background service worker loaded');
