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
      const result = await api.startTaskEngine('farming');
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
      const result = await api.stopTaskEngine();
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
      disabled={connected}
      loading={connecting}
      onclick={handleConnect}
    >
      {#if connecting}
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
      disabled={!connected || taskRunning}
      loading={starting}
      onclick={handleStart}
    >
      {#if starting}
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
      disabled={!taskRunning}
      loading={stopping}
      onclick={handleStop}
    >
      {#if stopping}
        停止中...
      {:else}
        停止任务
      {/if}
    </Button>
  </div>
</Card>
