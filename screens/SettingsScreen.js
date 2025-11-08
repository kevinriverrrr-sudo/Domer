import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const SettingsScreen = () => {
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [darkModeEnabled, setDarkModeEnabled] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);

  const handleLogout = () => {
    Alert.alert(
      'Выйти из аккаунта?',
      'Вы уверены, что хотите выйти?',
      [
        { text: 'Отмена', style: 'cancel' },
        {
          text: 'Выйти',
          style: 'destructive',
          onPress: () => Alert.alert('Выход', 'Вы вышли из аккаунта'),
        },
      ]
    );
  };

  const SettingItem = ({ icon, title, subtitle, onPress, rightComponent }) => (
    <TouchableOpacity style={styles.settingItem} onPress={onPress}>
      <View style={styles.settingIcon}>
        <Ionicons name={icon} size={24} color="#4A90E2" />
      </View>
      <View style={styles.settingText}>
        <Text style={styles.settingTitle}>{title}</Text>
        {subtitle && <Text style={styles.settingSubtitle}>{subtitle}</Text>}
      </View>
      {rightComponent || <Ionicons name="chevron-forward" size={24} color="#ccc" />}
    </TouchableOpacity>
  );

  return (
    <ScrollView style={styles.container}>
      {/* Основные настройки */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>ОСНОВНЫЕ</Text>
        
        <SettingItem
          icon="person-outline"
          title="Аккаунт"
          subtitle="Управление аккаунтом"
          onPress={() => Alert.alert('Аккаунт', 'Настройки аккаунта')}
        />
        
        <SettingItem
          icon="shield-checkmark-outline"
          title="Безопасность"
          subtitle="Пароль и конфиденциальность"
          onPress={() => Alert.alert('Безопасность', 'Настройки безопасности')}
        />
        
        <SettingItem
          icon="card-outline"
          title="Платежные методы"
          subtitle="Управление способами оплаты"
          onPress={() => Alert.alert('Платежи', 'Платежные методы')}
        />
      </View>

      {/* Уведомления */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>УВЕДОМЛЕНИЯ</Text>
        
        <SettingItem
          icon="notifications-outline"
          title="Push-уведомления"
          subtitle="Получать уведомления на устройство"
          rightComponent={
            <Switch
              value={notificationsEnabled}
              onValueChange={setNotificationsEnabled}
              trackColor={{ false: '#ccc', true: '#4A90E2' }}
            />
          }
        />
        
        <SettingItem
          icon="volume-high-outline"
          title="Звуковые уведомления"
          subtitle="Звук при новых сообщениях"
          rightComponent={
            <Switch
              value={soundEnabled}
              onValueChange={setSoundEnabled}
              trackColor={{ false: '#ccc', true: '#4A90E2' }}
            />
          }
        />
      </View>

      {/* Внешний вид */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>ВНЕШНИЙ ВИД</Text>
        
        <SettingItem
          icon="moon-outline"
          title="Темная тема"
          subtitle="Включить темное оформление"
          rightComponent={
            <Switch
              value={darkModeEnabled}
              onValueChange={setDarkModeEnabled}
              trackColor={{ false: '#ccc', true: '#4A90E2' }}
            />
          }
        />
        
        <SettingItem
          icon="language-outline"
          title="Язык"
          subtitle="Русский"
          onPress={() => Alert.alert('Язык', 'Выбор языка')}
        />
      </View>

      {/* Приложение */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>ПРИЛОЖЕНИЕ</Text>
        
        <SettingItem
          icon="help-circle-outline"
          title="Помощь и поддержка"
          subtitle="Часто задаваемые вопросы"
          onPress={() => Alert.alert('Помощь', 'Раздел помощи')}
        />
        
        <SettingItem
          icon="information-circle-outline"
          title="О приложении"
          subtitle="Версия 1.0.0"
          onPress={() => Alert.alert('О приложении', 'FunPay Mobile v1.0.0\n\nМобильное приложение для удобной работы с FunPay')}
        />
        
        <SettingItem
          icon="star-outline"
          title="Оценить приложение"
          subtitle="Поставьте оценку в магазине"
          onPress={() => Alert.alert('Спасибо!', 'Оценка приложения')}
        />
        
        <SettingItem
          icon="document-text-outline"
          title="Пользовательское соглашение"
          onPress={() => Alert.alert('Соглашение', 'Пользовательское соглашение')}
        />
        
        <SettingItem
          icon="shield-outline"
          title="Политика конфиденциальности"
          onPress={() => Alert.alert('Конфиденциальность', 'Политика конфиденциальности')}
        />
      </View>

      {/* Кнопка выхода */}
      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Ionicons name="log-out-outline" size={24} color="#fff" />
        <Text style={styles.logoutText}>Выйти из аккаунта</Text>
      </TouchableOpacity>

      <View style={styles.footer}>
        <Text style={styles.footerText}>FunPay Mobile © 2024</Text>
        <Text style={styles.footerText}>Все права защищены</Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  section: {
    backgroundColor: '#fff',
    marginTop: 16,
    marginBottom: 8,
  },
  sectionTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#999',
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 8,
    letterSpacing: 0.5,
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  settingIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#E3F2FD',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  settingText: {
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 2,
  },
  settingSubtitle: {
    fontSize: 14,
    color: '#666',
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#ff4444',
    marginHorizontal: 16,
    marginTop: 24,
    marginBottom: 16,
    padding: 16,
    borderRadius: 12,
  },
  logoutText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  footer: {
    alignItems: 'center',
    paddingVertical: 24,
  },
  footerText: {
    fontSize: 12,
    color: '#999',
    marginBottom: 4,
  },
});

export default SettingsScreen;
