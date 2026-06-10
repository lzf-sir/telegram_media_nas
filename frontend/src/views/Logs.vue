<template>
  <div class="logs-page">
    <div class="page-hero">
      <div class="hero-left">
        <h2 class="page-title">操作日志</h2>
        <p class="page-desc">系统操作和错误日志</p>
      </div>
    </div>

    <div class="logs-filters glass-card-sm">
      <el-select v-model="filters.level" placeholder="日志级别" clearable style="width:120px" @change="fetchLogs">
        <el-option label="调试" value="debug" />
        <el-option label="信息" value="info" />
        <el-option label="警告" value="warning" />
        <el-option label="错误" value="error" />
      </el-select>
      <el-select v-model="filters.log_type" placeholder="日志类型" clearable style="width:120px" @change="fetchLogs">
        <el-option label="任务" value="task" />
        <el-option label="下载" value="download" />
        <el-option label="转发" value="forward" />
        <el-option label="监听" value="listen" />
        <el-option label="系统" value="system" />
      </el-select>
      <el-button :icon="Refresh" @click="fetchLogs">刷新</el-button>
    </div>

    <div class="logs-content glass-card">
      <el-empty v-if="!loading && logs.length === 0" description="暂无日志记录" :image-size="120" />
      <el-table v-else :data="logs" v-loading="loading">
        <el-table-column label="级别" width="80">
          <template #default="{ row }">
            <span class="badge" :class="`badge-${getLevelBadge(row.level)}`">{{ row.level?.toUpperCase() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="80">
          <template #default="{ row }">
            <span class="badge badge-info">{{ getTypeText(row.log_type) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="消息" min-width="300" show-overflow-tooltip>
          <template #default="{ row }">{{ row.message }}</template>
        </el-table-column>
        <el-table-column label="关联" width="70">
          <template #default="{ row }"><code v-if="row.task_id" class="task-code">{{ row.task_id }}</code><span v-else class="no-data">-</span></template>
        </el-table-column>
        <el-table-column label="时间" width="160">
          <template #default="{ row }">{{ row.created_at ? formatDateTime(row.created_at) : '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button v-if="row.exception_message" size="small" link type="primary" @click="showDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="table-footer" v-if="pagination.total > 0">
        <el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.pageSize" :total="pagination.total" :page-sizes="[20,50,100]" layout="total,sizes,prev,pager,next" @current-change="fetchLogs" @size-change="fetchLogs" />
      </div>
    </div>

    <el-dialog v-model="detailVisible" title="日志详情" width="560px">
      <el-descriptions v-if="currentLog" :column="1" border>
        <el-descriptions-item label="级别"><span class="badge" :class="`badge-${getLevelBadge(currentLog.level)}`">{{ currentLog.level?.toUpperCase() }}</span></el-descriptions-item>
        <el-descriptions-item label="类型">{{ getTypeText(currentLog.log_type) }}</el-descriptions-item>
        <el-descriptions-item label="消息">{{ currentLog.message }}</el-descriptions-item>
        <el-descriptions-item v-if="currentLog.exception_message" label="异常"><pre class="exception-pre">{{ currentLog.exception_message }}</pre></el-descriptions-item>
        <el-descriptions-item v-if="currentLog.stack_trace" label="堆栈"><pre class="stack-pre">{{ currentLog.stack_trace }}</pre></el-descriptions-item>
        <el-descriptions-item label="时间">{{ currentLog.created_at ? formatDateTime(currentLog.created_at) : '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { logsApi, type ActivityLog } from '@/api/logs'
import { formatDateTime, getLogTypeText } from '@/utils/format'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const logs = ref<ActivityLog[]>([])
const detailVisible = ref(false)
const currentLog = ref<ActivityLog | null>(null)
const filters = reactive({ level: '', log_type: '' })
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })

async function fetchLogs() {
  loading.value = true
  try {
    const data = await logsApi.list({
      level: filters.level || undefined,
      log_type: filters.log_type || undefined,
      limit: pagination.pageSize,
      offset: (pagination.page - 1) * pagination.pageSize,
    }) as any
    logs.value = data.logs
    pagination.total = data.total
  } catch { ElMessage.error('加载日志失败') }
  finally { loading.value = false }
}

function getTypeText(t: string) { const m: Record<string,string> = { task:'任务', download:'下载', forward:'转发', listen:'监听', account:'账号', system:'系统' }; return m[t]||t }
function getLevelBadge(l: string) { const m: Record<string,string> = { info:'info', debug:'info', warning:'warning', error:'danger' }; return m[l]||'info' }
function showDetail(log: ActivityLog) { currentLog.value = log; detailVisible.value = true }

onMounted(fetchLogs)
</script>

<style scoped>
.logs-page { display: flex; flex-direction: column; gap: var(--space-4); }
.page-hero { display: flex; align-items: flex-start; justify-content: space-between; }
.page-title { font-family: var(--font-heading); font-size: 24px; font-weight: 700; }
.page-desc { color: var(--text-tertiary); margin-top: var(--space-1); }
.logs-filters { display: flex; gap: var(--space-3); padding: var(--space-4); }
.logs-content { padding: var(--space-4); flex: 1; }
.table-footer { padding: var(--space-4) 0 0; display: flex; justify-content: flex-end; }
.task-code { font-size: 12px; color: var(--text-tertiary); background: var(--surface-2); padding: 2px 6px; border-radius: var(--radius-xs); }
.no-data { color: var(--text-tertiary); }
.exception-pre, .stack-pre {
  font-family: var(--font-mono); font-size: 12px;
  color: var(--danger); max-height: 200px; overflow: auto;
  padding: var(--space-2); background: var(--surface-1); border-radius: var(--radius-sm);
  white-space: pre-wrap; word-break: break-all;
}
</style>
