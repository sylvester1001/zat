<script lang="ts">
  import { CheckCircleSolid, CloseCircleSolid, ClockSolid } from 'flowbite-svelte-icons';

  // 时间线记录类型
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

  // 评级颜色
  function getRankColor(rank: string | null) {
    switch (rank) {
      case 'S': return 'text-yellow-500';
      case 'A': return 'text-green-500';
      case 'B': return 'text-blue-500';
      case 'C': return 'text-gray-500';
      default: return 'text-gray-400';
    }
  }
</script>

<div class="clean-card p-5">
  <div class="flex items-center justify-between mb-4">
    <h3 class="text-base font-bold text-gray-900">活动记录</h3>
    <span class="text-xs text-gray-400">最近 {records.length} 条</span>
  </div>
  
  {#if records.length > 0}
    <div class="flex items-start">
      {#each records as record, index}
        {@const isLast = index === records.length - 1}
        <div class="flex-1 flex flex-col items-center">
          <!-- 节点和连接线 -->
          <div class="flex items-center w-full">
            <div class="flex-1 h-0.5 {index === 0 ? 'bg-transparent' : record.status === 'completed' ? 'bg-green-200' : record.status === 'failed' ? 'bg-red-200' : 'bg-orange-200'}"></div>
            <div
              class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full {
                record.status === 'completed' ? 'bg-green-100' :
                record.status === 'failed' ? 'bg-red-100' :
                'bg-orange-100'
              }"
            >
              {#if record.status === 'completed'}
                <CheckCircleSolid class="h-3.5 w-3.5 text-green-500" />
              {:else if record.status === 'failed'}
                <CloseCircleSolid class="h-3.5 w-3.5 text-red-500" />
              {:else}
                <ClockSolid class="h-3.5 w-3.5 text-orange-500 animate-pulse" />
              {/if}
            </div>
            <div class="flex-1 h-0.5 {isLast ? 'bg-transparent' : record.status === 'completed' ? 'bg-green-200' : record.status === 'failed' ? 'bg-red-200' : 'bg-orange-200'}"></div>
          </div>
          <!-- 内容 -->
          <div class="mt-2 text-center">
            <p class="text-xs font-medium text-gray-700">{record.name}</p>
            <p class="text-[10px] text-gray-400">{record.difficulty}</p>
            {#if record.rank}
              <span class="text-sm font-bold {getRankColor(record.rank)}">{record.rank}</span>
            {:else if record.status === 'running'}
              <span class="text-[10px] text-orange-500">进行中</span>
            {:else}
              <span class="text-[10px] text-red-400">失败</span>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {:else}
    <p class="text-center text-gray-400 text-sm py-4">暂无活动记录</p>
  {/if}
</div>
