<template>
  <div class="task-card glass-card" :class="`task-card-${task.status}`">
    <!-- 头部 -->
    <div class="task-header">
      <div class="task-info">
        <div class="status-badge" :class="`status-${task.status}`">
          <span class="status-dot"></span>
          <span class="status-text">{{ getStatusText(task.status) }}</span>
        </div>
        <el-tag v-if="task.task_type === 'bot'" size="small" class="bot-tag">Bot</el-tag>
        <h3 class="task-title">{{ task.chat_title || task.chat_id }}</h3>
      </div>
      <div class="task-actions">
        <el-button
          v-if="task.status === 'running'"
          type="warning"
          size="small"
          :icon="VideoPause"
          @click="handlePause"
          :loading="pausing"
          circle
        />
        <el-button
          v-if="task.status === 'paused'"
          type="success"
          size="small"
          :icon="VideoPlay"
          @click="handleResume"
          :loading="resuming"
          circle
        />
        <el-button
          v-if="task.status === 'running' || task.status === 'pending'"
          type="danger"
          size="small"
          :icon="CircleClose"
          @click="$emit('cancel', task.id)"
          circle
        />
        <el-button
          v-if="task.status === 'failed'"
          type="primary"
          size="small"
          :icon="RefreshRight"
          @click="$emit('retry', task.id)"
          circle
        />
      </div>
    </div>

    <!-- 内容 -->
    <div class="task-content">
      <!-- 进度条 -->
      <div class="progress-section">
        <div class="progress-header">
          <span class="progress-text">{{ task.success_count }} / {{ task.total_count }} 文件</span>
          <span class="progress-percentage">{{ progress }}%</span>
        </div>
        <div class="progress-bar-wrapper">
          <div class="progress-bar" :class="`progress-${task.status}`" :style="{ width: `${progress}%` }">
            <div class="progress-shine"></div>
          </div>
        </div>
        <div v-if="task.failed_count > 0 || task.skipped_count > 0" class="progress-details">
          <span v-if="task.failed_count > 0" class="failed-count">{{ task.failed_count }} 失败</span>
          <span v-if="task.skipped_count > 0" class="skipped-count">{{ task.skipped_count }} 跳过</span>
        </div>
      </div>

      <!-- 当前文件下载进度 -->
      <div v-if="task.status === 'running' && task.current_file_name" class="current-file-section">
        <div class="current-file-header">
          <el-icon class="loading-icon"><Loading /></el-icon>
          <span class="current-file-name">{{ task.current_file_name }}</span>
        </div>
        <div class="current-file-progress">
          <div class="progress-bar-wrapper">
            <div class="progress-bar progress-running" :style="{ width: `${task.current_file_progress || 0}%` }">
              <div class="progress-shine"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 任务详情 -->
      <div class="task-details">
        <div class="detail-item">
          <div class="detail-icon">
            <el-icon><Files /></el-icon>
          </div>
          <div class="detail-content">
            <span class="detail-label">文件类型</span>
            <span class="detail-value">{{ task.media_types?.join(', ') || '全部类型' }}</span>
          </div>
        </div>
        <div class="detail-item">
          <div class="detail-icon">
            <el-icon><Download /></el-icon>
          </div>
          <div class="detail-content">
            <span class="detail-label">已下载</span>
            <span class="detail-value">{{ formatBytes(task.downloaded_bytes) }} / {{ formatBytes(task.total_bytes || 0) }}</span>
          </div>
        </div>
      </div>

      <!-- 文件分类统计 -->
      <div v-if="Object.keys(task.stats_by_type || {}).length > 0" class="stats-section">
        <div class="stats-header">文件分类</div>
        <div class="stats-grid">
          <div
            v-for="(count, type) in task.stats_by_type"
            :key="type"
            class="stat-item"
          >
            <span class="stat-type">{{ getMediaTypeText(type) }}</span>
            <span class="stat-count">{{ count }}</span>
          </div>
        </div>
      </div>

      <!-- 过滤信息 -->
      <div v-if="hasFilters" class="filter-info">
        <el-icon><Filter /></el-icon>
        <span>已过滤: {{ getFilterText() }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import {
  CircleClose,
  RefreshRight,
  Files,
  Download,
  Loading,
  Filter,
  VideoPause,
  VideoPlay,
} from '@element-plus/icons-vue'
import { formatBytes } from '@/utils/format'
import type { Task } from '@/api/tasks'
import { useTaskWebSocket, type TaskProgressMessage } from '@/composables/useWebSocket'

const props = defineProps<{
  task: Task
}>()

const pausing = ref(false)
const resuming = ref(false)

const emit = defineEmits<{
  cancel: [id: number]
  retry: [id: number]
  pause: [id: number]
  resume: [id: number]
}>()

async function handlePause() {
  pausing.value = true
  try {
    await emit('pause', props.task.id)
  } finally {
    pausing.value = false
  }
}

async function handleResume() {
  resuming.value = true
  try {
    await emit('resume', props.task.id)
  } finally {
    resuming.value = false
  }
}

const progress = computed(() => {
  if (props.task.total_count > 0) {
    return Math.round((props.task.success_count / props.task.total_count) * 100)
  }
  return 0
})

const hasFilters = computed(() => {
  return (props.task.excluded_extensions?.length ?? 0) > 0 ||
         (props.task.included_extensions?.length ?? 0) > 0
})

function getStatusText(status: string): string {
  const texts: Record<string, string> = {
    completed: '已完成',
    running: '进行中',
    paused: '已暂停',
    pending: '等待中',
    failed: '失败',
    cancelled: '已取消',
  }
  return texts[status] || status
}

function getMediaTypeText(type: string): string {
  const texts: Record<string, string> = {
    audio: '音频',
    video: '视频',
    photo: '图片',
    document: '文档',
    voice: '语音',
    video_note: '视频留言',
    animation: '动画',
  }
  return texts[type] || type
}

function getFilterText(): string {
  if (props.task.included_extensions?.length) {
    return `仅包含 ${props.task.included_extensions.length} 种格式`
  }
  if (props.task.excluded_extensions?.length) {
    return `排除 ${props.task.excluded_extensions.length} 种格式`
  }
  return ''
}

// WebSocket for real-time updates
let ws: ReturnType<typeof useTaskWebSocket> | null = null

onMounted(() => {
  if (props.task.status === 'running' || props.task.status === 'pending') {
    ws = useTaskWebSocket(props.task.id)
    ws.connect()

    ws.$subscribe((msg) => {
      if (msg) {
        const data = msg as TaskProgressMessage
        props.task.success_count = data.success
        props.task.failed_count = data.failed
        props.task.total_count = data.total
        props.task.downloaded_bytes = data.downloaded_bytes
        props.task.current_file_name = data.current_file
        props.task.current_file_progress = data.current_file_progress || 0
        if (data.stats_by_type) props.task.stats_by_type = data.stats_by_type
        if (data.stats_by_format) props.task.stats_by_format = data.stats_by_format
      }
    })
  }
})

onUnmounted(() => {
  ws?.disconnect()
})
</script>

<style scoped>
.task-card {
  padding: var(--space-lg);
  transition: all var(--transition-normal);
}

.task-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

/* ============================================
   头部样式
   ============================================ */
.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-lg);
  gap: var(--space-md);
}

