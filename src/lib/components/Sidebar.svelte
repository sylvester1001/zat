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

<aside class="w-72 bg-white/80 backdrop-blur-sm flex flex-col rounded-r-[32px] shadow-lg shadow-purple-100/50">
  <!-- Logo -->
  <div class="p-6 mb-2">
    <div class="flex items-center gap-4">
      <div class="w-14 h-14 bg-gradient-to-br from-[var(--color-yellow)] to-[var(--color-mint)] rounded-2xl flex items-center justify-center text-3xl shadow-lg">
        ⚔️
      </div>
      <div>
        <h1 class="text-2xl font-bold text-gray-800">ZAT</h1>
        <p class="text-sm text-[var(--color-purple)]">杖剑传说助手</p>
      </div>
    </div>
  </div>
  
  <!-- Navigation -->
  <nav class="flex-1 px-4 space-y-2">
    {#each navItems as item}
      <button
        onclick={() => currentPage = item.id}
        class="w-full flex items-center gap-4 px-5 py-4 rounded-2xl transition-all duration-300 {
          isActive(item.id)
            ? 'cute-card-yellow shadow-md'
            : 'hover:bg-[var(--color-lavender-light)] text-gray-600'
        }"
      >
        <span class="text-2xl">{item.icon}</span>
        <span class="font-semibold {isActive(item.id) ? 'text-gray-800' : ''}">{item.label}</span>
        {#if isActive(item.id)}
          <div class="ml-auto">
            <div class="w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-sm">
              <span class="text-[var(--color-purple)]">→</span>
            </div>
          </div>
        {/if}
      </button>
    {/each}
  </nav>
  
  <!-- Footer -->
  <div class="p-6">
    <div class="cute-card-purple p-4 text-center">
      <p class="text-sm font-medium text-[var(--color-purple-dark)]">版本 0.1.0</p>
      <p class="text-xs text-gray-500 mt-1">© 2025 ZAT</p>
    </div>
  </div>
</aside>
