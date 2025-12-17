<script lang="ts">
  import { Card, GradientButton, Toggle, Spinner, Badge } from 'flowbite-svelte';
  import { api } from '$lib/api';
  import { appStore } from '$lib/stores/appStore';
  
  let screenshotUrl = $state('');
  let useGray = $state(false);
  let loading = $state(false);
  let imageWidth = $state(0);
  let imageHeight = $state(0);
  let imageSize = $state('');
  let loadTime = $state(0);
  
  // 从store获取连接状态
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
    
    // 获取图片信息
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

<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
  <!-- 左侧：截图预览 -->
  <div class="lg:col-span-2">
    <Card size="xl" class="p-4 h-full">
      <div class="mb-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white">实时截图</h3>
          <div class="flex items-center gap-3">
            <Toggle bind:checked={useGray} size="small">灰度模式</Toggle>
            <GradientButton
              shadow
              color="cyan"
              size="sm"
              disabled={!connected || loading}
              onclick={refreshScreenshot}
            >
              {#if loading}
                <Spinner class="mr-2" size="4" />
                加载中...
              {:else}
                🔄 刷新截图
              {/if}
            </GradientButton>
          </div>
        </div>
        
        <!-- 截图信息 -->
        {#if screenshotUrl}
          <div class="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-400">
            <Badge color="blue">
              📐 {imageWidth}x{imageHeight}
            </Badge>
            <Badge color="green">
              💾 {imageSize}
            </Badge>
            <Badge color="purple">
              ⏱️ {loadTime}ms
            </Badge>
            {#if deviceResolution}
              <Badge color="indigo">
                📱 设备: {deviceResolution}
              </Badge>
            {/if}
            {#if useGray}
              <Badge color="dark">
                🎨 灰度模式
              </Badge>
            {/if}
          </div>
        {/if}
      </div>
      
      <div class="bg-gray-100 dark:bg-gray-800 rounded-xl overflow-hidden aspect-video flex items-center justify-center">
        {#if screenshotUrl}
          <img src={screenshotUrl} alt="截图" class="w-full h-full object-contain" />
        {:else}
          <div class="text-center text-gray-400 dark:text-gray-500">
            <div class="text-6xl mb-4">📸</div>
            <p>点击"刷新截图"查看</p>
          </div>
        {/if}
      </div>
    </Card>
  </div>
  
  <!-- 右侧：工具和日志 -->
  <div class="space-y-6">
    <!-- 识别测试 -->
    <Card class="p-4">
      <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">识别测试</h3>
      <div class="space-y-3">
        <GradientButton shadow color="purple" size="sm" class="w-full">
          🎯 模板匹配测试
        </GradientButton>
        <GradientButton shadow color="pink" size="sm" class="w-full">
          📝 OCR 测试
        </GradientButton>
        <GradientButton shadow color="teal" size="sm" class="w-full">
          🔍 特征匹配测试
        </GradientButton>
      </div>
    </Card>
    
    <!-- ADB 工具 -->
    <Card class="p-4">
      <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">ADB 工具</h3>
      <div class="space-y-3">
        <GradientButton shadow color="blue" size="sm" class="w-full">
          📱 设备信息
        </GradientButton>
        <GradientButton shadow color="green" size="sm" class="w-full">
          🎮 启动游戏
        </GradientButton>
        <GradientButton shadow color="red" size="sm" class="w-full">
          🔄 重启 ADB
        </GradientButton>
      </div>
    </Card>
    
    <!-- 快速操作 -->
    <Card class="p-4">
      <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">快速操作</h3>
      <div class="space-y-3">
        <GradientButton shadow color="cyan" size="sm" class="w-full">
          💾 保存截图
        </GradientButton>
        <GradientButton shadow color="lime" size="sm" class="w-full">
          📋 复制日志
        </GradientButton>
        <GradientButton shadow color="red" size="sm" class="w-full">
          🗑️ 清空日志
        </GradientButton>
      </div>
    </Card>
  </div>
</div>

<!-- 详细日志 -->
<Card size="xl" class="p-4 mt-6">
  <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">详细日志</h3>
  <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm">
    <p class="text-gray-400 dark:text-gray-500">暂无日志...</p>
  </div>
</Card>
