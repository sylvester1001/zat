<script lang="ts">
  import type { Snippet } from 'svelte';
  
  interface Props {
    title?: string;
    subtitle?: string;
    toolbar?: Snippet;
  }
  
  let { title = '', subtitle = '', toolbar }: Props = $props();
</script>

<div class="h-16 px-6 flex items-center justify-between">
  <!-- Left: Title -->
  <div>
    <h2 class="text-xl font-bold text-gray-800">{title}</h2>
    {#if subtitle}
      <p class="text-sm text-(--color-purple)">{subtitle}</p>
    {/if}
  </div>
  
  <!-- Right: Actions Slot -->
  <div class="flex items-center gap-3">
    {#if toolbar}
      {@render toolbar()}
    {/if}
  </div>
</div>
