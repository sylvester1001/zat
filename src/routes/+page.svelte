<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import TaskControl from '$lib/components/TaskControl.svelte';
  import LogViewer from '$lib/components/LogViewer.svelte';
  import StatusBar from '$lib/components/StatusBar.svelte';
  import DebugPanel from '$lib/components/DebugPanel.svelte';
  
  let connected = false;
  let device = '';
  
  onMount(() => {
    console.log('ZAT 已启动');
  });
</script>

<main class="container mx-auto p-4 h-screen flex flex-col">
  <header class="mb-4">
    <h1 class="text-3xl font-bold">ZAT - 仗剑传说自动化工具</h1>
    <p class="text-gray-600">Zhangjianchuanshuo Automation Tool</p>
  </header>
  
  <div class="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-4">
    <!-- 左侧：控制面板 -->
    <div class="lg:col-span-1 space-y-4">
      <TaskControl bind:connected bind:device />
      <DebugPanel {connected} />
    </div>
    
    <!-- 右侧：日志和状态 -->
    <div class="lg:col-span-2 space-y-4">
      <StatusBar {connected} {device} />
      <LogViewer />
    </div>
  </div>
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  }
</style>
