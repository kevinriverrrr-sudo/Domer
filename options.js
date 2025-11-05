// Options page script

const DEFAULT_PROFILE = {
  name: 'John Doe',
  email: 'john.doe@example.com',
  phone: '+1 (555) 123-4567',
  country: 'US',
  line1: '123 Main Street',
  line2: 'Apt 4B',
  city: 'San Francisco',
  state: 'CA',
  postal_code: '94102'
};

// Load settings
async function loadSettings() {
  const settings = await chrome.storage.sync.get({
    cardScenario: 'success',
    billingProfile: DEFAULT_PROFILE,
    randomizeProfile: false,
    autoSubmit: false
  });
  
  // Set card scenario
  const radioButton = document.querySelector(`input[name="cardScenario"][value="${settings.cardScenario}"]`);
  if (radioButton) {
    radioButton.checked = true;
  }
  
  // Set billing profile
  document.getElementById('name').value = settings.billingProfile.name || '';
  document.getElementById('email').value = settings.billingProfile.email || '';
  document.getElementById('phone').value = settings.billingProfile.phone || '';
  document.getElementById('country').value = settings.billingProfile.country || 'US';
  document.getElementById('line1').value = settings.billingProfile.line1 || '';
  document.getElementById('line2').value = settings.billingProfile.line2 || '';
  document.getElementById('city').value = settings.billingProfile.city || '';
  document.getElementById('state').value = settings.billingProfile.state || '';
  document.getElementById('postal_code').value = settings.billingProfile.postal_code || '';
  
  // Set checkboxes
  document.getElementById('randomizeProfile').checked = settings.randomizeProfile;
  document.getElementById('autoSubmit').checked = settings.autoSubmit;
}

// Save settings
async function saveSettings() {
  const cardScenario = document.querySelector('input[name="cardScenario"]:checked')?.value || 'success';
  
  const billingProfile = {
    name: document.getElementById('name').value,
    email: document.getElementById('email').value,
    phone: document.getElementById('phone').value,
    country: document.getElementById('country').value,
    line1: document.getElementById('line1').value,
    line2: document.getElementById('line2').value,
    city: document.getElementById('city').value,
    state: document.getElementById('state').value,
    postal_code: document.getElementById('postal_code').value
  };
  
  const randomizeProfile = document.getElementById('randomizeProfile').checked;
  const autoSubmit = document.getElementById('autoSubmit').checked;
  
  try {
    await chrome.storage.sync.set({
      cardScenario,
      billingProfile,
      randomizeProfile,
      autoSubmit
    });
    
    showStatus('Settings saved successfully!', 'success');
  } catch (error) {
    showStatus('Failed to save settings: ' + error.message, 'error');
  }
}

// Reset to defaults
async function resetSettings() {
  try {
    await chrome.storage.sync.set({
      cardScenario: 'success',
      billingProfile: DEFAULT_PROFILE,
      randomizeProfile: false,
      autoSubmit: false
    });
    
    await loadSettings();
    showStatus('Settings reset to defaults', 'success');
  } catch (error) {
    showStatus('Failed to reset settings: ' + error.message, 'error');
  }
}

// Show status message
function showStatus(message, type) {
  const statusEl = document.getElementById('status');
  statusEl.textContent = message;
  statusEl.className = `status ${type} show`;
  
  setTimeout(() => {
    statusEl.classList.remove('show');
  }, 3000);
}

// Event listeners
document.getElementById('saveBtn').addEventListener('click', saveSettings);
document.getElementById('resetBtn').addEventListener('click', resetSettings);

// Load settings on page load
loadSettings();
