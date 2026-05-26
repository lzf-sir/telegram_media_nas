<template>
  <div class="task-list">
    <el-empty v-if="!loading && tasks.length === 0" description="暂无任务" />

    <div v-else class="task-cards">
      <task-card
        v-for="task in tasks"
        :key="task.id"
        :task="task"
        @cancel="$emit('cancel', task.id)"
        @retry="$emit('retry', task.id)"
        @pause="handlePause"
        @resume="handleResume"
      />
    </div>

    <el-skeleton v-if="loading" :rows="3" animated />
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import type { Task } from '@/api/tasks'
import { tasksApi } from '@/api/tasks'
import TaskCard from './TaskCard.vue'

defineProps<{
  tasks: Task[]
  loading: boolean
}>()

const emit = defineEmits<{
  cancel: [id: number]
  retry: [id: number]
  pause: [id: number]
  resume: [id: number]
  refresh: []
}>()

async function handlePause(id: number) {
  try {
    await tasksApi.pause(id)
    ElMessage.success('任务已暂停')
    emit('refresh')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '暂停失败')
  }
}

async function handleResume(id: number) {
  try {
    await tasksApi.resume(id)
    ElMessage.success('任务已恢复')
    emit('refresh')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '恢复失败')
  }
}
</script>

<style scoped>
.task-list {
  min-height: 200px;
}

.task-cards {
  display: grid;
  gap: 12px;
}
</style>
