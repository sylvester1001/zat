/**
 * 全局应用状态
 */
import { writable } from 'svelte/store';

export interface AppState {
  connected: boolean;
  device: string;
  resolution: string;
  taskEngineRunning: boolean;
}

const initialState: AppState = {
  connected: false,
  device: '',
  resolution: '',
  taskEngineRunning: false,
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
  }));
};

export const setTaskEngineRunning = (running: boolean) => {
  appStore.update(state => ({
    ...state,
    taskEngineRunning: running,
  }));
};
