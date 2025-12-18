<script lang="ts">
  import { api } from '$lib/api';
  import { appStore, setConnected, setTaskEngineRunning } from '$lib/stores/appStore';
  
  let connecting = $state(false);
  let startingTaskEngine = $state(false);
  let stoppingTaskEngine = $state(false);
  let startingGame = $state(false);
  
  let connected = $derived($appStore.connected);
  let device = $derived($appStore.device);
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

<div class="flex-1 overflow-auto px-5 pb-5 space-y-5">
  <!-- 渐变头部 -->
  <div class="gradient-header px-6 pt-6 pb-8 rounded-3xl">
    <p class="text-sm text-gray-700 font-medium mb-1">欢迎回来 👋</p>
    <h2 class="text-3xl font-bold text-gray-900">开始冒险吧！</h2>
  </div>

  <!-- 状态卡片 -->
  <div class="grid grid-cols-2 gap-4">
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
    
    <!-- 成功率 -->
    <div class="mini-card p-4">
      <div class="flex items-center gap-3 mb-3">
        <div class="w-10 h-10 bg-gray-100 rounded-xl flex items-center justify-center text-lg">
          📈
        </div>
        <span class="text-sm font-medium text-gray-600">成功率</span>
      </div>
      <p class="stat-value text-xl">{successRate}</p>
      <p class="text-xs text-gray-500 mt-1">最近 24 小时</p>
      <div class="progress-bar mt-3">
        <div class="progress-fill progress-fill-lime" style="width: 75%"></div>
      </div>
    </div>
  </div>

  <!-- 快速操作 -->
  <div class="clean-card p-5">
    <h3 class="text-base font-bold text-gray-900 mb-4">快速操作</h3>
    <div class="grid grid-cols-2 gap-3">
      <!-- 连接设备 -->
      <button
        class="pill-btn pill-btn-dark flex items-center justify-center gap-2 py-4"
        disabled={connecting}
        onclick={handleConnect}
      >
        {#if connecting}
          <span class="animate-spin">⏳</span>
          <span>连接中...</span>
        {:else if connected}
          <span>✅</span>
          <span>已连接</span>
        {:else}
          <span>📱</span>
          <span>连接设备</span>
        {/if}
      </button>
      
      <!-- 启动游戏 -->
      <button
        class="pill-btn pill-btn-yellow flex items-center justify-center gap-2 py-4"
        disabled={!connected || startingGame}
        onclick={() => handleStartGame(true)}
      >
        {#if startingGame}
          <span class="animate-bounce">🎮</span>
          <span>启动中...</span>
        {:else}
          <span>🎮</span>
          <span>启动游戏</span>
        {/if}
      </button>
      
      <!-- 启动自动化 -->
      <button
        class="pill-btn pill-btn-lime flex items-center justify-center gap-2 py-4"
        disabled={!connected || startingTaskEngine || taskEngineRunning}
        onclick={handleStartTaskEngine}
      >
        {#if startingTaskEngine}
          <span class="animate-pulse">🚀</span>
          <span>启动中...</span>
        {:else if taskEngineRunning}
          <span>▶️</span>
          <span>运行中</span>
        {:else}
          <span>🚀</span>
          <span>开始自动化</span>
        {/if}
      </button>
      
      <!-- 停止自动化 -->
      <button
        class="pill-btn pill-btn-light flex items-center justify-center gap-2 py-4"
        disabled={!taskEngineRunning || stoppingTaskEngine}
        onclick={handleStopTaskEngine}
      >
        {#if stoppingTaskEngine}
          <span class="animate-spin">⏳</span>
          <span>停止中...</span>
        {:else}
          <span>⏹️</span>
          <span>停止</span>
        {/if}
      </button>
    </div>
    
    {#if device}
      <p class="text-xs text-gray-400 mt-3 text-center">{device}</p>
    {/if}
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
