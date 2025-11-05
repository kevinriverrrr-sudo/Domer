export class DraggableButton {
  private element: HTMLElement;
  private isDragging = false;
  private startX = 0;
  private startY = 0;
  private initialX = 0;
  private initialY = 0;

  constructor(element: HTMLElement) {
    this.element = element;
    this.initDragEvents();
  }

  private initDragEvents(): void {
    this.element.addEventListener('mousedown', this.handleMouseDown.bind(this));
    document.addEventListener('mousemove', this.handleMouseMove.bind(this));
    document.addEventListener('mouseup', this.handleMouseUp.bind(this));

    // Touch events for mobile
    this.element.addEventListener('touchstart', this.handleTouchStart.bind(this));
    document.addEventListener('touchmove', this.handleTouchMove.bind(this));
    document.addEventListener('touchend', this.handleTouchEnd.bind(this));
  }

  private handleMouseDown(e: MouseEvent): void {
    if ((e.target as HTMLElement).classList.contains('funpay-close-btn')) return;
    
    this.isDragging = true;
    this.startX = e.clientX;
    this.startY = e.clientY;
    const rect = this.element.getBoundingClientRect();
    this.initialX = rect.left;
    this.initialY = rect.top;
    this.element.style.cursor = 'grabbing';
    e.preventDefault();
  }

  private handleMouseMove(e: MouseEvent): void {
    if (!this.isDragging) return;

    const deltaX = e.clientX - this.startX;
    const deltaY = e.clientY - this.startY;
    
    const newX = Math.max(0, Math.min(window.innerWidth - this.element.offsetWidth, this.initialX + deltaX));
    const newY = Math.max(0, Math.min(window.innerHeight - this.element.offsetHeight, this.initialY + deltaY));
    
    this.element.style.left = `${newX}px`;
    this.element.style.top = `${newY}px`;
    this.element.style.right = 'auto';
    this.element.style.bottom = 'auto';
  }

  private handleMouseUp(): void {
    if (this.isDragging) {
      this.isDragging = false;
      this.element.style.cursor = 'grab';
      
      // Save position to storage
      const rect = this.element.getBoundingClientRect();
      const position = { x: rect.left, y: rect.top };
      chrome.storage.local.set({ buttonPosition: position });
    }
  }

  private handleTouchStart(e: TouchEvent): void {
    if ((e.target as HTMLElement).classList.contains('funpay-close-btn')) return;
    
    const touch = e.touches[0];
    this.isDragging = true;
    this.startX = touch.clientX;
    this.startY = touch.clientY;
    const rect = this.element.getBoundingClientRect();
    this.initialX = rect.left;
    this.initialY = rect.top;
    e.preventDefault();
  }

  private handleTouchMove(e: TouchEvent): void {
    if (!this.isDragging) return;

    const touch = e.touches[0];
    const deltaX = touch.clientX - this.startX;
    const deltaY = touch.clientY - this.startY;
    
    const newX = Math.max(0, Math.min(window.innerWidth - this.element.offsetWidth, this.initialX + deltaX));
    const newY = Math.max(0, Math.min(window.innerHeight - this.element.offsetHeight, this.initialY + deltaY));
    
    this.element.style.left = `${newX}px`;
    this.element.style.top = `${newY}px`;
    this.element.style.right = 'auto';
    this.element.style.bottom = 'auto';
  }

  private handleTouchEnd(): void {
    if (this.isDragging) {
      this.isDragging = false;
      
      // Save position to storage
      const rect = this.element.getBoundingClientRect();
      const position = { x: rect.left, y: rect.top };
      chrome.storage.local.set({ buttonPosition: position });
    }
  }

  public async restorePosition(): Promise<void> {
    const result = await chrome.storage.local.get('buttonPosition');
    const position = result.buttonPosition;
    
    if (position) {
      this.element.style.left = `${position.x}px`;
      this.element.style.top = `${position.y}px`;
      this.element.style.right = 'auto';
      this.element.style.bottom = 'auto';
    }
  }
}