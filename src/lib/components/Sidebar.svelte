<script lang="ts">
  interface NavItem {
    id: string;
    label: string;
    icon: string;
    path: string;
  }
  
  const navItems: NavItem[] = [
    { id: 'home', label: '首页', icon: '🏠', path: '/' },
    { id: 'tasks', label: '任务', icon: '🎮', path: '/tasks' },
    { id: 'stats', label: '统计', icon: '📊', path: '/stats' },
    { id: 'debug', label: '调试', icon: '🐛', path: '/debug' },
    { id: 'settings', label: '设置', icon: '⚙️', path: '/settings' },
  ];
  
  interface Props {
    currentPage?: string;
  }
  
  let { currentPage = $bindable('home') }: Props = $props();
  
  function isActive(itemId: string) {
    return currentPage === itemId;
  }
</script>

<aside class="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
  <!-- Logo -->
  <div class="p-6 border-b border-gray-200 dark:border-gray-700">
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 bg-gradient-to-br from-lime-400 to-green-500 rounded-xl flex items-center justify-center text-2xl shadow-lg">
        ⚔️
      </div>
      <div>
        <h1 class="text-xl font-bold text-gray-900 dark:text-white">ZAT</h1>
        <p class="text-xs text-gray-500 dark:text-gray-400">杖剑传说助手</p>
      </div>
    </div>
  </div>
  
  <!-- Navigation -->
  <nav class="flex-1 p-4 space-y-2">
    {#each navItems as item}
      <button
        onclick={() => currentPage = item.id}
        class="w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 {
          isActive(item.id)
            ? 'bg-gradient-to-r from-lime-50 to-green-50 dark:from-lime-900/20 dark:to-green-900/20 text-lime-600 dark:text-lime-400 shadow-sm'
            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
        }"
      >
        <span class="text-2xl">{item.icon}</span>
        <span class="font-medium">{item.label}</span>
        {#if isActive(item.id)}
          <div class="ml-auto w-1.5 h-1.5 bg-lime-500 rounded-full"></div>
        {/if}
      </button>
    {/each}
  </nav>
  
  <!-- Footer -->
  <div class="p-4 border-t border-gray-200 dark:border-gray-700">
    <div class="text-xs text-gray-500 dark:text-gray-400 text-center">
      <p>版本 0.1.0</p>
      <p class="mt-1">© 2025 ZAT</p>
    </div>
  </div>
</aside>
