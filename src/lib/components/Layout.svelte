<script lang="ts">
  import Sidebar from './Sidebar.svelte';
  import TitleBar from './TitleBar.svelte';
  import type { Snippet } from 'svelte';
  
  interface Props {
    currentPage?: string;
    children?: Snippet;
  }
  
  let { currentPage = $bindable('home'), children }: Props = $props();
</script>

<div class="h-screen flex flex-col bg-[var(--color-bg)]">
  <!-- 自定义标题栏 -->
  <TitleBar />
  
  <!-- 主体内容 -->
  <div class="flex-1 flex p-4 gap-1 overflow-hidden">
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
