<script lang="ts">
  import { Button } from 'flowbite-svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import DifficultySelector from '$lib/components/DifficultySelector.svelte';
  import { appStore, type AppState } from '$lib/stores/appStore';
  import { api } from '$lib/api';
  import { DUNGEONS, type DifficultyId } from '$lib/config/dungeonConfig';
  
  // 订阅 store
  let storeValue = $state<AppState | null>(null);
  $effect(() => {
    const unsubscribe = appStore.subscribe(value => {
      storeValue = value;
    });
    return unsubscribe;
  });
  
  let connected = $derived(storeValue?.connected ?? false);
  
  let selectedDungeon = $state<string | null>(null);
  // 每个副本的难度选择状态
  let selectedDifficulties = $state<Record<string, DifficultyId>>({});
  let navigating = $state(false);
  
  // 获取当前选中副本的难度
  let currentDifficulty = $derived(
    selectedDungeon ? (selectedDifficulties[selectedDungeon] || 'normal') : 'normal'
  );
  
  function selectDungeon(id: string) {
    selectedDungeon = selectedDungeon === id ? null : id;
    // 初始化难度为 normal（如果还没选过）
    if (selectedDungeon && !selectedDifficulties[selectedDungeon]) {
      selectedDifficulties[selectedDungeon] = 'normal';
    }
  }
  
  function handleDifficultySelect(dungeonId: string, difficulty: DifficultyId) {
    selectedDifficulties[dungeonId] = difficulty;
  }
  
  // 导航到副本
  async function handleEnterDungeon() {
    if (!selectedDungeon || !connected) return;
    
    navigating = true;
    try {
      const result = await api.navigateToDungeon(selectedDungeon, currentDifficulty);
      if (result.success) {
        const dungeonName = DUNGEONS.find(d => d.id === selectedDungeon)?.name;
        console.log(`已进入副本: ${dungeonName} (${currentDifficulty})`);
      } else {
        alert('进入副本失败: ' + (result.message || '未知错误'));
      }
    } catch (error) {
      console.error('进入副本失败:', error);
      alert('进入副本失败：' + error);
    } finally {
      navigating = false;
    }
  }
</script>

<div class="flex-1 overflow-auto px-5 pb-5 space-y-5 flex flex-col">
  <PageHeader title="任务配置" subtitle="选择副本开始 🎮" />

  <!-- 副本选择 -->
  <div class="grid grid-cols-4 gap-4">
    {#each DUNGEONS as dungeon}
      <div class="dungeon-card-wrapper {selectedDungeon === dungeon.id ? 'selected' : ''}">
        <div class="select-badge"></div>
        <button
          class="dungeon-card with-bg {dungeon.bgClass} {selectedDungeon === dungeon.id ? 'selected' : ''}"
          onclick={() => selectDungeon(dungeon.id)}
        >
          <!-- 跑马灯 -->
          <div class="carousel" data-position="top">
            <span class="carousel-text">{dungeon.name} • {dungeon.name} • {dungeon.name} • {dungeon.name} • {dungeon.name} • {dungeon.name} • {dungeon.name} • {dungeon.name} • </span>
          </div>
          <div class="carousel" data-position="bottom" data-direction="right">
            <span class="carousel-text">{dungeon.name} • {dungeon.name} • {dungeon.name} • {dungeon.name} • {dungeon.name} • {dungeon.name} • {dungeon.name} • {dungeon.name} • </span>
          </div>
          
          <span class="card-title">{dungeon.name}</span>
          <span class="card-desc">{dungeon.desc}</span>
        </button>
      </div>
    {/each}
  </div>

  <!-- 难度选择 -->
  {#if selectedDungeon}
    <div>
      <DifficultySelector
        dungeonId={selectedDungeon}
        selected={selectedDifficulties[selectedDungeon] || 'normal'}
        onSelect={(diff) => handleDifficultySelect(selectedDungeon!, diff)}
      />
    </div>
  {/if}

  <!-- 底部操作区 -->
  <div class="mt-auto flex justify-end gap-3">
    <Button
      pill
      size="md"
      class="min-w-30 zat-lime"
      disabled={!selectedDungeon || !connected}
      loading={navigating}
      onclick={handleEnterDungeon}
    >
      {#if navigating}
        进入副本中...
      {:else}
        进入副本
      {/if}
    </Button>
  </div>
</div>
