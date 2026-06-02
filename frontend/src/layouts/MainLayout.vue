<template>
  <div class="app-layout">
    <!-- 悬浮胶囊侧边栏 -->
    <nav class="sidebar-capsule" :class="{ collapsed: isCollapsed }">
      <!-- Logo -->
      <div class="sidebar-logo" @click="$router.push('/dashboard')">
        <div class="logo-mark">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <rect width="28" height="28" rx="8" fill="url(#logo-grad)"/>
            <path d="M7 14L12 19L21 9" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <defs>
              <linearGradient id="logo-grad" x1="0" y1="0" x2="28" y2="28">
                <stop stop-color="#22C55E"/>
                <stop offset="1" stop-color="#22D3BB"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        <transition name="fade">
          <span v-show="!isCollapsed" class="logo-text gradient-text">TMN</span>
        </transition>
      </div>

      <!-- 导航菜单 — 胶囊式 -->
      <div class="nav-list">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item) }"
          :title="item.label"
        >
          <div class="nav-icon-box">
            <el-icon :size="20"><component :is="item.icon" /></el-icon>
          </div>
          <transition name="fade">
            <span v-show="!isCollapsed" class="nav-label">{{ item.label }}</span>
          </transition>
          <!-- 活跃指示器 -->
          <div v-if="isActive(item)" class="nav-indicator"></div>
        </router-link>
      </div>

      <!-- 可展开分组 — 系统管理 -->
      <div class="nav-group">
        <button
          class="nav-group-trigger"
          :class="{ expanded: sysExpanded }"
          @click="sysExpanded = !sysExpanded"
          :title="isCollapsed ? '系统管理' : undefined"
        >
          <div class="nav-icon-box">
            <el-icon :size="20"><Setting /></el-icon>
          </div>
          <transition name="fade">
            <span v-show="!isCollapsed" class="nav-label">系统管理</span>
          </transition>
          <transition name="fade">
            <el-icon v-show="!isCollapsed" class="nav-chevron" :class="{ rotated: sysExpanded }">
              <ArrowDown />
            </el-icon>
          </transition>
        </button>
        <transition name="collapse">
          <div v-show="sysExpanded && !isCollapsed" class="nav-sub-list">
            <router-link
              v-for="sub in sysNavItems"
              :key="sub.path"
              :to="sub.path"
              class="nav-sub-item"
              :class="{ active: $route.path.startsWith(sub.path) }"
            >
              <el-icon :size="16"><component :is="sub.icon" /></el-icon>
              <span>{{ sub.label }}</span>
            </router-link>
          </div>
        </transition>
      </div>

      <!-- 底部：折叠 + 用户 -->
      <div class="sidebar-bottom">
        <!-- 折叠按钮 -->
        <button class="nav-item collapse-btn" @click="toggleCollapse" title="折叠侧边栏">
          <div class="nav-icon-box">
            <el-icon :size="20">
              <Fold v-if="!isCollapsed" />
              <Expand v-else />
            </el-icon>
          </div>
        </button>

        <!-- 用户信息 -->
        <div class="user-mini" @click="showUserMenu = !showUserMenu">
          <el-avatar :size="32" style="background: var(--accent-gradient);">
            <el-icon><UserFilled /></el-icon>
          </el-avatar>
          <transition name="fade">
            <div v-show="!isCollapsed" class="user-detail">
              <span class="user-name truncate">{{ authStore.user?.username || 'Admin' }}</span>
              <span class="user-role">管理员</span>
            </div>
          </transition>
          <!-- 用户下拉 -->
          <transition name="pop">
            <div v-if="showUserMenu && isCollapsed" class="user-popup glass-card" @click.stop>
              <div class="popup-header">{{ authStore.user?.username }}</div>
              <button class="popup-item" @click="handleLogout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </button>
            </div>
          </transition>
        </div>
      </div>
    </nav>

    <!-- 主内容区 -->
    <div class="main-area">
      <!-- 顶部栏 -->
      <header class="topbar glass-card-sm">
        <!-- 面包屑 -->
        <div class="topbar-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">
              <el-icon><DataBoard /></el-icon>
              <span>Home</span>
            </el-breadcrumb-item>
            <el-breadcrumb-item v-if="pageTitle !== '仪表板'">
              {{ pageTitle }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <!-- 顶部操作区 -->
        <div class="topbar-right">
          <!-- 全局搜索 -->
          <div class="global-search" @click="showSearch = true">
            <el-icon><Search /></el-icon>
            <span class="search-hint">⌘K</span>
          </div>

          <!-- 运行任务指示器 -->
          <el-badge :value="runningCount" :hidden="!runningCount" class="running-badge">
            <div class="header-icon-btn" @click="$router.push('/tasks')" title="运行中的任务">
              <el-icon :size="20"><Download /></el-icon>
            </div>
          </el-badge>

          <!-- 主题切换 -->
          <ThemeToggle />

          <!-- 用户下拉（展开模式） -->
          <el-dropdown v-if="!isCollapsed" trigger="click" @command="handleUserCommand">
            <div class="user-dropdown-trigger">
              <el-avatar :size="32" style="background: var(--accent-gradient);">
                <el-icon><UserFilled /></el-icon>
              </el-avatar>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 内容区 -->
      <main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>

    <!-- 命令面板 -->
    <teleport to="body">
      <transition name="pop">
        <div v-if="showSearch" class="command-overlay" @click.self="showSearch = false">
          <div class="command-palette glass-card">
            <div class="command-input-wrapper">
              <el-icon class="command-icon"><Search /></el-icon>
              <input
                ref="commandInput"
                v-model="searchQuery"
                class="command-input"
                placeholder="输入命令搜索..."
                @keydown.escape="showSearch = false"
                @keydown.enter="executeCommand"
              />
              <kbd class="command-kbd">ESC</kbd>
            </div>
            <div class="command-results">
              <button
                v-for="cmd in filteredCommands"
                :key="cmd.label"
                class="command-item"
                @click="executeNav(cmd)"
              >
                <el-icon :size="16"><component :is="cmd.icon" /></el-icon>
                <span>{{ cmd.label }}</span>
                <kbd>{{ cmd.shortcut }}</kbd>
              </button>
            </div>
          </div>
        </div>
      </transition>
    </teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  DataBoard, Download, Files, ChatDotRound, Share,
  Bell, User, Document, Setting, Search,
  UserFilled, SwitchButton, ArrowDown, Expand, Fold,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useTaskStore } from '@/stores/task'
