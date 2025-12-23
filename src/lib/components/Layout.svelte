<script lang="ts">
  import { onMount } from 'svelte';
  import Sidebar from './Sidebar.svelte';
  import TitleBar from './TitleBar.svelte';
  import type { Snippet } from 'svelte';
  
  interface Props {
    currentPage?: string;
    children?: Snippet;
  }
  
  let { currentPage = $bindable('home'), children }: Props = $props();
  let isMacOS = $state(false);
  
  onMount(async () => {
    try {
      const { platform } = await import('@tauri-apps/plugin-os');
      isMacOS = platform() === 'macos';
      if (isMacOS) {
        document.documentElement.classList.add('platform-macos');
      }
    } catch (e) {
      // 浏览器环境
    }
    
    // 显示窗口，等待 WebView 渲染完成
    setTimeout(async () => {
      try {
        const { getCurrentWindow } = await import('@tauri-apps/api/window');
        await getCurrentWindow().show();
      } catch (e) {
        // 浏览器环境
      }
    }, 250);
  });
</script>

<div class="app-layout h-screen flex flex-col bg-[var(--color-bg)]">
  <!-- 自定义标题栏（macOS 上通过 CSS 绝对定位） -->
  <TitleBar />
  
  <!-- 主体内容 -->
  <div class="flex-1 flex px-4 pb-4 gap-1 overflow-hidden">
    <!-- Sidebar -->
    <Sidebar bind:currentPage />
  
    <!-- Main Content -->
    <main class="flex-1 overflow-y-auto">
      {#if children}
        {@render children()}
      {/if}
    </main>
  </div>
</div>
