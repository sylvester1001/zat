<script lang="ts">
  import Sidebar from './Sidebar.svelte';
  import type { Snippet } from 'svelte';
  
  interface Props {
    currentPage?: string;
    children?: Snippet;
  }
  
  let { currentPage = $bindable('home'), children }: Props = $props();
</script>

<div class="h-screen flex bg-[var(--color-bg)] p-4 gap-1">
  <!-- Sidebar -->
  <Sidebar bind:currentPage />
  
  <!-- Main Content -->
  <main class="flex-1 overflow-y-auto">
    {#if children}
      {@render children()}
    {/if}
  </main>
</div>
