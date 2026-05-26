<template>
  <div class="tasks-view">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>下载任务</span>
          <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
            创建任务
          </el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="进行中" name="running">
          <task-list :tasks="runningTasks" :loading="loading" @refresh="fetchTasks" @pause="handlePause" @resume="handleResume" />
        </el-tab-pane>
        <el-tab-pane label="已完成" name="completed">
          <task-list :tasks="completedTasks" :loading="loading" @refresh="fetchTasks" @pause="handlePause" @resume="handleResume" />
        </el-tab-pane>
        <el-tab-pane label="失败" name="failed">
          <task-list :tasks="failedTasks" :loading="loading" @refresh="fetchTasks" @pause="handlePause" @resume="handleResume" />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <create-task-dialog v-model="showCreateDialog" @created="handleTaskCreated" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { useTaskStore } from '@/stores/task'
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
  await taskStore.fetchTasks({ limit: 50 })
  loading.value = false
}

function handleTabChange() {
  fetchTasks()
}

function handleTaskCreated() {
  showCreateDialog.value = false
  fetchTasks()
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
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
