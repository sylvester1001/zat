<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  
  let appWindow: any = null;
  let isMaximized = $state(false);
  let unlisten: (() => void) | null = null;
  
  onMount(async () => {
    // 动态导入 Tauri API
    const { getCurrentWindow } = await import('@tauri-apps/api/window');
    appWindow = getCurrentWindow();
    
    // 监听窗口状态变化
    isMaximized = await appWindow.isMaximized();
    
    unlisten = await appWindow.onResized(async () => {
      isMaximized = await appWindow.isMaximized();
    });
  });
  
  onDestroy(() => {
    unlisten?.();
  });
  
  async function minimize() {
    await appWindow?.minimize();
  }
  
  async function toggleMaximize() {
    await appWindow?.toggleMaximize();
  }
  
  async function close() {
    await appWindow?.close();
  }
</script>

<div class="titlebar" data-tauri-drag-region>
  <!-- 拖拽区域 -->
  <div class="titlebar-center" data-tauri-drag-region></div>
  
  <!-- 右侧窗口控制按钮 - 贴边 -->
  <div class="titlebar-controls">
    <button class="titlebar-btn" onclick={minimize} aria-label="最小化">
      <svg width="12" height="12" viewBox="0 0 12 12">
        <rect y="5" width="12" height="2" rx="1" fill="currentColor"/>
      </svg>
    </button>
    
    <button class="titlebar-btn" onclick={toggleMaximize} aria-label={isMaximized ? '还原' : '最大化'}>
      {#if isMaximized}
        <svg width="12" height="12" viewBox="0 0 12 12">
          <path d="M3 1h6a2 2 0 012 2v6a2 2 0 01-2 2H3a2 2 0 01-2-2V3a2 2 0 012-2zm0 1.5a.5.5 0 00-.5.5v6a.5.5 0 00.5.5h6a.5.5 0 00.5-.5V3a.5.5 0 00-.5-.5H3z" fill="currentColor"/>
          <path d="M4.5 0H10a2 2 0 012 2v5.5" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round"/>
        </svg>
      {:else}
        <svg width="12" height="12" viewBox="0 0 12 12">
          <rect x="1" y="1" width="10" height="10" rx="2" stroke="currentColor" stroke-width="1.5" fill="none"/>
        </svg>
      {/if}
    </button>
    
    <button class="titlebar-btn close" onclick={close} aria-label="关闭">
      <svg width="12" height="12" viewBox="0 0 12 12">
        <path d="M2 2l8 8M10 2l-8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
    </button>
  </div>
</div>
