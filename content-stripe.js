// Content script for Stripe frames
// Detects test mode and fills payment forms

const TEST_MODE_INDICATORS = {
  TEST_BANNER: ['test mode', 'test data', 'using test'],
  TEST_KEY: ['pk_test_'],
  TEST_SESSION: ['cs_test_']
};

let autofillData = null;
let isTestMode = null;

// Detect if we're in Stripe test mode
function detectTestMode() {
  if (isTestMode !== null) return isTestMode;
  
  // Check for test mode banner
  const bodyText = document.body.innerText.toLowerCase();
  for (const indicator of TEST_MODE_INDICATORS.TEST_BANNER) {
    if (bodyText.includes(indicator)) {
      isTestMode = true;
      return true;
    }
  }
  
  // Check for test publishable key in page
  const scripts = document.querySelectorAll('script');
  for (const script of scripts) {
    if (script.textContent.includes('pk_test_')) {
      isTestMode = true;
      return true;
    }
  }
  
  // Check URL for test session
  if (window.location.href.includes('cs_test_')) {
    isTestMode = true;
    return true;
  }
  
  // Check for test mode in data attributes
  const testElements = document.querySelectorAll('[data-test-mode="true"], [data-env="test"]');
  if (testElements.length > 0) {
    isTestMode = true;
    return true;
  }
  
  // Check localStorage/sessionStorage for test indicators
  try {
    const storage = JSON.stringify({ ...localStorage, ...sessionStorage });
    if (storage.includes('pk_test_') || storage.includes('test_mode')) {
      isTestMode = true;
      return true;
    }
  } catch (e) {
    // Storage access might be restricted in iframe
  }
  
  // Default to false (block if uncertain)
  isTestMode = false;
  return false;
}

// Notify about test mode status
function notifyTestModeStatus(isTest) {
  chrome.runtime.sendMessage({
    type: 'AUTOFILL_STATUS',
    status: isTest ? 'test_mode_confirmed' : 'live_mode_blocked',
    details: isTest ? 'Proceeding with autofill' : 'Cannot autofill in live mode'
  }).catch(() => {});
}

// Wait for element with timeout
function waitForElement(selector, timeout = 10000) {
  return new Promise((resolve, reject) => {
    const element = document.querySelector(selector);
    if (element) {
      resolve(element);
      return;
    }
    
    const observer = new MutationObserver((mutations, obs) => {
      const element = document.querySelector(selector);
      if (element) {
        obs.disconnect();
        resolve(element);
      }
    });
    
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
    
    setTimeout(() => {
      observer.disconnect();
      reject(new Error(`Element ${selector} not found within ${timeout}ms`));
    }, timeout);
  });
}

// Fill input field with typing simulation
function fillField(element, value, label = '') {
  if (!element || !value) return false;
  
  try {
    // Focus the field
    element.focus();
    
    // Clear existing value
    element.value = '';
    
    // Trigger input event
    element.dispatchEvent(new Event('input', { bubbles: true }));
    
    // Set value
    element.value = value;
    
    // Trigger various events that Stripe listens to
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));
    element.dispatchEvent(new Event('blur', { bubbles: true }));
    
    // Trigger keyboard events
    element.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true }));
    element.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true }));
    
    if (label) {
      console.log(`Filled ${label}:`, value);
    }
    
    return true;
  } catch (error) {
    console.error(`Error filling field ${label}:`, error);
    return false;
  }
}

