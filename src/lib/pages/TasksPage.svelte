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
    { id: 'world-tree', name: '世界之树', desc: '魔物隐藏于树荫之下，唯有深入才能将其消灭', color: 'with-bg world-tree-bg' },
    { id: 'mount-mechagod', name: '机神山', desc: '向古老试炼之地发起挑战，只有胜者能获得一切', color: 'with-bg mount-mechagod-bg' },
    { id: 'sea-palace', name: '海之宫遗迹', desc: '原本只存在于传说中的古之宫殿，埋藏着无数珍宝', color: 'with-bg sea-palace-bg' },
    { id: 'mizumoto-shrine', name: '源水大社', desc: '供奉河川神明之所，最深处被强悍的古代构造体守护着', color: 'with-bg mizumoto-shrine-bg' },
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
  <PageHeader title="任务配置" subtitle="选择副本开始 🎮" />

  <!-- 副本选择 -->
  <div class="grid grid-cols-4 gap-4">
    {#each dungeons as dungeon}
      <div class="dungeon-card-wrapper {selectedDungeon === dungeon.id ? 'selected' : ''}">
        <div class="select-badge"></div>
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
          
          <span class="card-title">{dungeon.name}</span>
          <span class="card-desc">{dungeon.desc}</span>
        </button>
      </div>
    {/each}
  </div>

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
