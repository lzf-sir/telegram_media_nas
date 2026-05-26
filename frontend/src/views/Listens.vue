<template>
  <div class="listens-view">
    <div class="listens-header">
      <div class="header-left">
        <h2 class="page-title-section">实时监听</h2>
        <p class="page-subtitle">监听聊天消息并自动下载转发</p>
      </div>
      <el-button type="primary" :icon="Plus" size="large" @click="showAddDialog = true">
        添加监听
      </el-button>
    </div>

    <div class="content-grid">
      <!-- 监听列表 -->
      <div class="listens-content glass-card">
        <el-table :data="subscriptions" v-loading="loading" class="listens-table">
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <span class="status-badge" :class="`status-${row.status}`">
                <span class="status-dot"></span>
                {{ getStatusText(row.status) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="聊天" min-width="180">
            <template #default="{ row }">
              <div class="chat-cell">
                <el-icon><ChatDotRound /></el-icon>
                <span>{{ row.chat_title || row.chat_id }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="统计" width="180">
            <template #default="{ row }">
              <div class="stats-cell">
                <span class="stat-item">
                  <el-icon><Headset /></el-icon>
                  {{ row.total_listened }}
                </span>
                <span class="stat-item">
                  <el-icon><Download /></el-icon>
                  {{ row.total_downloaded }}
                </span>
                <span class="stat-item">
                  <el-icon><Share /></el-icon>
                  {{ row.total_forwarded }}
                </span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button
                v-if="row.status === 'active'"
                type="warning"
                size="small"
                :icon="VideoPause"
                @click="handleStop(row)"
              >
                停止
              </el-button>
              <el-button
                v-else
                type="success"
                size="small"
                :icon="VideoPlay"
                @click="handleStart(row)"
              >
                启动
              </el-button>
              <el-button
                type="danger"
                size="small"
                link
                :icon="Delete"
                @click="handleDelete(row)"
              />
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-section">
        <div class="stat-card glass-card">
          <div class="stat-icon-wrapper" style="background: var(--success-gradient)">
            <el-icon><VideoPlay /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ activeCount }}</div>
            <div class="stat-label">活跃监听</div>
          </div>
        </div>
        <div class="stat-card glass-card">
          <div class="stat-icon-wrapper" style="background: var(--primary-gradient)">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ totalMessages }}</div>
            <div class="stat-label">总消息数</div>
          </div>
        </div>
        <div class="stat-card glass-card">
          <div class="stat-icon-wrapper" style="background: var(--info-gradient)">
            <el-icon><Download /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ totalDownloads }}</div>
            <div class="stat-label">总下载</div>
          </div>
        </div>
        <div class="stat-card glass-card">
          <div class="stat-icon-wrapper" style="background: var(--warning-gradient)">
            <el-icon><Share /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ totalForwards }}</div>
            <div class="stat-label">总转发</div>
          </div>
        </div>
      </div>
    </div>

    <add-listen-dialog v-model="showAddDialog" :accounts="accounts" @confirm="handleAdded" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, VideoPlay, VideoPause, Delete, ChatDotRound, Headset, Download, Share } from '@element-plus/icons-vue'
import { listensApi, type ListenSubscription } from '@/api/listens'
import { accountsApi, type TelegramAccount } from '@/api/accounts'
import { ElMessage, ElMessageBox } from 'element-plus'
import AddListenDialog from '@/components/AddListenDialog.vue'

const loading = ref(false)
const subscriptions = ref<ListenSubscription[]>([])
const accounts = ref<TelegramAccount[]>([])
const showAddDialog = ref(false)

const activeCount = computed(() =>
  subscriptions.value.filter((s) => s.status === 'active').length
)
const totalMessages = computed(() =>
  subscriptions.value.reduce((sum, s) => sum + s.total_listened, 0)
)
const totalDownloads = computed(() =>
  subscriptions.value.reduce((sum, s) => sum + s.total_downloaded, 0)
)
const totalForwards = computed(() =>
  subscriptions.value.reduce((sum, s) => sum + s.total_forwarded, 0)
)

