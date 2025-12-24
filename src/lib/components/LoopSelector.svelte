<script lang="ts">
  import { Input, Label } from 'flowbite-svelte';

  interface Props {
    mode: string;
    count: number;
    onModeChange: (mode: string) => void;
    onCountChange: (count: number) => void;
  }

  let { mode, count, onModeChange, onCountChange }: Props = $props();

  const options = [
    { id: 'single', label: '单次' },
    { id: 'loop', label: '循环' },
    { id: 'infinite', label: '无限' },
  ];

  let selectedIndex = $derived(options.findIndex(o => o.id === mode));

  function handleCountInput(e: Event) {
    const target = e.target as HTMLInputElement;
    let value = parseInt(target.value) || 1;
    if (value < 1) value = 1;
    if (value > 999) value = 999;
    onCountChange(value);
  }
</script>

<div class="inline-flex flex-col gap-2">
  <Label class="text-gray-500 text-sm">执行次数</Label>
  <div class="flex items-center gap-3">
    <div class="pill-selector">
      <div 
        class="pill-indicator" 
        style="transform: translateX(calc({selectedIndex} * var(--pill-btn-width)));"
      ></div>
      {#each options as opt}
        <button
          class="pill-option {mode === opt.id ? 'selected' : ''}"
          onclick={() => onModeChange(opt.id)}
        >
          {opt.label}
        </button>
      {/each}
    </div>
    
    {#if mode === 'loop'}
      <Input
        type="number"
        size="sm"
        value={count}
        min={1}
        max={999}
        oninput={handleCountInput}
      />
    {/if}
  </div>
</div>
