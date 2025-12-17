<script lang="ts">
  export let title = '';
  export let subtitle = '';
</script>

<div class="h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 flex items-center justify-between">
  <!-- Left: Title -->
  <div>
    <h2 class="text-lg font-bold text-gray-900 dark:text-white">{title}</h2>
    {#if subtitle}
      <p class="text-sm text-gray-500 dark:text-gray-400">{subtitle}</p>
    {/if}
  </div>
  
  <!-- Right: Actions Slot -->
  <div class="flex items-center gap-3">
    <slot />
  </div>
</div>
