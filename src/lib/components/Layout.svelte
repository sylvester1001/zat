<script lang="ts">
  import Sidebar from './Sidebar.svelte';
  import Toolbar from './Toolbar.svelte';
  import type { Snippet } from 'svelte';
  
  interface Props {
    currentPage?: string;
    title?: string;
    subtitle?: string;
    hideToolbar?: boolean;
    toolbar?: Snippet;
    children?: Snippet;
  }
  
  let { currentPage = $bindable('home'), title = '', subtitle = '', hideToolbar = false, toolbar, children }: Props = $props();
</script>

<div class="h-screen flex bg-[var(--color-bg)] p-4 gap-1">
  <!-- Sidebar -->
  <Sidebar bind:currentPage />
  
  <!-- Main Content -->
  <div class="flex-1 flex flex-col overflow-hidden">
    <!-- Toolbar -->
    {#if !hideToolbar}
      <Toolbar {title} {subtitle} {toolbar} />
    {/if}
    
    <!-- Content Area -->
    <main class="flex-1 overflow-y-auto {hideToolbar ? '' : 'px-2 py-4'}">
      {#if children}
        {@render children()}
      {/if}
    </main>
  </div>
</div>
