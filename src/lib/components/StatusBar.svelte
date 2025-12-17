<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { Card, Badge, Indicator } from 'flowbite-svelte';
  import { WebSocketManager, type StateMessage } from '$lib/api';
  
  interface Props {
    connected?: boolean;
    device?: string;
  }
  
  let { connected = false, device = '' }: Props = $props();
  
  let currentState = $state('IDLE');
  let isRunning = $state(false);
  let loopCount = $state(0);
  let wsManager: WebSocketManager | null = null;
  
  onMount(() => {
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
  
  function getStateColor(state: string): 'green' | 'red' | 'yellow' | 'gray' {
    switch (state) {
      case 'RUNNING': return 'green';
      case 'ERROR': return 'red';
      case 'STOPPING':
      case 'STARTING': return 'yellow';
      default: return 'gray';
    }
  }
</script>

<Card size="xl">
  <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
    <!-- 连接状态 -->
    <div class="flex flex-col gap-1">
      <span class="text-xs text-gray-500 dark:text-gray-400 font-medium">连接状态</span>
      <div class="flex items-center gap-2">
        <Indicator color={connected ? 'green' : 'gray'} size="sm" />
        <span class="text-sm font-semibold text-gray-900 dark:text-white">
          {connected ? '已连接' : '未连接'}
        </span>
      </div>
      {#if device}
        <span class="text-xs text-gray-400">{device}</span>
      {/if}
    </div>
    
    <!-- 任务状态 -->
    <div class="flex flex-col gap-1">
      <span class="text-xs text-gray-500 dark:text-gray-400 font-medium">任务状态</span>
      <div class="flex items-center gap-2">
        <Indicator color={getStateColor(currentState)} size="sm" />
        <Badge color={getStateColor(currentState)}>{currentState}</Badge>
      </div>
    </div>
    
    <!-- 运行状态 -->
    <div class="flex flex-col gap-1">
      <span class="text-xs text-gray-500 dark:text-gray-400 font-medium">运行状态</span>
      <span class="text-sm font-semibold text-gray-900 dark:text-white">
        {isRunning ? '运行中' : '已停止'}
      </span>
    </div>
    
    <!-- 循环次数 -->
    <div class="flex flex-col gap-1">
      <span class="text-xs text-gray-500 dark:text-gray-400 font-medium">循环次数</span>
      <span class="text-sm font-semibold text-gray-900 dark:text-white">
        {loopCount}
      </span>
    </div>
  </div>
</Card>
