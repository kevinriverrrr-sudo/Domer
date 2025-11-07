# Gemini Telegram Bot Android App

## Overview
This Android application integrates Google's Gemini AI with a Telegram bot, allowing users to interact with the AI through both the Android app interface and Telegram messages.

## Features

### 1. **Gemini AI Integration**
- Uses Google's Gemini Pro model for natural language processing
- API Key: `AIzaSyC-u6Of5R3wYfXXie6kwh5yAcyDq1HCNAc`
- Provides intelligent responses to user queries

### 2. **Telegram Bot Integration**
- Bot Token: `7560458678:AAHbtiK7z0QiII5Iz3fzo17cReOaDS-2tBU`
- Automatically responds to messages sent to the Telegram bot
- Processes messages through Gemini AI and sends back intelligent responses

### 3. **Dual Interface**
- **Android App UI**: Clean, modern interface with:
  - Text input field for user messages
  - Send button to submit queries
  - Scrollable response area showing Gemini AI responses
  - Real-time status updates
  
- **Telegram Bot**: 
  - Users can send messages directly to the Telegram bot
  - Bot processes messages through Gemini AI
  - Responds automatically with AI-generated content

## Technical Details

### Architecture
- **Language**: Java
- **Min SDK**: API 21 (Android 5.0)
- **Target SDK**: API 34 (Android 14)
- **Build System**: Gradle 8.5
- **Android Gradle Plugin**: 8.1.0

### Key Dependencies
- `androidx.appcompat:appcompat:1.6.1` - AppCompat support
- `com.google.android.material:material:1.9.0` - Material Design components
- `com.github.pengrad:java-telegram-bot-api:6.9.1` - Telegram Bot API
- `com.squareup.okhttp3:okhttp:4.11.0` - HTTP client for Gemini API
- `com.google.code.gson:gson:2.10.1` - JSON parsing
- `org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1` - Coroutines support

### Permissions Required
- `INTERNET` - For API calls to Gemini and Telegram
- `ACCESS_NETWORK_STATE` - To check network connectivity

## APK Information

### Build Details
- **APK File**: `GeminiTelegramBot.apk`
- **Size**: 6.8 MB
- **Signing**: Signed with custom keystore
- **Signature Schemes**: v1 (JAR), v2, and v3

### Keystore Information
- **Keystore**: `gemini-telegram.keystore`
- **Alias**: `gemini-telegram-key`
- **Algorithm**: RSA 2048-bit
- **Validity**: 10,000 days
- **Password**: `android123`

## Installation

1. Transfer the APK file to your Android device
2. Enable "Install from Unknown Sources" in your device settings
3. Open the APK file and follow the installation prompts
4. Grant necessary permissions when prompted

## Usage

### Using the Android App
1. Open the app
2. Enter your message in the text field
3. Tap "Send"
4. Wait for Gemini AI to process and display the response

### Using the Telegram Bot
1. Find the bot using the token on Telegram
2. Send a message to the bot
3. Receive AI-generated responses automatically

## How It Works

1. **Message Input**: User enters a message either through the Android app or Telegram
2. **API Call**: The message is sent to Google's Gemini API
3. **AI Processing**: Gemini Pro model processes the message and generates a response
4. **Response Delivery**: The response is displayed in the app or sent back via Telegram

## API Endpoints

- **Gemini API**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent`
- **Telegram Bot API**: Uses the java-telegram-bot-api library for webhook handling

## Architecture Components

### MainActivity.java
- Handles UI interactions
- Manages Telegram bot listener
- Coordinates API calls to Gemini
- Manages threading with ExecutorService

### Key Methods
- `initTelegramBot()`: Initializes Telegram bot and sets up message listeners
- `sendToGemini()`: Sends user input to Gemini API from the app
- `processMessageWithGemini()`: Processes Telegram messages through Gemini
- `callGeminiAPI()`: Makes HTTP requests to Gemini API
- `updateStatus()`: Updates UI status messages

## Threading Model
- Main thread for UI updates
- Background ExecutorService for:
  - Telegram bot operations
  - Gemini API calls
  - Network operations

## Error Handling
- Network error detection and reporting
- API error handling with user-friendly messages
- Graceful fallback for failed operations

## Future Enhancements
- Add conversation history
- Implement image analysis with Gemini Vision
- Add user authentication
- Implement rate limiting
- Add offline message queue
- Support for multiple languages
- Custom AI model parameters

## Troubleshooting

### App won't install
- Ensure "Unknown Sources" is enabled
- Check if you have enough storage space
- Verify Android version is 5.0 or higher

### Bot not responding
- Check internet connection
- Verify API keys are valid
- Ensure app has necessary permissions

### Gemini API errors
- Check API key validity
- Verify network connectivity
- Review API usage quotas

## License
This is a demonstration application. The API keys included are for testing purposes only.

## Security Notice
⚠️ **Important**: The API keys in this application are exposed in the source code. For production use:
- Store API keys securely (e.g., using Android Keystore)
- Use environment variables or secure configuration
- Implement proper authentication
- Use backend proxy for API calls

## Developer Information
- **Package**: com.gemini.telegram
- **Version Code**: 1
- **Version Name**: 1.0

## Build Instructions

To rebuild the APK from source:

```bash
cd android-app
export ANDROID_SDK_ROOT=$HOME/android-sdk
gradle clean assembleRelease
```

To sign the APK:

```bash
apksigner sign --ks gemini-telegram.keystore \
  --ks-key-alias gemini-telegram-key \
  --ks-pass pass:android123 \
  --key-pass pass:android123 \
  --out app-release-signed.apk \
  app/build/outputs/apk/release/app-release-unsigned.apk
```

## Project Structure

```
android-app/
├── app/
│   ├── build.gradle
│   ├── proguard-rules.pro
│   └── src/
│       └── main/
│           ├── AndroidManifest.xml
│           ├── java/com/gemini/telegram/
│           │   └── MainActivity.java
│           └── res/
│               ├── layout/
│               │   └── activity_main.xml
│               └── values/
│                   └── strings.xml
├── build.gradle
├── settings.gradle
├── gradle.properties
└── local.properties
```

---

**Created**: November 7, 2025
**Build Status**: ✅ Successfully built and signed
