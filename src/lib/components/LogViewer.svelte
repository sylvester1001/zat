<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { Card, Button, Toggle } from 'flowbite-svelte';
  import { WebSocketManager, type LogMessage } from '$lib/api';
  
  let logs = $state<LogMessage[]>([]);
  let wsManager: WebSocketManager | null = null;
  let logContainer: HTMLDivElement;
  let autoScroll = $state(true);
  
  onMount(() => {
    wsManager = new WebSocketManager(
      '/ws/log',
      (message: LogMessage) => {
        if (message.type === 'log') {
          logs = [...logs, message];
          if (logs.length > 500) {
            logs = logs.slice(-500);
          }
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
      case 'error': return 'text-red-600 dark:text-red-400';
      case 'warning': return 'text-yellow-600 dark:text-yellow-400';
      case 'info': return 'text-blue-600 dark:text-blue-400';
      case 'debug': return 'text-gray-500 dark:text-gray-400';
      default: return 'text-gray-700 dark:text-gray-300';
    }
  }
  
  function formatTime(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('zh-CN', { hour12: false });
  }
</script>

<Card size="xl" class="flex flex-col h-96">
  <div class="flex justify-between items-center mb-4">
    <h2 class="text-xl font-bold text-gray-900 dark:text-white">日志</h2>
    <div class="flex items-center gap-3">
      <Toggle bind:checked={autoScroll} size="small">自动滚动</Toggle>
      <Button size="xs" color="alternative" onclick={clearLogs}>清空</Button>
    </div>
  </div>
  
  <div
    bind:this={logContainer}
    class="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-800 rounded-lg p-3 font-mono text-sm"
  >
    {#if logs.length === 0}
      <p class="text-gray-400 dark:text-gray-500">暂无日志</p>
    {:else}
      {#each logs as log}
        <div class="mb-1 leading-relaxed">
          <span class="text-gray-400 dark:text-gray-500">[{formatTime(log.timestamp)}]</span>
          <span class={getLevelClass(log.level)}>[{log.level.toUpperCase()}]</span>
          <span class="text-gray-700 dark:text-gray-300">{log.message}</span>
        </div>
      {/each}
    {/if}
  </div>
</Card>
