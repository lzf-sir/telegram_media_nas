<template>
  <div class="tasks-view">
    <div class="tasks-header">
      <div class="header-left">
        <h2 class="page-title-section">下载任务</h2>
        <p class="page-subtitle">管理您的媒体下载任务</p>
      </div>
      <el-button type="primary" :icon="Plus" size="large" @click="showCreateDialog = true">
        创建任务
      </el-button>
    </div>

    <div class="tasks-content glass-card">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange" class="task-tabs">
        <el-tab-pane label="进行中" name="running">
          <task-list
            :tasks="runningTasks"
            :loading="loading"
            @refresh="fetchTasks"
            @pause="handlePause"
            @resume="handleResume"
            @cancel="handleCancel"
            @retry="handleRetry"
          />
        </el-tab-pane>
        <el-tab-pane label="已完成" name="completed">
          <task-list
            :tasks="completedTasks"
            :loading="loading"
            @refresh="fetchTasks"
            @pause="handlePause"
            @resume="handleResume"
            @cancel="handleCancel"
            @retry="handleRetry"
          />
        </el-tab-pane>
        <el-tab-pane label="失败" name="failed">
          <task-list
            :tasks="failedTasks"
            :loading="loading"
            @refresh="fetchTasks"
            @pause="handlePause"
            @resume="handleResume"
            @cancel="handleCancel"
            @retry="handleRetry"
          />
        </el-tab-pane>
      </el-tabs>
    </div>

    <create-task-dialog v-model="showCreateDialog" @created="handleTaskCreated" />
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

async function fetchTasks() {
  loading.value = true
  try {
    await taskStore.fetchTasks({ limit: 50 })
  } finally {
    loading.value = false
  }
}

function handleTabChange() {
  fetchTasks()
}

function handleTaskCreated() {
  showCreateDialog.value = false
  fetchTasks()
  ElMessage.success('任务创建成功')
}

async function handleCancel(id: number) {
  try {
    await tasksApi.cancel(id)
    ElMessage.success('任务已取消')
    fetchTasks()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '取消失败')
  }
}

async function handleRetry(id: number) {
  try {
    await tasksApi.retry(id)
    ElMessage.success('任务已重新开始')
    fetchTasks()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '重试失败')
  }
}

function handlePause(id: number) {
  // 事件由 TaskList 处理
}

function handleResume(id: number) {
  // 事件由 TaskList 处理
}

onMounted(() => {
  fetchTasks()
})
</script>

<style scoped>
.tasks-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

/* ============================================
   头部样式
   ============================================ */
.tasks-header {
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
.tasks-content {
  padding: var(--space-lg);
  min-height: 400px;
}

:deep(.task-tabs) {
  display: flex;
  flex-direction: column;
  height: 100%;
}

:deep(.task-tabs .el-tabs__header) {
  margin: 0 0 var(--space-lg) 0;
}

:deep(.task-tabs .el-tabs__nav-wrap::after) {
  display: none;
}

:deep(.task-tabs .el-tabs__item) {
  padding: 0 var(--space-lg);
  height: 44px;
  line-height: 44px;
  font-size: 15px;
  font-weight: 500;
}

:deep(.task-tabs .el-tabs__active-bar) {
  height: 3px;
  border-radius: var(--radius-full);
}

:deep(.task-tabs .el-tab-pane) {
  display: flex;
  flex-direction: column;
}

/* ============================================
   响应式设计
   ============================================ */
@media (max-width: 640px) {
  .tasks-header {
    flex-direction: column;
    align-items: stretch;
  }

  .page-title-section {
    font-size: 20px;
  }

  .tasks-header .el-button {
    width: 100%;
  }
}
</style>
