<template>
  <div class="chats-page">
    <div class="page-hero">
      <div class="hero-left">
        <h2 class="page-title">聊天订阅</h2>
        <p class="page-desc">订阅聊天以自动下载媒体文件</p>
      </div>
      <el-button type="primary" size="large" :icon="Plus" @click="showSubscribe = true">订阅新聊天</el-button>
    </div>

    <div class="chats-content glass-card">
      <el-table :data="subscriptions" v-loading="loading">
        <el-table-column label="聊天" min-width="180">
          <template #default="{ row }">
            <div class="chat-name">
              <div class="chat-type-dot" :class="`type-${row.chat_type}`"></div>
              <span>{{ row.chat_title || row.chat_id }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="ID" width="140">
          <template #default="{ row }"><code class="chat-id">{{ row.chat_id }}</code></template>
        </el-table-column>
        <el-table-column label="类型" width="90">
          <template #default="{ row }">
            <span class="badge badge-info">{{ getChatTypeText(row.chat_type) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <span class="badge" :class="row.is_active ? 'badge-success' : 'badge-warning'">
              <span class="status-dot" :class="row.is_active ? 'status-dot-active' : 'status-dot-inactive'"></span>
              {{ row.is_active ? '启用' : '禁用' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="媒体类型" width="120">
          <template #default="{ row }"><span class="media-types">{{ row.media_types?.join(', ') || '全部' }}</span></template>
        </el-table-column>
        <el-table-column label="已下载" width="80" align="right">
          <template #default="{ row }"><span class="font-mono">{{ row.total_downloaded }}</span></template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" link @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" link type="danger" @click="handleUnsubscribe(row)">取消订阅</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <SubscribeDialog v-model="showSubscribe" @subscribed="fetchSubscriptions" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { chatsApi, type ChatSubscription } from '@/api/chats'
import SubscribeDialog from '@/components/SubscribeDialog.vue'

const loading = ref(false)
const subscriptions = ref<ChatSubscription[]>([])
const showSubscribe = ref(false)

async function fetchSubscriptions() {
  loading.value = true
  try { subscriptions.value = await chatsApi.listSubscriptions() as any }
  catch { ElMessage.error('加载失败') }
  finally { loading.value = false }
}
function getChatTypeText(t: string) { const m: Record<string,string> = { private: '私聊', group: '群组', supergroup: '超级群组', channel: '频道' }; return m[t] || t }
function handleEdit(_s: ChatSubscription) { ElMessage.info('编辑功能即将上线') }
async function handleUnsubscribe(row: ChatSubscription) {
  try {
    await ElMessageBox.confirm(`确认取消订阅 "${row.chat_title || row.chat_id}"？`, '取消订阅', { type: 'warning' })
    await chatsApi.unsubscribe(row.chat_id)
    fetchSubscriptions()
    ElMessage.success('已取消订阅')
  } catch { /* 取消 */ }
}

onMounted(fetchSubscriptions)
</script>

<style scoped>
.chats-page { display: flex; flex-direction: column; gap: var(--space-6); }
.page-hero { display: flex; align-items: flex-start; justify-content: space-between; }
.page-title { font-family: var(--font-heading); font-size: 24px; font-weight: 700; }
.page-desc { color: var(--text-tertiary); margin-top: var(--space-1); }
.chats-content { padding: var(--space-4); }
.chat-name { display: flex; align-items: center; gap: var(--space-2); }
.chat-type-dot { width: 8px; height: 8px; border-radius: 50%; }
.chat-type-dot.type-channel { background: var(--info); }
.chat-type-dot.type-group, .chat-type-dot.type-supergroup { background: var(--success); }
.chat-type-dot.type-private { background: var(--warning); }
.chat-id { font-size: 12px; color: var(--text-tertiary); background: var(--surface-2); padding: 2px 6px; border-radius: var(--radius-xs); }
.media-types { font-size: 12px; color: var(--text-secondary); }
.font-mono { font-family: var(--font-mono); }
</style>
