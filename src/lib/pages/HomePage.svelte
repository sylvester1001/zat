<script lang="ts">
  import { Card, GradientButton, Badge, Indicator } from 'flowbite-svelte';
  import { api } from '$lib/api';
  import { appStore, setConnected, setTaskEngineRunning } from '$lib/stores/appStore';
  import DungeonSelector from '$lib/components/DungeonSelector.svelte';
  
  let connecting = $state(false);
  let startingTaskEngine = $state(false);
  let stoppingTaskEngine = $state(false);
  let startingGame = $state(false);
  
  // 从store获取状态
  let storeValue = $state<import('$lib/stores/appStore').AppState | null>(null);
  
  // 订阅 store
  $effect(() => {
    const unsubscribe = appStore.subscribe(value => {
      storeValue = value;
    });
    return unsubscribe;
  });
  
  let connected = $derived(storeValue?.connected ?? false);
  let device = $derived(storeValue?.device ?? '');
  let resolution = $derived(storeValue?.resolution ?? '');
  let taskEngineRunning = $derived(storeValue?.taskEngineRunning ?? false);
  
  // 状态统计
  let todayTasks = $state(0);
  let todayTime = $state('0h 0m');
  let successRate = $state('0%');
  
  async function handleConnect() {
    connecting = true;
    try {
      const result = await api.connect();
      console.log('连接结果:', result);
      if (result.success && result.device) {
        const resolutionStr = result.resolution 
          ? `${result.resolution.width}x${result.resolution.height}`
          : '';
        console.log('调用 setConnected:', result.device, resolutionStr);
        setConnected(result.device, resolutionStr);
        
        if (result.resolution) {
          if (result.resolution.width !== 720 || result.resolution.height !== 1280) {
            alert(
              `⚠️ 分辨率警告\n\n` +
              `当前分辨率: ${resolutionStr}\n` +
              `推荐分辨率: 720x1280 (竖屏)\n\n` +
              `不同分辨率可能影响图像识别准确性。\n` +
              `建议使用: adb shell wm size 720x1280`
            );
          }
        }
      } else {
        alert('连接失败：未找到设备');
      }
    } catch (error) {
      console.error('连接失败:', error);
      alert('连接失败：' + error);
    } finally {
      connecting = false;
    }
  }
  
  async function handleStartTaskEngine() {
    startingTaskEngine = true;
    try {
      const result = await api.startTaskEngine('farming');
      if (result.success) {
        setTaskEngineRunning(true);
      }
    } catch (error) {
      console.error('启动任务引擎失败:', error);
      alert('启动任务引擎失败：' + error);
    } finally {
      startingTaskEngine = false;
    }
  }
  
  async function handleStopTaskEngine() {
    stoppingTaskEngine = true;
    try {
      const result = await api.stopTaskEngine();
      if (result.success) {
        setTaskEngineRunning(false);
      }
    } catch (error) {
      console.error('停止任务引擎失败:', error);
      alert('停止任务引擎失败：' + error);
    } finally {
      stoppingTaskEngine = false;
    }
  }
  
  async function handleStartGame(waitReady: boolean = false) {
    startingGame = true;
    try {
      const result = await api.startGame(waitReady, 60);
      if (result.success) {
        if (waitReady) {
          if (result.entered) {
            console.log('游戏已启动并进入');
          } else {
            alert('游戏已启动，但等待进入超时。请手动点击进入游戏。');
          }
        } else {
          console.log('游戏已启动:', result.package);
        }
      }
    } catch (error) {
      console.error('启动游戏失败:', error);
      alert('启动游戏失败：' + error);
    } finally {
      startingGame = false;
    }
  }
</script>

