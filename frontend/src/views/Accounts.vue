<template>
  <div class="accounts-view">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>Telegram 账号管理</span>
          <el-button type="primary" :icon="Plus" @click="showAddDialog = true">
            添加账号
          </el-button>
        </div>
      </template>

      <el-table :data="accounts" v-loading="loading">
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="手机号" prop="phone" width="150" />
        <el-table-column label="用户名" prop="username" width="120">
          <template #default="{ row }">
            {{ row.username || row.first_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="默认" width="60">
          <template #default="{ row }">
            <el-tag v-if="row.is_default" type="success" size="small">默认</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="上次使用" width="160">
          <template #default="{ row }">
            {{ row.last_used_at ? formatDateTime(row.last_used_at) : '从未使用' }}
          </template>
        </el-table-column>
        <el-table-column label="错误信息" prop="last_error" show-overflow-tooltip />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status !== 'active'"
              size="small"
              type="success"
              :icon="VideoPlay"
              @click="handleActivate(row)"
            >
              激活
            </el-button>
            <el-button
              v-else
              size="small"
              type="warning"
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

    <add-account-dialog v-model="showAddDialog" @added="handleAccountAdded" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, VideoPlay, VideoPause, Star, Delete } from '@element-plus/icons-vue'
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

function getStatusType(status: string): 'success' | 'warning' | 'danger' | 'info' {
  const types: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    active: 'success',
    inactive: 'info',
    banned: 'danger',
    error: 'danger',
  }
  return types[status] || 'info'
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
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
