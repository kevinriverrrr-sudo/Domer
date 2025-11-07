# Add project specific ProGuard rules here.
-keep class com.gemini.telegram.** { *; }
-dontwarn okhttp3.**
-dontwarn okio.**
-keep class okhttp3.** { *; }
-keep class okio.** { *; }
