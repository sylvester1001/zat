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
  let selectedDifficulties = $state<Record<string, DifficultyId>>({});
  let running = $state(false);
  
  let currentDifficulty = $derived(
    selectedDungeon ? (selectedDifficulties[selectedDungeon] || 'normal') : 'normal'
  );
  
  function selectDungeon(id: string) {
    selectedDungeon = selectedDungeon === id ? null : id;
  }
  
  function handleDifficultySelect(dungeonId: string, difficulty: DifficultyId) {
    selectedDifficulties[dungeonId] = difficulty;
  }
  
  // 执行副本
  async function handleStartDungeon() {
    if (!selectedDungeon || !connected) return;
    
    running = true;
    try {
      const result = await api.runDungeon(selectedDungeon, currentDifficulty);
      if (result.success) {
        const dungeonName = DUNGEONS.find(d => d.id === selectedDungeon)?.name;
        console.log(`副本完成: ${dungeonName} (${currentDifficulty}) - 评级: ${result.rank}`);
      } else {
        console.warn('副本执行失败: ' + (result.message || '未知错误'));
      }
    } catch (error) {
      console.error('副本执行失败:', error);
    } finally {
      running = false;
    }
  }
  
  // 中断副本
  async function handleStopDungeon() {
    try {
      await api.stopDungeon();
      console.log('已发送中断请求');
    } catch (error) {
      console.error('中断失败:', error);
    }
    running = false;
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
      {#key selectedDungeon}
        <DifficultySelector
          dungeonId={selectedDungeon}
          selected={selectedDifficulties[selectedDungeon] || 'normal'}
          onSelect={(diff) => handleDifficultySelect(selectedDungeon!, diff)}
        />
      {/key}
    </div>
  {/if}

  <!-- 底部操作区 -->
  <div class="mt-auto flex justify-end gap-3">
    {#if running}
      <Button
        pill
        size="md"
        color="red"
        class="min-w-30"
        onclick={handleStopDungeon}
      >
        中断
      </Button>
    {:else}
      <Button
        pill
        size="md"
        class="min-w-30 zat-lime"
        disabled={!selectedDungeon || !connected}
        onclick={handleStartDungeon}
      >
        进入副本
      </Button>
    {/if}
  </div>
</div>
