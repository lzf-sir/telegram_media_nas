<template>
  <div class="task-list">
    <!-- 骨架屏 -->
    <div v-if="loading" class="skeleton-list">
      <div v-for="i in 3" :key="i" class="skeleton-item glass-card-sm">
        <div class="sk-row">
          <div class="skeleton" style="width:80px;height:20px"></div>
          <div class="skeleton" style="width:40px;height:32px;margin-left:auto"></div>
        </div>
        <div class="skeleton" style="width:100%;height:6px;margin-top:8px"></div>
        <div class="sk-row" style="margin-top:8px">
          <div class="skeleton" style="width:120px;height:16px"></div>
          <div class="skeleton" style="width:80px;height:16px"></div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="tasks.length === 0" class="empty-state">
      <el-icon :size="56" color="var(--text-tertiary)"><Download /></el-icon>
      <h3>暂无任务</h3>
      <p>点击"创建任务"按钮开始下载</p>
    </div>

    <!-- 任务列表 -->
    <transition-group v-else name="list" tag="div" class="task-cards">
      <TaskCard
        v-for="task in tasks"
        :key="task.id"
        :task="task"
        @cancel="emit('cancel', task.id)"
        @retry="emit('retry', task.id)"
        @pause="handlePause(task.id)"
        @resume="handleResume(task.id)"
      />
    </transition-group>
  </div>
</template>

<script setup lang="ts">
import { Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { Task } from '@/api/tasks'
import { tasksApi } from '@/api/tasks'
import TaskCard from './TaskCard.vue'

defineProps<{ tasks: Task[]; loading: boolean }>()
const emit = defineEmits<{ cancel: [id: number]; retry: [id: number]; pause: [id: number]; resume: [id: number]; refresh: [] }>()

async function handlePause(id: number) {
  try { await tasksApi.pause(id); emit('refresh') }
  catch (e: any) { ElMessage.error(e.response?.data?.detail || '暂停失败') }
}
async function handleResume(id: number) {
  try { await tasksApi.resume(id); emit('refresh') }
  catch (e: any) { ElMessage.error(e.response?.data?.detail || '恢复失败') }
}
</script>

<style scoped>
.task-list { min-height: 100px; }
.skeleton-list { display: flex; flex-direction: column; gap: var(--space-3); }
.skeleton-item { padding: var(--space-4); }
.sk-row { display: flex; align-items: center; gap: var(--space-3); }
.task-cards { display: flex; flex-direction: column; gap: var(--space-3); }
.empty-state {
  text-align: center; padding: var(--space-12);
  color: var(--text-tertiary);
}
.empty-state h3 { margin: var(--space-3) 0 var(--space-1); font-size: 16px; color: var(--text-secondary); }
.empty-state p { font-size: 13px; }
</style>
