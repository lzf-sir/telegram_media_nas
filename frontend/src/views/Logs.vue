<template>
  <div class="logs-view">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>操作日志</span>
          <div class="header-actions">
            <el-select v-model="filters.level" placeholder="日志级别" clearable style="width: 120px; margin-right: 10px" @change="fetchLogs">
              <el-option label="全部" value="" />
              <el-option label="调试" value="debug" />
              <el-option label="信息" value="info" />
              <el-option label="警告" value="warning" />
              <el-option label="错误" value="error" />
            </el-select>
            <el-select v-model="filters.log_type" placeholder="日志类型" clearable style="width: 120px; margin-right: 10px" @change="fetchLogs">
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
      </template>

      <el-table :data="logs" v-loading="loading" stripe>
        <el-table-column label="级别" width="80">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)" size="small">
              {{ row.level.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="80">
          <template #default="{ row }">{{ getTypeText(row.log_type) }}</template>
        </el-table-column>
        <el-table-column label="消息" min-width="300" show-overflow-tooltip>
          <template #default="{ row }">{{ row.message }}</template>
        </el-table-column>
        <el-table-column label="关联任务" width="80">
          <template #default="{ row }">{{ row.task_id || '-' }}</template>
        </el-table-column>
        <el-table-column label="时间" width="160">
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

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @current-change="fetchLogs"
        @size-change="fetchLogs"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <el-dialog v-model="detailVisible" title="日志详情" width="600px">
      <div v-if="currentLog" class="log-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="级别">
            <el-tag :type="getLevelType(currentLog.level)">
              {{ currentLog.level.toUpperCase() }}
            </el-tag>
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

function getLevelType(level: string): 'success' | 'warning' | 'danger' | 'info' {
  const types: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    debug: 'info',
    info: 'primary',
    warning: 'warning',
    error: 'danger',
    critical: 'danger',
  }
  return types[level] || 'info'
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
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.log-detail pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
}

.exception-text {
  color: #f56c6c;
}

.stack-trace {
  font-size: 12px;
  color: #909399;
  max-height: 200px;
  overflow-y: auto;
}
</style>
