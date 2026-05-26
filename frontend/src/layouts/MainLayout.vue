<template>
  <el-container class="layout">
    <!-- 侧边栏 -->
    <el-aside :width="sidebarWidth" class="sidebar">
      <div class="sidebar-container">
        <!-- Logo -->
        <div class="logo" @click="navigateToDashboard">
          <div class="logo-icon">
            <el-icon><Platform /></el-icon>
          </div>
          <transition name="fade">
            <span v-show="!isCollapsed" class="logo-text">TMN</span>
          </transition>
        </div>

        <!-- 折叠按钮 -->
        <div class="collapse-trigger" @click="toggleCollapse">
          <el-icon :size="18">
            <Expand v-if="isCollapsed" />
            <Fold v-else />
          </el-icon>
        </div>

        <!-- 导航菜单 -->
        <el-menu
          :default-active="$route.path"
          router
          class="menu"
          :collapse="isCollapsed"
          :collapse-transition="false"
        >
          <el-tooltip
            v-for="item in menuItems"
            :key="item.path"
            :content="item.title"
            :disabled="!isCollapsed"
            placement="right"
          >
            <el-menu-item :index="item.path">
              <el-icon>
                <component :is="item.icon" />
              </el-icon>
              <template #title>
                <span>{{ item.title }}</span>
              </template>
            </el-menu-item>
          </el-tooltip>
        </el-menu>

        <!-- 底部信息 -->
        <div class="sidebar-footer">
          <transition name="fade">
            <div v-show="!isCollapsed" class="footer-info">
              <el-text size="small" type="info">v1.0.0</el-text>
            </div>
          </transition>
        </div>
      </div>
    </el-aside>

    <!-- 主内容区 -->
    <el-container class="main-container">
      <!-- 头部 -->
      <el-header class="header">
        <div class="header-left">
          <h2 class="page-title">{{ currentTitle }}</h2>
        </div>
        <div class="header-right">
          <!-- 运行任务徽章 -->
          <el-badge :value="runningTasksCount" :hidden="runningTasksCount === 0" type="primary">
            <div class="header-icon-btn">
              <el-icon :size="20">
                <Download />
              </el-icon>
            </div>
          </el-badge>

          <!-- 主题切换 -->
          <theme-toggle />

          <!-- 用户菜单 -->
          <el-dropdown @command="handleCommand" trigger="click">
            <div class="user-dropdown">
              <div class="user-avatar">
                <el-icon><UserFilled /></el-icon>
              </div>
              <transition name="fade">
                <span v-show="!isCollapsed" class="user-name">{{ authStore.user?.username || 'Admin' }}</span>
              </transition>
              <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu class="user-dropdown-menu">
                <el-dropdown-item command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  <span>退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Platform,
  DataBoard,
  Download,
  Files,
  ChatDotRound,
  Setting,
  Share,
  Bell,
  User,
  Document,
  UserFilled,
  SwitchButton,
  ArrowDown,
  Expand,
  Fold,
} from '@element-plus/icons-vue'
import { useTaskStore } from '@/stores/task'
import { useAuthStore } from '@/stores/auth'
import ThemeToggle from '@/components/ThemeToggle.vue'

const route = useRoute()
const router = useRouter()
const taskStore = useTaskStore()
const authStore = useAuthStore()

// 侧边栏折叠状态
const isCollapsed = ref(false)

// 菜单项配置
const menuItems = [
  { path: '/dashboard', title: '仪表板', icon: DataBoard },
  { path: '/tasks', title: '下载任务', icon: Download },
  { path: '/forwards', title: '转发任务', icon: Share },
  { path: '/listens', title: '实时监听', icon: Bell },
  { path: '/files', title: '文件管理', icon: Files },
  { path: '/chats', title: '聊天订阅', icon: ChatDotRound },
  { path: '/accounts', title: '账号管理', icon: User },
  { path: '/logs', title: '操作日志', icon: Document },
  { path: '/settings', title: '系统设置', icon: Setting },
]

// 当前页面标题
const currentTitle = computed(() => route.meta.title as string || '仪表板')

// 运行中的任务数
const runningTasksCount = computed(() => taskStore.runningTasks.length)

// 侧边栏宽度
const sidebarWidth = computed(() => (isCollapsed.value ? '64px' : '240px'))

