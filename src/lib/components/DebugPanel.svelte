<script lang="ts">
  import { Card, Button, Toggle, Spinner } from 'flowbite-svelte';
  import { api } from '$lib/api';
  
  interface Props {
    connected?: boolean;
  }
  
  let { connected = false }: Props = $props();
  
  let screenshotUrl = $state('');
  let useGray = $state(false);
  let loading = $state(false);
  
  function refreshScreenshot() {
    if (!connected) return;
    
    loading = true;
    screenshotUrl = api.getScreenshotUrl(useGray);
    
    const img = new Image();
    img.onload = () => {
      loading = false;
    };
    img.onerror = () => {
      loading = false;
      alert('截图失败');
    };
    img.src = screenshotUrl;
  }
</script>

<Card size="xl">
  <h2 class="text-xl font-bold mb-4 text-gray-900 dark:text-white">调试面板</h2>
  
  <div class="space-y-4">
    <!-- 控制选项 -->
    <div class="flex items-center gap-4">
      <Toggle bind:checked={useGray} size="small">灰度图</Toggle>
      
      <Button
        color="blue"
        size="sm"
        disabled={!connected || loading}
        onclick={refreshScreenshot}
      >
        {#if loading}
          <Spinner class="mr-2" size="4" />
          加载中...
        {:else}
          刷新截图
        {/if}
      </Button>
    </div>
    
    <!-- 截图预览 -->
    <div class="w-full aspect-video bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden flex items-center justify-center">
      {#if screenshotUrl}
        <img src={screenshotUrl} alt="截图" class="w-full h-full object-contain" />
      {:else}
        <p class="text-gray-400 dark:text-gray-500">点击"刷新截图"查看</p>
      {/if}
    </div>
  </div>
</Card>
