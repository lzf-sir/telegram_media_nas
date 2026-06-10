<template>
  <div class="dashboard">
    <!-- 问候语 + 统计概览 -->
    <div class="dashboard-hero">
      <div class="hero-greeting">
        <h1 class="hero-title">
          欢迎回来，
          <span class="gradient-text">{{ authStore.user?.username || 'Admin' }}</span>
        </h1>
        <p class="hero-subtitle">{{ greetingText }}</p>
      </div>
      <div class="hero-date">
        <span class="date-text font-mono">{{ today }}</span>
      </div>
    </div>

    <!-- KPI 统计卡片 -->
    <div class="kpi-grid">
      <div class="kpi-card glass-card kpi-accent" @click="$router.push('/tasks')">
        <div class="kpi-icon-box" style="background: var(--accent-gradient)">
          <el-icon :size="24"><Loading /></el-icon>
        </div>
        <div class="kpi-body">
          <span class="kpi-value font-mono">{{ runningCount }}</span>
          <span class="kpi-label">运行中</span>
        </div>
        <div class="kpi-spark">
          <div class="kpi-ring" v-if="runningCount > 0"></div>
        </div>
      </div>

      <div class="kpi-card glass-card kpi-success" @click="$router.push('/tasks')">
        <div class="kpi-icon-box" style="background: var(--success-gradient)">
          <el-icon :size="24"><CircleCheck /></el-icon>
        </div>
        <div class="kpi-body">
          <span class="kpi-value font-mono">{{ completedCount }}</span>
          <span class="kpi-label">已完成</span>
        </div>
      </div>

      <div class="kpi-card glass-card kpi-danger">
        <div class="kpi-icon-box" style="background: var(--danger-gradient)">
          <el-icon :size="24"><CircleClose /></el-icon>
        </div>
        <div class="kpi-body">
          <span class="kpi-value font-mono">{{ failedCount }}</span>
          <span class="kpi-label">失败</span>
        </div>
      </div>

      <div class="kpi-card glass-card kpi-info" @click="$router.push('/files')">
        <div class="kpi-icon-box" style="background: var(--info-gradient)">
          <el-icon :size="24"><Files /></el-icon>
        </div>
        <div class="kpi-body">
          <span class="kpi-value font-mono">{{ fileStats?.total_files ?? '-' }}</span>
          <span class="kpi-label">总文件</span>
        </div>
      </div>

      <div class="kpi-card glass-card kpi-purple">
        <div class="kpi-icon-box" style="background: var(--purple-gradient)">
          <el-icon :size="24"><FolderOpened /></el-icon>
        </div>
        <div class="kpi-body">
          <span class="kpi-value font-mono">{{ formatBytes(fileStats?.total_size ?? 0) }}</span>
          <span class="kpi-label">总大小</span>
        </div>
      </div>
    </div>

    <!-- Bento 网格：任务 + 存储 -->
    <div class="bento-grid">
      <!-- 最近任务 -->
      <section class="bento-card glass-card bento-tasks">
        <div class="card-header">
          <div class="card-header-left">
            <el-icon :size="18"><Download /></el-icon>
            <h3>最近任务</h3>
            <span class="badge badge-accent">{{ recentTasks.length }}</span>
          </div>
          <el-button size="small" text type="primary" @click="$router.push('/tasks')">
            查看全部
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
        <div class="card-body">
          <TaskList
            :tasks="recentTasks"
            :loading="loading"
            @refresh="fetchData"
            @cancel="handleCancel"
            @retry="handleRetry"
          />
        </div>
      </section>

      <!-- 存储概览 -->
      <section class="bento-card glass-card bento-storage">
        <div class="card-header">
          <div class="card-header-left">
            <el-icon :size="18"><PieChart /></el-icon>
            <h3>存储概览</h3>
          </div>
        </div>
        <div class="card-body">
          <div v-if="statsLoading" class="storage-loading">
            <div class="skeleton" style="height: 160px;"></div>
          </div>
          <div v-else class="storage-stats">
            <!-- 媒体类型分布 -->
            <div class="stat-row">
              <span class="stat-dot" style="background: var(--accent)"></span>
              <span class="stat-key">图片</span>
              <span class="stat-val font-mono">{{ fileStats?.by_media_type?.photo?.count ?? 0 }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-dot" style="background: #3B82F6"></span>
              <span class="stat-key">视频</span>
              <span class="stat-val font-mono">{{ fileStats?.by_media_type?.video?.count ?? 0 }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-dot" style="background: #8B5CF6"></span>
              <span class="stat-key">音频</span>
              <span class="stat-val font-mono">{{ fileStats?.by_media_type?.audio?.count ?? 0 }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-dot" style="background: #F59E0B"></span>
              <span class="stat-key">文档</span>
              <span class="stat-val font-mono">{{ fileStats?.by_media_type?.document?.count ?? 0 }}</span>
            </div>
            <div class="divider"></div>
            <div class="stat-row total-row">
              <span class="stat-key">总计</span>
              <span class="stat-val font-mono gradient-text">{{ fileStats?.total_files ?? 0 }} 文件</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 快捷操作 -->
      <section class="bento-card glass-card bento-actions">
        <div class="card-header">
          <div class="card-header-left">
            <el-icon :size="18"><Lightning /></el-icon>
            <h3>快捷操作</h3>
          </div>
        </div>
        <div class="card-body quick-actions">
          <button class="quick-action-btn" @click="$router.push('/tasks')">
            <div class="qa-icon" style="background: var(--accent-gradient)">
              <el-icon><Plus /></el-icon>
            </div>
            <span>新建下载任务</span>
          </button>
          <button class="quick-action-btn" @click="$router.push('/chats')">
            <div class="qa-icon" style="background: var(--info-gradient)">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <span>订阅新聊天</span>
          </button>
          <button class="quick-action-btn" @click="$router.push('/listens')">
            <div class="qa-icon" style="background: var(--purple-gradient)">
              <el-icon><Bell /></el-icon>
            </div>
            <span>添加监听规则</span>
          </button>
          <button class="quick-action-btn" @click="$router.push('/files')">
            <div class="qa-icon" style="background: var(--warning-gradient)">
              <el-icon><Search /></el-icon>
            </div>
            <span>搜索文件</span>
          </button>
          <button class="quick-action-btn" @click="showFavDialog = !showFavDialog">
            <div class="qa-icon" style="background: var(--success-gradient)">
              <el-icon><Star /></el-icon>
            </div>
            <span>{{ favoriteCount > 0 ? `${favoriteCount} 个收藏` : '管理收藏' }}</span>
          </button>
        </div>
      </section>

      <!-- 系统健康 -->
      <section class="bento-card glass-card bento-health">
        <div class="card-header">
          <div class="card-header-left">
            <el-icon :size="18"><Monitor /></el-icon>
            <h3>系统健康</h3>
          </div>
          <el-button size="small" text type="primary" @click="fetchHealth">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
        <div class="card-body">
          <div v-if="healthLoading" class="storage-loading">
            <div class="skeleton" style="height:140px"></div>
          </div>
          <div v-else-if="healthData" class="health-grid">
            <div class="health-item">
              <span class="health-label">磁盘剩余</span>
              <span class="health-value font-mono" :class="{ 'text-danger': healthData.disk?.downloads?.status === 'warning' }">
                {{ healthData.disk?.downloads?.free_gb ?? '--' }} GB
              </span>
            </div>
            <div class="health-item">
              <span class="health-label">下载队列</span>
              <span class="health-value font-mono">{{ healthData.queue?.running ?? 0 }}/{{ healthData.queue?.max_concurrent ?? 5 }}</span>
            </div>
            <div class="health-item">
              <span class="health-label">活跃监听</span>
              <span class="health-value font-mono">{{ healthData.listeners?.active ?? 0 }}</span>
            </div>
            <div class="health-item">
              <span class="health-label">在线账号</span>
              <span class="health-value font-mono">{{ healthData.accounts?.active ?? 0 }}</span>
            </div>
            <div class="health-item">
              <span class="health-label">总文件数</span>
              <span class="health-value font-mono">{{ healthData.storage?.total_files ?? 0 }}</span>
            </div>
            <div class="health-item">
              <span class="health-label">今日完成</span>
              <span class="health-value font-mono">{{ healthData.completed_today ?? 0 }}</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import {
  Loading, CircleCheck, CircleClose, Files, FolderOpened,
  Download, PieChart, Lightning, Plus, ChatDotRound,
  Bell, Search, ArrowRight, Monitor, Refresh, Star,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useTaskStore } from '@/stores/task'
import { tasksApi } from '@/api/tasks'
import { filesApi, type FileStats } from '@/api/files'
import { formatBytes } from '@/utils/format'
import { ElMessage } from 'element-plus'
import TaskList from '@/components/TaskList.vue'
import { useGlobalWebSocket } from '@/composables/useWebSocket'
import { favoritesApi } from '@/api/favorites'

const authStore = useAuthStore()
const taskStore = useTaskStore()

const loading = ref(false)
const statsLoading = ref(false)
const fileStats = ref<FileStats | null>(null)

// 系统健康
interface HealthData {
  disk?: { downloads?: { free_gb: number; status: string } }
  queue?: { running: number; max_concurrent: number }
  listeners?: { active: number }
  accounts?: { active: number }
  storage?: { total_files: number }
  completed_today?: number
}
const healthData = ref<HealthData | null>(null)
const healthLoading = ref(false)

// 收藏
const favoriteCount = ref(0)
const showFavDialog = ref(false)

async function fetchHealth() {
  healthLoading.value = true
  try {
    const res = await fetch('/api/v1/system/health')
    healthData.value = await res.json()
  } catch { /* ignore */ }
  finally { healthLoading.value = false }
}

async function fetchFavorites() {
  try {
    const favs = await favoritesApi.list()
    favoriteCount.value = favs.length
  } catch { /* ignore */ }
}

const runningCount = computed(() => taskStore.runningTasks.length)
const completedCount = computed(() => taskStore.completedTasks.length)
const failedCount = computed(() => taskStore.failedTasks.length)
const recentTasks = computed(() => taskStore.tasks.slice(0, 5))

const today = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 ${['日','一','二','三','四','五','六'][d.getDay()]}`
})

const greetingText = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了，注意休息 🌙'
  if (h < 12) return '早上好，开启高效的一天 ☀️'
  if (h < 18) return '下午好，一切运行正常 🚀'
  return '晚上好，今天辛苦了 ⭐'
})

async function fetchData() {
  loading.value = true
  statsLoading.value = true
  try {
    await Promise.all([
      taskStore.fetchTasks({ limit: 10 }),
      filesApi.getStats().then((d: any) => fileStats.value = d),
      fetchHealth(),
      fetchFavorites(),
    ])
  } finally {
    loading.value = false
    statsLoading.value = false
  }
}

async function handleCancel(id: number) {
  try {
    await tasksApi.cancel(id)
    ElMessage.success('任务已取消')
    fetchData()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '取消失败')
  }
}
async function handleRetry(id: number) {
  try {
    await tasksApi.retry(id)
    ElMessage.success('任务已重新发起')
    fetchData()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '重试失败')
  }
}

// WebSocket 实时更新
const { connected: wsConnected, lastMessage, connect: wsConnect, disconnect: wsDisconnect } = useGlobalWebSocket()

watch(lastMessage, (msg) => {
  if (msg && (msg.type === 'complete' || msg.type === 'progress')) {
    // 任务状态变化时自动刷新数据
    fetchData()
  }
})

onMounted(() => {
  fetchData()
  wsConnect()
})

onUnmounted(() => {
  wsDisconnect()
})
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: var(--space-6); }

/* Hero */
.dashboard-hero {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
}
.hero-title {
  font-family: var(--font-heading);
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
}
.hero-subtitle {
  color: var(--text-tertiary);
  margin-top: var(--space-1);
  font-size: 14px;
}
.date-text {
  color: var(--text-tertiary);
  font-size: 13px;
}
.font-mono { font-family: var(--font-mono); }

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--space-4);
}
.kpi-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}
.kpi-card:hover { transform: translateY(-2px); }
.kpi-icon-box {
  width: 48px; height: 48px;
  border-radius: var(--radius-lg);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  color: white;
}
.kpi-body { display: flex; flex-direction: column; }
.kpi-value { font-size: 28px; font-weight: 700; color: var(--text-primary); line-height: 1; }
.kpi-label { font-size: 12px; color: var(--text-tertiary); margin-top: var(--space-1); }
.kpi-spark { position: absolute; right: 12px; bottom: 12px; }
.kpi-ring {
  width: 12px; height: 12px;
  border-radius: 50%;
  border: 2px solid var(--accent);
  border-top-color: transparent;
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Bento Grid */
.bento-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  grid-template-rows: auto auto;
  gap: var(--space-4);
}

@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}

/* ============================================
   内容区域
   ============================================ */
.content-section {
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
}
.card-header-left {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
.card-header-left h3 {
  font-family: var(--font-heading);
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}
.card-body { flex: 1; min-height: 0; }

/* Storage */
.storage-stats { display: flex; flex-direction: column; gap: var(--space-3); }
.stat-row {
  display: flex; align-items: center; gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
}
.stat-row:hover { background: var(--glass-bg-hover); }
.stat-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.stat-key { color: var(--text-secondary); flex: 1; font-size: 13px; }
.stat-val { color: var(--text-primary); font-size: 14px; font-weight: 600; }
.total-row { background: var(--glass-bg); font-weight: 600; }

/* Quick Actions */
.quick-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
}
.quick-action-btn {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-subtle);
  background: var(--surface-2);
  cursor: pointer;
  color: var(--text-secondary);
  font-family: var(--font-body);
  font-size: 13px;
  transition: all var(--transition-fast);
}
.quick-action-btn:hover {
  border-color: var(--border-accent);
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}
.qa-icon {
  width: 36px; height: 36px;
  border-radius: var(--radius-md);
  display: flex; align-items: center; justify-content: center;
  color: white;
  flex-shrink: 0;
}

/* 响应式 */
@media (max-width: 1024px) {
  .bento-grid { grid-template-columns: 1fr; }
  .bento-tasks { grid-row: auto; }
}
@media (max-width: 640px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}

/* 系统健康 */
.bento-health { grid-row: span 1; }
.health-grid {
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: var(--space-3);
}
.health-item {
  display: flex; flex-direction: column; gap: 2px;
  padding: var(--space-2) var(--space-3);
  background: var(--surface-2); border-radius: var(--radius-md);
}
.health-label { font-size: 12px; color: var(--text-tertiary); }
.health-value { font-size: 18px; font-weight: 700; color: var(--text-primary); }
.text-danger { color: var(--danger) !important; }
</style>
