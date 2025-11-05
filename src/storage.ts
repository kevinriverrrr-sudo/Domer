interface StorageData {
  buttonPosition?: {
    x: number;
    y: number;
  };
  isPanelOpen?: boolean;
  isButtonVisible?: boolean;
}

export class StorageManager {
  private static readonly KEYS = {
    BUTTON_POSITION: 'buttonPosition',
    IS_PANEL_OPEN: 'isPanelOpen',
    IS_BUTTON_VISIBLE: 'isButtonVisible'
  };

  static async getButtonPosition(): Promise<{ x: number; y: number }> {
    const result = await chrome.storage.local.get(this.KEYS.BUTTON_POSITION);
    return result[this.KEYS.BUTTON_POSITION] || { x: 20, y: 20 };
  }

  static async setButtonPosition(position: { x: number; y: number }): Promise<void> {
    await chrome.storage.local.set({ [this.KEYS.BUTTON_POSITION]: position });
  }

  static async getIsPanelOpen(): Promise<boolean> {
    const result = await chrome.storage.local.get(this.KEYS.IS_PANEL_OPEN);
    return result[this.KEYS.IS_PANEL_OPEN] || false;
  }

  static async setIsPanelOpen(isOpen: boolean): Promise<void> {
    await chrome.storage.local.set({ [this.KEYS.IS_PANEL_OPEN]: isOpen });
  }

  static async getIsButtonVisible(): Promise<boolean> {
    const result = await chrome.storage.local.get(this.KEYS.IS_BUTTON_VISIBLE);
    return result[this.KEYS.IS_BUTTON_VISIBLE] !== false; // Default to true
  }

  static async setIsButtonVisible(isVisible: boolean): Promise<void> {
    await chrome.storage.local.set({ [this.KEYS.IS_BUTTON_VISIBLE]: isVisible });
  }
}