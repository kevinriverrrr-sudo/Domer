# Stripe Test Autofill for Cursor

A Chrome/Edge Manifest V3 extension that adds automated test card autofill functionality for Stripe payment forms when browsing cursor.com. This extension uses **official Stripe test cards only** and includes comprehensive billing information.

## ⚠️ Important: Test Mode Only

This extension **only works with Stripe test mode** and will automatically block any attempts to use it in live mode. It detects test mode through:
- Test mode banners
- Publishable keys starting with `pk_test_`
- Test checkout sessions (`cs_test_`)
- Test mode data attributes

**The extension will refuse to fill any form in live mode and will show a warning message.**

## Features

- 🎯 **One-Click Autofill**: Fixed-position button on cursor.com to trigger autofill
- 🔐 **Test Mode Safety**: Automatic detection and blocking of live mode
- 💳 **Official Stripe Test Cards**: Uses only official test card numbers from Stripe documentation
- 📋 **Full Billing Details**: Fills card number, expiry, CVC, name, email, phone, and complete address
- 🎨 **Multiple Scenarios**: Support for success, 3DS, and various decline scenarios
- 🔄 **Profile Randomization**: Option to use different billing profiles per run
- ⚡ **Auto-Submit**: Optional automatic form submission after filling
- 🎨 **Visual Feedback**: Toast notifications for all actions and status updates
- ⌨️ **Keyboard Shortcut**: `Ctrl+Shift+A` (or `Cmd+Shift+A` on Mac)

## Installation

### Install as Unpacked Extension

1. **Download or Clone** this repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Open Chrome/Edge Extensions Page**:
   - Chrome: Navigate to `chrome://extensions/`
   - Edge: Navigate to `edge://extensions/`

3. **Enable Developer Mode**:
   - Toggle the "Developer mode" switch in the top-right corner

4. **Load the Extension**:
   - Click "Load unpacked"
   - Select the folder containing this extension's files
   - The extension icon should appear in your browser toolbar

