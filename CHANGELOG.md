# Changelog

All notable changes to the Stripe Test Autofill for Cursor extension will be documented in this file.

## [1.0.0] - 2024-11-05

### Initial Release

#### Added
- **Chrome/Edge Manifest V3 Extension**
  - Full MV3 compatibility
  - Service worker background script
  - Content scripts for cursor.com and Stripe frames
  
- **Cursor.com Integration**
  - Fixed-position floating button in bottom-right corner
  - Gradient purple styling with hover effects
  - Toast notification system (info, success, error, warning)
  - Keyboard shortcut support (Ctrl+Shift+A / Cmd+Shift+A)
  
- **Stripe Test Mode Autofill**
  - Automatic test mode detection (pk_test_, cs_test_, banners)
  - Hard block in live mode with warning messages
  - Support for Stripe Checkout and Stripe Elements
  - Works in iframes (all_frames: true)
  
- **Official Stripe Test Cards**
  - Success (4242 4242 4242 4242)
  - Success with 3DS (4000 0025 0000 3155)
  - Generic decline (4000 0000 0000 0002)
  - Insufficient funds decline (4000 0000 0000 9995)
  - Fraud decline (4100 0000 0000 0019)
  
- **Comprehensive Field Support**
  - Card number
  - Expiry date (MM/YY or separate fields)
  - CVC/CVV
  - Cardholder name
  - Email address
  - Phone number
  - Full address (line1, line2, city, state, postal code, country)
  
- **Options Page**
  - Test card scenario selection
  - Custom billing profile configuration
  - Profile randomization toggle
  - Auto-submit toggle
  - Beautiful gradient UI design
  
- **Extension Popup**
  - Quick usage instructions
  - Link to settings
  - Version display
  - Safety warnings
  
- **Safety Features**
  - Test mode only operation
  - Multiple detection methods
  - Live mode blocking
  - Clear warning messages
  - No external network calls
  
- **Documentation**
  - Comprehensive README with installation and usage
  - Quick Start Guide for rapid onboarding
  - Test Instructions for validation
  - Technical Summary document
  - MIT License
  
- **Developer Experience**
  - No build process required
  - Vanilla JavaScript (ES6+)
  - Clean, commented code
  - Proper event handling
  - Error handling and logging

### Technical Details
- **Languages**: JavaScript (ES6+), HTML5, CSS3
- **Framework**: None (vanilla JavaScript)
- **Chrome API**: Manifest V3
- **Storage**: Chrome sync storage for settings
- **Permissions**: storage, host_permissions for cursor.com and Stripe domains

### Browser Compatibility
- ✅ Chrome 88+
- ✅ Edge 88+
- ✅ Any Chromium-based browser with MV3 support

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backwards compatible manner
- **PATCH** version for backwards compatible bug fixes

## Future Roadmap Ideas

Potential future enhancements (not yet implemented):
- Additional test card scenarios (declined by network, expired card, etc.)
- More billing profile templates
- Import/export settings
- Custom test card numbers (still test mode only)
- Support for additional payment form frameworks
- Dark mode for options page
- Multiple language support
- Analytics for most-used scenarios
- Quick profile switching from popup

---

For detailed release notes and updates, check the repository releases page.
