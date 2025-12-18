<script lang="ts">
  import { Button } from 'flowbite-svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import { appStore, type AppState } from '$lib/stores/appStore';
  import { api } from '$lib/api';
  
  // 订阅 store
  let storeValue = $state<AppState | null>(null);
  $effect(() => {
    const unsubscribe = appStore.subscribe(value => {
      storeValue = value;
    });
    return unsubscribe;
  });
  
  let connected = $derived(storeValue?.connected ?? false);
  
  // 副本配置 (ID 需要和后端 scene_graph.py 一致)
  const dungeons = [
    { id: 'world-tree', name: '世界之树', icon: '🌳', color: '' },
    { id: 'mount-mechagod', name: '机神山', icon: '⛰️', color: 'yellow' },
    { id: 'sea-palace', name: '海之宫遗迹', icon: '🏛️', color: 'with-bg sea-palace-bg' },
    { id: 'mizumoto-shrine', name: '源水大社', icon: '⛩️', color: 'white' },
  ];
  
  let selectedDungeon = $state<string | null>(null);
  let navigating = $state(false);
  
  function selectDungeon(id: string) {
    selectedDungeon = selectedDungeon === id ? null : id;
  }
  
  // 导航到副本
  async function handleEnterDungeon() {
    if (!selectedDungeon || !connected) return;
    
    navigating = true;
    try {
      const result = await api.navigateToDungeon(selectedDungeon, 'normal');
      if (result.success) {
        const dungeonName = dungeons.find(d => d.id === selectedDungeon)?.name;
        console.log(`已进入副本: ${dungeonName}`);
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
      </button>
    {/each}
  </div>

  <!-- 底部操作区 -->
  <div class="mt-auto flex justify-end">
    <Button
      pill
      class="px-8 py-4 zat-lime"
      disabled={!selectedDungeon || !connected || navigating}
      onclick={handleEnterDungeon}
    >
      {#if navigating}
        <svg class="animate-spin -ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        进入副本中...
      {:else}
        <span class="mr-2">🚀</span>进入副本
      {/if}
    </Button>
  </div>
</div>
