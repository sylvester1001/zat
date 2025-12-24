<script lang="ts">
  interface Props {
    title: string;
    subtitle?: string;
    compact?: boolean;
  }
  
  let { title, subtitle = '', compact = false }: Props = $props();
</script>

{#if compact}
  <div class="gradient-header-compact px-4 pt-4 pb-4">
    <h2 class="text-xl font-bold text-gray-900">{title}</h2>
  </div>
{:else}
  <div class="gradient-header px-6 pt-6 pb-8">
    {#if subtitle}
      <p class="text-sm text-gray-700 font-medium mb-1">{subtitle}</p>
    {/if}
    <h2 class="text-3xl font-bold text-gray-900">{title}</h2>
  </div>
{/if}
