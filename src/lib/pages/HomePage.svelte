<script lang="ts">
  import { api } from '$lib/api';
  import { appStore, setConnected, setTaskEngineRunning, type AppState } from '$lib/stores/appStore';
  import { Button } from 'flowbite-svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';

  let connecting = $state(false);
  let startingTaskEngine = $state(false);
  let stoppingTaskEngine = $state(false);
  let startingGame = $state(false);
  
  // 订阅 store
  let storeValue = $state<AppState | null>(null);
  $effect(() => {
    const unsubscribe = appStore.subscribe(value => {
      storeValue = value;
    });
    return unsubscribe;
  });
  
  let connected = $derived(storeValue?.connected ?? false);
  let device = $derived(storeValue?.device ?? '');
  let taskEngineRunning = $derived(storeValue?.taskEngineRunning ?? false);

  let todayTasks = $state(0);
  let todayTime = $state('0h 0m');
  
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

<div class="flex-1 overflow-auto px-5 pb-5 space-y-5">
  <PageHeader title="开始冒险吧！" subtitle="欢迎回来 👋" />

  <!-- 状态卡片 -->
  <div class="grid grid-cols-2 gap-4">
    <!-- 连接状态 -->
    <div class="mini-card p-4 flex flex-col">
      <div class="flex items-center gap-3 mb-3">
        <div class="w-10 h-10 bg-[var(--color-lime)] rounded-xl flex items-center justify-center text-lg">
          📱
        </div>
        <span class="text-sm font-medium text-gray-600">连接状态</span>
      </div>
      <div class="flex items-center gap-2">
        <div class="w-2 h-2 rounded-full {connected ? 'bg-green-500' : 'bg-gray-400'}"></div>
        <p class="stat-value text-xl">{connected ? '已连接' : '未连接'}</p>
      </div>
      {#if device}
        <p class="text-xs text-gray-500 mt-1 truncate">{device}</p>
      {:else}
        <p class="text-xs text-gray-500 mt-1">等待连接设备</p>
      {/if}
      <!-- 连接按钮 -->
      <div class="mt-auto pt-3 flex justify-end">
        <button
          class="connect-btn"
          disabled={connecting}
          onclick={handleConnect}
        >
          <svg class="connect-btn-icon" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
            <path d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zm50.7-186.9L162.4 380.6c-19.4 7.5-38.5-11.6-31-31l55.5-144.3c3.3-8.5 9.9-15.1 18.4-18.4l144.3-55.5c19.4-7.5 38.5 11.6 31 31L325.1 306.7c-3.2 8.5-9.9 15.1-18.4 18.4zM288 256a32 32 0 1 0 -64 0 32 32 0 1 0 64 0z"></path>
          </svg>
          {#if connecting}
            连接中...
          {:else if connected}
            重新连接
          {:else}
            连接设备
          {/if}
        </button>
      </div>
    </div>
    
    <!-- 今日任务 -->
    <div class="mini-card p-4">
      <div class="flex items-center gap-3 mb-3">
        <div class="w-10 h-10 bg-[var(--color-yellow)] rounded-xl flex items-center justify-center text-lg">
          🎮
        </div>
        <span class="text-sm font-medium text-gray-600">今日任务</span>
      </div>
      <p class="stat-value text-xl">{todayTasks} 次</p>
      <p class="text-xs text-gray-500 mt-1">运行时长: {todayTime}</p>
      <div class="flex gap-2 mt-3">
        <span class="tag tag-lime">进行中</span>
      </div>
    </div>
  </div>

  <!-- 快速操作 -->
  <div class="clean-card p-5">
    <h3 class="text-base font-bold text-gray-900 mb-4">快速操作</h3>
    <div class="grid grid-cols-3 gap-3">
      <!-- 启动游戏 -->
      <button
        class="play-btn"
        disabled={!connected || startingGame}
        onclick={() => handleStartGame(true)}
      >
        <img src="/assets/sword.png" alt="" class="play-btn-img" />
        <span class="now-text">Now!</span>
        <span class="play-text">启动游戏</span>
      </button>
      
      <!-- 启动自动化 -->
      <Button
        pill
        class="py-4 zat-lime"
        disabled={!connected || startingTaskEngine || taskEngineRunning}
        onclick={handleStartTaskEngine}
      >
        {#if startingTaskEngine}
          <span class="animate-pulse mr-2">🚀</span>启动中...
        {:else if taskEngineRunning}
          <span class="mr-2">▶️</span>运行中
        {:else}
          <span class="mr-2">🚀</span>开始自动化
        {/if}
      </Button>
      
      <!-- 停止自动化 -->
      <Button
        pill
        class="py-4 zat-light"
        disabled={!taskEngineRunning || stoppingTaskEngine}
        onclick={handleStopTaskEngine}
      >
        {#if stoppingTaskEngine}
          <span class="animate-spin mr-2">⏳</span>停止中...
        {:else}
          <span class="mr-2">⏹️</span>停止
        {/if}
      </Button>
    </div>
  </div>

  <!-- 实时日志 -->
  <div class="clean-card p-5">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-base font-bold text-gray-900">实时日志</h3>
      <span class="tag tag-lime">运行中</span>
    </div>
    <div class="bg-gray-50 rounded-2xl p-4 h-40 overflow-y-auto font-mono text-sm">
      <p class="text-gray-400">暂无日志...</p>
    </div>
  </div>
</div>
