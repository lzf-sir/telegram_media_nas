<template>
  <div class="listens-view">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>实时监听订阅</span>
              <el-button type="primary" :icon="Plus" @click="showAddDialog = true">
                添加监听
              </el-button>
            </div>
          </template>

          <el-table :data="subscriptions" v-loading="loading">
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="聊天" prop="chat_title" min-width="150" />
            <el-table-column label="已监听" width="80">
              <template #default="{ row }">{{ row.total_listened }}</template>
            </el-table-column>
            <el-table-column label="已下载" width="80">
              <template #default="{ row }">{{ row.total_downloaded }}</template>
            </el-table-column>
            <el-table-column label="已转发" width="80">
              <template #default="{ row }">{{ row.total_forwarded }}</template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button
                  v-if="row.status === 'active'"
                  size="small"
                  type="warning"
                  :icon="VideoPause"
                  @click="handleStop(row)"
                >
                  停止
                </el-button>
                <el-button
                  v-else
                  size="small"
                  type="success"
                  :icon="VideoPlay"
                  @click="handleStart(row)"
                >
                  启动
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  :icon="Delete"
                  link
                  @click="handleDelete(row)"
                />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="never">
          <template #header>
            <span>统计概览</span>
          </template>

          <el-descriptions :column="1" border>
            <el-descriptions-item label="活跃监听">
              {{ activeCount }}
            </el-descriptions-item>
            <el-descriptions-item label="总消息数">
              {{ totalMessages }}
            </el-descriptions-item>
            <el-descriptions-item label="总下载">
              {{ totalDownloads }}
            </el-descriptions-item>
            <el-descriptions-item label="总转发">
              {{ totalForwards }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <add-listen-dialog v-model="showAddDialog" @added="handleAdded" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, VideoPlay, VideoPause, Delete } from '@element-plus/icons-vue'
import { listensApi, type ListenSubscription } from '@/api/listens'
import { ElMessage, ElMessageBox } from 'element-plus'
import AddListenDialog from '@/components/AddListenDialog.vue'

const loading = ref(false)
const subscriptions = ref<ListenSubscription[]>([])
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

function getStatusType(status: string): 'success' | 'warning' | 'danger' | 'info' {
  const types: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    active: 'success',
    paused: 'warning',
    stopped: 'info',
    error: 'danger',
  }
  return types[status] || 'info'
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
})
</script>

<style scoped>
.listens-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
