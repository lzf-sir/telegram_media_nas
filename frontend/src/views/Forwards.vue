<template>
  <div class="forwards-page">
    <div class="page-hero">
      <div class="hero-left">
        <h2 class="page-title">转发任务</h2>
        <p class="page-desc">管理聊天消息自动转发</p>
      </div>
      <el-button type="primary" size="large" :icon="Plus" @click="showCreate = true">创建转发任务</el-button>
    </div>

    <div class="forwards-content glass-card">
      <el-table :data="tasks" v-loading="loading">
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <span class="badge" :class="`badge-${getStatusBadge(row.status)}`">
              <span class="status-dot" :class="`status-dot-${row.status === 'running' ? 'active' : 'inactive'}`"></span>
              {{ getStatusText(row.status) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="源聊天" min-width="180">
          <template #default="{ row }">
            <div class="chat-cell"><el-icon><ChatDotRound /></el-icon><span>{{ row.source_chat_title || row.source_chat_id }}</span></div>
          </template>
        </el-table-column>
        <el-table-column label="目标聊天" min-width="180">
          <template #default="{ row }">
            <div class="chat-cell"><el-icon><ChatLineRound /></el-icon><span>{{ row.destination_chat_title || row.destination_chat_id }}</span></div>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="160">
          <template #default="{ row }">
            <span class="font-mono">{{ row.success_count }}/{{ row.total_count }}</span>
            <span v-if="row.failed_count" class="fail-count">({{ row.failed_count }} 失败)</span>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="160">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'running'" type="danger" size="small" link :icon="CircleClose" @click="handleCancel(row)">取消</el-button>
            <el-button v-else type="primary" size="small" link :icon="RefreshRight" @click="handleRetry(row)">重试</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <CreateForwardDialog v-model="showCreate" @created="onCreated" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, CircleClose, RefreshRight, ChatDotRound, ChatLineRound } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { forwardsApi, type ForwardTask } from '@/api/forwards'
import { formatDateTime } from '@/utils/format'
import CreateForwardDialog from '@/components/CreateForwardDialog.vue'

const loading = ref(false)
const tasks = ref<ForwardTask[]>([])
const showCreate = ref(false)

async function fetchTasks() {
  loading.value = true
  try { tasks.value = await forwardsApi.list() as any }
  catch { ElMessage.error('加载失败') }
  finally { loading.value = false }
}
function onCreated() { showCreate.value = false; fetchTasks(); ElMessage.success('创建成功') }
async function handleCancel(row: ForwardTask) {
  try {
    await ElMessageBox.confirm('确认取消此转发任务？', '取消确认', { type: 'warning' })
    await forwardsApi.cancel(row.id)
    fetchTasks()
    ElMessage.success('已取消')
  } catch { /* 取消 */ }
}
async function handleRetry(row: ForwardTask) {
  try {
    await ElMessageBox.confirm('确认重试此转发任务？', '重试确认', { type: 'info' })
    await forwardsApi.retry(row.id)
    fetchTasks()
    ElMessage.success('已重试')
  } catch { /* 取消 */ }
}
function getStatusText(s: string) { const m: Record<string,string> = { running: '运行中', pending: '等待中', completed: '已完成', failed: '失败' }; return m[s] || s }
function getStatusBadge(s: string) { const m: Record<string,string> = { running: 'success', completed: 'info', failed: 'danger', pending: 'warning' }; return m[s] || 'info' }

onMounted(fetchTasks)
</script>

<style scoped>
.forwards-page { display: flex; flex-direction: column; gap: var(--space-6); }
.page-hero { display: flex; align-items: flex-start; justify-content: space-between; }
.page-title { font-family: var(--font-heading); font-size: 24px; font-weight: 700; }
.page-desc { color: var(--text-tertiary); margin-top: var(--space-1); }
.forwards-content { padding: var(--space-4); }
.chat-cell { display: flex; align-items: center; gap: var(--space-2); }
.fail-count { color: var(--danger); font-size: 12px; }
.font-mono { font-family: var(--font-mono); }
</style>
