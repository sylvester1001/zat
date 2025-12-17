<script lang="ts">
  import { Card, GradientButton, Button, Badge, Indicator } from 'flowbite-svelte';
  import { api } from '$lib/api';
  
  let connected = false;
  let device = '';
  let connecting = false;
  let taskRunning = false;
  let starting = false;
  let stopping = false;
  
  // 状态统计
  let todayTasks = 0;
  let todayTime = '0h 0m';
  let successRate = '0%';
  
  async function handleConnect() {
    connecting = true;
    try {
      const result = await api.connect();
      if (result.success && result.device) {
        connected = true;
        device = result.device;
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
  
  async function handleStart() {
    starting = true;
    try {
      const result = await api.start('farming');
      if (result.success) {
        taskRunning = true;
      }
    } catch (error) {
      console.error('启动失败:', error);
      alert('启动失败：' + error);
    } finally {
      starting = false;
    }
  }
  
  async function handleStop() {
    stopping = true;
    try {
      const result = await api.stop();
      if (result.success) {
        taskRunning = false;
      }
    } catch (error) {
      console.error('停止失败:', error);
      alert('停止失败：' + error);
    } finally {
      stopping = false;
    }
  }
</script>

<div class="space-y-6">
  <!-- 状态卡片 -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <!-- 连接状态 -->
    <Card class="hover:shadow-lg transition-shadow">
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
          {/if}
        </div>
        <div class="text-4xl">📱</div>
      </div>
    </Card>
    
    <!-- 今日任务 -->
    <Card class="hover:shadow-lg transition-shadow">
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
    <Card class="hover:shadow-lg transition-shadow">
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
  <Card size="xl">
    <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">快速操作</h3>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- 连接设备 -->
      <div class="text-center">
        <GradientButton
          shadow
          color="blue"
          size="xl"
          class="w-full mb-2"
          disabled={connecting || connected}
          on:click={handleConnect}
        >
          {#if connecting}
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            连接中...
          {:else if connected}
            ✓ 已连接
          {:else}
            📱 连接设备
          {/if}
        </GradientButton>
        <p class="text-xs text-gray-500 dark:text-gray-400">连接到模拟器</p>
      </div>
      
      <!-- 启动任务 -->
      <div class="text-center">
        <GradientButton
          shadow
          color="lime"
          size="xl"
          class="w-full mb-2"
          disabled={!connected || starting || taskRunning}
          on:click={handleStart}
        >
          {#if starting}
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            启动中...
          {:else if taskRunning}
            ▶ 运行中
          {:else}
            🚀 启动任务
          {/if}
        </GradientButton>
        <p class="text-xs text-gray-500 dark:text-gray-400">开始自动刷图</p>
      </div>
      
      <!-- 停止任务 -->
      <div class="text-center">
        <GradientButton
          shadow
          color="red"
          size="xl"
          class="w-full mb-2"
          disabled={!taskRunning || stopping}
          on:click={handleStop}
        >
          {#if stopping}
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            停止中...
          {:else}
            ⏹ 停止任务
          {/if}
        </GradientButton>
        <p class="text-xs text-gray-500 dark:text-gray-400">停止当前任务</p>
      </div>
    </div>
  </Card>
  
  <!-- 实时日志（可折叠） -->
  <Card size="xl">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-bold text-gray-900 dark:text-white">实时日志</h3>
      <Badge color="green">运行中</Badge>
    </div>
    <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 h-48 overflow-y-auto font-mono text-sm">
      <p class="text-gray-400 dark:text-gray-500">暂无日志...</p>
    </div>
  </Card>
</div>
