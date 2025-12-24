<script lang="ts">
  import { Label } from 'flowbite-svelte';
  import { getDungeonDifficulties, type DifficultyId } from '$lib/config/dungeonConfig';

  interface Props {
    dungeonId: string;
    selected: DifficultyId;
    onSelect: (difficulty: DifficultyId) => void;
  }

  let { dungeonId, selected, onSelect }: Props = $props();

  let difficulties = $derived(getDungeonDifficulties(dungeonId));
  let selectedIndex = $derived(difficulties.findIndex(d => d.id === selected));
</script>

<div class="inline-flex flex-col gap-2">
  <Label class="text-gray-500 text-sm">难度选择</Label>
  <div class="pill-selector">
    <div 
      class="pill-indicator" 
      style="transform: translateX(calc({selectedIndex} * var(--pill-btn-width)));"
    ></div>
    {#each difficulties as diff}
      <button
        class="pill-option {selected === diff.id ? 'selected' : ''}"
        onclick={() => onSelect(diff.id)}
      >
        {diff.name}
      </button>
    {/each}
  </div>
</div>