import ThemeToggle from '@/components/ThemeToggle.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const taskStore = useTaskStore()

// 侧边栏折叠
const isCollapsed = ref(false)
const sysExpanded = ref(false)
const showUserMenu = ref(false)

// 命令面板
const showSearch = ref(false)
const searchQuery = ref('')
const commandInput = ref<HTMLInputElement>()

// 主导航
const navItems = [
  { path: '/dashboard', label: '仪表板', icon: DataBoard },
  { path: '/tasks', label: '下载任务', icon: Download },
  { path: '/files', label: '文件管理', icon: Files },
  { path: '/chats', label: '聊天订阅', icon: ChatDotRound },
  { path: '/forwards', label: '转发任务', icon: Share },
  { path: '/listens', label: '实时监听', icon: Bell },
]

// 系统管理导航
const sysNavItems = [
  { path: '/accounts', label: '账号管理', icon: User },
  { path: '/logs', label: '操作日志', icon: Document },
  { path: '/settings', label: '系统设置', icon: Setting },
]

// 命令列表
const commands = [
  ...navItems,
  ...sysNavItems,
].map(item => ({
  ...item,
  shortcut: item.path.slice(1).charAt(0).toUpperCase(),
}))

const filteredCommands = computed(() => {
  if (!searchQuery.value) return commands
  const q = searchQuery.value.toLowerCase()
  return commands.filter(c => c.label.toLowerCase().includes(q))
})

const pageTitle = computed(() => (route.meta.title as string) || '仪表板')
const runningCount = computed(() => taskStore.runningTasks.length)

function isActive(item: { path: string }) {
  if (item.path === '/dashboard') return route.path === '/dashboard'
  return route.path.startsWith(item.path)
}

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
  if (isCollapsed.value) sysExpanded.value = false
}

