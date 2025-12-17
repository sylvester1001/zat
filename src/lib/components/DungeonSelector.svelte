<script lang="ts">
  import { Card, GradientButton, Select, Label } from 'flowbite-svelte';
  import { api } from '$lib/api';
  import { appStore, type AppState } from '$lib/stores/appStore';
  
  let dungeons = $state<Array<{id: string; name: string; difficulties: string[]}>>([]);
  let selectedDungeon = $state('');
  let selectedDifficulty = $state('normal');
  let navigating = $state(false);
  let loaded = $state(false);
  
  // 订阅 store
  let storeValue = $state<AppState | null>(null);
  $effect(() => {
    const unsubscribe = appStore.subscribe(value => {
      storeValue = value;
    });
    return unsubscribe;
  });
  
  let connected = $derived(storeValue?.connected ?? false);
  
  // 难度显示名称
  const difficultyNames: Record<string, string> = {
    normal: '普通',
    hard: '困难',
    nightmare: '噩梦',
  };
  
  // 加载副本列表
  async function loadDungeons() {
    try {
      const result = await api.getDungeons();
      dungeons = result.dungeons;
      if (dungeons.length > 0 && !selectedDungeon) {
        selectedDungeon = dungeons[0].id;
      }
      loaded = true;
    } catch (error) {
      console.error('加载副本列表失败:', error);
    }
  }
  
  // 获取当前选中副本的难度选项
  let currentDungeonDifficulties = $derived(() => {
    const dungeon = dungeons.find(d => d.id === selectedDungeon);
    return dungeon?.difficulties || ['normal'];
  });
  
  // 导航到副本
  async function handleNavigate() {
    if (!selectedDungeon) return;
    
    navigating = true;
    try {
      const result = await api.navigateToDungeon(selectedDungeon, selectedDifficulty);
      if (result.success) {
        console.log('导航成功');
      } else {
        alert('导航失败: ' + (result.message || '未知错误'));
      }
    } catch (error) {
      console.error('导航失败:', error);
      alert('导航失败: ' + error);
    } finally {
      navigating = false;
    }
  }
  
  // 组件挂载时加载副本列表
  $effect(() => {
    if (!loaded) {
      loadDungeons();
    }
  });
</script>

<Card class="p-4">
  <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">副本选择</h3>
  
  <div class="space-y-4">
    <!-- 副本选择 -->
    <div>
      <Label for="dungeon-select" class="mb-2">选择副本</Label>
      <Select id="dungeon-select" bind:value={selectedDungeon} disabled={!connected || navigating}>
        {#each dungeons as dungeon}
          <option value={dungeon.id}>{dungeon.name}</option>
        {/each}
      </Select>
    </div>
    
    <!-- 难度选择 -->
    <div>
      <Label for="difficulty-select" class="mb-2">选择难度</Label>
      <Select id="difficulty-select" bind:value={selectedDifficulty} disabled={!connected || navigating}>
        {#each currentDungeonDifficulties() as diff}
          <option value={diff}>{difficultyNames[diff] || diff}</option>
        {/each}
      </Select>
    </div>
    
    <!-- 导航按钮 -->
    <GradientButton
      shadow
      color="green"
      class="w-full"
      disabled={!connected || !selectedDungeon || navigating}
      onclick={handleNavigate}
    >
      {#if navigating}
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        导航中...
      {:else}
        进入副本
      {/if}
    </GradientButton>
    
    {#if !connected}
      <p class="text-xs text-gray-500 dark:text-gray-400 text-center">请先连接设备</p>
    {/if}
  </div>
</Card>
