/**
 * 全局应用状态
 */
import { writable } from 'svelte/store';
import { api } from '$lib/api';

export type DungeonState = 'idle' | 'navigating' | 'matching' | 'battling' | 'finished';

export interface AppState {
  connected: boolean;
  device: string;
  resolution: string;
  taskEngineRunning: boolean;
  gameRunning: boolean;
  dungeonState: DungeonState;
  dungeonRunning: boolean;
}

const initialState: AppState = {
  connected: false,
  device: '',
  resolution: '',
  taskEngineRunning: false,
  gameRunning: false,
  dungeonState: 'idle',
  dungeonRunning: false,
};

export const appStore = writable<AppState>(initialState);

// 便捷方法
export const setConnected = (device: string, resolution?: string) => {
  appStore.update(state => ({
    ...state,
    connected: true,
    device,
    resolution: resolution || '',
  }));
};

export const setDisconnected = () => {
  appStore.update(state => ({
    ...state,
    connected: false,
    device: '',
    resolution: '',
    taskEngineRunning: false,
    gameRunning: false,
    dungeonState: 'idle',
    dungeonRunning: false,
  }));
};

export const setGameRunning = (running: boolean) => {
  appStore.update(state => ({
    ...state,
    gameRunning: running,
  }));
};

export const setTaskEngineRunning = (running: boolean) => {
  appStore.update(state => ({
    ...state,
    taskEngineRunning: running,
  }));
};

// 心跳检测（仅检测连接状态，副本状态通过 WebSocket 推送）
let heartbeatInterval: ReturnType<typeof setInterval> | null = null;
const HEARTBEAT_INTERVAL = 5000; // 5秒检测一次连接

export const startHeartbeat = () => {
  if (heartbeatInterval) return;
  
  heartbeatInterval = setInterval(async () => {
    try {
      const status = await api.getStatus();
      appStore.update(state => {
        if (state.connected && !status.connected) {
          console.log('检测到设备离线');
          return {
            ...state,
            connected: false,
            device: '',
            resolution: '',
            taskEngineRunning: false,
            gameRunning: false,
            dungeonState: 'idle',
            dungeonRunning: false,
          };
        }
        // 只更新连接和游戏状态，副本状态由 WebSocket 更新
        return {
          ...state,
          connected: status.connected,
          gameRunning: status.game_running,
        };
      });
    } catch (error) {
      console.error('心跳检测失败:', error);
      appStore.update(state => ({
        ...state,
        connected: false,
        taskEngineRunning: false,
        gameRunning: false,
        dungeonState: 'idle',
        dungeonRunning: false,
      }));
    }
  }, HEARTBEAT_INTERVAL);
};

export const stopHeartbeat = () => {
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval);
    heartbeatInterval = null;
  }
};

// WebSocket 状态推送
let stateWs: WebSocket | null = null;
let stateWsReconnectTimer: ReturnType<typeof setTimeout> | null = null;

export const startStateWebSocket = () => {
  if (stateWs?.readyState === WebSocket.OPEN) return;
  
  const url = 'ws://127.0.0.1:8000/ws/state';
  stateWs = new WebSocket(url);
  
  stateWs.onopen = () => {
    console.log('状态 WebSocket 已连接');
    if (stateWsReconnectTimer) {
      clearTimeout(stateWsReconnectTimer);
      stateWsReconnectTimer = null;
    }
  };
  
  stateWs.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.type === 'state') {
        appStore.update(state => ({
          ...state,
          dungeonState: data.dungeon_state || 'idle',
          dungeonRunning: data.dungeon_running || false,
          taskEngineRunning: data.task_running || false,
        }));
      }
    } catch (e) {
      console.error('解析状态消息失败:', e);
    }
  };
  
  stateWs.onclose = () => {
    console.log('状态 WebSocket 已断开');
    // 自动重连
    stateWsReconnectTimer = setTimeout(() => {
      startStateWebSocket();
    }, 3000);
  };
  
  stateWs.onerror = (error) => {
    console.error('状态 WebSocket 错误:', error);
  };
};

export const stopStateWebSocket = () => {
  if (stateWsReconnectTimer) {
    clearTimeout(stateWsReconnectTimer);
    stateWsReconnectTimer = null;
  }
  if (stateWs) {
    stateWs.close();
    stateWs = null;
  }
};
