import { StorageManager } from './storage';
import { DraggableButton } from './draggable';
import { SidePanel } from './panel';

class FunpayExtension {
  private button: HTMLElement | null = null;
  private draggable: DraggableButton | null = null;
  private panel: SidePanel | null = null;
  private isInitialized = false;

  constructor() {
    this.init();
  }

  private async init(): Promise<void> {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.initExtension());
    } else {
      this.initExtension();
    }
  }

  private async initExtension(): Promise<void> {
    // Prevent multiple injections
    if (this.isInitialized || document.getElementById('funpay-extension-button')) {
      return;
    }

    this.isInitialized = true;
    
    // Create and inject styles
    this.injectStyles();
    
    // Create button
    await this.createButton();
    
    // Create panel
    this.createPanel();
    
    // Restore states
    await this.restoreStates();
  }

  private injectStyles(): void {
    const style = document.createElement('style');
    style.textContent = this.getButtonStyles();
    document.head.appendChild(style);
  }

  private getButtonStyles(): string {
    return `
      #funpay-extension-button {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 16px;
        cursor: grab;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 8px;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        transition: all 0.2s ease;
        z-index: 9999;
        user-select: none;
      }
      
      #funpay-extension-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
      }
      
      #funpay-extension-button:active {
        transform: translateY(0);
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
      }
      
      #funpay-extension-button.dragging {
        cursor: grabbing;
        opacity: 0.8;
      }
      
      .funpay-button-icon {
        font-size: 16px;
      }
      
      .funpay-button-text {
        white-space: nowrap;
      }
      
      .funpay-close-btn {
        background: rgba(255, 255, 255, 0.2);
        border: none;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-size: 12px;
        margin-left: 8px;
        transition: background-color 0.2s;
      }
      
      .funpay-close-btn:hover {
        background: rgba(255, 255, 255, 0.3);
      }
      
      .funpay-minimize-label {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #333;
        color: white;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 12px;
        cursor: pointer;
        z-index: 9998;
        display: none;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }
      
      @media (prefers-color-scheme: dark) {
        #funpay-extension-button {
          background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }
        
        #funpay-extension-button:hover {
          box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
        }
      }
    `;
  }

  private async createButton(): Promise<void> {
    this.button = document.createElement('button');
    this.button.id = 'funpay-extension-button';
    
    this.button.innerHTML = `
      <span class="funpay-button-icon">📝</span>
      <span class="funpay-button-text">Пакетный покупатель</span>
      <button class="funpay-close-btn" title="Свернуть">×</button>
    `;
    
    // Add click event for main action
    this.button.addEventListener('click', (e) => {
      if (!(e.target as HTMLElement).classList.contains('funpay-close-btn')) {
        this.togglePanel();
      }
    });
    
    // Add close button event
    const closeBtn = this.button.querySelector('.funpay-close-btn');
    if (closeBtn) {
      closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.hideButton();
      });
    }
    
    document.body.appendChild(this.button);
    
    // Make draggable
    this.draggable = new DraggableButton(this.button);
    await this.draggable.restorePosition();
  }

  private createPanel(): void {
    this.panel = new SidePanel();
  }

  private async restoreStates(): Promise<void> {
    // Restore button position
    if (this.draggable) {
      await this.draggable.restorePosition();
    }
    
    // Restore panel state
    if (this.panel) {
      await this.panel.restoreState();
    }
    
    // Restore button visibility
    const isVisible = await StorageManager.getIsButtonVisible();
    if (!isVisible && this.button) {
      this.button.style.display = 'none';
      await this.showMinimizeLabel();
    }
  }

  private togglePanel(): void {
    if (this.panel) {
      this.panel.toggle();
    }
  }

  private async hideButton(): Promise<void> {
    if (this.button) {
      this.button.style.display = 'none';
      await StorageManager.setIsButtonVisible(false);
      await this.showMinimizeLabel();
    }
  }

  private async showMinimizeLabel(): Promise<void> {
    const existingLabel = document.getElementById('funpay-minimize-label');
    if (existingLabel) {
      existingLabel.style.display = 'block';
      return;
    }
    
    const label = document.createElement('div');
    label.id = 'funpay-minimize-label';
    label.className = 'funpay-minimize-label';
    label.textContent = '📝 Показать';
    
    const pos = await StorageManager.getButtonPosition();
    label.style.right = `${Math.max(20, window.innerWidth - pos.x - 100)}px`;
    label.style.bottom = `${Math.max(20, window.innerHeight - pos.y - 40)}px`;
    
    label.addEventListener('click', () => this.showButton());
    document.body.appendChild(label);
  }

  private async showButton(): Promise<void> {
    if (this.button) {
      this.button.style.display = 'flex';
      await StorageManager.setIsButtonVisible(true);
      
      const label = document.getElementById('funpay-minimize-label');
      if (label) {
        label.style.display = 'none';
      }
    }
  }

  public destroy(): void {
    if (this.button) {
      this.button.remove();
    }
    if (this.panel) {
      this.panel.destroy();
    }
    if (this.draggable) {
      // Draggable doesn't have destroy method, just remove references
      this.draggable = null;
    }
  }
}

// Initialize extension
new FunpayExtension();