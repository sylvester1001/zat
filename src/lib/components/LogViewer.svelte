<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { WebSocketManager, type LogMessage } from '$lib/api';
  
  let logs: LogMessage[] = [];
  let wsManager: WebSocketManager | null = null;
  let logContainer: HTMLDivElement;
  let autoScroll = true;
  
  onMount(() => {
    // 连接日志 WebSocket
    wsManager = new WebSocketManager(
      '/ws/log',
      (message: LogMessage) => {
        if (message.type === 'log') {
          logs = [...logs, message];
          
          // 限制日志数量
          if (logs.length > 500) {
            logs = logs.slice(-500);
          }
          
          // 自动滚动
          if (autoScroll) {
            setTimeout(() => {
              if (logContainer) {
                logContainer.scrollTop = logContainer.scrollHeight;
              }
            }, 10);
          }
        }
      },
      () => console.log('日志 WebSocket 已连接'),
      () => console.log('日志 WebSocket 已断开')
    );
    
    wsManager.connect();
  });
  
  onDestroy(() => {
    wsManager?.disconnect();
  });
  
  function clearLogs() {
    logs = [];
  }
  
  function getLevelClass(level: string): string {
    switch (level) {
      case 'error':
        return 'text-red-600';
      case 'warning':
        return 'text-yellow-600';
      case 'info':
        return 'text-blue-600';
      case 'debug':
        return 'text-gray-500';
      default:
        return 'text-gray-700';
    }
  }
  
  function formatTime(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('zh-CN', { hour12: false });
  }
</script>

<div class="card bg-white shadow-lg rounded-lg p-6 flex flex-col h-96">
  <div class="flex justify-between items-center mb-4">
    <h2 class="text-xl font-bold">日志</h2>
    <div class="flex gap-2">
      <label class="flex items-center gap-2">
        <input type="checkbox" bind:checked={autoScroll} />
        <span class="text-sm">自动滚动</span>
      </label>
      <button class="btn-sm btn-secondary" on:click={clearLogs}>
        清空
      </button>
    </div>
  </div>
  
  <div
    bind:this={logContainer}
    class="flex-1 overflow-y-auto bg-gray-50 rounded p-3 font-mono text-sm"
  >
    {#if logs.length === 0}
      <p class="text-gray-400">暂无日志</p>
    {:else}
      {#each logs as log}
        <div class="log-entry">
          <span class="text-gray-400">[{formatTime(log.timestamp)}]</span>
          <span class={getLevelClass(log.level)}>[{log.level.toUpperCase()}]</span>
          <span class="text-gray-700">{log.message}</span>
        </div>
      {/each}
    {/if}
  </div>
</div>

<style>
  .card {
    border: 1px solid #e5e7eb;
  }
  
  .log-entry {
    margin-bottom: 0.25rem;
    line-height: 1.5;
  }
  
  .btn-sm {
    padding: 0.375rem 0.75rem;
    border-radius: 0.375rem;
    font-size: 0.875rem;
    font-weight: 500;
    border: none;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .btn-secondary {
    background-color: #6b7280;
    color: white;
  }
  
  .btn-secondary:hover {
    background-color: #4b5563;
  }
</style>
