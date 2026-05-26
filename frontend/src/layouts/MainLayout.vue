<template>
  <el-container class="layout">
    <el-aside width="240px">
      <div class="logo">
        <el-icon><Platform /></el-icon>
        <span>Telegram Media NAS</span>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        class="menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <span>仪表板</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><Download /></el-icon>
          <span>下载任务</span>
        </el-menu-item>
        <el-menu-item index="/forwards">
          <el-icon><Share /></el-icon>
          <span>转发任务</span>
        </el-menu-item>
        <el-menu-item index="/listens">
          <el-icon><Bell /></el-icon>
          <span>实时监听</span>
        </el-menu-item>
        <el-menu-item index="/files">
          <el-icon><Files /></el-icon>
          <span>文件管理</span>
        </el-menu-item>
        <el-menu-item index="/chats">
          <el-icon><ChatDotRound /></el-icon>
          <span>聊天订阅</span>
        </el-menu-item>
        <el-menu-item index="/accounts">
          <el-icon><User /></el-icon>
          <span>账号管理</span>
        </el-menu-item>
        <el-menu-item index="/logs">
          <el-icon><Document /></el-icon>
          <span>操作日志</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header>
        <div class="header-left">
          <h2>{{ currentTitle }}</h2>
        </div>
        <div class="header-right">
          <el-badge :value="runningTasksCount" :hidden="runningTasksCount === 0">
            <el-button :icon="Download" circle />
          </el-badge>
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><UserFilled /></el-icon>
              <span>{{ authStore.user?.username || 'Admin' }}</span>
            </span>
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
      </el-header>

      <el-main>
        <router-view v-slot="{ Component }">
          <component :is="Component" />
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Platform, DataBoard, Download, Files, ChatDotRound, Setting,
  Share, Bell, User, Document, UserFilled, SwitchButton
} from '@element-plus/icons-vue'
import { useTaskStore } from '@/stores/task'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const taskStore = useTaskStore()
const authStore = useAuthStore()

const currentTitle = computed(() => route.meta.title as string || '仪表板')
const runningTasksCount = computed(() => taskStore.runningTasks.length)

// 处理下拉菜单命令
async function handleCommand(command: string) {
  if (command === 'logout') {
    await authStore.logout()
    router.push({ name: 'Login' })
  }
}

// Initial load
taskStore.fetchTasks({ limit: 10 })
</script>

<style scoped>
.layout {
  height: 100vh;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px;
  font-size: 16px;
  font-weight: bold;
  color: #409eff;
}

.menu {
  border-right: none;
}

.el-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e4e7ed;
  background: #fff;
}

.header-left h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.el-main {
  background: #f5f7fa;
  padding: 20px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background 0.2s;
}

.user-info:hover {
  background: #f5f7fa;
}
</style>
