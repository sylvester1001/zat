<script lang="ts">
  import { Button, Card } from 'flowbite-svelte';
  import { api } from '$lib/api';
  
  interface Props {
    connected?: boolean;
    device?: string;
  }
  
  let { connected = $bindable(false), device = $bindable('') }: Props = $props();
  
  let connecting = $state(false);
  let starting = $state(false);
  let stopping = $state(false);
  let taskRunning = $state(false);
  
  async function handleConnect() {
    connecting = true;
    try {
      const result = await api.connect();
      if (result.success && result.device) {
        connected = true;
        device = result.device;
        console.log('已连接设备:', device);
      } else {
        alert('连接失败：未找到设备');
      }
    } catch (error) {
      console.error('连接失败:', error);
      alert('连接失败：' + error);
    } finally {
      connecting = false;
    }
  }
  
  async function handleStart() {
    starting = true;
    try {
      const result = await api.start('farming');
      if (result.success) {
        taskRunning = true;
        console.log('任务已启动');
      }
    } catch (error) {
      console.error('启动失败:', error);
      alert('启动失败：' + error);
    } finally {
      starting = false;
    }
  }
  
  async function handleStop() {
    stopping = true;
    try {
      const result = await api.stop();
      if (result.success) {
        taskRunning = false;
        console.log('任务已停止');
      }
    } catch (error) {
      console.error('停止失败:', error);
      alert('停止失败：' + error);
    } finally {
      stopping = false;
    }
  }
</script>

<Card size="xl">
  <h2 class="text-xl font-bold mb-4 text-gray-900 dark:text-white">任务控制</h2>
  
  <div class="space-y-4">
    <!-- 连接设备 -->
    <Button
      color="blue"
      class="w-full"
      disabled={connecting || connected}
      onclick={handleConnect}
    >
      {#if connecting}
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        连接中...
      {:else if connected}
        ✓ 已连接: {device}
      {:else}
        连接设备
      {/if}
    </Button>
    
    <!-- 启动任务 -->
    <Button
      color="green"
      class="w-full"
      disabled={!connected || starting || taskRunning}
      onclick={handleStart}
    >
      {#if starting}
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        启动中...
      {:else if taskRunning}
        ▶ 任务运行中
      {:else}
        启动任务
      {/if}
    </Button>
    
    <!-- 停止任务 -->
    <Button
      color="red"
      class="w-full"
      disabled={!taskRunning || stopping}
      onclick={handleStop}
    >
      {#if stopping}
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        停止中...
      {:else}
        停止任务
      {/if}
    </Button>
  </div>
</Card>
