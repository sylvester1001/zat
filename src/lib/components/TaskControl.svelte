<script lang="ts">
  import { api } from '$lib/api';
  
  export let connected = false;
  export let device = '';
  
  let connecting = false;
  let starting = false;
  let stopping = false;
  let taskRunning = false;
  
  async function handleConnect() {
    connecting = true;
    try {
      const result = await api.connect();
      if (result.success && result.device) {
        connected = true;
        device = result.device;
        console.log('已连接设备:', device);
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
        console.log('任务已启动');
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
        console.log('任务已停止');
      }
    } catch (error) {
      console.error('停止失败:', error);
      alert('停止失败：' + error);
    } finally {
      stopping = false;
    }
  }
</script>

<div class="card bg-white shadow-lg rounded-lg p-6">
  <h2 class="text-xl font-bold mb-4">任务控制</h2>
  
  <div class="space-y-4">
    <!-- 连接设备 -->
    <div>
      <button
        class="btn btn-primary w-full"
        class:btn-disabled={connecting || connected}
        on:click={handleConnect}
        disabled={connecting || connected}
      >
        {#if connecting}
          连接中...
        {:else if connected}
          已连接: {device}
        {:else}
          连接设备
        {/if}
      </button>
    </div>
    
    <!-- 启动任务 -->
    <div>
      <button
        class="btn btn-success w-full"
        class:btn-disabled={!connected || starting || taskRunning}
        on:click={handleStart}
        disabled={!connected || starting || taskRunning}
      >
        {#if starting}
          启动中...
        {:else if taskRunning}
          任务运行中
        {:else}
          启动任务
        {/if}
      </button>
    </div>
    
    <!-- 停止任务 -->
    <div>
      <button
        class="btn btn-error w-full"
        class:btn-disabled={!taskRunning || stopping}
        on:click={handleStop}
        disabled={!taskRunning || stopping}
      >
        {#if stopping}
          停止中...
        {:else}
          停止任务
        {/if}
      </button>
    </div>
  </div>
</div>

<style>
  .card {
    border: 1px solid #e5e7eb;
  }
  
  .btn {
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    font-weight: 600;
    border: none;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .btn-primary {
    background-color: #3b82f6;
    color: white;
  }
  
  .btn-primary:hover:not(.btn-disabled) {
    background-color: #2563eb;
  }
  
  .btn-success {
    background-color: #10b981;
    color: white;
  }
  
  .btn-success:hover:not(.btn-disabled) {
    background-color: #059669;
  }
  
  .btn-error {
    background-color: #ef4444;
    color: white;
  }
  
  .btn-error:hover:not(.btn-disabled) {
    background-color: #dc2626;
  }
  
  .btn-disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
