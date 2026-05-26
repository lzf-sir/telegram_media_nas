<template>
  <div class="task-list">
    <!-- 骨架屏 -->
    <div v-if="loading" class="task-skeleton">
      <div v-for="i in 3" :key="i" class="skeleton-card glass-card-sm">
        <div class="skeleton-header">
          <div class="skeleton-badge"></div>
          <div class="skeleton-title"></div>
        </div>
        <div class="skeleton-progress">
          <div class="skeleton-progress-bar"></div>
        </div>
        <div class="skeleton-details">
          <div class="skeleton-detail"></div>
          <div class="skeleton-detail"></div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="tasks.length === 0" class="empty-state">
      <div class="empty-icon">
        <el-icon :size="64"><Download /></el-icon>
      </div>
      <h3 class="empty-title">暂无任务</h3>
      <p class="empty-description">点击上方"创建任务"按钮开始下载</p>
    </div>

    <!-- 任务列表 -->
    <div v-else class="task-cards">
      <transition-group name="list">
        <task-card
          v-for="task in tasks"
          :key="task.id"
          :task="task"
          @cancel="$emit('cancel', task.id)"
          @retry="$emit('retry', task.id)"
          @pause="handlePause"
          @resume="handleResume"
        />
      </transition-group>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
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

/* ============================================
   骨架屏样式
   ============================================ */
.task-skeleton {
  display: grid;
  gap: var(--space-md);
}

.skeleton-card {
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.skeleton-header {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.skeleton-badge {
  width: 60px;
  height: 24px;
  background: linear-gradient(90deg, var(--glass-bg) 25%, var(--input-bg) 50%, var(--glass-bg) 75%);
  background-size: 200% 100%;
  border-radius: var(--radius-full);
  animation: shimmer 1.5s infinite;
}

.skeleton-title {
  width: 150px;
  height: 20px;
  background: linear-gradient(90deg, var(--glass-bg) 25%, var(--input-bg) 50%, var(--glass-bg) 75%);
  background-size: 200% 100%;
  border-radius: var(--radius-sm);
  animation: shimmer 1.5s infinite;
}

.skeleton-progress {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.skeleton-progress-bar {
  width: 100%;
  height: 8px;
  background: linear-gradient(90deg, var(--glass-bg) 25%, var(--input-bg) 50%, var(--glass-bg) 75%);
  background-size: 200% 100%;
  border-radius: var(--radius-full);
  animation: shimmer 1.5s infinite;
}

.skeleton-details {
  display: flex;
  gap: var(--space-md);
}

.skeleton-detail {
  width: 120px;
  height: 36px;
  background: linear-gradient(90deg, var(--glass-bg) 25%, var(--input-bg) 50%, var(--glass-bg) 75%);
  background-size: 200% 100%;
  border-radius: var(--radius-md);
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ============================================
   空状态样式
   ============================================ */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-3xl) var(--space-xl);
  text-align: center;
}

.empty-icon {
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-bg);
  border-radius: var(--radius-xl);
  color: var(--text-tertiary);
  margin-bottom: var(--space-lg);
}

.empty-title {
  margin: 0 0 var(--space-sm) 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.empty-description {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
}

/* ============================================
   任务列表样式
   ============================================ */
.task-cards {
  display: grid;
  gap: var(--space-md);
}

/* 列表过渡动画 */
.list-enter-active,
.list-leave-active {
  transition: all var(--transition-normal);
}

.list-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.list-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.list-move {
  transition: transform var(--transition-normal);
}
</style>
