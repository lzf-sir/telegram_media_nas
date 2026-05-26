<template>
  <div class="accounts-view">
    <div class="accounts-header">
      <div class="header-left">
        <h2 class="page-title-section">账号管理</h2>
        <p class="page-subtitle">管理 Telegram 下载账号</p>
      </div>
      <el-button type="primary" :icon="Plus" size="large" @click="showAddDialog = true">
        添加账号
      </el-button>
    </div>

    <div class="accounts-content glass-card">
      <el-table :data="accounts" v-loading="loading" class="accounts-table">
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <span class="status-badge" :class="`status-${row.status}`">
              <span class="status-dot"></span>
              {{ getStatusText(row.status) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="账号信息" min-width="200">
          <template #default="{ row }">
            <div class="account-info">
              <div class="account-avatar">
                <el-icon><User /></el-icon>
              </div>
              <div class="account-details">
                <div class="account-name">{{ row.username || row.first_name || '未设置' }}</div>
                <div class="account-phone">{{ row.phone }}</div>
              </div>
              <el-tag v-if="row.is_default" size="small" class="default-tag">默认</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="上次使用" width="160">
          <template #default="{ row }">
            <span class="last-used">{{ row.last_used_at ? formatDateTime(row.last_used_at) : '从未使用' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="错误信息" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.last_error" class="error-text">{{ row.last_error }}</span>
            <span v-else class="no-error">-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button
                v-if="row.status !== 'active'"
                type="success"
                size="small"
                :icon="VideoPlay"
                @click="handleActivate(row)"
              >
                激活
              </el-button>
              <el-button
                v-else
                type="warning"
                size="small"
                :icon="VideoPause"
                @click="handleDeactivate(row)"
              >
                停用
              </el-button>
              <el-button
                v-if="!row.is_default"
                size="small"
                :icon="Star"
                @click="handleSetDefault(row)"
              >
                设为默认
              </el-button>
              <el-button
                type="danger"
                size="small"
                :icon="Delete"
                link
                @click="handleDelete(row)"
              />
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <add-account-dialog v-model="showAddDialog" @added="handleAccountAdded" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, VideoPlay, VideoPause, Star, Delete, User } from '@element-plus/icons-vue'
import { accountsApi, type TelegramAccount } from '@/api/accounts'
import { formatDateTime } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import AddAccountDialog from '@/components/AddAccountDialog.vue'

const loading = ref(false)
const accounts = ref<TelegramAccount[]>([])
const showAddDialog = ref(false)

async function fetchAccounts() {
  loading.value = true
  try {
    accounts.value = await accountsApi.list()
  } catch (error) {
    ElMessage.error('加载账号列表失败')
  } finally {
    loading.value = false
  }
}

function getStatusText(status: string): string {
  const texts: Record<string, string> = {
    active: '活跃',
    inactive: '未激活',
    banned: '已封禁',
    error: '错误',
  }
  return texts[status] || status
}

async function handleActivate(account: TelegramAccount) {
  try {
    await accountsApi.activate(account.id)
    ElMessage.success('账号激活成功')
    fetchAccounts()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '激活失败')
  }
}

async function handleDeactivate(account: TelegramAccount) {
  try {
    await accountsApi.deactivate(account.id)
    ElMessage.success('账号已停用')
    fetchAccounts()
  } catch (error) {
    ElMessage.error('停用失败')
  }
}

async function handleSetDefault(account: TelegramAccount) {
  try {
    await accountsApi.setDefault(account.id)
    ElMessage.success('已设为默认账号')
    fetchAccounts()
  } catch (error) {
    ElMessage.error('设置失败')
  }
}

async function handleDelete(account: TelegramAccount) {
  try {
    await ElMessageBox.confirm(
      `确定要删除账号 ${account.phone} 吗？这将同时删除该账号的会话文件。`,
      '确认删除',
      { type: 'warning' }
    )
    await accountsApi.delete(account.id)
    ElMessage.success('账号已删除')
    fetchAccounts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function handleAccountAdded() {
  showAddDialog.value = false
  fetchAccounts()
}

onMounted(() => {
  fetchAccounts()
})
</script>

<style scoped>
.accounts-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

/* ============================================
   头部样式
   ============================================ */
.accounts-header {
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
.accounts-content {
  padding: var(--space-lg);
  min-height: 400px;
}

:deep(.accounts-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: transparent;
}

:deep(.accounts-table .el-table__body-wrapper) {
  background: transparent;
}

:deep(.accounts-table tr) {
  background: transparent !important;
}

:deep(.accounts-table th.el-table__cell) {
  background: transparent !important;
  color: var(--text-secondary);
  font-weight: 500;
  border-bottom: 1px solid var(--divider-color);
}

:deep(.accounts-table td.el-table__cell) {
  border-bottom: 1px solid var(--divider-color);
}

:deep(.accounts-table .el-table__row:hover td.el-table__cell) {
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

.status-active {
  background: var(--success-bg);
  color: var(--success-color);
}

.status-active .status-dot {
  background: var(--success-color);
  animation: pulse 2s infinite;
}

.status-inactive {
  background: var(--info-bg);
  color: var(--info-color);
}

.status-inactive .status-dot {
  background: var(--info-color);
}

.status-banned,
.status-error {
  background: var(--danger-bg);
  color: var(--danger-color);
}

.status-banned .status-dot,
.status-error .status-dot {
  background: var(--danger-color);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 账号信息 */
.account-info {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.account-avatar {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-gradient);
  border-radius: var(--radius-md);
  color: #fff;
  font-size: 18px;
  flex-shrink: 0;
}

.account-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.account-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.account-phone {
  font-size: 12px;
  color: var(--text-tertiary);
}

.default-tag {
  background: var(--success-bg);
  color: var(--success-color);
  border: none;
  font-size: 11px;
  padding: 2px 8px;
  height: 20px;
}

/* 上次使用 */
.last-used {
  font-size: 13px;
  color: var(--text-secondary);
}

/* 错误信息 */
.error-text {
  font-size: 13px;
  color: var(--danger-color);
}

.no-error {
  font-size: 13px;
  color: var(--text-tertiary);
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: var(--space-xs);
  flex-wrap: wrap;
}

/* ============================================
   响应式设计
   ============================================ */
@media (max-width: 640px) {
  .accounts-header {
    flex-direction: column;
    align-items: stretch;
  }

  .page-title-section {
    font-size: 20px;
  }

  .accounts-header .el-button {
    width: 100%;
  }
}
</style>
