<script lang="ts">
  import { api } from '$lib/api';
  import { appStore, setConnected, setTaskEngineRunning } from '$lib/stores/appStore';
  
  let connecting = $state(false);
  let startingTaskEngine = $state(false);
  let stoppingTaskEngine = $state(false);
  let startingGame = $state(false);
  
  let connected = $derived($appStore.connected);
  let device = $derived($appStore.device);
  let resolution = $derived($appStore.resolution);
  let taskEngineRunning = $derived($appStore.taskEngineRunning);
  
  let todayTasks = $state(0);
  let todayTime = $state('0h 0m');
  let successRate = $state('0%');
  
  async function handleConnect() {
    connecting = true;
    try {
      const result = await api.connect();
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

<div class="space-y-6 p-2">
  <!-- 欢迎区域 -->
  <div class="cute-card p-6">
    <p class="text-sm text-[var(--color-purple)] font-medium">欢迎回来 ✨</p>
    <h2 class="text-3xl font-bold text-gray-800 mt-1">开始冒险吧！</h2>
  </div>

  <!-- 状态卡片 -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
    <!-- 连接状态 -->
    <div class="cute-card-yellow p-5">
      <div class="flex items-start justify-between relative z-10">
        <div>
          <div class="w-12 h-12 bg-white/80 rounded-2xl flex items-center justify-center text-xl shadow-sm mb-3">
            📱
          </div>
          <p class="text-sm text-gray-700 font-medium mb-1">连接状态</p>
          <div class="flex items-center gap-2">
            <div class="w-2.5 h-2.5 rounded-full {connected ? 'bg-green-600' : 'bg-gray-500'}"></div>
            <span class="text-lg font-bold text-gray-800">
              {connected ? '已连接' : '未连接'}
            </span>
          </div>
          {#if device}
            <p class="text-xs text-gray-600 mt-1">{device}</p>
          {/if}
        </div>
      </div>
      <span class="card-deco text-[var(--color-yellow-dark)]">📱</span>
    </div>
    
    <!-- 今日任务 -->
    <div class="cute-card-cyan p-5">
      <div class="flex items-start justify-between relative z-10">
        <div>
          <div class="w-12 h-12 bg-white/80 rounded-2xl flex items-center justify-center text-xl shadow-sm mb-3">
            🎮
          </div>
          <p class="text-sm text-gray-700 font-medium mb-1">今日任务</p>
          <p class="text-lg font-bold text-gray-800">{todayTasks} 次</p>
          <p class="text-xs text-gray-600 mt-1">运行时长: {todayTime}</p>
        </div>
      </div>
      <span class="card-deco text-[var(--color-cyan-dark)]">🎮</span>
    </div>
      
    <!-- 成功率 -->
    <div class="cute-card-violet p-5">
      <div class="flex items-start justify-between relative z-10">
        <div>
          <div class="w-12 h-12 bg-white/80 rounded-2xl flex items-center justify-center text-xl shadow-sm mb-3">
            📈
          </div>
          <p class="text-sm text-gray-700 font-medium mb-1">成功率</p>
          <p class="text-lg font-bold text-gray-800">{successRate}</p>
          <p class="text-xs text-gray-600 mt-1">最近 24 小时</p>
        </div>
      </div>
      <span class="card-deco text-[var(--color-violet-dark)]">📈</span>
    </div>
  </div>

  <!-- 快速操作 -->
  <div class="cute-card p-6">
    <h3 class="text-lg font-bold text-gray-800 mb-5">快速操作</h3>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <!-- 连接设备 -->
      <button
        class="cute-btn cute-btn-primary flex flex-col items-center gap-2 py-5"
        disabled={connecting}
        onclick={handleConnect}
      >
        {#if connecting}
          <span class="text-2xl animate-spin">⏳</span>
          <span class="text-sm">连接中...</span>
        {:else if connected}
          <span class="text-2xl">🔄</span>
          <span class="text-sm">重新连接</span>
        {:else}
          <span class="text-2xl">📱</span>
          <span class="text-sm">连接设备</span>
        {/if}
      </button>
      
      <!-- 启动游戏 -->
      <button
        class="cute-btn cute-btn-yellow flex flex-col items-center gap-2 py-5"
        disabled={!connected || startingGame}
        onclick={() => handleStartGame(true)}
      >
        {#if startingGame}
          <span class="text-2xl animate-bounce">🎮</span>
          <span class="text-sm">启动中...</span>
        {:else}
          <span class="text-2xl">🎮</span>
          <span class="text-sm">启动游戏</span>
        {/if}
      </button>
      
      <!-- 启动自动化 -->
      <button
        class="cute-btn cute-btn-cyan flex flex-col items-center gap-2 py-5"
        disabled={!connected || startingTaskEngine || taskEngineRunning}
        onclick={handleStartTaskEngine}
      >
        {#if startingTaskEngine}
          <span class="text-2xl animate-pulse">🚀</span>
          <span class="text-sm">启动中...</span>
        {:else if taskEngineRunning}
          <span class="text-2xl">▶️</span>
          <span class="text-sm">运行中</span>
        {:else}
          <span class="text-2xl">🚀</span>
          <span class="text-sm">开始自动化</span>
        {/if}
      </button>
      
      <!-- 停止自动化 -->
      <button
        class="cute-btn flex flex-col items-center gap-2 py-5 bg-[var(--color-pink)] text-gray-700"
        disabled={!taskEngineRunning || stoppingTaskEngine}
        onclick={handleStopTaskEngine}
      >
        {#if stoppingTaskEngine}
          <span class="text-2xl animate-spin">⏳</span>
          <span class="text-sm">停止中...</span>
        {:else}
          <span class="text-2xl">⏹️</span>
          <span class="text-sm">停止</span>
        {/if}
      </button>
    </div>
  </div>

  <!-- 实时日志 -->
  <div class="cute-card p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-bold text-gray-800">实时日志</h3>
      <span class="px-3 py-1 bg-[var(--color-cyan)] text-[#2D5A5A] text-xs font-medium rounded-full">
        运行中
      </span>
    </div>
    <div class="bg-gray-50 rounded-2xl p-4 h-48 overflow-y-auto font-mono text-sm">
      <p class="text-gray-400">暂无日志...</p>
    </div>
  </div>
</div>
