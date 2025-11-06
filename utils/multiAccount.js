// Модуль мультиаккаунта
class MultiAccountManager {
  constructor() {
    this.accounts = [];
    this.currentAccount = null;
  }

  async init() {
    await this.loadAccounts();
  }

  async loadAccounts() {
    return new Promise((resolve) => {
      chrome.storage.local.get(['multiAccounts'], (result) => {
        if (result.multiAccounts) {
          this.accounts = result.multiAccounts;
        }
        resolve();
      });
    });
  }

  async saveAccounts() {
    return new Promise((resolve) => {
      chrome.storage.local.set({ multiAccounts: this.accounts }, resolve);
    });
  }

  async addAccount(accountData) {
    const account = {
      id: this.generateAccountId(),
      name: accountData.name || `Аккаунт ${this.accounts.length + 1}`,
      authKey: accountData.authKey,
      settings: accountData.settings || {},
      createdAt: new Date().toISOString()
    };

    this.accounts.push(account);
    await this.saveAccounts();
    return account;
  }

  async removeAccount(accountId) {
    this.accounts = this.accounts.filter(acc => acc.id !== accountId);
    await this.saveAccounts();
  }

  async switchAccount(accountId) {
    const account = this.accounts.find(acc => acc.id === accountId);
    if (!account) return false;

    this.currentAccount = account;
    
    // Применение настроек аккаунта
    await this.applyAccountSettings(account);
    
    await this.saveAccounts();
    return true;
  }

  async applyAccountSettings(account) {
    if (account.settings) {
      await chrome.storage.local.set({ 
        settings: account.settings,
        currentAccountId: account.id
      });
    }
  }

  getCurrentAccount() {
    return this.currentAccount || this.accounts[0];
  }

  getAllAccounts() {
    return this.accounts;
  }

  generateAccountId() {
    return `acc-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  exportAccounts() {
    return JSON.stringify(this.accounts, null, 2);
  }

  async importAccounts(jsonData) {
    try {
      const accounts = JSON.parse(jsonData);
      if (Array.isArray(accounts)) {
        this.accounts = accounts;
        await this.saveAccounts();
        return true;
      }
    } catch (error) {
      console.error('Ошибка импорта аккаунтов:', error);
    }
    return false;
  }
}

// Экспорт
if (typeof window !== 'undefined') {
  window.MultiAccountManager = MultiAccountManager;
}