.task-info {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-sm);
}

.status-badge {
  display: flex;
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
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-running {
  background: var(--primary-bg);
  color: var(--primary-color);
}

.status-running .status-dot {
  background: var(--primary-color);
}

.status-completed {
  background: var(--success-bg);
  color: var(--success-color);
}

.status-completed .status-dot {
  background: var(--success-color);
  animation: none;
}

.status-failed {
  background: var(--danger-bg);
  color: var(--danger-color);
}

.status-failed .status-dot {
  background: var(--danger-color);
  animation: none;
}

.status-paused,
.status-cancelled {
  background: var(--warning-bg);
  color: var(--warning-color);
}

.status-paused .status-dot,
.status-cancelled .status-dot {
  background: var(--warning-color);
  animation: none;
}

.status-pending {
  background: var(--info-bg);
  color: var(--info-color);
}

.status-pending .status-dot {
  background: var(--info-color);
  animation: pulse 2s infinite;
}

.bot-tag {
  background: var(--info-bg);
  color: var(--info-color);
  border: none;
  font-size: 11px;
  padding: 2px 8px;
  height: 20px;
}

.task-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.task-actions {
  display: flex;
  gap: var(--space-xs);
}

/* ============================================
   内容样式
   ============================================ */
.task-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

/* 进度条 */
.progress-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-text {
  font-size: 13px;
  color: var(--text-secondary);
}

.progress-percentage {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.progress-bar-wrapper {
  width: 100%;
  height: 8px;
  background: var(--input-bg);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: var(--radius-full);
  position: relative;
  overflow: hidden;
  transition: width var(--transition-normal);
}

.progress-running {
  background: var(--primary-gradient);
}

.progress-completed {
  background: var(--success-gradient);
}

.progress-failed {
  background: var(--danger-gradient);
}

.progress-paused,
.progress-pending {
  background: var(--warning-gradient);
}

.progress-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.3) 50%,
    transparent 100%
  );
  animation: shine 2s infinite;
}

@keyframes shine {
  0% { left: -100%; }
  100% { left: 100%; }
}

.progress-details {
  display: flex;
  gap: var(--space-md);
  font-size: 12px;
}

.failed-count {
  color: var(--danger-color);
}

.skipped-count {
  color: var(--text-tertiary);
}

/* 当前文件 */
.current-file-section {
  padding: var(--space-md);
  background: var(--input-bg);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.current-file-header {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-sm);
}

.loading-icon {
  color: var(--primary-color);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.current-file-name {
  flex: 1;
  font-size: 13px;
  color: var(--primary-color);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.current-file-progress {
  margin-top: var(--space-sm);
}

/* 任务详情 */
.task-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-md);
}

.detail-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm);
  background: var(--input-bg);
  border-radius: var(--radius-md);
}

.detail-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-bg);
  border-radius: var(--radius-md);
  color: var(--primary-color);
  font-size: 16px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.detail-label {
  font-size: 11px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
}

/* 文件分类统计 */
.stats-section {
  padding: var(--space-md);
  background: var(--input-bg);
  border-radius: var(--radius-md);
}

.stats-header {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-bottom: var(--space-sm);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(70px, 1fr));
  gap: var(--space-sm);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-sm);
  background: var(--glass-bg);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
}

.stat-type {
  font-size: 11px;
  color: var(--text-tertiary);
}

.stat-count {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

/* 过滤信息 */
.filter-info {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  background: var(--info-bg);
  border-radius: var(--radius-md);
  font-size: 12px;
  color: var(--info-color);
}
</style>
