<script lang="ts">
  import { CheckCircleSolid, CloseCircleSolid, ClockSolid } from 'flowbite-svelte-icons';

  export type TimelineRecord = {
    id: number;
    name: string;
    difficulty: string;
    rank: 'S' | 'A' | 'B' | 'C' | null;
    time: string;
    status: 'completed' | 'failed' | 'running';
  };

  type Props = {
    records: TimelineRecord[];
  };

  let { records }: Props = $props();

  // 状态颜色映射
  const getStatusColor = (status: TimelineRecord['status'], type: 'bg' | 'text' | 'line') => {
    const map = {
      completed: { bg: 'bg-green-100', text: 'text-green-500', line: 'bg-green-400' },
      failed: { bg: 'bg-red-100', text: 'text-red-500', line: 'bg-red-300' },
      running: { bg: 'bg-orange-100', text: 'text-orange-500', line: 'bg-orange-300' }
    };
    return map[status][type];
  };

  function getRankColor(rank: string | null) {
    switch (rank) {
      case 'S': return 'text-yellow-500';
      case 'A': return 'text-green-500';
      case 'B': return 'text-blue-500';
      case 'C': return 'text-gray-500';
      default: return 'text-gray-300';
    }
  }
</script>

<div class="w-full bg-white rounded-xl p-5 shadow-sm border border-gray-100">
  <div class="flex items-center justify-between mb-8"> <h3 class="text-base font-bold text-gray-800">冒险记录</h3>
    <span class="text-xs text-gray-400 bg-gray-50 px-2 py-1 rounded-full">近 {records.length} 条</span>
  </div>

  {#if records.length > 0}
    <div class="flex w-full px-2"> {#each records as record, index}
        {@const isLast = index === records.length - 1}
        
        <div class="relative flex flex-col items-center flex-none">
          
          <div class={`relative z-10 flex items-center justify-center w-7 h-7 rounded-full border-2 transition-transform duration-300 ${
            record.status === 'running' ? 'scale-110 border-orange-400 bg-orange-50' : 
            record.status === 'failed' ? 'border-red-100 bg-red-50' :
            'border-green-100 bg-green-50'
          }`}>
            {#if record.status === 'running'}
              <span class="absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-20 animate-ping"></span>
            {/if}

            {#if record.status === 'completed'}
              <CheckCircleSolid class="w-4 h-4 text-green-500" />
            {:else if record.status === 'failed'}
              <CloseCircleSolid class="w-4 h-4 text-red-500" />
            {:else}
              <ClockSolid class="w-4 h-4 text-orange-500 animate-spin-slow" />
            {/if}
          </div>

          <div class="absolute top-9 left-1/2 -translate-x-1/2 flex flex-col items-center text-center w-32 pointer-events-none">
            <span class="text-xs font-bold text-gray-700 leading-tight truncate w-full px-1">
              {record.name}
            </span>
            <div class="flex items-center gap-1 mt-0.5">
              <span class="text-[10px] text-gray-400">{record.difficulty}</span>
              <span class="text-gray-300 text-[10px]">|</span>
              {#if record.status === 'running'}
                <span class="text-[10px] font-medium text-orange-500">进行中</span>
              {:else if record.status === 'failed'}
                 <span class="text-[10px] font-medium text-red-500">失败</span>
              {:else}
                <span class={`text-[10px] font-bold ${getRankColor(record.rank)}`}>{record.rank}</span>
              {/if}
            </div>
          </div>
        </div>

        {#if !isLast}
          <div class="flex-1 h-[2px] mt-[13px] bg-gray-100 relative mx-[-2px]"> 
            <div class={`h-full transition-all duration-500 ${
               record.status === 'completed' ? 'bg-green-400' : 
               record.status === 'failed' ? 'bg-red-200' : 
               'bg-gray-100'
             }`}></div>
          </div>
        {/if}

      {/each}
    </div>
    
    <div class="h-12"></div>

  {:else}
    <div class="py-8 text-center text-gray-400">
      <p class="text-xs">暂无冒险记录</p>
    </div>
  {/if}
</div>

<style>
  :global(.animate-spin-slow) {
    animation: spin 3s linear infinite;
  }
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
</style>