5. **Verify Installation**:
   - Visit [cursor.com](https://cursor.com)
   - You should see a purple "Fill Stripe Test" button in the bottom-right corner

## Usage

### Basic Usage

1. **Navigate to cursor.com** in your browser
2. **Look for the floating button** in the bottom-right corner with "Fill Stripe Test" text
3. **When a Stripe test checkout page loads**, click the button or press `Ctrl+Shift+A`
4. The extension will:
   - Detect if the page is in test mode
   - Fill all card and billing fields
   - Show progress toasts
   - Optionally submit the form (if enabled in settings)

### Configuring Settings

1. **Open Settings**:
   - Click the extension icon in the toolbar
   - Click "Open Settings"
   - Or right-click the extension icon and select "Options"

2. **Choose Test Card Scenario**:
   - **Success (No Authentication)**: `4242 4242 4242 4242` - Payment succeeds without 3DS
   - **Success with 3DS**: `4000 0025 0000 3155` - Requires authentication
   - **Decline (Generic)**: `4000 0000 0000 0002` - Always declined
   - **Decline (Insufficient Funds)**: `4000 0000 0000 9995` - Insufficient funds
   - **Decline (Fraud)**: `4100 0000 0000 0019` - Suspected fraud

3. **Customize Billing Profile**:
   - Set default name, email, phone
   - Configure address (line1, line2, city, state, postal code, country)
   - Enable "Randomize Profile" to use different profiles each time

4. **Additional Options**:
   - **Auto-Submit Form**: Automatically submit after filling fields
   - **Randomize Profile**: Use a different billing profile for each autofill

5. **Save Settings**: Click "Save Settings" to apply changes

## Supported Fields

The extension automatically detects and fills:

### Card Fields
- Card Number
- Expiry Date (MM/YY or separate month/year)
- CVC/CVV
- Cardholder Name

### Billing Fields
- Email Address
- Phone Number
- Country
- Address Line 1
- Address Line 2
- City
- State/Province/Region
- Postal Code/ZIP Code

## Technical Details

### Architecture

- **Manifest V3**: Modern Chrome extension architecture
- **Background Service Worker**: Orchestrates autofill flow and manages settings
- **Content Scripts**:
  - `content-cursor.js`: Injects button and UI feedback on cursor.com
  - `content-stripe.js`: Fills Stripe payment forms (runs in all frames)

### Supported Stripe Implementations

- ✅ Stripe Checkout
- ✅ Stripe Elements
- ✅ Custom Stripe form implementations
- ✅ Embedded payment forms
- ✅ iFrame-based forms

### Test Mode Detection

The extension uses multiple methods to ensure it's in test mode:
1. Checks for test mode banners in page text
2. Scans for `pk_test_` publishable keys
3. Looks for `cs_test_` checkout sessions in URLs
4. Checks data attributes for test mode flags
5. Inspects localStorage/sessionStorage for test indicators

**If test mode cannot be confirmed, the extension will block autofill and show a warning.**

## Official Stripe Test Cards

All card numbers are official Stripe test cards from [stripe.com/docs/testing](https://stripe.com/docs/testing):

| Card Number | Brand | Scenario |
|-------------|-------|----------|
| 4242 4242 4242 4242 | Visa | Success (no auth) |
| 4000 0025 0000 3155 | Visa | Success with 3DS |
| 4000 0000 0000 0002 | Visa | Generic decline |
| 4000 0000 0000 9995 | Visa | Insufficient funds |
| 4100 0000 0000 0019 | Visa | Suspected fraud |

Expiry dates and CVC codes are generated automatically (always valid).

## Security & Privacy

- ✅ **No external network requests**: All data is generated locally
- ✅ **No data collection**: Extension doesn't collect or transmit any data
- ✅ **Test mode only**: Hard-blocked in live mode
- ✅ **Open source**: All code is visible and auditable
- ✅ **Minimal permissions**: Only requests necessary host permissions
- ✅ **Local storage only**: Settings stored in Chrome's sync storage

## Keyboard Shortcuts

- **`Ctrl+Shift+A`** (Windows/Linux) or **`Cmd+Shift+A`** (Mac): Trigger autofill when on cursor.com

## Troubleshooting

### Button doesn't appear on cursor.com
- Refresh the page after installing the extension
- Check that the extension is enabled in `chrome://extensions/`
- Verify you're on `https://cursor.com/*`

### Fields aren't being filled
- Ensure the page is in Stripe test mode (look for test indicators)
- Check the browser console for error messages
- Try refreshing the page and clicking the button again
- Verify in settings that you have a complete billing profile

### "Live mode blocked" warning
- This is a safety feature - the extension only works in test mode
- Verify the Stripe integration is using test keys (`pk_test_`)
- Check that the checkout session is a test session (`cs_test_`)

### Form doesn't submit automatically
- Verify "Auto-Submit Form" is enabled in settings
- Some forms may require manual submission for security
- Wait a moment after filling - the extension waits 1 second before submitting

## Development

### File Structure

```
.
├── manifest.json           # Extension configuration
├── background.js          # Service worker (orchestration)
├── content-cursor.js      # Cursor.com button & UI
├── content-cursor.css     # Styles for button & toasts
├── content-stripe.js      # Stripe form autofill logic
├── options.html           # Settings page HTML
├── options.css            # Settings page styles
├── options.js             # Settings page logic
├── popup.html             # Extension popup HTML
├── popup.css              # Extension popup styles
├── popup.js               # Extension popup logic
├── icons/                 # Extension icons
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md              # This file
```

### Building & Testing

No build step required - this is a vanilla JavaScript extension.

1. Make changes to source files
2. Reload the extension in `chrome://extensions/`
3. Test on a Stripe test checkout page

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please ensure:
- All card numbers are official Stripe test cards
- Test mode detection remains robust
- No live mode functionality is added
- Code follows existing patterns and style

## Disclaimer

This extension is for **testing purposes only**. It uses official Stripe test card numbers and only works in test mode. Do not attempt to use this extension with live Stripe integrations.

## Support

For issues, questions, or contributions, please open an issue on the repository.

---

**Made for testing Stripe integrations safely and efficiently** 🚀
