import React, { useState, useRef } from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
  Alert,
  Dimensions,
} from 'react-native';
import { WebView } from 'react-native-webview';
import { Ionicons } from '@expo/vector-icons';

const HomeScreen = () => {
  const [url, setUrl] = useState('https://funpay.com');
  const [currentUrl, setCurrentUrl] = useState('https://funpay.com');
  const [canGoBack, setCanGoBack] = useState(false);
  const [canGoForward, setCanGoForward] = useState(false);
  const [loading, setLoading] = useState(false);
  const webViewRef = useRef(null);

  const handleNavigationStateChange = (navState) => {
    setCurrentUrl(navState.url);
    setCanGoBack(navState.canGoBack);
    setCanGoForward(navState.canGoForward);
    setUrl(navState.url);
  };

  const handleGoBack = () => {
    if (canGoBack && webViewRef.current) {
      webViewRef.current.goBack();
    }
  };

  const handleGoForward = () => {
    if (canGoForward && webViewRef.current) {
      webViewRef.current.goForward();
    }
  };

  const handleRefresh = () => {
    if (webViewRef.current) {
      webViewRef.current.reload();
    }
  };

  const handleHome = () => {
    setUrl('https://funpay.com');
    if (webViewRef.current) {
      webViewRef.current.injectJavaScript(`window.location.href = 'https://funpay.com'`);
    }
  };

  const handleSubmitUrl = () => {
    let newUrl = url.trim();
    if (!newUrl.startsWith('http://') && !newUrl.startsWith('https://')) {
      newUrl = 'https://' + newUrl;
    }
    setUrl(newUrl);
  };

  // JavaScript для улучшения UX
  const injectedJavaScript = `
    (function() {
      // Скрыть элементы, которые могут выдать WebView
      const style = document.createElement('style');
      style.innerHTML = \`
        * {
          -webkit-user-select: text !important;
          -webkit-touch-callout: default !important;
        }
      \`;
      document.head.appendChild(style);
      
      // Улучшение производительности
      window.addEventListener('load', function() {
        document.body.style.webkitTouchCallout = 'default';
      });
    })();
    true;
  `;

  return (
    <View style={styles.container}>
      {/* Кастомная адресная строка */}
      <View style={styles.toolbar}>
        <TouchableOpacity
          onPress={handleGoBack}
          disabled={!canGoBack}
          style={[styles.toolbarButton, !canGoBack && styles.disabledButton]}
        >
          <Ionicons
            name="arrow-back"
            size={24}
            color={canGoBack ? '#4A90E2' : '#ccc'}
          />
        </TouchableOpacity>

        <TouchableOpacity
          onPress={handleGoForward}
          disabled={!canGoForward}
          style={[styles.toolbarButton, !canGoForward && styles.disabledButton]}
        >
          <Ionicons
            name="arrow-forward"
            size={24}
            color={canGoForward ? '#4A90E2' : '#ccc'}
          />
        </TouchableOpacity>

        <TouchableOpacity onPress={handleHome} style={styles.toolbarButton}>
          <Ionicons name="home" size={24} color="#4A90E2" />
        </TouchableOpacity>

        <TextInput
          style={styles.urlInput}
          value={url}
          onChangeText={setUrl}
          onSubmitEditing={handleSubmitUrl}
          placeholder="Введите URL..."
          placeholderTextColor="#999"
          autoCapitalize="none"
          autoCorrect={false}
          keyboardType="url"
        />

        <TouchableOpacity onPress={handleRefresh} style={styles.toolbarButton}>
          <Ionicons name="reload" size={24} color="#4A90E2" />
        </TouchableOpacity>
      </View>

      {/* WebView с FunPay */}
      <WebView
        ref={webViewRef}
        source={{ uri: url }}
        style={styles.webView}
        onNavigationStateChange={handleNavigationStateChange}
        onLoadStart={() => setLoading(true)}
        onLoadEnd={() => setLoading(false)}
        injectedJavaScript={injectedJavaScript}
        javaScriptEnabled={true}
        domStorageEnabled={true}
        startInLoadingState={true}
        scalesPageToFit={true}
        mixedContentMode="compatibility"
        allowsBackForwardNavigationGestures={true}
        renderLoading={() => (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#4A90E2" />
          </View>
        )}
        onError={(syntheticEvent) => {
          const { nativeEvent } = syntheticEvent;
          Alert.alert('Ошибка загрузки', 'Не удалось загрузить страницу');
        }}
      />

      {loading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#4A90E2" />
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  toolbar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  toolbarButton: {
    padding: 8,
    marginHorizontal: 4,
  },
  disabledButton: {
    opacity: 0.5,
  },
  urlInput: {
    flex: 1,
    height: 40,
    backgroundColor: '#f5f5f5',
    borderRadius: 20,
    paddingHorizontal: 16,
    marginHorizontal: 8,
    fontSize: 14,
    color: '#333',
  },
  webView: {
    flex: 1,
  },
  loadingContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ffffff',
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.8)',
  },
});

export default HomeScreen;
