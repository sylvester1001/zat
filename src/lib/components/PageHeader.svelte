<script lang="ts">
  interface Props {
    title: string;
    subtitle?: string;
  }
  
  let { title, subtitle = '' }: Props = $props();
</script>

<div class="gradient-header px-6 pt-6 pb-8 rounded-3xl">
  {#if subtitle}
    <p class="text-sm text-gray-700 font-medium mb-1">{subtitle}</p>
  {/if}
  <h2 class="text-3xl font-bold text-gray-900">{title}</h2>
</div>
