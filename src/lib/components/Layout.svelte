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
  
  onMount(() => {
    // 延迟显示窗口，等待 WebView 渲染完成
    setTimeout(async () => {
      const { getCurrentWindow } = await import('@tauri-apps/api/window');
      await getCurrentWindow().show();
    }, 250);
  });
</script>

<div class="h-screen flex flex-col bg-[var(--color-bg)]">
  <!-- 自定义标题栏 -->
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