async function fetchSubscriptions() {
  loading.value = true
  try {
    subscriptions.value = await listensApi.listSubscriptions()
  } catch (error) {
    ElMessage.error('加载监听列表失败')
  } finally {
    loading.value = false
  }
}

async function fetchAccounts() {
  try {
    accounts.value = await accountsApi.list()
  } catch (error) {
    ElMessage.error('加载账号列表失败')
  }
}

function getStatusText(status: string): string {
  const texts: Record<string, string> = {
    active: '活跃',
    paused: '已暂停',
    stopped: '已停止',
    error: '错误',
  }
  return texts[status] || status
}

async function handleStart(subscription: ListenSubscription) {
  try {
    await listensApi.start(subscription.id)
    ElMessage.success('监听已启动')
    fetchSubscriptions()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '启动失败')
  }
}

async function handleStop(subscription: ListenSubscription) {
  try {
    await listensApi.stop(subscription.id)
    ElMessage.success('监听已停止')
    fetchSubscriptions()
  } catch (error) {
    ElMessage.error('停止失败')
  }
}

async function handleDelete(subscription: ListenSubscription) {
  try {
    await ElMessageBox.confirm('确定要删除此监听订阅吗？', '确认', { type: 'warning' })
    await listensApi.delete(subscription.id)
    ElMessage.success('已删除')
    fetchSubscriptions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function handleAdded() {
  showAddDialog.value = false
  fetchSubscriptions()
}

onMounted(() => {
  fetchSubscriptions()
  fetchAccounts()
})
</script>

<style scoped>
.listens-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

/* ============================================
   头部样式
   ============================================ */
.listens-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-md);
}

.header-left {
  flex: 1;
}

.page-title-section {
  margin: 0 0 var(--space-xs) 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.page-subtitle {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
}

/* ============================================
   内容网格
   ============================================ */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: var(--space-lg);
}

@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}

/* ============================================
   监听列表
   ============================================ */
.listens-content {
  padding: var(--space-lg);
  min-height: 400px;
}

:deep(.listens-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: transparent;
}

:deep(.listens-table .el-table__body-wrapper) {
  background: transparent;
}

:deep(.listens-table tr) {
  background: transparent !important;
}

:deep(.listens-table th.el-table__cell) {
  background: transparent !important;
  color: var(--text-secondary);
  font-weight: 500;
  border-bottom: 1px solid var(--divider-color);
}

:deep(.listens-table td.el-table__cell) {
  border-bottom: 1px solid var(--divider-color);
}

:deep(.listens-table .el-table__row:hover td.el-table__cell) {
  background: var(--sidebar-item-hover) !important;
}

/* 状态徽章 */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 500;
}

.status-badge .status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-active {
  background: var(--success-bg);
  color: var(--success-color);
}

.status-active .status-dot {
  background: var(--success-color);
  animation: pulse 2s infinite;
}

.status-paused {
  background: var(--warning-bg);
  color: var(--warning-color);
}

.status-paused .status-dot {
  background: var(--warning-color);
}

.status-stopped {
  background: var(--info-bg);
  color: var(--info-color);
}

.status-stopped .status-dot {
  background: var(--info-color);
}

.status-error {
  background: var(--danger-bg);
  color: var(--danger-color);
}

.status-error .status-dot {
  background: var(--danger-color);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 聊天单元格 */
.chat-cell {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  color: var(--text-primary);
}

.chat-cell .el-icon {
  color: var(--text-tertiary);
  font-size: 16px;
}

/* 统计单元格 */
.stats-cell {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-size: 12px;
  color: var(--text-secondary);
}

.stat-item .el-icon {
  font-size: 14px;
}

/* ============================================
   统计卡片区域
   ============================================ */
.stats-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.stat-card {
  padding: var(--space-md);
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  color: #fff;
  font-size: 20px;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
  margin-bottom: var(--space-xs);
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
}

/* ============================================
   响应式设计
   ============================================ */
@media (max-width: 640px) {
  .listens-header {
    flex-direction: column;
    align-items: stretch;
  }

  .page-title-section {
    font-size: 20px;
  }

  .listens-header .el-button {
    width: 100%;
  }
}
</style>
