/**
 * 全局应用状态
 */
import { writable } from 'svelte/store';
import { api } from '$lib/api';

export interface AppState {
  connected: boolean;
  device: string;
  resolution: string;
  taskEngineRunning: boolean;
  gameRunning: boolean;
}

const initialState: AppState = {
  connected: false,
  device: '',
  resolution: '',
  taskEngineRunning: false,
  gameRunning: false,
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

// 心跳检测
let heartbeatInterval: ReturnType<typeof setInterval> | null = null;
const HEARTBEAT_INTERVAL = 5000; // 5秒检测一次

export const startHeartbeat = () => {
  if (heartbeatInterval) return;
  
  heartbeatInterval = setInterval(async () => {
    try {
      const status = await api.getStatus();
      appStore.update(state => {
        // 如果之前是连接状态，现在断开了，更新状态
        if (state.connected && !status.connected) {
          console.log('检测到设备离线');
          return {
            ...state,
            connected: false,
            device: '',
            resolution: '',
            taskEngineRunning: false,
            gameRunning: false,
          };
        }
        // 同步状态
        const needsUpdate = 
          state.taskEngineRunning !== status.task_running ||
          state.gameRunning !== status.game_running;
        
        if (needsUpdate) {
          return {
            ...state,
            taskEngineRunning: status.task_running,
            gameRunning: status.game_running,
          };
        }
        return state;
      });
    } catch (error) {
      // 后端不可用时，标记为断开
      console.error('心跳检测失败:', error);
      appStore.update(state => ({
        ...state,
        connected: false,
        taskEngineRunning: false,
        gameRunning: false,
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
