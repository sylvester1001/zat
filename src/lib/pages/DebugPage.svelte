<script lang="ts">
  import { api } from '$lib/api';
  import { appStore } from '$lib/stores/appStore';
  import { Button, Toggle } from 'flowbite-svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  
  let screenshotUrl = $state('');
  let useGray = $state(false);
  let loading = $state(false);
  let imageWidth = $state(0);
  let imageHeight = $state(0);
  let imageSize = $state('');
  let loadTime = $state(0);
  
  let connected = $derived($appStore.connected);
  let deviceResolution = $derived($appStore.resolution);
  
  async function refreshScreenshot() {
    if (!connected) {
      alert('请先连接设备');
      return;
    }
    
    loading = true;
    const startTime = performance.now();
    screenshotUrl = api.getScreenshotUrl(useGray);
    
    try {
      const response = await fetch(screenshotUrl);
      const blob = await response.blob();
      imageSize = formatBytes(blob.size);
      
      const img = new Image();
      img.onload = () => {
        imageWidth = img.naturalWidth;
        imageHeight = img.naturalHeight;
        loadTime = Math.round(performance.now() - startTime);
        loading = false;
      };
      img.onerror = () => {
        loading = false;
        alert('截图失败');
      };
      img.src = URL.createObjectURL(blob);
      screenshotUrl = img.src;
    } catch (error) {
      loading = false;
      alert('截图失败: ' + error);
    }
  }
  
  function formatBytes(bytes: number): string {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  }
</script>

<div class="flex-1 overflow-auto px-5 pb-5 space-y-5">
  <PageHeader title="实时调试" compact />

  <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
    <!-- 左侧：截图预览 -->
    <div class="lg:col-span-2">
      <div class="clean-card p-5 h-full">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-base font-bold text-gray-900">实时截图</h3>
          <div class="flex items-center gap-3">
            <Toggle bind:checked={useGray} size="small">灰度</Toggle>
            <Button
              pill
              size="sm"
              class="zat-lime"
              disabled={!connected || loading}
              onclick={refreshScreenshot}
            >
              {#if loading}
                ⏳ 加载中...
              {:else}
                🔄 刷新截图
              {/if}
            </Button>
          </div>
        </div>
        
        <!-- 截图信息 -->
        {#if screenshotUrl}
          <div class="flex items-center gap-2 mb-4 flex-wrap">
            <span class="tag tag-outline">📐 {imageWidth}x{imageHeight}</span>
            <span class="tag tag-outline">💾 {imageSize}</span>
            <span class="tag tag-outline">⏱️ {loadTime}ms</span>
            {#if deviceResolution}
              <span class="tag tag-lime">📱 {deviceResolution}</span>
            {/if}
            {#if useGray}
              <span class="tag tag-outline">🎨 灰度</span>
            {/if}
          </div>
        {/if}
        
        <div class="bg-gray-50 rounded-2xl overflow-hidden aspect-video flex items-center justify-center">
          {#if screenshotUrl}
            <img src={screenshotUrl} alt="截图" class="w-full h-full object-contain" />
          {:else}
            <div class="text-center text-gray-400">
              <div class="text-6xl mb-4">📸</div>
              <p>点击"刷新截图"查看</p>
            </div>
          {/if}
        </div>
      </div>
    </div>
    
    <!-- 右侧：工具 -->
    <div class="space-y-5">
      <!-- 识别测试 -->
      <div class="clean-card p-5">
        <h3 class="text-base font-bold text-gray-900 mb-4">识别测试</h3>
        <div class="space-y-3">
          <Button pill class="w-full zat-dark">🎯 模板匹配测试</Button>
          <Button pill class="w-full zat-light">📝 OCR 测试</Button>
          <Button pill class="w-full zat-light">🔍 特征匹配测试</Button>
        </div>
      </div>
      
      <!-- ADB 工具 -->
      <div class="clean-card p-5">
        <h3 class="text-base font-bold text-gray-900 mb-4">ADB 工具</h3>
        <div class="space-y-3">
          <Button pill class="w-full zat-lime">📱 设备信息</Button>
          <Button pill class="w-full zat-yellow">🎮 启动游戏</Button>
          <Button pill class="w-full zat-light">🔄 重启 ADB</Button>
        </div>
      </div>
      
      <!-- 快速操作 -->
      <div class="clean-card p-5">
        <h3 class="text-base font-bold text-gray-900 mb-4">快速操作</h3>
        <div class="space-y-3">
          <Button pill class="w-full zat-dark">💾 保存截图</Button>
          <Button pill class="w-full zat-light">📋 复制日志</Button>
          <Button pill class="w-full zat-danger">🗑️ 清空日志</Button>
        </div>
      </div>
    </div>
  </div>

  <!-- 详细日志 -->
  <div class="clean-card p-5">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-base font-bold text-gray-900">详细日志</h3>
      <span class="tag tag-lime">实时</span>
    </div>
    <div class="bg-gray-50 rounded-2xl p-4 h-48 overflow-y-auto font-mono text-sm">
      <p class="text-gray-400">暂无日志...</p>
    </div>
  </div>
</div>
