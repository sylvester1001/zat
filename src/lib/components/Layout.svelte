<script lang="ts">
  import Sidebar from './Sidebar.svelte';
  import Toolbar from './Toolbar.svelte';
  
  export let currentPage = 'home';
  export let title = '';
  export let subtitle = '';
</script>

<div class="h-screen flex bg-gray-50 dark:bg-gray-900">
  <!-- Sidebar -->
  <Sidebar bind:currentPage />
  
  <!-- Main Content -->
  <div class="flex-1 flex flex-col overflow-hidden">
    <!-- Toolbar -->
    <Toolbar {title} {subtitle}>
      <slot name="toolbar" />
    </Toolbar>
    
    <!-- Content Area -->
    <main class="flex-1 overflow-y-auto p-6">
      <slot />
    </main>
  </div>
</div>
