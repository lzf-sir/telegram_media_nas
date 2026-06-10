<template>
  <div class="listens-page">
    <div class="page-hero">
      <div class="hero-left">
        <h2 class="page-title">实时监听</h2>
        <p class="page-desc">监听聊天消息并自动下载/转发</p>
      </div>
      <el-button type="primary" size="large" :icon="Plus" @click="showAdd = true">添加监听</el-button>
    </div>

    <div class="listens-stats">
      <div class="mini-stat glass-card-sm">
        <el-icon :size="20" color="var(--success)"><VideoPlay /></el-icon>
        <span class="font-mono stat-num">{{ activeCount }}</span>
        <span>活跃监听</span>
      </div>
      <div class="mini-stat glass-card-sm">
        <el-icon :size="20" color="var(--info)"><Headset /></el-icon>
        <span class="font-mono stat-num">{{ totalListened }}</span>
        <span>总消息</span>
      </div>
      <div class="mini-stat glass-card-sm">
        <el-icon :size="20" color="var(--accent)"><Download /></el-icon>
        <span class="font-mono stat-num">{{ totalDownloaded }}</span>
        <span>总下载</span>
      </div>
      <div class="mini-stat glass-card-sm">
        <el-icon :size="20" color="var(--purple)"><Share /></el-icon>
        <span class="font-mono stat-num">{{ totalForwarded }}</span>
        <span>总转发</span>
      </div>
    </div>

    <div class="listens-content glass-card">
      <el-table :data="subscriptions" v-loading="loading">
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <span class="badge" :class="row.status === 'active' ? 'badge-success' : 'badge-warning'">
              <span :class="row.status === 'active' ? 'status-dot-active' : 'status-dot-inactive'" class="status-dot"></span>
              {{ row.status === 'active' ? '监听中' : '已停止' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="聊天" min-width="180">
          <template #default="{ row }"><div class="chat-cell"><el-icon><ChatDotRound /></el-icon><span>{{ row.chat_title || row.chat_id }}</span></div></template>
        </el-table-column>
        <el-table-column label="统计" width="200">
          <template #default="{ row }">
            <div class="stats-cell">
              <span><el-icon><Headset /></el-icon> {{ row.total_listened }}</span>
              <span><el-icon><Download /></el-icon> {{ row.total_downloaded }}</span>
              <span><el-icon><Share /></el-icon> {{ row.total_forwarded }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'active'" type="warning" size="small" :icon="VideoPause" @click="handleStop(row)">停止</el-button>
            <el-button v-else type="success" size="small" :icon="VideoPlay" @click="handleStart(row)">启动</el-button>
            <el-button type="danger" size="small" :icon="Delete" link @click="handleDelete(row)" />
          </template>
        </el-table-column>
      </el-table>
    </div>

    <AddListenDialog v-model="showAdd" :accounts="accounts" @confirm="onAdded" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, VideoPlay, VideoPause, Delete, Headset, Download, Share, ChatDotRound } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listensApi, type ListenSubscription } from '@/api/listens'
import { accountsApi, type TelegramAccount } from '@/api/accounts'
import AddListenDialog from '@/components/AddListenDialog.vue'

const loading = ref(false)
const subscriptions = ref<ListenSubscription[]>([])
const accounts = ref<TelegramAccount[]>([])
const showAdd = ref(false)

const activeCount = computed(() => subscriptions.value.filter(s => s.status === 'active').length)
const totalListened = computed(() => subscriptions.value.reduce((s, r) => s + (r.total_listened || 0), 0))
const totalDownloaded = computed(() => subscriptions.value.reduce((s, r) => s + (r.total_downloaded || 0), 0))
const totalForwarded = computed(() => subscriptions.value.reduce((s, r) => s + (r.total_forwarded || 0), 0))

async function fetchAccounts() {
  try { accounts.value = await accountsApi.list() as any }
  catch { /* 静默处理 */ }
}

async function fetchSubscriptions() {
  loading.value = true
  try { subscriptions.value = await listensApi.list() as any }
  catch { ElMessage.error('加载失败') }
  finally { loading.value = false }
}
function onAdded() { showAdd.value = false; fetchSubscriptions(); ElMessage.success('添加成功') }
async function handleStop(row: ListenSubscription) {
  try { await listensApi.stop(row.id); fetchSubscriptions(); ElMessage.success('已停止') }
  catch { ElMessage.error('操作失败') }
}
async function handleStart(row: ListenSubscription) {
  try { await listensApi.start(row.id); fetchSubscriptions(); ElMessage.success('已启动') }
  catch { ElMessage.error('操作失败') }
}
async function handleDelete(row: ListenSubscription) {
  try {
    await ElMessageBox.confirm('确认删除此监听规则？', '删除确认', { type: 'warning' })
    await listensApi.delete(row.id)
    fetchSubscriptions()
    ElMessage.success('已删除')
  } catch { /* 取消 */ }
}

onMounted(() => { fetchAccounts(); fetchSubscriptions() })
</script>

<style scoped>
.listens-page { display: flex; flex-direction: column; gap: var(--space-6); }
.page-hero { display: flex; align-items: flex-start; justify-content: space-between; }
.page-title { font-family: var(--font-heading); font-size: 24px; font-weight: 700; }
.page-desc { color: var(--text-tertiary); margin-top: var(--space-1); }
.listens-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: var(--space-3); }
.mini-stat {
  display: flex; align-items: center; gap: var(--space-3);
  padding: var(--space-4); font-size: 13px; color: var(--text-secondary);
}
.stat-num { font-size: 22px; font-weight: 700; color: var(--text-primary); margin-right: auto; }
.listens-content { padding: var(--space-4); }
.chat-cell { display: flex; align-items: center; gap: var(--space-2); }
.stats-cell { display: flex; gap: var(--space-3); font-size: 13px; color: var(--text-secondary); align-items: center; }
.stats-cell .el-icon { margin-right: 2px; font-size: 14px; }
.font-mono { font-family: var(--font-mono); }
</style>
