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

  // 评级 badge 样式
  function getRankBadge(rank: string | null) {
    switch (rank) {
      case 'S': return 'bg-yellow-100 text-yellow-600';
      case 'A': return 'bg-green-100 text-green-600';
      case 'B': return 'bg-blue-100 text-blue-600';
      case 'C': return 'bg-gray-100 text-gray-600';
      default: return 'bg-gray-100 text-gray-400';
    }
  }

  // 难度 badge 样式
  function getDifficultyBadge(difficulty: string) {
    switch (difficulty) {
      case '噩梦': return 'bg-red-50 text-red-500';
      case '困难': return 'bg-orange-50 text-orange-500';
      default: return 'bg-gray-50 text-gray-500';
    }
  }
</script>

<div class="mini-card w-full p-5">
  <div class="flex items-center justify-between mb-8"> <h3 class="text-base font-bold text-gray-800">冒险记录</h3>
    <span class="text-xs text-gray-400 bg-gray-50 px-2 py-1 rounded-full">近 {records.length} 条</span>
  </div>

  {#if records.length > 0}
    <div class="flex w-full px-5"> {#each records as record, index}
        {@const isLast = index === records.length - 1}
        
        <div class="relative flex flex-col items-center flex-none">
          
          <div class={`relative z-10 flex items-center justify-center w-7 h-7 rounded-full transition-transform duration-300 ${
            record.status === 'running' ? 'scale-110 bg-orange-50' : 
            record.status === 'failed' ? 'border-2 border-red-100 bg-red-50' :
            'border-2 border-green-100 bg-green-50'
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
            <div class="flex items-center gap-1 mt-1">
              <span class={`text-[10px] px-1.5 py-0.5 rounded font-medium ${getDifficultyBadge(record.difficulty)}`}>
                {record.difficulty}
              </span>
              {#if record.status === 'running'}
                <span class="text-[10px] px-1.5 py-0.5 rounded font-medium bg-orange-100 text-orange-500">进行中</span>
              {:else if record.status === 'failed'}
                <span class="text-[10px] px-1.5 py-0.5 rounded font-medium bg-red-100 text-red-500">失败</span>
              {:else}
                <span class={`text-[10px] px-1.5 py-0.5 rounded font-bold ${getRankBadge(record.rank)}`}>{record.rank}</span>
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