<script lang="ts">
  import { onMount } from 'svelte';
  import '../app.css';
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

<main class="h-screen bg-gray-50 dark:bg-gray-900">
  <div class="container mx-auto p-6 h-full flex flex-col">
    <!-- Header -->
    <header class="mb-6">
      <h1 class="text-4xl font-bold text-gray-900 dark:text-white">
        ZAT - 仗剑传说自动化工具
      </h1>
      <p class="text-gray-600 dark:text-gray-400 mt-2">
        Zhangjianchuanshuo Automation Tool
      </p>
    </header>
    
    <!-- Main Content -->
    <div class="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6 overflow-hidden">
      <!-- 左侧：控制面板 -->
      <div class="lg:col-span-1 space-y-6 overflow-y-auto">
        <TaskControl bind:connected bind:device />
        <DebugPanel {connected} />
      </div>
      
      <!-- 右侧：日志和状态 -->
      <div class="lg:col-span-2 space-y-6 overflow-y-auto">
        <StatusBar {connected} {device} />
        <LogViewer />
      </div>
    </div>
  </div>
</main>
