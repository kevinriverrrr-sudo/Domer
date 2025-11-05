# Testing Instructions for Stripe Test Autofill Extension

## Quick Test Checklist

### 1. Load the Extension
1. Open Chrome or Edge browser
2. Navigate to `chrome://extensions/` (or `edge://extensions/`)
3. Enable "Developer mode" (toggle in top-right)
4. Click "Load unpacked"
5. Select this directory
6. ✓ Extension should load without errors
7. ✓ Extension icon should appear in toolbar

### 2. Test on cursor.com
1. Navigate to `https://cursor.com`
2. ✓ A purple button "Fill Stripe Test" should appear in bottom-right corner
3. Click the button (or press Ctrl+Shift+A)
4. ✓ A toast notification should appear saying "Initiating Stripe test autofill..."
5. ✓ Another toast should say "Looking for Stripe payment forms..."

### 3. Test Options Page
1. Click the extension icon in toolbar
2. Click "Open Settings"
3. ✓ Options page should open
4. ✓ Test card scenarios should be listed
5. ✓ Billing profile form should be visible
6. Change some settings and click "Save Settings"
7. ✓ Should see "Settings saved successfully!" message

### 4. Test on Stripe Checkout (Test Mode)
To fully test the autofill functionality, you'll need a Stripe test checkout page:

**Option A: Use Stripe's demo**
1. Go to https://stripe.com/docs/testing
2. Look for interactive examples with test mode
3. Click the "Fill Stripe Test" button on cursor.com while on that page
4. ✓ Should detect test mode and fill fields

**Option B: Create your own test checkout**
1. Set up a Stripe account in test mode
2. Create a test checkout session
3. Open the checkout page while on cursor.com
4. Click the autofill button
5. ✓ Should fill: card number, expiry, CVC, name, email, phone, address

### 5. Test Safety Feature (Live Mode Block)
1. Visit any LIVE Stripe checkout (not test mode)
2. Click the autofill button
3. ✓ Should see toast: "⚠ BLOCKED: Live mode detected. This extension only works in TEST mode."
4. ✓ No fields should be filled

## Expected Behavior

### Test Mode Detection
The extension should detect test mode by checking for:
- Test mode banners with text like "test mode" or "using test"
- Publishable keys starting with `pk_test_`
- Checkout sessions starting with `cs_test_`
- Test mode data attributes

### Fields That Should Be Filled
- ✓ Card Number (e.g., 4242 4242 4242 4242)
- ✓ Expiry Date (MM/YY format, auto-generated)
- ✓ CVC (3 digits, auto-generated)
- ✓ Cardholder Name
- ✓ Email Address
- ✓ Phone Number
- ✓ Country
- ✓ Address Line 1
- ✓ Address Line 2
- ✓ City
- ✓ State/Region
- ✓ Postal Code

### Toast Notifications
You should see various toasts:
- "Initiating Stripe test autofill..."
- "Looking for Stripe payment forms..."
- "Detecting Stripe test mode..."
- "✓ Test mode confirmed, filling fields..."
- "✓ Filled X fields: ..."
- "⚠ BLOCKED: Live mode detected..." (if live mode)
- "✗ Error: ..." (if something goes wrong)

## Common Issues

### Button doesn't appear
- Refresh cursor.com after loading the extension
- Check console for errors (F12 → Console tab)
- Verify extension is enabled

### Fields not filling
- Ensure you're on a Stripe test page (not live)
- Check that Stripe fields are visible and not disabled
- Look for error messages in toasts or console

### "Live mode blocked" on test pages
- Verify the page has test indicators (pk_test_, test banner, etc.)
- Some custom implementations may not be detected
- Check browser console for more details

## Browser Console Logs

Expected console messages:
```
Stripe Test Autofill background service worker loaded
Stripe Test Autofill: Button injected on cursor.com
Stripe Test Autofill content script loaded in frame: https://...
```

## Test Card Numbers

The extension uses these official Stripe test cards:
- **4242 4242 4242 4242**: Success (no authentication)
- **4000 0025 0000 3155**: Success with 3DS authentication
- **4000 0000 0000 0002**: Generic decline
- **4000 0000 0000 9995**: Insufficient funds decline
- **4100 0000 0000 0019**: Fraud decline

Choose different scenarios in the options page.

---

**All tests passing?** The extension is working correctly! 🎉
