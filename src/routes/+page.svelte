<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import '../app.css';
  import Layout from '$lib/components/Layout.svelte';
  import HomePage from '$lib/pages/HomePage.svelte';
  import DebugPage from '$lib/pages/DebugPage.svelte';
  import { Badge } from 'flowbite-svelte';
  import { appStore, startHeartbeat, stopHeartbeat } from '$lib/stores/appStore';
  
  let currentPage = $state('home');
  
  // 从store获取状态
  let connected = $derived($appStore.connected);
  let taskEngineRunning = $derived($appStore.taskEngineRunning);
  
  onMount(() => {
    console.log('ZAT 已启动');
    startHeartbeat();
  });
  
  onDestroy(() => {
    stopHeartbeat();
  });
  
  // 根据当前页面返回标题和副标题
  let pageInfo = $derived(getPageInfo(currentPage));
  
  function getPageInfo(page: string) {
    switch (page) {
      case 'home':
        return { title: '首页', subtitle: '快速开始你的自动化任务' };
      case 'tasks':
        return { title: '任务管理', subtitle: '配置和管理你的任务' };
      case 'stats':
        return { title: '统计分析', subtitle: '查看任务执行统计' };
      case 'debug':
        return { title: '调试工具', subtitle: '实时调试和测试' };
      case 'settings':
        return { title: '设置', subtitle: '配置应用参数' };
      default:
        return { title: '', subtitle: '' };
    }
  }
</script>

<Layout bind:currentPage title={pageInfo.title} subtitle={pageInfo.subtitle}>
  <!-- Toolbar Actions -->
  {#snippet toolbar()}
    {#if currentPage === 'home'}
      {#if taskEngineRunning}
        <Badge color="green" large>运行中</Badge>
      {:else if connected}
        <Badge color="blue" large>已连接</Badge>
      {:else}
        <Badge color="dark" large>未连接</Badge>
      {/if}
    {:else if currentPage === 'debug'}
      {#if connected}
        <Badge color="green" large>已连接</Badge>
      {:else}
        <Badge color="dark" large>未连接</Badge>
      {/if}
    {/if}
  {/snippet}
  
  <!-- Page Content -->
  {#if currentPage === 'home'}
    <HomePage />
  {:else if currentPage === 'debug'}
    <DebugPage />
  {:else if currentPage === 'tasks'}
    <div class="text-center py-20">
      <div class="text-6xl mb-4">🎮</div>
      <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">任务管理</h3>
      <p class="text-gray-500 dark:text-gray-400">功能开发中...</p>
    </div>
  {:else if currentPage === 'stats'}
    <div class="text-center py-20">
      <div class="text-6xl mb-4">📊</div>
      <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">统计分析</h3>
      <p class="text-gray-500 dark:text-gray-400">功能开发中...</p>
    </div>
  {:else if currentPage === 'settings'}
    <div class="text-center py-20">
      <div class="text-6xl mb-4">⚙️</div>
      <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">设置</h3>
      <p class="text-gray-500 dark:text-gray-400">功能开发中...</p>
    </div>
  {/if}
</Layout>
