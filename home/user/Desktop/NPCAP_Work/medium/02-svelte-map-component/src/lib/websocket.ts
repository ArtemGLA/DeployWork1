// websocket.ts
import type { DronePosition, Mission } from './types';

export class DroneWebSocket {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private reconnectTimer: number | null = null;
  
  // Колбэки
  public onPosition: ((pos: DronePosition) => void) | null = null;
  public onMission: ((mission: Mission) => void) | null = null;
  public onOpen: (() => void) | null = null;
  public onClose: (() => void) | null = null;
  public onError: ((error: Event) => void) | null = null;

  // Задаем адрес mock сервера
  constructor(url: string) {
    this.url = url;
  }

  connect() {
    // Очистка таймера
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    // Подсоединение к mock серверу,
    // принимаем от него сообщения
    this.ws = new WebSocket(this.url);
    
    this.ws.onopen = () => {
      if (this.onOpen) this.onOpen();
      this.reconnectAttempts = 0;
    };
    
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      if (message.type === 'mission' && this.onMission) {
        this.onMission(message.data);
      }
      
      if (message.type === 'position' && this.onPosition) {
        this.onPosition(message.data);
      }
    };
    
    this.ws.onerror = (error) => {
      if (this.onError) this.onError(error);
    };
    
    this.ws.onclose = () => {
      if (this.onClose) this.onClose();
      
      // Переподключение с задержкой
      const baseDelay = 1000;
      const maxDelay = 30000;
      const delay = Math.min(baseDelay * Math.pow(2, this.reconnectAttempts), maxDelay);
      
      this.reconnectTimer = window.setTimeout(() => {
        this.reconnectAttempts++;
        this.connect();
      }, delay);
    };
  }
  
  close() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}