async function handleLogout() {
  showUserMenu.value = false
  await authStore.logout()
  router.push('/login')
}

function handleUserCommand(cmd: string) {
  if (cmd === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}

function executeNav(cmd: typeof commands[0]) {
  showSearch.value = false
  searchQuery.value = ''
  router.push(cmd.path)
}

function executeCommand() {
  if (filteredCommands.value.length > 0) {
    executeNav(filteredCommands.value[0])
  }
}

// 快捷键
function handleKeydown(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    showSearch.value = !showSearch.value
    if (showSearch.value) {
      nextTick(() => commandInput.value?.focus())
    }
  }
  if (e.key === 'Escape') showSearch.value = false
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  taskStore.fetchTasks({ limit: 10 })
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
/* ============================================
   布局容器
   ============================================ */
.app-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

/* ============================================
   悬浮胶囊侧边栏
   ============================================ */
.sidebar-capsule {
  position: relative;
  z-index: var(--z-sticky);
  display: flex;
  flex-direction: column;
  width: 240px;
  flex-shrink: 0;
  padding: var(--space-4);
  padding-top: var(--space-6);
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border-right: 1px solid var(--border-subtle);
  transition: width var(--transition-slow);
  gap: var(--space-2);
}
.sidebar-capsule.collapsed {
  width: 72px;
  padding: var(--space-3) var(--space-2);
}

/* Logo */
.sidebar-logo {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  margin-bottom: var(--space-4);
  cursor: pointer;
  user-select: none;
}
.logo-mark {
  flex-shrink: 0;
}
.logo-text {
  font-family: var(--font-heading);
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 2px;
}

/* 导航列表 */
.nav-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  flex: 1;
  overflow-y: auto;
}

/* 导航项 */
.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  border-radius: var(--radius-lg);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all var(--transition-fast);
  cursor: pointer;
  border: none;
  background: none;
  width: 100%;
  font-family: var(--font-body);
  font-size: 14px;
  overflow: hidden;
}
.nav-item:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}
.nav-item.active {
  background: var(--glass-bg-active);
  color: var(--accent);
}
.nav-icon-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  flex-shrink: 0;
  transition: all var(--transition-fast);
}
.nav-item.active .nav-icon-box {
  background: var(--success-soft);
}
.nav-indicator {
  position: absolute;
  right: 8px;
  width: 3px;
  height: 20px;
  border-radius: var(--radius-full);
  background: var(--accent);
  box-shadow: var(--shadow-glow-sm);
}
.nav-label {
  white-space: nowrap;
  font-weight: 500;
}

/* 导航分组 */
.nav-group {
  border-top: 1px solid var(--border-subtle);
  padding-top: var(--space-2);
  margin-top: auto;
}
.nav-group-trigger {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  border-radius: var(--radius-lg);
  color: var(--text-tertiary);
  background: none;
  border: none;
  cursor: pointer;
  width: 100%;
  font-family: var(--font-body);
  font-size: 13px;
  transition: all var(--transition-fast);
}
.nav-group-trigger:hover {
  color: var(--text-primary);
  background: var(--glass-bg-hover);
}
.nav-chevron {
  margin-left: auto;
  transition: transform var(--transition-normal);
}
.nav-chevron.rotated {
  transform: rotate(180deg);
}

/* 子导航 */
.nav-sub-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-1) 0 var(--space-1) var(--space-8);
}
.nav-sub-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  color: var(--text-tertiary);
  text-decoration: none;
  font-size: 13px;
  transition: all var(--transition-fast);
}
.nav-sub-item:hover {
  color: var(--text-primary);
  background: var(--glass-bg-hover);
}
.nav-sub-item.active {
  color: var(--accent);
  background: var(--glass-bg-active);
}

