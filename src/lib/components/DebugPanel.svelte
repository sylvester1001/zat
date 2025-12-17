<script lang="ts">
  import { api } from '$lib/api';
  
  export let connected = false;
  
  let screenshotUrl = '';
  let useGray = false;
  let loading = false;
  
  function refreshScreenshot() {
    if (!connected) return;
    
    loading = true;
    screenshotUrl = api.getScreenshotUrl(useGray);
    
    // 等待图片加载完成
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

<div class="card bg-white shadow-lg rounded-lg p-6">
  <h2 class="text-xl font-bold mb-4">调试面板</h2>
  
  <div class="space-y-4">
    <!-- 控制选项 -->
    <div class="flex items-center gap-4">
      <label class="flex items-center gap-2">
        <input type="checkbox" bind:checked={useGray} />
        <span class="text-sm">灰度图</span>
      </label>
      
      <button
        class="btn-sm btn-primary"
        class:btn-disabled={!connected || loading}
        on:click={refreshScreenshot}
        disabled={!connected || loading}
      >
        {loading ? '加载中...' : '刷新截图'}
      </button>
    </div>
    
    <!-- 截图预览 -->
    <div class="screenshot-container">
      {#if screenshotUrl}
        <img src={screenshotUrl} alt="截图" class="screenshot" />
      {:else}
        <div class="placeholder">
          <p class="text-gray-400">点击"刷新截图"查看</p>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .card {
    border: 1px solid #e5e7eb;
  }
  
  .btn-sm {
    padding: 0.375rem 0.75rem;
    border-radius: 0.375rem;
    font-size: 0.875rem;
    font-weight: 500;
    border: none;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .btn-primary {
    background-color: #3b82f6;
    color: white;
  }
  
  .btn-primary:hover:not(.btn-disabled) {
    background-color: #2563eb;
  }
  
  .btn-disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .screenshot-container {
    width: 100%;
    aspect-ratio: 16 / 9;
    background-color: #f3f4f6;
    border-radius: 0.5rem;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .screenshot {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
  
  .placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
  }
</style>
