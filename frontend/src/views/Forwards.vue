<template>
  <div class="forwards-view">
    <div class="forwards-header">
      <div class="header-left">
        <h2 class="page-title-section">转发任务</h2>
        <p class="page-subtitle">管理聊天消息转发任务</p>
      </div>
      <el-button type="primary" :icon="Plus" size="large" @click="showCreateDialog = true">
        创建转发任务
      </el-button>
    </div>

    <div class="forwards-content glass-card">
      <el-table :data="tasks" v-loading="loading" class="forwards-table">
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <span class="status-badge" :class="`status-${row.status}`">
              <span class="status-dot"></span>
              {{ getStatusText(row.status) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="源聊天" min-width="180">
          <template #default="{ row }">
            <div class="chat-cell">
              <el-icon><ChatDotRound /></el-icon>
              <span>{{ row.source_chat_title || row.source_chat_id }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="目标聊天" min-width="180">
          <template #default="{ row }">
            <div class="chat-cell">
              <el-icon><ChatLineRound /></el-icon>
              <span>{{ row.destination_chat_title || row.destination_chat_id }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="150">
          <template #default="{ row }">
            <div class="progress-cell">
              <span class="progress-text">{{ row.success_count }} / {{ row.total_count }}</span>
              <span v-if="row.failed_count > 0" class="failed-count">({{ row.failed_count }} 失败)</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="170">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'running' || row.status === 'pending'"
              type="danger"
              size="small"
              link
              :icon="CircleClose"
              @click="handleCancel(row)"
            >
              取消
            </el-button>
            <el-button
              v-else
              type="primary"
              size="small"
              link
              :icon="RefreshRight"
              @click="handleRetry(row)"
            >
              重试
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <create-forward-dialog v-model="showCreateDialog" @created="handleCreated" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, CircleClose, RefreshRight, ChatDotRound, ChatLineRound } from '@element-plus/icons-vue'
import { forwardsApi, type ForwardTask } from '@/api/forwards'
import { formatDateTime } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import CreateForwardDialog from '@/components/CreateForwardDialog.vue'

const loading = ref(false)
const tasks = ref<ForwardTask[]>([])
const showCreateDialog = ref(false)

async function fetchTasks() {
  loading.value = true
  try {
    tasks.value = await forwardsApi.list()
  } catch (error) {
    ElMessage.error('加载转发任务失败')
  } finally {
    loading.value = false
  }
}

function getStatusText(status: string): string {
  const texts: Record<string, string> = {
    completed: '已完成',
    running: '进行中',
    pending: '等待中',
    failed: '失败',
    cancelled: '已取消',
  }
  return texts[status] || status
}

async function handleCancel(task: ForwardTask) {
  try {
    await ElMessageBox.confirm('确定要取消此转发任务吗？', '确认', { type: 'warning' })
    await forwardsApi.cancel(task.id)
    ElMessage.success('任务已取消')
    fetchTasks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消失败')
    }
  }
}

async function handleRetry(task: ForwardTask) {
  try {
    await forwardsApi.create({
      source_chat_id: task.source_chat_id,
      destination_chat_id: task.destination_chat_id,
      source_chat_title: task.source_chat_title || undefined,
      destination_chat_title: task.destination_chat_title || undefined,
      media_types: task.media_types || undefined,
      download_filter: task.download_filter || undefined,
      forward_with_caption: task.forward_with_caption,
      copy_media: task.copy_media,
    })
    ElMessage.success('已创建新任务')
    fetchTasks()
  } catch (error) {
    ElMessage.error('创建任务失败')
  }
}

function handleCreated() {
  showCreateDialog.value = false
  fetchTasks()
}

onMounted(() => {
  fetchTasks()
})
</script>

<style scoped>
.forwards-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

/* ============================================
   头部样式
   ============================================ */
.forwards-header {
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
   内容区域
   ============================================ */
.forwards-content {
  padding: var(--space-lg);
  min-height: 400px;
  overflow-x: auto;
}

/* 表格样式 */
:deep(.forwards-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: transparent;
}

:deep(.forwards-table .el-table__body-wrapper) {
  background: transparent;
}

:deep(.forwards-table tr) {
  background: transparent !important;
}

:deep(.forwards-table th.el-table__cell) {
  background: transparent !important;
  color: var(--text-secondary);
  font-weight: 500;
  border-bottom: 1px solid var(--divider-color);
}

:deep(.forwards-table td.el-table__cell) {
  border-bottom: 1px solid var(--divider-color);
}

:deep(.forwards-table .el-table__row:hover td.el-table__cell) {
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

.status-running {
  background: var(--primary-bg);
  color: var(--primary-color);
}

.status-running .status-dot {
  background: var(--primary-color);
  animation: pulse 2s infinite;
}

.status-completed {
  background: var(--success-bg);
  color: var(--success-color);
}

.status-completed .status-dot {
  background: var(--success-color);
}

.status-failed {
  background: var(--danger-bg);
  color: var(--danger-color);
}

.status-failed .status-dot {
  background: var(--danger-color);
}

.status-pending,
.status-cancelled {
  background: var(--warning-bg);
  color: var(--warning-color);
}

.status-pending .status-dot,
.status-cancelled .status-dot {
  background: var(--warning-color);
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

/* 进度单元格 */
.progress-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.progress-text {
  font-size: 13px;
  color: var(--text-primary);
}

.failed-count {
  font-size: 11px;
  color: var(--danger-color);
}

/* ============================================
   响应式设计
   ============================================ */
@media (max-width: 640px) {
  .forwards-header {
    flex-direction: column;
    align-items: stretch;
  }

  .page-title-section {
    font-size: 20px;
  }

  .forwards-header .el-button {
    width: 100%;
  }
}
</style>
