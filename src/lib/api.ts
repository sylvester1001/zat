/**
 * ZAT API 客户端
 */

const API_BASE = 'http://127.0.0.1:8000';

export interface ApiResponse<T = any> {
  success?: boolean;
  data?: T;
  error?: string;
}

export interface Status {
  connected: boolean;
  device: string | null;
  task_running: boolean;
  current_state: string | null;
}

export interface LogMessage {
  type: 'log';
  level: 'info' | 'warning' | 'error' | 'debug';
  timestamp: string;
  logger: string;
  message: string;
}

export interface StateMessage {
  type: 'state';
  current_state: string | null;
  is_running: boolean;
  loop_count: number;
}

export interface Resolution {
  width: number;
  height: number;
}

export interface ConnectResponse {
  success: boolean;
  device?: string;
  resolution?: Resolution;
}

/**
 * HTTP API
 */
export const api = {
  async connect(): Promise<ConnectResponse> {
    const res = await fetch(`${API_BASE}/connect`, { method: 'POST' });
    return res.json();
  },

  async getStatus(): Promise<Status> {
    const res = await fetch(`${API_BASE}/status`);
    return res.json();
  },

  async startTaskEngine(taskName: string = 'farming'): Promise<{ success: boolean }> {
    const res = await fetch(`${API_BASE}/task-engine/start?task_name=${taskName}`, {
      method: 'POST',
    });
    return res.json();
  },

  async stopTaskEngine(): Promise<{ success: boolean }> {
    const res = await fetch(`${API_BASE}/task-engine/stop`, { method: 'POST' });
    return res.json();
  },

  async startGame(waitReady: boolean = false, timeout: number = 60): Promise<{ 
    success: boolean; 
    package?: string;
    entered?: boolean;
    message?: string;
  }> {
    const params = new URLSearchParams();
    params.set('wait_ready', String(waitReady));
    params.set('timeout', String(timeout));
    const res = await fetch(`${API_BASE}/start-game?${params}`, { method: 'POST' });
    return res.json();
  },

  getScreenshotUrl(gray: boolean = false): string {
    return `${API_BASE}/debug/screenshot?gray=${gray}&t=${Date.now()}`;
  },

  async getDungeons(): Promise<{
    dungeons: Array<{
      id: string;
      name: string;
      difficulties: string[];
    }>;
  }> {
    const res = await fetch(`${API_BASE}/dungeons`);
    return res.json();
  },

  async navigateToDungeon(dungeonId: string, difficulty: string = 'normal'): Promise<{
    success: boolean;
    dungeon?: string;
    difficulty?: string;
    message?: string;
  }> {
    const params = new URLSearchParams();
    params.set('dungeon_id', dungeonId);
    params.set('difficulty', difficulty);
    const res = await fetch(`${API_BASE}/navigate-to-dungeon?${params}`, { method: 'POST' });
    return res.json();
  },
};

/**
 * WebSocket 连接管理
 */
export class WebSocketManager {
  private ws: WebSocket | null = null;
  private reconnectTimer: number | null = null;
  private reconnectDelay = 3000;

  constructor(
    private endpoint: string,
    private onMessage: (data: any) => void,
    private onConnect?: () => void,
    private onDisconnect?: () => void
  ) {}

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    const url = `ws://127.0.0.1:8000${this.endpoint}`;
    console.log(`连接 WebSocket: ${url}`);

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log(`WebSocket 已连接: ${this.endpoint}`);
      this.onConnect?.();
      
      // 清除重连定时器
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer);
        this.reconnectTimer = null;
      }
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.onMessage(data);
      } catch (e) {
        console.error('解析 WebSocket 消息失败:', e);
      }
    };

    this.ws.onerror = (error) => {
      console.error(`WebSocket 错误: ${this.endpoint}`, error);
    };

    this.ws.onclose = () => {
      console.log(`WebSocket 已断开: ${this.endpoint}`);
      this.onDisconnect?.();
      
      // 自动重连
      this.reconnectTimer = setTimeout(() => {
        console.log(`尝试重连: ${this.endpoint}`);
        this.connect();
      }, this.reconnectDelay) as unknown as number;
    };
  }

  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
}
