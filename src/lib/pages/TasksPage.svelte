<script lang="ts">
  import { Button } from 'flowbite-svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import DifficultySelector from '$lib/components/DifficultySelector.svelte';
  import LoopSelector from '$lib/components/LoopSelector.svelte';
  import { appStore, type AppState, type DungeonState } from '$lib/stores/appStore';
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
  let dungeonState = $derived(storeValue?.dungeonState ?? 'idle');
  let dungeonRunning = $derived(storeValue?.dungeonRunning ?? false);
  
  let selectedDungeon = $state<string | null>(null);
  let selectedDifficulties = $state<Record<string, DifficultyId>>({});
  
  // 循环模式状态
  let loopMode = $state('single');
  let loopCount = $state(5);
  
  let currentDifficulty = $derived(
    selectedDungeon ? (selectedDifficulties[selectedDungeon] || 'normal') : 'normal'
  );
  
  // 按钮文字
  const stateLabels: Record<DungeonState, string> = {
    idle: '进入副本',
    navigating: '进入中...',
    matching: '匹配中...',
    battling: '战斗中...',
    finished: '完成',
  };
  
  let buttonLabel = $derived(stateLabels[dungeonState] || '进入副本');
  
  function selectDungeon(id: string) {
    selectedDungeon = selectedDungeon === id ? null : id;
  }
  
  function handleDifficultySelect(dungeonId: string, difficulty: DifficultyId) {
    selectedDifficulties[dungeonId] = difficulty;
  }
  
  // 执行副本
  async function handleStartDungeon() {
    if (!selectedDungeon || !connected || dungeonRunning) return;
    
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
    <div class="pt-4">
      {#key selectedDungeon}
        <DifficultySelector
          dungeonId={selectedDungeon}
          selected={selectedDifficulties[selectedDungeon] || 'normal'}
          onSelect={(diff) => handleDifficultySelect(selectedDungeon!, diff)}
        />
      {/key}
    </div>
    
    <!-- 循环次数选择 -->
    <div>
      <LoopSelector
        mode={loopMode}
        count={loopCount}
        onModeChange={(m) => loopMode = m}
        onCountChange={(c) => loopCount = c}
      />
    </div>
  {/if}

  <!-- 底部操作区 -->
  <div class="mt-auto flex justify-end gap-3">
    <Button
      pill
      size="md"
      class="min-w-30 zat-lime"
      disabled={!selectedDungeon || !connected || dungeonRunning}
      onclick={handleStartDungeon}
    >
      {buttonLabel}
    </Button>
    {#if dungeonRunning}
      <Button
        pill
        color="red"
        class="p-2! w-9 h-9"
        onclick={handleStopDungeon}
      >
        <span class="w-3 h-3 bg-white rounded-sm"></span>
      </Button>
    {/if}
  </div>
</div>
