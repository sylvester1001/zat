<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { WebSocketManager, type StateMessage } from '$lib/api';
  
  export let connected = false;
  export let device = '';
  
  let currentState = 'IDLE';
  let isRunning = false;
  let loopCount = 0;
  let wsManager: WebSocketManager | null = null;
  
  onMount(() => {
    // 连接状态 WebSocket
    wsManager = new WebSocketManager(
      '/ws/state',
      (message: StateMessage) => {
        if (message.type === 'state') {
          currentState = message.current_state || 'IDLE';
          isRunning = message.is_running;
          loopCount = message.loop_count;
        }
      }
    );
    
    wsManager.connect();
  });
  
  onDestroy(() => {
    wsManager?.disconnect();
  });
  
  function getStateColor(state: string): string {
    switch (state) {
      case 'RUNNING':
        return 'bg-green-500';
      case 'ERROR':
        return 'bg-red-500';
      case 'STOPPING':
      case 'STARTING':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-400';
    }
  }
</script>

<div class="card bg-white shadow-lg rounded-lg p-4">
  <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
    <!-- 连接状态 -->
    <div class="status-item">
      <div class="status-label">连接状态</div>
      <div class="status-value">
        <span class="status-dot {connected ? 'bg-green-500' : 'bg-gray-400'}"></span>
        {connected ? '已连接' : '未连接'}
      </div>
      {#if device}
        <div class="status-detail">{device}</div>
      {/if}
    </div>
    
    <!-- 任务状态 -->
    <div class="status-item">
      <div class="status-label">任务状态</div>
      <div class="status-value">
        <span class="status-dot {getStateColor(currentState)}"></span>
        {currentState}
      </div>
    </div>
    
    <!-- 运行状态 -->
    <div class="status-item">
      <div class="status-label">运行状态</div>
      <div class="status-value">
        {isRunning ? '运行中' : '已停止'}
      </div>
    </div>
    
    <!-- 循环次数 -->
    <div class="status-item">
      <div class="status-label">循环次数</div>
      <div class="status-value">
        {loopCount}
      </div>
    </div>
  </div>
</div>

<style>
  .card {
    border: 1px solid #e5e7eb;
  }
  
  .status-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .status-label {
    font-size: 0.75rem;
    color: #6b7280;
    font-weight: 500;
  }
  
  .status-value {
    font-size: 1rem;
    font-weight: 600;
    color: #111827;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .status-detail {
    font-size: 0.75rem;
    color: #9ca3af;
  }
  
  .status-dot {
    width: 0.5rem;
    height: 0.5rem;
    border-radius: 50%;
    display: inline-block;
  }
</style>
