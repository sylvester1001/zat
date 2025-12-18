<script lang="ts">
  import { Button } from 'flowbite-svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import { appStore } from '$lib/stores/appStore';
  
  let connected = $derived($appStore.connected);
  
  // 副本配置
  const dungeons = [
    { id: 'world_tree', name: '世界之树', icon: '🌳', difficulties: ['normal', 'hard'], color: '' },
    { id: 'machine_mountain', name: '机神山', icon: '⛰️', difficulties: ['normal', 'hard'], color: 'yellow' },
    { id: 'sea_palace', name: '海之宫遗迹', icon: '🏛️', difficulties: ['normal', 'hard'], color: 'with-bg sea-palace-bg' },
    { id: 'water_shrine', name: '源水大社', icon: '⛩️', difficulties: ['normal', 'hard', 'nightmare'], color: 'white' },
  ];
  
  const difficultyLabels: Record<string, string> = {
    normal: '普通',
    hard: '困难',
    nightmare: '噩梦',
  };
  
  let selectedDungeon = $state<string | null>(null);
  let selectedDifficulty = $state<string>('normal');
  let starting = $state(false);
  
  // 获取当前选中副本的可用难度
  let availableDifficulties = $derived(() => {
    const dungeon = dungeons.find(d => d.id === selectedDungeon);
    return dungeon?.difficulties || ['normal', 'hard'];
  });
  
  // 当选中副本变化时，检查当前难度是否可用
  $effect(() => {
    const difficulties = availableDifficulties();
    if (!difficulties.includes(selectedDifficulty)) {
      selectedDifficulty = 'normal';
    }
  });
  
  function selectDungeon(id: string) {
    selectedDungeon = selectedDungeon === id ? null : id;
  }
  
  async function handleStartTask() {
    if (!selectedDungeon || !connected) return;
    
    starting = true;
    try {
      // TODO: 调用后端 API 开始任务
      console.log('开始任务:', selectedDungeon, selectedDifficulty);
      alert(`开始任务: ${dungeons.find(d => d.id === selectedDungeon)?.name} - ${difficultyLabels[selectedDifficulty]}`);
    } catch (error) {
      console.error('启动任务失败:', error);
      alert('启动任务失败：' + error);
    } finally {
      starting = false;
    }
  }
</script>

<div class="flex-1 overflow-auto px-5 pb-5 space-y-5 flex flex-col">
  <PageHeader title="任务配置" subtitle="选择副本开始自动化 🎮" />

  <!-- 副本选择 -->
  <div class="grid grid-cols-4 gap-4">
    {#each dungeons as dungeon}
      <button
        class="dungeon-card {dungeon.color} {selectedDungeon === dungeon.id ? 'selected' : ''}"
        onclick={() => selectDungeon(dungeon.id)}
      >
        <!-- 跑马灯 -->
        <div class="carousel" data-position="top">
          <span class="carousel-text">{dungeon.name} • {dungeon.name} • {dungeon.name} • {dungeon.name} • {dungeon.name} • {dungeon.name} • {dungeon.name} • {dungeon.name} • </span>
        </div>
        <div class="carousel" data-position="bottom" data-direction="right">
          <span class="carousel-text">{dungeon.name} • {dungeon.name} • {dungeon.name} • {dungeon.name} • {dungeon.name} • {dungeon.name} • {dungeon.name} • {dungeon.name} • </span>
        </div>
        
        <div class="card-icon">{dungeon.icon}</div>
        <span class="card-title">{dungeon.name}</span>
        <span class="card-desc">{dungeon.difficulties.length} 种难度</span>
      </button>
    {/each}
  </div>

  <!-- 难度选择 -->
  <div class="clean-card p-5">
    <h3 class="text-base font-bold text-gray-900 mb-4">难度选择</h3>
    <div class="flex gap-3">
      {#each ['normal', 'hard', 'nightmare'] as difficulty}
        {@const isAvailable = availableDifficulties().includes(difficulty)}
        <button
          class="difficulty-btn {selectedDifficulty === difficulty ? 'selected' : ''} {!isAvailable ? 'unavailable' : ''}"
          disabled={!isAvailable}
          onclick={() => selectedDifficulty = difficulty}
        >
          {difficultyLabels[difficulty]}
        </button>
      {/each}
    </div>
    {#if selectedDungeon && !availableDifficulties().includes('nightmare')}
      <p class="text-xs text-gray-400 mt-2">噩梦难度仅源水大社可选</p>
    {/if}
  </div>

  <!-- 底部操作区 -->
  <div class="mt-auto flex justify-end">
    <Button
      pill
      class="px-8 py-4 zat-lime"
      disabled={!selectedDungeon || !connected || starting}
      onclick={handleStartTask}
    >
      {#if starting}
        <span class="animate-pulse mr-2">🚀</span>启动中...
      {:else}
        <span class="mr-2">🚀</span>开始任务
      {/if}
    </Button>
  </div>
</div>

<style>
  .difficulty-btn {
    padding: 0.75rem 1.5rem;
    background: var(--color-gray-100);
    border: 2px solid transparent;
    border-radius: 50px;
    font-weight: 600;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s ease;
    color: var(--color-gray-700);
  }
  
  .difficulty-btn:hover:not(:disabled) {
    background: var(--color-gray-200);
  }
  
  .difficulty-btn.selected {
    background: var(--color-lime);
    border-color: var(--color-gray-900);
    color: var(--color-gray-900);
  }
  
  .difficulty-btn.unavailable {
    opacity: 0.4;
    cursor: not-allowed;
  }
</style>