// Common field selectors for Stripe
const FIELD_SELECTORS = {
  // Card number
  cardNumber: [
    'input[name="cardnumber"]',
    'input[name="number"]',
    'input[placeholder*="card number" i]',
    'input[placeholder*="Card number" i]',
    'input[aria-label*="card number" i]',
    'input[id*="cardnumber" i]',
    'input[data-testid*="card-number"]',
    '#card-number',
    '.CardNumberField-input',
    '[name="card-number"]'
  ],
  
  // Expiry
  expiry: [
    'input[name="exp-date"]',
    'input[name="expiry"]',
    'input[placeholder*="MM" i]',
    'input[placeholder*="expir" i]',
    'input[aria-label*="expir" i]',
    'input[id*="expiry" i]',
    'input[data-testid*="expiry"]',
    '#card-expiry',
    '.CardExpiryField-input'
  ],
  
  expiryMonth: [
    'input[name="exp-month"]',
    'input[placeholder*="MM" i]',
    'select[name="exp-month"]',
    'select[name="month"]'
  ],
  
  expiryYear: [
    'input[name="exp-year"]',
    'input[placeholder*="YY" i]',
    'select[name="exp-year"]',
    'select[name="year"]'
  ],
  
  // CVC
  cvc: [
    'input[name="cvc"]',
    'input[name="cvv"]',
    'input[placeholder*="CVC" i]',
    'input[placeholder*="CVV" i]',
    'input[placeholder*="security" i]',
    'input[aria-label*="CVC" i]',
    'input[id*="cvc" i]',
    'input[data-testid*="cvc"]',
    '#card-cvc',
    '.CardCVCField-input'
  ],
  
  // Cardholder name
  name: [
    'input[name="name"]',
    'input[name="cardholder"]',
    'input[name="cardholderName"]',
    'input[name="ccname"]',
    'input[placeholder*="name on card" i]',
    'input[placeholder*="cardholder" i]',
    'input[aria-label*="name" i]',
    'input[id*="cardholder" i]',
    'input[autocomplete="cc-name"]'
  ],
  
  // Billing fields
  email: [
    'input[name="email"]',
    'input[type="email"]',
    'input[placeholder*="email" i]',
    'input[autocomplete="email"]'
  ],
  
  phone: [
    'input[name="phone"]',
    'input[name="phoneNumber"]',
    'input[type="tel"]',
    'input[placeholder*="phone" i]',
    'input[autocomplete="tel"]'
  ],
  
  country: [
    'select[name="country"]',
    'select[name="billingCountry"]',
    'input[name="country"]',
    'select[autocomplete="country"]'
  ],
  
  addressLine1: [
    'input[name="address"]',
    'input[name="addressLine1"]',
    'input[name="billingAddressLine1"]',
    'input[name="line1"]',
    'input[placeholder*="address" i]',
    'input[autocomplete="address-line1"]'
  ],
  
  addressLine2: [
    'input[name="addressLine2"]',
    'input[name="billingAddressLine2"]',
    'input[name="line2"]',
    'input[placeholder*="apartment" i]',
    'input[placeholder*="suite" i]',
    'input[autocomplete="address-line2"]'
  ],
  
  city: [
    'input[name="city"]',
    'input[name="billingCity"]',
    'input[placeholder*="city" i]',
    'input[autocomplete="address-level2"]'
  ],
  
  state: [
    'input[name="state"]',
    'input[name="province"]',
    'select[name="state"]',
    'select[name="province"]',
    'input[name="billingState"]',
    'input[placeholder*="state" i]',
    'input[autocomplete="address-level1"]'
  ],
  
  postalCode: [
    'input[name="postalCode"]',
    'input[name="zipCode"]',
    'input[name="zip"]',
    'input[name="postal"]',
    'input[placeholder*="postal" i]',
    'input[placeholder*="zip" i]',
    'input[autocomplete="postal-code"]'
  ]
};

// Find element by multiple selectors
function findElement(selectors) {
  for (const selector of selectors) {
    const element = document.querySelector(selector);
    if (element) return element;
  }
  return null;
}

// Fill all card and billing fields
async function fillPaymentForm(data) {
  let filledFields = [];
  let errors = [];
  
  // Fill card number
  const cardNumberField = findElement(FIELD_SELECTORS.cardNumber);
  if (cardNumberField) {
    if (fillField(cardNumberField, data.card.number, 'Card Number')) {
      filledFields.push('Card Number');
    }
  }
  
  await sleep(300);
  
  // Fill expiry (combined or separate)
  const expiryField = findElement(FIELD_SELECTORS.expiry);
  if (expiryField) {
    if (fillField(expiryField, data.card.expiry, 'Expiry')) {
      filledFields.push('Expiry');
    }
  } else {
    // Try separate month/year fields
    const monthField = findElement(FIELD_SELECTORS.expiryMonth);
    const yearField = findElement(FIELD_SELECTORS.expiryYear);
    
    if (monthField && yearField) {
      if (fillField(monthField, data.card.expiryMM, 'Expiry Month')) {
        filledFields.push('Expiry Month');
      }
      await sleep(200);
      if (fillField(yearField, data.card.expiryYY, 'Expiry Year')) {
        filledFields.push('Expiry Year');
      }
    }
  }
  
  await sleep(300);
  
  // Fill CVC
  const cvcField = findElement(FIELD_SELECTORS.cvc);
  if (cvcField) {
    if (fillField(cvcField, data.card.cvc, 'CVC')) {
      filledFields.push('CVC');
    }
  }
  
  await sleep(300);
  
  // Fill cardholder name
  const nameField = findElement(FIELD_SELECTORS.name);
  if (nameField) {
    if (fillField(nameField, data.card.name, 'Cardholder Name')) {
      filledFields.push('Cardholder Name');
    }
  }
  
  await sleep(300);
  
  // Fill billing fields
  const emailField = findElement(FIELD_SELECTORS.email);
  if (emailField) {
    if (fillField(emailField, data.billing.email, 'Email')) {
      filledFields.push('Email');
    }
  }
  
  await sleep(200);
  
  const phoneField = findElement(FIELD_SELECTORS.phone);
  if (phoneField) {
    if (fillField(phoneField, data.billing.phone, 'Phone')) {
      filledFields.push('Phone');
    }
  }
  
  await sleep(200);
  
  // Fill country first (it may change other field options)
  const countryField = findElement(FIELD_SELECTORS.country);
  if (countryField) {
    if (countryField.tagName === 'SELECT') {
      countryField.value = data.billing.country;
      countryField.dispatchEvent(new Event('change', { bubbles: true }));
      filledFields.push('Country');
    } else {
      if (fillField(countryField, data.billing.country, 'Country')) {
        filledFields.push('Country');
      }
    }
    await sleep(300);
  }
  
  const line1Field = findElement(FIELD_SELECTORS.addressLine1);
  if (line1Field) {
    if (fillField(line1Field, data.billing.line1, 'Address Line 1')) {
      filledFields.push('Address Line 1');
    }
  }
  
  await sleep(200);
  
  const line2Field = findElement(FIELD_SELECTORS.addressLine2);
  if (line2Field && data.billing.line2) {
    if (fillField(line2Field, data.billing.line2, 'Address Line 2')) {
      filledFields.push('Address Line 2');
    }
  }
  
  await sleep(200);
  
  const cityField = findElement(FIELD_SELECTORS.city);
  if (cityField) {
    if (fillField(cityField, data.billing.city, 'City')) {
      filledFields.push('City');
    }
  }
  
  await sleep(200);
  
  const stateField = findElement(FIELD_SELECTORS.state);
  if (stateField && data.billing.state) {
    if (stateField.tagName === 'SELECT') {
      stateField.value = data.billing.state;
      stateField.dispatchEvent(new Event('change', { bubbles: true }));
      filledFields.push('State');
    } else {
      if (fillField(stateField, data.billing.state, 'State')) {
        filledFields.push('State');
      }
    }
  }
  
  await sleep(200);
  
  const postalField = findElement(FIELD_SELECTORS.postalCode);
  if (postalField) {
    if (fillField(postalField, data.billing.postal_code, 'Postal Code')) {
      filledFields.push('Postal Code');
    }
  }
  
  return { filledFields, errors };
}

