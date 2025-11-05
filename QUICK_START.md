# Quick Start Guide

## Installation (30 seconds)

1. Open Chrome/Edge and go to: `chrome://extensions/`
2. Enable "Developer mode" (top-right toggle)
3. Click "Load unpacked"
4. Select this folder
5. Done! ✅

## Usage (3 steps)

1. **Visit cursor.com**
   - Look for purple button in bottom-right corner

2. **Navigate to a Stripe test checkout page**
   - Must be in TEST MODE (not live)

3. **Click the button or press `Ctrl+Shift+A`**
   - Watch the magic happen! ✨

## What Gets Filled?

✅ Card Number (official Stripe test card)  
✅ Expiry Date (auto-generated, always valid)  
✅ CVC (auto-generated)  
✅ Cardholder Name  
✅ Email Address  
✅ Phone Number  
✅ Full Address (line 1, line 2, city, state, postal, country)

## Configure Settings

1. Click extension icon in toolbar
2. Click "Open Settings"
3. Choose your test card scenario:
   - ✅ Success (no auth)
   - 🔐 Success with 3DS
   - ❌ Various decline types
4. Customize billing profile
5. Enable/disable auto-submit
6. Save!

## Safety First 🛡️

- ⛔ **Blocks live mode automatically**
- ✅ **Only works in Stripe test mode**
- 📢 **Shows warning if blocked**
- 🔒 **Uses only official Stripe test cards**

## Need Help?

- 📖 See `README.md` for full documentation
- 🧪 See `TEST_INSTRUCTIONS.md` for testing guide
- 📝 See `SUMMARY.md` for technical details

## Test Cards Included

| Card | Scenario |
|------|----------|
| 4242 4242 4242 4242 | ✅ Success |
| 4000 0025 0000 3155 | 🔐 3DS Auth |
| 4000 0000 0000 0002 | ❌ Decline |
| 4000 0000 0000 9995 | 💰 Insufficient Funds |
| 4100 0000 0000 0019 | 🚨 Fraud |

All cards from: https://stripe.com/docs/testing

---

**Ready to test Stripe integrations faster!** 🚀
