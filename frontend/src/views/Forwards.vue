<template>
  <div class="forwards-view">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>转发任务</span>
          <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
            创建转发任务
          </el-button>
        </div>
      </template>

      <el-table :data="tasks" v-loading="loading">
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="源聊天" min-width="150">
          <template #default="{ row }">
            {{ row.source_chat_title || row.source_chat_id }}
          </template>
        </el-table-column>
        <el-table-column label="→" width="30" align="center">
          <template #default><el-icon><Right /></el-icon></template>
        </el-table-column>
        <el-table-column label="目标聊天" min-width="150">
          <template #default="{ row }">
            {{ row.destination_chat_title || row.destination_chat_id }}
          </template>
        </el-table-column>
        <el-table-column label="进度" width="150">
          <template #default="{ row }">
            {{ row.success_count }} / {{ row.total_count }}
            <span v-if="row.failed_count > 0" class="failed-text">
              ({{ row.failed_count }} 失败)
            </span>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="160">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
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
              重新执行
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <create-forward-dialog v-model="showCreateDialog" @created="handleCreated" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Right, CircleClose, RefreshRight } from '@element-plus/icons-vue'
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

function getStatusType(status: string): 'success' | 'warning' | 'danger' | 'info' {
  const types: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    completed: 'success',
    running: 'primary',
    pending: 'info',
    failed: 'danger',
    cancelled: 'warning',
  }
  return types[status] || 'info'
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
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.failed-text {
  color: #f56c6c;
}
</style>
