<script lang="ts">
  import Sidebar from './Sidebar.svelte';
  import Toolbar from './Toolbar.svelte';
  import type { Snippet } from 'svelte';
  
  interface Props {
    currentPage?: string;
    title?: string;
    subtitle?: string;
    toolbar?: Snippet;
    children?: Snippet;
  }
  
  let { currentPage = $bindable('home'), title = '', subtitle = '', toolbar, children }: Props = $props();
</script>

<div class="h-screen flex bg-gray-50 dark:bg-gray-900">
  <!-- Sidebar -->
  <Sidebar bind:currentPage />
  
  <!-- Main Content -->
  <div class="flex-1 flex flex-col overflow-hidden">
    <!-- Toolbar -->
    <Toolbar {title} {subtitle} {toolbar} />
    
    <!-- Content Area -->
    <main class="flex-1 overflow-y-auto p-6">
      {#if children}
        {@render children()}
      {/if}
    </main>
  </div>
</div>
