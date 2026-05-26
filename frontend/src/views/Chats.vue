<template>
  <div class="chats-view">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>聊天订阅</span>
          <el-button type="primary" :icon="Plus" @click="showSubscribeDialog = true">
            订阅新聊天
          </el-button>
        </div>
      </template>

      <el-table :data="subscriptions" v-loading="loading">
        <el-table-column prop="chat_title" label="聊天名称" min-width="150" />
        <el-table-column prop="chat_id" label="聊天ID" width="150" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">{{ getChatTypeText(row.chat_type) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="媒体类型" width="150">
          <template #default="{ row }">
            {{ row.media_types?.join(', ') || '全部' }}
          </template>
        </el-table-column>
        <el-table-column label="已下载" width="80">
          <template #default="{ row }">{{ row.total_downloaded }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" link @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" link type="danger" @click="handleUnsubscribe(row)">
              取消订阅
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <subscribe-dialog v-model="showSubscribeDialog" @subscribed="handleSubscribed" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { chatsApi, type ChatSubscription } from '@/api/chats'
import { ElMessage, ElMessageBox } from 'element-plus'
import SubscribeDialog from '@/components/SubscribeDialog.vue'

const loading = ref(false)
const subscriptions = ref<ChatSubscription[]>([])
const showSubscribeDialog = ref(false)

async function fetchSubscriptions() {
  loading.value = true
  try {
    subscriptions.value = await chatsApi.listSubscriptions()
  } catch (error) {
    ElMessage.error('加载订阅列表失败')
  } finally {
    loading.value = false
  }
}

function getChatTypeText(type: string): string {
  const types: Record<string, string> = {
    private: '私聊',
    group: '群组',
    supergroup: '超级群组',
    channel: '频道',
  }
  return types[type] || type
}

function handleEdit(subscription: ChatSubscription) {
  // TODO: Implement edit dialog
  ElMessage.info('编辑功能开发中')
}

async function handleUnsubscribe(subscription: ChatSubscription) {
  try {
    await ElMessageBox.confirm(`确定要取消订阅 "${subscription.chat_title}" 吗？`, '确认', {
      type: 'warning',
    })
    await chatsApi.unsubscribe(subscription.chat_id)
    ElMessage.success('取消订阅成功')
    fetchSubscriptions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消订阅失败')
    }
  }
}

function handleSubscribed() {
  showSubscribeDialog.value = false
  fetchSubscriptions()
}

onMounted(() => {
  fetchSubscriptions()
})
</script>

<style scoped>
.chats-view {
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
