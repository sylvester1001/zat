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

<aside class="w-64 bg-white flex flex-col rounded-2xl shadow-[0_2px_12px_rgba(0,0,0,0.04)]">
  <!-- Logo -->
  <div class="p-5 mb-2">
    <div class="flex items-center gap-3">
      <div class="w-12 h-12 bg-(--color-lime) rounded-2xl flex items-center justify-center text-2xl">
        ⚔️
      </div>
      <div>
        <h1 class="text-xl font-bold text-gray-900">ZAT</h1>
        <p class="text-xs text-gray-500">杖剑传说助手</p>
      </div>
    </div>
  </div>
  
  <!-- Navigation -->
  <nav class="flex-1 px-3 space-y-1">
    {#each navItems as item}
      <button
        onclick={() => currentPage = item.id}
        class="nav-item w-full {isActive(item.id) ? 'active' : ''}"
      >
        <span class="text-xl">{item.icon}</span>
        <span class="font-medium">{item.label}</span>
      </button>
    {/each}
  </nav>
  
  <!-- Footer -->
  <div class="p-4">
    <div class="bg-gray-50 rounded-2xl p-4 text-center">
      <p class="text-xs text-gray-500">版本 0.1.0</p>
    </div>
  </div>
</aside>