/* 底部区 */
.sidebar-bottom {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  border-top: 1px solid var(--border-subtle);
  padding-top: var(--space-2);
}
.collapse-btn {
  justify-content: center;
  color: var(--text-tertiary);
}
.collapse-btn:hover {
  color: var(--text-primary);
}
.user-mini {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-lg);
  cursor: pointer;
  position: relative;
  transition: all var(--transition-fast);
}
.user-mini:hover {
  background: var(--glass-bg-hover);
}
.user-detail {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.user-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}
.user-role {
  font-size: 11px;
  color: var(--text-tertiary);
}
.user-popup {
  position: absolute;
  left: calc(100% + 12px);
  bottom: 0;
  width: 180px;
  padding: var(--space-2);
  z-index: var(--z-dropdown);
}
.popup-header {
  padding: var(--space-2) var(--space-3);
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-subtle);
  margin-bottom: var(--space-1);
}
.popup-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  width: 100%;
  padding: var(--space-2) var(--space-3);
  border: none;
  background: none;
  color: var(--danger);
  cursor: pointer;
  border-radius: var(--radius-md);
  font-size: 13px;
  transition: background var(--transition-fast);
}
.popup-item:hover {
  background: var(--danger-soft);
}

/* 折叠过渡 */
.collapse-enter-active { transition: all var(--transition-normal); overflow: hidden; }
.collapse-leave-active { transition: all var(--transition-fast); overflow: hidden; }
.collapse-enter-from, .collapse-leave-to { opacity: 0; max-height: 0; }

/* ============================================
   主内容区
   ============================================ */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

/* ── 顶部栏 ── */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-6);
  margin: var(--space-4);
  margin-bottom: 0;
  z-index: var(--z-sticky);
  min-height: 52px;
}
.topbar-left {
  display: flex;
  align-items: center;
}
.topbar-right {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

/* 全局搜索 */
.global-search {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all var(--transition-fast);
  color: var(--text-tertiary);
}
.global-search:hover {
  border-color: var(--border-accent);
  color: var(--text-secondary);
}
.search-hint {
  font-family: var(--font-mono);
  font-size: 11px;
  padding: 1px 6px;
  background: var(--surface-2);
  border-radius: var(--radius-xs);
  color: var(--text-tertiary);
}

/* 运行徽章 */
.running-badge :deep(.el-badge__content) {
  background: var(--accent) !important;
}

/* Header 图标按钮 */
.header-icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  color: var(--text-secondary);
}
.header-icon-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}

/* 用户下拉 */
.user-dropdown-trigger {
  cursor: pointer;
  transition: transform var(--transition-fast);
}
.user-dropdown-trigger:hover {
  transform: scale(1.05);
}

/* ── 主内容 ── */
.main-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: var(--space-4) var(--space-6) var(--space-6);
  scroll-behavior: smooth;
}

/* ============================================
   命令面板
   ============================================ */
.command-overlay {
  position: fixed;
  inset: 0;
  z-index: var(--z-modal);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 15vh;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}
.command-palette {
  width: 520px;
  max-width: 90vw;
  padding: var(--space-2);
  border-radius: var(--radius-2xl);
}
.command-input-wrapper {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
}
.command-icon {
  color: var(--text-tertiary);
  flex-shrink: 0;
}
.command-input {
  flex: 1;
  border: none;
  background: none;
  outline: none;
  font-size: 16px;
  color: var(--text-primary);
  font-family: var(--font-body);
}
.command-input::placeholder {
  color: var(--text-tertiary);
}
.command-kbd {
  font-family: var(--font-mono);
  font-size: 11px;
  padding: 2px 8px;
  background: var(--surface-2);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xs);
  color: var(--text-tertiary);
}
.command-results {
  padding: var(--space-2);
  max-height: 320px;
  overflow-y: auto;
}
.command-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
  padding: var(--space-3) var(--space-4);
  border: none;
  background: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 14px;
  font-family: var(--font-body);
  transition: all var(--transition-fast);
}
.command-item:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}
.command-item kbd {
  margin-left: auto;
}

/* 响应式 */
@media (max-width: 768px) {
  .sidebar-capsule {
    width: 72px;
    padding: var(--space-3) var(--space-2);
  }
  .sidebar-capsule .nav-label,
  .sidebar-capsule .logo-text,
  .sidebar-capsule .user-detail,
  .sidebar-capsule .nav-chevron,
  .sidebar-capsule .nav-sub-list { display: none !important; }
  .topbar {
    margin: var(--space-2);
  }
  .main-content {
    padding: var(--space-3) var(--space-4) var(--space-4);
  }
}
</style>
