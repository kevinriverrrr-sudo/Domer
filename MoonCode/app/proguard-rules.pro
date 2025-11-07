# Add project specific ProGuard rules here.
# By default, the flags in this file are appended to flags specified
# in the Android SDK.

-keep class com.markusgarantor.mooncode.** { *; }
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}

-dontwarn javax.annotation.**
-dontwarn org.codehaus.mojo.animal_sniffer.*
