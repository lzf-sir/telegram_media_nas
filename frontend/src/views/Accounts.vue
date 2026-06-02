<template>
  <div class="accounts-page">
    <div class="page-hero">
      <div class="hero-left">
        <h2 class="page-title">账号管理</h2>
        <p class="page-desc">管理 Telegram 下载账号</p>
      </div>
      <el-button type="primary" size="large" :icon="Plus" @click="showAdd = true">添加账号</el-button>
    </div>

    <div class="accounts-content glass-card">
      <el-table :data="accounts" v-loading="loading">
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <span class="badge" :class="row.status === 'active' ? 'badge-success' : 'badge-warning'">
              <span :class="row.status === 'active' ? 'status-dot-active' : 'status-dot-inactive'" class="status-dot"></span>
              {{ row.status === 'active' ? '在线' : '离线' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="账号信息" min-width="200">
          <template #default="{ row }">
            <div class="account-info">
              <el-avatar :size="36" style="background: var(--accent-gradient)"><el-icon><User /></el-icon></el-avatar>
              <div>
                <div class="account-name">{{ row.username || row.first_name || '未设置' }}</div>
                <div class="account-phone font-mono">{{ row.phone }}</div>
              </div>
              <el-tag v-if="row.is_default" size="small" type="success">默认</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="上次使用" width="160">
          <template #default="{ row }">{{ row.last_used_at ? formatDateTime(row.last_used_at) : '从未' }}</template>
        </el-table-column>
        <el-table-column label="错误" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.last_error" class="error-text">{{ row.last_error }}</span>
            <span v-else class="no-error">-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status !== 'active'" type="success" size="small" :icon="VideoPlay" @click="activate(row)">激活</el-button>
            <el-button v-else type="warning" size="small" :icon="VideoPause" @click="deactivate(row)">停用</el-button>
            <el-button v-if="!row.is_default" size="small" :icon="Star" @click="setDefault(row)">默认</el-button>
            <el-button type="danger" size="small" :icon="Delete" link @click="handleDelete(row)" />
          </template>
        </el-table-column>
      </el-table>
    </div>

    <AddAccountDialog v-model="showAdd" @added="fetchAccounts" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, VideoPlay, VideoPause, Star, Delete, User } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { accountsApi, type TelegramAccount } from '@/api/accounts'
import { formatDateTime } from '@/utils/format'
import AddAccountDialog from '@/components/AddAccountDialog.vue'

const loading = ref(false)
const accounts = ref<TelegramAccount[]>([])
const showAdd = ref(false)

async function fetchAccounts() {
  loading.value = true
  try { accounts.value = await accountsApi.list() }
  catch { ElMessage.error('加载失败') }
  finally { loading.value = false }
}
async function activate(row: TelegramAccount) {
  try { await accountsApi.activate(row.id); fetchAccounts(); ElMessage.success('已激活') }
  catch { ElMessage.error('激活失败') }
}
async function deactivate(row: TelegramAccount) {
  try { await accountsApi.deactivate(row.id); fetchAccounts(); ElMessage.success('已停用') }
  catch { ElMessage.error('停用失败') }
}
async function setDefault(row: TelegramAccount) {
  try { await accountsApi.setDefault(row.id); fetchAccounts(); ElMessage.success('已设为默认') }
  catch { ElMessage.error('设置失败') }
}
async function handleDelete(row: TelegramAccount) {
  try {
    await ElMessageBox.confirm('确认删除此账号？', '删除确认', { type: 'warning' })
    await accountsApi.delete(row.id)
    fetchAccounts()
    ElMessage.success('已删除')
  } catch { /* 取消 */ }
}

onMounted(fetchAccounts)
</script>

<style scoped>
.accounts-page { display: flex; flex-direction: column; gap: var(--space-6); }
.page-hero { display: flex; align-items: flex-start; justify-content: space-between; }
.page-title { font-family: var(--font-heading); font-size: 24px; font-weight: 700; }
.page-desc { color: var(--text-tertiary); margin-top: var(--space-1); }
.accounts-content { padding: var(--space-4); }
.account-info { display: flex; align-items: center; gap: var(--space-3); }
.account-name { font-weight: 500; }
.account-phone { font-size: 12px; color: var(--text-tertiary); }
.error-text { color: var(--danger); font-size: 12px; }
.no-error { color: var(--text-tertiary); }
.font-mono { font-family: var(--font-mono); }
</style>