<div class="space-y-6">
  <!-- 状态卡片 -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <!-- 连接状态 -->
    <Card class="p-4 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">连接状态</p>
          <div class="flex items-center gap-2">
            <Indicator color={connected ? 'green' : 'gray'} size="lg" />
            <span class="text-2xl font-bold text-gray-900 dark:text-white">
              {connected ? '已连接' : '未连接'}
            </span>
          </div>
          {#if device}
            <p class="text-xs text-gray-400 mt-1">{device}</p>
            {#if resolution}
              <p class="text-xs text-gray-400">分辨率: {resolution}</p>
            {/if}
          {/if}
        </div>
        <div class="text-4xl">📱</div>
      </div>
    </Card>
    
    <!-- 今日任务 -->
    <Card class="p-4 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">今日任务</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">{todayTasks} 次</p>
          <p class="text-xs text-gray-400 mt-1">运行时长: {todayTime}</p>
        </div>
        <div class="text-4xl">🎮</div>
      </div>
    </Card>
    
    <!-- 成功率 -->
    <Card class="p-4 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">成功率</p>
          <p class="text-2xl font-bold text-lime-600 dark:text-lime-400">{successRate}</p>
          <p class="text-xs text-gray-400 mt-1">最近 24 小时</p>
        </div>
        <div class="text-4xl">📈</div>
      </div>
    </Card>
  </div>

  <!-- 快速操作 -->
  <Card size="xl" class="p-4">
    <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">快速操作</h3>
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <!-- 连接设备 -->
      <div class="text-center">
        <GradientButton
          shadow
          color={connected ? 'cyan' : 'blue'}
          size="xl"
          class="w-full mb-2"
          disabled={connecting}
          onclick={handleConnect}
        >
          {#if connecting}
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            连接中...
          {:else if connected}
            🔄 重新连接
          {:else}
            📱 连接设备
          {/if}
        </GradientButton>
        <p class="text-xs text-gray-500 dark:text-gray-400">{connected ? '重新连接设备' : '连接到模拟器'}</p>
      </div>
      
      <!-- 启动游戏 -->
      <div class="text-center">
        <GradientButton
          shadow
          color="purple"
          size="xl"
          class="w-full mb-2"
          disabled={!connected || startingGame}
          onclick={() => handleStartGame(true)}
        >
          {#if startingGame}
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            等待进入...
          {:else}
            🎮 启动游戏
          {/if}
        </GradientButton>
        <p class="text-xs text-gray-500 dark:text-gray-400">启动并自动进入游戏</p>
      </div>
      
      <!-- 启动自动化 -->
      <div class="text-center">
        <GradientButton
          shadow
          color="lime"
          size="xl"
          class="w-full mb-2"
          disabled={!connected || startingTaskEngine || taskEngineRunning}
          onclick={handleStartTaskEngine}
        >
          {#if startingTaskEngine}
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            启动中...
          {:else if taskEngineRunning}
            ▶ 运行中
          {:else}
            🚀 启动自动化
          {/if}
        </GradientButton>
        <p class="text-xs text-gray-500 dark:text-gray-400">开始自动刷图</p>
      </div>
      
      <!-- 停止自动化 -->
      <div class="text-center">
        <GradientButton
          shadow
          color="red"
          size="xl"
          class="w-full mb-2"
          disabled={!taskEngineRunning || stoppingTaskEngine}
          onclick={handleStopTaskEngine}
        >
          {#if stoppingTaskEngine}
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            停止中...
          {:else}
            ⏹ 停止自动化
          {/if}
        </GradientButton>
        <p class="text-xs text-gray-500 dark:text-gray-400">停止自动化任务</p>
      </div>
    </div>
  </Card>

  <!-- 副本选择和实时日志 -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    <!-- 副本选择 -->
    <DungeonSelector />
    
    <!-- 实时日志 -->
    <Card class="p-4">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white">实时日志</h3>
        <Badge color="green">运行中</Badge>
      </div>
      <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 h-48 overflow-y-auto font-mono text-sm">
        <p class="text-gray-400 dark:text-gray-500">暂无日志...</p>
      </div>
    </Card>
  </div>
</div>
