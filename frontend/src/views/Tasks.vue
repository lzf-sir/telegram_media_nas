<template>
  <div class="tasks-page">
    <!-- 页头 -->
    <div class="page-hero">
      <div class="hero-left">
        <h2 class="page-title">下载任务</h2>
        <p class="page-desc">管理和监控所有媒体下载任务</p>
      </div>
      <el-button type="primary" size="large" :icon="Plus" @click="showCreateDialog = true">
        创建任务
      </el-button>
    </div>

    <!-- 内容 -->
    <div class="tasks-content glass-card">
      <el-tabs v-model="activeTab" @tab-change="fetchTasks" class="tasks-tabs">
        <el-tab-pane name="running">
          <template #label>
            <span class="tab-label">
              进行中
              <span class="tab-count">{{ runningTasks.length }}</span>
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane name="completed">
          <template #label>
            <span class="tab-label">
              已完成
              <span class="tab-count done">{{ completedTasks.length }}</span>
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane name="failed">
          <template #label">
            <span class="tab-label">
              失败
              <span class="tab-count fail">{{ failedTasks.length }}</span>
            </span>
          </template>
        </el-tab-pane>
      </el-tabs>

      <TaskList
        :tasks="currentTasks"
        :loading="loading"
        @refresh="fetchTasks"
        @cancel="handleCancel"
        @retry="handleRetry"
        @pause="handlePause"
        @resume="handleResume"
      />
    </div>

    <CreateTaskDialog v-model="showCreateDialog" @created="onTaskCreated" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useTaskStore } from '@/stores/task'
import { tasksApi } from '@/api/tasks'
import TaskList from '@/components/TaskList.vue'
import CreateTaskDialog from '@/components/CreateTaskDialog.vue'

const taskStore = useTaskStore()
const activeTab = ref('running')
const loading = ref(false)
const showCreateDialog = ref(false)

const runningTasks = computed(() => taskStore.runningTasks)
const completedTasks = computed(() => taskStore.completedTasks)
const failedTasks = computed(() => taskStore.failedTasks)

const currentTasks = computed(() => {
  const map: Record<string, any[]> = {
    running: runningTasks.value,
    completed: completedTasks.value,
    failed: failedTasks.value,
  }
  return map[activeTab.value] || []
})

async function fetchTasks() {
  loading.value = true
  try { await taskStore.fetchTasks({ limit: 50 }) }
  finally { loading.value = false }
}

function onTaskCreated() {
  showCreateDialog.value = false
  activeTab.value = 'running'
  fetchTasks()
  ElMessage.success('任务创建成功')
}

async function handleCancel(id: number) {
  try { await tasksApi.cancel(id); fetchTasks(); ElMessage.success('已取消') }
  catch (e: any) { ElMessage.error(e.response?.data?.detail || '取消失败') }
}
async function handleRetry(id: number) {
  try { await tasksApi.retry(id); fetchTasks(); ElMessage.success('已重新发起') }
  catch (e: any) { ElMessage.error(e.response?.data?.detail || '重试失败') }
}
async function handlePause(id: number) {
  try { await tasksApi.pause(id); fetchTasks(); ElMessage.success('已暂停') }
  catch (e: any) { ElMessage.error(e.response?.data?.detail || '暂停失败') }
}
async function handleResume(id: number) {
  try { await tasksApi.resume(id); fetchTasks(); ElMessage.success('已恢复') }
  catch (e: any) { ElMessage.error(e.response?.data?.detail || '恢复失败') }
}

onMounted(fetchTasks)
</script>

<style scoped>
.tasks-page { display: flex; flex-direction: column; gap: var(--space-6); }
.page-hero {
  display: flex; align-items: flex-start; justify-content: space-between;
}
.page-title {
  font-family: var(--font-heading);
  font-size: 24px; font-weight: 700;
  color: var(--text-primary);
}
.page-desc {
  color: var(--text-tertiary);
  margin-top: var(--space-1);
  font-size: 14px;
}
.tasks-content {
  padding: var(--space-5);
  flex: 1;
}
.tab-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
.tab-count {
  font-family: var(--font-mono);
  font-size: 11px;
  padding: 1px 7px;
  border-radius: var(--radius-full);
  background: var(--success-soft);
  color: var(--accent);
}
.tab-count.done { background: var(--info-soft); color: var(--info); }
.tab-count.fail { background: var(--danger-soft); color: var(--danger); }
</style>
