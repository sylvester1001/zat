<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import '../app.css';
  import Layout from '$lib/components/Layout.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import HomePage from '$lib/pages/HomePage.svelte';
  import DebugPage from '$lib/pages/DebugPage.svelte';
  import TasksPage from '$lib/pages/TasksPage.svelte';
  import { startHeartbeat, stopHeartbeat, startStateWebSocket, stopStateWebSocket } from '$lib/stores/appStore';
  
  let currentPage = $state('home');
  
  onMount(() => {
    console.log('ZAT 已启动');
    startHeartbeat();
    startStateWebSocket();
  });
  
  onDestroy(() => {
    stopHeartbeat();
    stopStateWebSocket();
  });
</script>

<Layout bind:currentPage>
  {#if currentPage === 'home'}
    <HomePage />
  {:else if currentPage === 'debug'}
    <DebugPage />
  {:else if currentPage === 'tasks'}
    <TasksPage />
  {:else if currentPage === 'stats'}
    <div class="flex-1 overflow-auto px-5 pb-5 space-y-5">
      <PageHeader title="统计分析" subtitle="查看任务执行统计 📊" />
      <div class="clean-card text-center py-20">
        <div class="w-20 h-20 mx-auto mb-4 bg-[var(--color-lime)] rounded-3xl flex items-center justify-center text-4xl">📊</div>
        <h3 class="text-2xl font-bold text-gray-800 mb-2">统计分析</h3>
        <p class="text-gray-500">功能开发中...</p>
      </div>
    </div>
  {:else if currentPage === 'settings'}
    <div class="flex-1 overflow-auto px-5 pb-5 space-y-5">
      <PageHeader title="设置" subtitle="配置应用参数 ⚙️" />
      <div class="clean-card text-center py-20">
        <div class="w-20 h-20 mx-auto mb-4 bg-gray-100 rounded-3xl flex items-center justify-center text-4xl">⚙️</div>
        <h3 class="text-2xl font-bold text-gray-800 mb-2">设置</h3>
        <p class="text-gray-500">功能开发中...</p>
      </div>
    </div>
  {/if}
</Layout>
