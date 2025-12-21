<script lang="ts">
  import { ButtonGroup, Button } from 'flowbite-svelte';
  import { getDungeonDifficulties, type DifficultyId } from '$lib/config/dungeonConfig';

  interface Props {
    dungeonId: string;
    selected: DifficultyId;
    onSelect: (difficulty: DifficultyId) => void;
  }

  let { dungeonId, selected, onSelect }: Props = $props();

  let difficulties = $derived(getDungeonDifficulties(dungeonId));
</script>

<div class="py-3">
  <ButtonGroup>
    {#each difficulties as diff}
      <Button
        color="dark"
        class={selected === diff.id ? 'zat-lime' : ''}
        onclick={() => onSelect(diff.id)}
      >
        {diff.name}
      </Button>
    {/each}
  </ButtonGroup>
</div>
