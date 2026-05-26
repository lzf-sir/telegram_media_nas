<template>
  <div class="chats-view">
    <div class="chats-header">
      <div class="header-left">
        <h2 class="page-title-section">聊天订阅</h2>
        <p class="page-subtitle">订阅聊天以便自动下载媒体文件</p>
      </div>
      <el-button type="primary" :icon="Plus" size="large" @click="showSubscribeDialog = true">
        订阅新聊天
      </el-button>
    </div>

    <div class="chats-content glass-card">
      <el-table :data="subscriptions" v-loading="loading" class="chats-table">
        <el-table-column prop="chat_title" label="聊天名称" min-width="180">
          <template #default="{ row }">
            <div class="chat-name">
              <div class="chat-icon" :class="`type-${row.chat_type}`">
                <el-icon><ChatDotRound /></el-icon>
              </div>
              <span>{{ row.chat_title || row.chat_id }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="chat_id" label="聊天ID" width="140" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <span class="chat-type-badge">{{ getChatTypeText(row.chat_type) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <span class="status-badge" :class="{ active: row.is_active }">
              <span class="status-dot"></span>
              {{ row.is_active ? '启用' : '禁用' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="媒体类型" width="140">
          <template #default="{ row }">
            <span class="media-types">{{ row.media_types?.join(', ') || '全部' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="已下载" width="90">
          <template #default="{ row }">
            <span class="download-count">{{ row.total_downloaded }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" link @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" link type="danger" @click="handleUnsubscribe(row)">
              取消订阅
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <subscribe-dialog v-model="showSubscribeDialog" @subscribed="handleSubscribed" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, ChatDotRound } from '@element-plus/icons-vue'
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
  gap: var(--space-lg);
}

/* ============================================
   头部样式
   ============================================ */
.chats-header {
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
.chats-content {
  padding: var(--space-lg);
  min-height: 400px;
}

:deep(.chats-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: transparent;
}

:deep(.chats-table .el-table__body-wrapper) {
  background: transparent;
}

:deep(.chats-table tr) {
  background: transparent !important;
}

:deep(.chats-table th.el-table__cell) {
  background: transparent !important;
  color: var(--text-secondary);
  font-weight: 500;
  border-bottom: 1px solid var(--divider-color);
}

:deep(.chats-table td.el-table__cell) {
  border-bottom: 1px solid var(--divider-color);
}

:deep(.chats-table .el-table__row:hover td.el-table__cell) {
  background: var(--sidebar-item-hover) !important;
}

/* 聊天名称 */
.chat-name {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.chat-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  font-size: 16px;
}

.chat-icon.type-private {
  background: var(--success-bg);
  color: var(--success-color);
}

.chat-icon.type-group,
.chat-icon.type-supergroup {
  background: var(--primary-bg);
  color: var(--primary-color);
}

.chat-icon.type-channel {
  background: var(--warning-bg);
  color: var(--warning-color);
}

/* 聊天类型徽章 */
.chat-type-badge {
  padding: var(--space-xs) var(--space-sm);
  background: var(--glass-bg);
  border-radius: var(--radius-sm);
  font-size: 12px;
  color: var(--text-secondary);
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
  background: var(--glass-bg);
  color: var(--text-tertiary);
}

.status-badge .status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-tertiary);
}

.status-badge.active {
  background: var(--success-bg);
  color: var(--success-color);
}

.status-badge.active .status-dot {
  background: var(--success-color);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 媒体类型 */
.media-types {
  font-size: 13px;
  color: var(--text-secondary);
}

/* 下载计数 */
.download-count {
  font-weight: 600;
  color: var(--primary-color);
}

/* ============================================
   响应式设计
   ============================================ */
@media (max-width: 640px) {
  .chats-header {
    flex-direction: column;
    align-items: stretch;
  }

  .page-title-section {
    font-size: 20px;
  }

  .chats-header .el-button {
    width: 100%;
  }
}
</style>
