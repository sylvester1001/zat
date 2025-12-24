<script lang="ts">
  import { Badge } from 'flowbite-svelte';
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

  // 评级 badge 颜色
  function getRankColor(rank: string | null): 'yellow' | 'green' | 'blue' | 'gray' {
    switch (rank) {
      case 'S': return 'yellow';
      case 'A': return 'green';
      case 'B': return 'blue';
      default: return 'gray';
    }
  }

  // 难度 badge 颜色
  function getDifficultyColor(difficulty: string): 'green' | 'yellow' | 'red' {
    switch (difficulty) {
      case '噩梦': return 'red';
      case '困难': return 'yellow';
      default: return 'green';
    }
  }
</script>

<div class="mini-card w-full p-5">
  <div class="flex items-center justify-between mb-8">
    <h3 class="text-base font-bold text-gray-800">冒险记录</h3>
    <Badge color="gray" class="text-xs">{records.length} 条</Badge>
  </div>

  {#if records.length > 0}
    <div class="flex w-full px-5">
      {#each records as record, index}
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
              <Badge color={getDifficultyColor(record.difficulty)} class="text-[10px]">{record.difficulty}</Badge>
              {#if record.status === 'running'}
                <Badge color="yellow" class="text-[10px]">进行中</Badge>
              {:else if record.status === 'failed'}
                <Badge color="red" class="text-[10px]">失败</Badge>
              {:else}
                <Badge color={getRankColor(record.rank)} class="text-[10px] font-bold">{record.rank}</Badge>
              {/if}
            </div>
          </div>
        </div>

        {#if !isLast}
          <div class="flex-1 h-0.5 mt-3.25 bg-gray-100 relative -mx-0.5">
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
