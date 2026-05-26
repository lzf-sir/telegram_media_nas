<template>
  <div class="logs-view">
    <div class="logs-header">
      <div class="header-left">
        <h2 class="page-title-section">操作日志</h2>
        <p class="page-subtitle">查看系统操作和错误日志</p>
      </div>
      <div class="header-actions">
        <el-select v-model="filters.level" placeholder="日志级别" clearable class="filter-select" @change="fetchLogs">
          <el-option label="全部" value="" />
          <el-option label="调试" value="debug" />
          <el-option label="信息" value="info" />
          <el-option label="警告" value="warning" />
          <el-option label="错误" value="error" />
        </el-select>
        <el-select v-model="filters.log_type" placeholder="日志类型" clearable class="filter-select" @change="fetchLogs">
          <el-option label="全部" value="" />
          <el-option label="任务" value="task" />
          <el-option label="下载" value="download" />
          <el-option label="转发" value="forward" />
          <el-option label="监听" value="listen" />
          <el-option label="系统" value="system" />
        </el-select>
        <el-button :icon="Refresh" @click="fetchLogs">刷新</el-button>
      </div>
    </div>

    <div class="logs-content glass-card">
      <el-table :data="logs" v-loading="loading" class="logs-table">
        <el-table-column label="级别" width="80">
          <template #default="{ row }">
            <span class="level-badge" :class="`level-${row.level}`">
              {{ row.level.toUpperCase() }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="80">
          <template #default="{ row }">
            <span class="type-badge">{{ getTypeText(row.log_type) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="消息" min-width="300" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="log-message">{{ row.message }}</span>
          </template>
        </el-table-column>
        <el-table-column label="关联任务" width="80">
          <template #default="{ row }">
            <span class="task-id">{{ row.task_id || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="时间" width="170">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button
              v-if="row.exception_message"
              type="primary"
              size="small"
              link
              @click="showDetail(row)"
            >
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @current-change="fetchLogs"
          @size-change="fetchLogs"
        />
      </div>
    </div>

    <el-dialog v-model="detailVisible" title="日志详情" width="600px" class="log-detail-dialog">
      <div v-if="currentLog" class="log-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="级别">
            <span class="level-badge" :class="`level-${currentLog.level}`">
              {{ currentLog.level.toUpperCase() }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="类型">
            {{ getTypeText(currentLog.log_type) }}
          </el-descriptions-item>
          <el-descriptions-item label="消息">
            {{ currentLog.message }}
          </el-descriptions-item>
          <el-descriptions-item v-if="currentLog.exception_type" label="异常类型">
            {{ currentLog.exception_type }}
          </el-descriptions-item>
          <el-descriptions-item v-if="currentLog.exception_message" label="异常信息">
            <pre class="exception-text">{{ currentLog.exception_message }}</pre>
          </el-descriptions-item>
          <el-descriptions-item v-if="currentLog.stack_trace" label="堆栈跟踪">
            <pre class="stack-trace">{{ currentLog.stack_trace }}</pre>
          </el-descriptions-item>
          <el-descriptions-item label="时间">
            {{ formatDateTime(currentLog.created_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { logsApi, type ActivityLog } from '@/api/logs'
import { formatDateTime } from '@/utils/format'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const logs = ref<ActivityLog[]>([])
const detailVisible = ref(false)
const currentLog = ref<ActivityLog | null>(null)

const filters = reactive({
  level: '',
  log_type: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

async function fetchLogs() {
  loading.value = true
  try {
    const response = await logsApi.list({
      level: filters.level || undefined,
      log_type: filters.log_type || undefined,
      limit: pagination.pageSize,
      offset: (pagination.page - 1) * pagination.pageSize,
    })
    logs.value = response.logs
    pagination.total = response.total
  } catch (error) {
    ElMessage.error('加载日志失败')
  } finally {
    loading.value = false
  }
}

function getTypeText(type: string): string {
  const texts: Record<string, string> = {
    task: '任务',
    download: '下载',
    forward: '转发',
    listen: '监听',
    account: '账号',
    system: '系统',
  }
  return texts[type] || type
}

function showDetail(log: ActivityLog) {
  currentLog.value = log
  detailVisible.value = true
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.logs-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

/* ============================================
   头部样式
   ============================================ */
.logs-header {
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

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  flex-wrap: wrap;
}

.filter-select {
  width: 120px;
}

/* ============================================
   内容区域
   ============================================ */
.logs-content {
  padding: var(--space-lg);
  min-height: 400px;
}

:deep(.logs-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: transparent;
}

:deep(.logs-table .el-table__body-wrapper) {
  background: transparent;
}

:deep(.logs-table tr) {
  background: transparent !important;
}

:deep(.logs-table th.el-table__cell) {
  background: transparent !important;
  color: var(--text-secondary);
  font-weight: 500;
  border-bottom: 1px solid var(--divider-color);
}

:deep(.logs-table td.el-table__cell) {
  border-bottom: 1px solid var(--divider-color);
}

:deep(.logs-table .el-table__row:hover td.el-table__cell) {
  background: var(--sidebar-item-hover) !important;
}

/* 日志级别徽章 */
.level-badge {
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-sm);
  font-size: 11px;
  font-weight: 600;
}

.level-debug {
  background: var(--info-bg);
  color: var(--info-color);
}

.level-info {
  background: var(--primary-bg);
  color: var(--primary-color);
}

.level-warning {
  background: var(--warning-bg);
  color: var(--warning-color);
}

.level-error,
.level-critical {
  background: var(--danger-bg);
  color: var(--danger-color);
}

/* 类型徽章 */
.type-badge {
  padding: var(--space-xs) var(--space-sm);
  background: var(--glass-bg);
  border-radius: var(--radius-sm);
  font-size: 12px;
  color: var(--text-secondary);
}

/* 日志消息 */
.log-message {
  font-size: 13px;
  color: var(--text-primary);
}

/* 任务ID */
.task-id {
  font-family: monospace;
  font-size: 12px;
  color: var(--text-tertiary);
}

/* 分页 */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--space-lg);
  padding-top: var(--space-md);
  border-top: 1px solid var(--divider-color);
}

/* 详情对话框 */
.log-detail pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
}

.exception-text {
  color: var(--danger-color);
}

.stack-trace {
  font-size: 12px;
  color: var(--text-secondary);
  max-height: 200px;
  overflow-y: auto;
}

:deep(.log-detail-dialog) {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
}

/* ============================================
   响应式设计
   ============================================ */
@media (max-width: 640px) {
  .logs-header {
    flex-direction: column;
    align-items: stretch;
  }

  .page-title-section {
    font-size: 20px;
  }

  .header-actions {
    flex-direction: column;
    width: 100%;
  }

  .filter-select {
    width: 100%;
  }
}
</style>