// Auto-submit form if enabled
function autoSubmitForm(data) {
  if (!data.autoSubmit) return false;
  
  // Look for submit button
  const submitSelectors = [
    'button[type="submit"]',
    'button:not([type="button"])',
    'input[type="submit"]',
    'button[class*="submit" i]',
    'button[class*="pay" i]',
    '.SubmitButton',
    '[data-testid="hosted-payment-submit-button"]'
  ];
  
  for (const selector of submitSelectors) {
    const button = document.querySelector(selector);
    if (button && !button.disabled) {
      setTimeout(() => {
        button.click();
        chrome.runtime.sendMessage({
          type: 'AUTOFILL_STATUS',
          status: 'success',
          details: 'Form submitted automatically'
        }).catch(() => {});
      }, 1000);
      return true;
    }
  }
  
  return false;
}

// Handle 3DS authentication
function handle3DS() {
  // Look for 3DS challenge iframe or buttons
  const continueButtons = [
    'button:contains("Complete")',
    'button:contains("Authenticate")',
    'button:contains("Continue")',
    'button[id*="test-source-authorize"]',
    'button[id*="test-payment-method-authorize"]',
    '#test-source-authorize-3ds',
    '.common-StripeRedirectButton'
  ];
  
  setTimeout(() => {
    for (const selector of continueButtons) {
      const button = document.querySelector(selector);
      if (button) {
        button.click();
        chrome.runtime.sendMessage({
          type: 'AUTOFILL_STATUS',
          status: 'success',
          details: '3DS authentication completed'
        }).catch(() => {});
        break;
      }
    }
  }, 1500);
}

// Sleep utility
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Execute autofill
async function executeAutofill(data) {
  autofillData = data;
  
  // First, detect test mode
  chrome.runtime.sendMessage({
    type: 'AUTOFILL_STATUS',
    status: 'detecting',
    details: 'Checking for test mode'
  }).catch(() => {});
  
  await sleep(500);
  
  const isTest = detectTestMode();
  notifyTestModeStatus(isTest);
  
  if (!isTest) {
    console.log('Live mode detected - blocking autofill');
    return;
  }
  
  // Wait a bit for form to be ready
  await sleep(1000);
  
  chrome.runtime.sendMessage({
    type: 'AUTOFILL_STATUS',
    status: 'filling',
    details: 'payment form'
  }).catch(() => {});
  
  // Fill the form
  const result = await fillPaymentForm(data);
  
  if (result.filledFields.length > 0) {
    chrome.runtime.sendMessage({
      type: 'AUTOFILL_STATUS',
      status: 'success',
      details: `Filled ${result.filledFields.length} fields: ${result.filledFields.join(', ')}`
    }).catch(() => {});
    
    // Auto-submit if enabled
    const submitted = autoSubmitForm(data);
    
    // Handle 3DS if needed
    if (data.scenario === 'success_3ds') {
      handle3DS();
    }
  } else {
    chrome.runtime.sendMessage({
      type: 'AUTOFILL_STATUS',
      status: 'warning',
      details: 'No payment fields found on this page'
    }).catch(() => {});
  }
}

// Listen for messages from background
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'EXECUTE_AUTOFILL') {
    executeAutofill(message.data)
      .then(() => sendResponse({ success: true }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
});

console.log('Stripe Test Autofill content script loaded in frame:', window.location.href);
