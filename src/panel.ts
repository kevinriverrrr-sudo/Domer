export class SidePanel {
  private shadowRoot!: ShadowRoot;
  private panelElement!: HTMLElement;
  private isOpen = false;

  constructor() {
    this.createPanel();
    this.initEvents();
  }

  private createPanel(): void {
    // Create panel container
    this.panelElement = document.createElement('div');
    this.panelElement.id = 'funpay-side-panel';
    this.panelElement.className = 'funpay-side-panel';
    
    // Create shadow root
    this.shadowRoot = this.panelElement.attachShadow({ mode: 'closed' });
    
    // Add styles to shadow root
    const style = document.createElement('style');
    style.textContent = this.getPanelStyles();
    this.shadowRoot.appendChild(style);
    
    // Create panel content
    const panelContent = this.createPanelContent();
    this.shadowRoot.appendChild(panelContent);
    
    // Add to document
    document.body.appendChild(this.panelElement);
  }

  private createPanelContent(): HTMLElement {
    const container = document.createElement('div');
    container.className = 'funpay-panel-container';
    
    container.innerHTML = `
      <div class="funpay-panel-header">
        <div class="funpay-panel-title">
          <h2>📝 Пакетный покупатель</h2>
          <span class="funpay-panel-version">v1.0.0</span>
        </div>
        <button class="funpay-panel-close" id="funpay-close-panel">×</button>
      </div>
      
      <div class="funpay-panel-tabs">
        <div class="funpay-tab active" data-tab="templates">
          <span class="funpay-tab-icon">📋</span>
          <span class="funpay-tab-text">Шаблоны</span>
        </div>
        <div class="funpay-tab" data-tab="monitoring">
          <span class="funpay-tab-icon">👁️</span>
          <span class="funpay-tab-text">Мониторинг</span>
        </div>
        <div class="funpay-tab" data-tab="history">
          <span class="funpay-tab-icon">📊</span>
          <span class="funpay-tab-text">История</span>
        </div>
      </div>
      
      <div class="funpay-panel-content">
        <div class="funpay-tab-content active" data-content="templates">
          <div class="funpay-placeholder">
            <div class="funpay-placeholder-icon">📋</div>
            <h3>Шаблоны покупок</h3>
            <p>Здесь будут доступны ваши шаблоны для быстрой покупки</p>
            <div class="funpay-placeholder-actions">
              <button class="funpay-btn funpay-btn-primary" disabled>Создать шаблон</button>
            </div>
          </div>
        </div>
        
        <div class="funpay-tab-content" data-content="monitoring">
          <div class="funpay-placeholder">
            <div class="funpay-placeholder-icon">👁️</div>
            <h3>Мониторинг товаров</h3>
            <p>Отслеживайте изменения цен и наличие товаров</p>
            <div class="funpay-placeholder-actions">
              <button class="funpay-btn funpay-btn-primary" disabled>Добавить товар</button>
            </div>
          </div>
        </div>
        
        <div class="funpay-tab-content" data-content="history">
          <div class="funpay-placeholder">
            <div class="funpay-placeholder-icon">📊</div>
            <h3>История покупок</h3>
            <p>Просматривайте историю ваших покупок и аналитику</p>
            <div class="funpay-placeholder-actions">
              <button class="funpay-btn funpay-btn-primary" disabled>Загрузить историю</button>
            </div>
          </div>
        </div>
      </div>
    `;
    
    return container;
  }

  private getPanelStyles(): string {
    return `
      .funpay-panel-container {
        position: fixed;
        top: 0;
        right: -360px;
        width: 360px;
        height: 100vh;
        background: #ffffff;
        box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
        transition: right 0.3s ease-in-out;
        z-index: 10000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        display: flex;
        flex-direction: column;
      }
      
      .funpay-panel-container.open {
        right: 0;
      }
      
      .funpay-panel-header {
        padding: 16px 20px;
        border-bottom: 1px solid #e0e0e0;
        background: #f8f9fa;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      
      .funpay-panel-title h2 {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
        color: #333;
      }
      
      .funpay-panel-version {
        font-size: 12px;
        color: #666;
        background: #e0e0e0;
        padding: 2px 6px;
        border-radius: 4px;
      }
      
      .funpay-panel-close {
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #666;
        padding: 0;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
        transition: background-color 0.2s;
      }
      
      .funpay-panel-close:hover {
        background: #e0e0e0;
      }
      
      .funpay-panel-tabs {
        display: flex;
        border-bottom: 1px solid #e0e0e0;
        background: #ffffff;
      }
      
      .funpay-tab {
        flex: 1;
        padding: 12px 8px;
        cursor: pointer;
        border: none;
        background: none;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
        transition: background-color 0.2s;
        font-size: 12px;
      }
      
      .funpay-tab:hover {
        background: #f8f9fa;
      }
      
      .funpay-tab.active {
        color: #007bff;
        border-bottom: 2px solid #007bff;
      }
      
      .funpay-tab-icon {
        font-size: 16px;
      }
      
      .funpay-panel-content {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
      }
      
      .funpay-tab-content {
        display: none;
      }
      
      .funpay-tab-content.active {
        display: block;
      }
      
      .funpay-placeholder {
        text-align: center;
        padding: 40px 20px;
      }
      
      .funpay-placeholder-icon {
        font-size: 48px;
        margin-bottom: 16px;
      }
      
      .funpay-placeholder h3 {
        margin: 0 0 8px 0;
        font-size: 18px;
        color: #333;
      }
      
      .funpay-placeholder p {
        margin: 0 0 24px 0;
        color: #666;
        line-height: 1.5;
      }
      
      .funpay-btn {
        padding: 10px 20px;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.2s;
      }
      
      .funpay-btn-primary {
        background: #007bff;
        color: white;
      }
      
      .funpay-btn-primary:hover:not(:disabled) {
        background: #0056b3;
      }
      
      .funpay-btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
      
      @media (prefers-color-scheme: dark) {
        .funpay-panel-container {
          background: #2d2d2d;
          color: #ffffff;
        }
        
        .funpay-panel-header {
          background: #3d3d3d;
          border-bottom-color: #4d4d4d;
        }
        
        .funpay-panel-title h2 {
          color: #ffffff;
        }
        
        .funpay-panel-tabs {
          background: #2d2d2d;
          border-bottom-color: #4d4d4d;
        }
        
        .funpay-tab:hover {
          background: #3d3d3d;
        }
        
        .funpay-panel-close:hover {
          background: #4d4d4d;
        }
        
        .funpay-placeholder h3 {
          color: #ffffff;
        }
        
        .funpay-placeholder p {
          color: #cccccc;
        }
      }
    `;
  }

  private initEvents(): void {
    // Close button
    const closeBtn = this.shadowRoot.getElementById('funpay-close-panel');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.close());
    }
    
    // Tab switching
    const tabs = this.shadowRoot.querySelectorAll('.funpay-tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', (e) => {
        const target = e.currentTarget as HTMLElement;
        const tabName = target.getAttribute('data-tab');
        if (tabName) {
          this.switchTab(tabName);
        }
      });
    });
  }

  private switchTab(tabName: string): void {
    // Update tab states
    const tabs = this.shadowRoot.querySelectorAll('.funpay-tab');
    tabs.forEach(tab => {
      if (tab.getAttribute('data-tab') === tabName) {
        tab.classList.add('active');
      } else {
        tab.classList.remove('active');
      }
    });
    
    // Update content visibility
    const contents = this.shadowRoot.querySelectorAll('.funpay-tab-content');
    contents.forEach(content => {
      if (content.getAttribute('data-content') === tabName) {
        content.classList.add('active');
      } else {
        content.classList.remove('active');
      }
    });
  }

  public async open(): Promise<void> {
    this.isOpen = true;
    this.panelElement.querySelector('.funpay-panel-container')?.classList.add('open');
    await chrome.storage.local.set({ isPanelOpen: true });
  }

  public async close(): Promise<void> {
    this.isOpen = false;
    this.panelElement.querySelector('.funpay-panel-container')?.classList.remove('open');
    await chrome.storage.local.set({ isPanelOpen: false });
  }

  public async toggle(): Promise<void> {
    if (this.isOpen) {
      await this.close();
    } else {
      await this.open();
    }
  }

  public async restoreState(): Promise<void> {
    const result = await chrome.storage.local.get('isPanelOpen');
    if (result.isPanelOpen) {
      this.open();
    }
  }

  public destroy(): void {
    this.panelElement.remove();
  }
}