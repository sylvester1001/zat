<script lang="ts">
  import { api } from '$lib/api';
  import { appStore, setConnected, setGameRunning, type AppState } from '$lib/stores/appStore';
  import PageHeader from '$lib/components/PageHeader.svelte';

  let connecting = $state(false);
  let startingGame = $state(false);
  let stoppingGame = $state(false);
  
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
  let gameRunning = $derived(storeValue?.gameRunning ?? false);

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
  
  async function handleStartGame() {
    startingGame = true;
    try {
      const result = await api.startGame(true, 60);
      if (result.success) {
        setGameRunning(true);
        if (result.entered) {
          console.log('游戏已启动并进入');
        } else {
          alert('游戏已启动，但等待进入超时。请手动点击进入游戏。');
        }
      }
    } catch (error) {
      console.error('启动游戏失败:', error);
      alert('启动游戏失败：' + error);
    } finally {
      startingGame = false;
    }
  }
  
  async function handleStopGame() {
    stoppingGame = true;
    try {
      const result = await api.stopGame();
      if (result.success) {
        setGameRunning(false);
        console.log('游戏已停止');
      }
    } catch (error) {
      console.error('停止游戏失败:', error);
      alert('停止游戏失败：' + error);
    } finally {
      stoppingGame = false;
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
    <div class="flex gap-3">
      <!-- 启动游戏 -->
      <button
        class="play-btn flex-1"
        disabled={!connected || startingGame || gameRunning}
        onclick={handleStartGame}
      >
        <img src="/assets/sword-border.png" alt="" class="play-btn-img" />
        <span class="now-text">Now!</span>
        <span class="play-text">
          {#if startingGame}
            启动中...
          {:else if gameRunning}
            游戏运行中
          {:else}
            启动游戏
          {/if}
        </span>
      </button>
      
      <!-- 停止游戏 -->
      <button
        class="stop-btn"
        disabled={!gameRunning || stoppingGame}
        onclick={handleStopGame}
      >
        {#if stoppingGame}
          <span class="animate-spin">⏳</span>
        {:else}
          <span>⏹️</span>
        {/if}
        <span>停止游戏</span>
      </button>
    </div>
  </div>

  <!-- 实时日志 -->
  <div class="clean-card p-5">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-base font-bold text-gray-900">实时日志</h3>
      <span class="tag {gameRunning ? 'tag-lime' : 'tag-gray'}">{gameRunning ? '运行中' : '已停止'}</span>
    </div>
    <div class="bg-gray-50 rounded-2xl p-4 h-40 overflow-y-auto font-mono text-sm">
      <p class="text-gray-400">暂无日志...</p>
    </div>
  </div>
</div>

<style>
  .stop-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 1rem 1.5rem;
    background: var(--color-gray-100);
    border: 2px solid transparent;
    border-radius: 1rem;
    font-weight: 600;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s ease;
    color: var(--color-gray-700);
  }
  
  .stop-btn:hover:not(:disabled) {
    background: #fee2e2;
    border-color: #ef4444;
    color: #ef4444;
  }
  
  .stop-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
  
  .tag-gray {
    background: var(--color-gray-100);
    color: var(--color-gray-600);
  }
</style>