// 切换侧边栏折叠状态
function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
}

// 导航到仪表板
function navigateToDashboard() {
  router.push({ name: 'Dashboard' })
}

// 处理用户菜单命令
async function handleCommand(command: string) {
  if (command === 'logout') {
    await authStore.logout()
    router.push({ name: 'Login' })
  }
}

// 初始加载任务数据
onMounted(() => {
  taskStore.fetchTasks({ limit: 10 })
})
</script>

<style scoped>
.layout {
  height: 100vh;
  width: 100%;
}

/* ============================================
   侧边栏样式
   ============================================ */
.sidebar {
  background: var(--sidebar-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border-right: 1px solid var(--sidebar-border);
  transition: width var(--transition-normal);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.sidebar-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: var(--space-md);
}

/* Logo */
.logo {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md);
  margin-bottom: var(--space-md);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.logo:hover {
  background: var(--sidebar-item-hover);
}

.logo-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-gradient);
  border-radius: var(--radius-md);
  color: #fff;
  font-size: 20px;
  flex-shrink: 0;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 折叠按钮 */
.collapse-trigger {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  margin: 0 auto var(--space-md);
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--text-secondary);
  transition: all var(--transition-normal);
}

.collapse-trigger:hover {
  background: var(--sidebar-item-hover);
  color: var(--text-primary);
}

/* 菜单 */
.menu {
  flex: 1;
  border: none;
  overflow-x: hidden;
  overflow-y: auto;
  padding: var(--space-sm);
}

.menu:not(.el-menu--collapse) {
  width: 100%;
}

:deep(.el-menu-item) {
  height: 44px;
  line-height: 44px;
  margin-bottom: var(--space-xs);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
}

:deep(.el-menu-item:hover) {
  background: var(--sidebar-item-hover);
  color: var(--text-primary);
}

:deep(.el-menu-item.is-active) {
  background: var(--sidebar-item-active);
  color: var(--primary-color);
}

:deep(.el-menu-item .el-icon) {
  font-size: 18px;
}

/* 底部信息 */
.sidebar-footer {
  padding-top: var(--space-md);
  border-top: 1px solid var(--divider-color);
}

.footer-info {
  text-align: center;
}

/* ============================================
   主容器样式
   ============================================ */
.main-container {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ============================================
   头部样式
   ============================================ */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--header-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border-bottom: 1px solid var(--header-border);
  padding: 0 var(--space-lg);
  height: 64px;
}

.header-left {
  flex: 1;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.header-icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--text-secondary);
  transition: all var(--transition-normal);
}

.header-icon-btn:hover {
  background: var(--sidebar-item-hover);
  color: var(--text-primary);
}

/* 用户下拉菜单 */
.user-dropdown {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.user-dropdown:hover {
  background: var(--sidebar-item-hover);
}

.user-avatar {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-gradient);
  border-radius: var(--radius-md);
  color: #fff;
  font-size: 16px;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.dropdown-arrow {
  font-size: 12px;
  color: var(--text-tertiary);
  transition: transform var(--transition-normal);
}

.user-dropdown:hover .dropdown-arrow {
  transform: rotate(180deg);
}

/* 用户下拉菜单样式 */
:deep(.user-dropdown-menu) {
  background: var(--glass-bg) !important;
  backdrop-filter: var(--glass-blur) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-lg) !important;
  padding: var(--space-sm);
  min-width: 140px !important;
}

:deep(.user-dropdown-menu .el-dropdown-menu__item) {
  color: var(--text-primary) !important;
  border-radius: var(--radius-md) !important;
  padding: var(--space-sm) var(--space-md) !important;
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

:deep(.user-dropdown-menu .el-dropdown-menu__item:hover) {
  background: var(--sidebar-item-hover) !important;
}

/* ============================================
   主内容区样式
   ============================================ */
.main-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: var(--space-lg);
}

/* ============================================
   过渡动画
   ============================================ */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-normal);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* ============================================
   响应式设计
   ============================================ */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100%;
    z-index: 1000;
  }

  .sidebar.collapsed {
    transform: translateX(-100%);
  }

  .header {
    padding: 0 var(--space-md);
  }

  .page-title {
    font-size: 18px;
  }

  .main-content {
    padding: var(--space-md);
  }
}
</style>
