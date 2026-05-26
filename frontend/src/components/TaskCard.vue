<template>
  <el-card shadow="hover" class="task-card">
    <template #header>
      <div class="card-header">
        <div class="task-info">
          <el-tag :type="getStatusType(task.status)" size="small">
            {{ getStatusText(task.status) }}
          </el-tag>
          <el-tag v-if="task.task_type === 'bot'" type="info" size="small" class="ml-1">Bot</el-tag>
          <span class="task-title">{{ task.chat_title || task.chat_id }}</span>
        </div>
        <div class="task-actions">
          <!-- 暂停按钮 -->
          <el-button
            v-if="task.status === 'running'"
            type="warning"
            size="small"
            :icon="VideoPause"
            @click="$emit('pause', task.id)"
            :loading="pausing"
          >
            暂停
          </el-button>
          <!-- 继续按钮 -->
          <el-button
            v-if="task.status === 'paused'"
            type="success"
            size="small"
            :icon="VideoPlay"
            @click="$emit('resume', task.id)"
            :loading="resuming"
          >
            继续
          </el-button>
          <!-- 取消按钮 -->
          <el-button
            v-if="task.status === 'running' || task.status === 'pending'"
            type="danger"
            size="small"
            :icon="CircleClose"
            @click="$emit('cancel', task.id)"
          >
            取消
          </el-button>
          <!-- 重试按钮 -->
          <el-button
            v-if="task.status === 'failed'"
            type="primary"
            size="small"
            :icon="RefreshRight"
            @click="$emit('retry', task.id)"
          >
            重试
          </el-button>
        </div>
      </div>
    </template>

    <div class="task-content">
      <!-- 进度条 -->
      <div class="progress-section">
        <div class="progress-info">
          <span>{{ task.success_count }} / {{ task.total_count }} 文件</span>
          <span v-if="task.failed_count > 0" class="failed-text">
            ({{ task.failed_count }} 失败)
          </span>
          <span v-if="task.skipped_count > 0" class="skipped-text">
            ({{ task.skipped_count }} 跳过)
          </span>
        </div>
        <el-progress
          :percentage="progress"
          :status="progressStatus"
        />
      </div>

      <!-- 当前文件下载进度 -->
      <div v-if="task.status === 'running' && task.current_file_name" class="current-file-section">
        <div class="current-file-header">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span class="current-file-name">{{ task.current_file_name }}</span>
        </div>
        <el-progress
          :percentage="task.current_file_progress || 0"
          :indeterminate="task.current_file_progress === 0"
          :stroke-width="6"
        />
      </div>

      <!-- 任务详情 -->
      <div class="task-details">
        <div class="detail-item">
          <el-icon><Files /></el-icon>
          <span>{{ task.media_types?.join(', ') || '全部类型' }}</span>
        </div>
        <div class="detail-item">
          <el-icon><Download /></el-icon>
          <span>{{ formatBytes(task.downloaded_bytes) }} / {{ formatBytes(task.total_bytes || 0) }}</span>
        </div>
      </div>

      <!-- 文件分类统计 -->
      <div v-if="Object.keys(task.stats_by_type || {}).length > 0" class="stats-section">
        <div class="stats-header">文件分类统计</div>
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
        <span>已过滤格式: {{ getFilterText() }}</span>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { CircleClose, RefreshRight, Files, Download, Loading, Filter, VideoPause, VideoPlay } from '@element-plus/icons-vue'
import { formatBytes } from '@/utils/format'
import type { Task } from '@/api/tasks'
import { useTaskWebSocket, type TaskProgressMessage } from '@/composables/useWebSocket'
import { onMounted, onUnmounted } from 'vue'

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

const progressStatus = computed(() => {
  if (props.task.status === 'completed') return 'success'
  if (props.task.status === 'failed') return 'exception'
  return undefined
})

const hasFilters = computed(() => {
  return (props.task.excluded_extensions?.length ?? 0) > 0 ||
         (props.task.included_extensions?.length ?? 0) > 0
})

function getStatusType(status: string): 'success' | 'warning' | 'danger' | 'info' | 'primary' {
  const types: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'primary'> = {
    completed: 'success',
    running: 'primary',
    paused: 'warning',
    pending: 'info',
    failed: 'danger',
    cancelled: 'warning',
  }
  return types[status] || 'info'
}

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
  border: 1px solid #e4e7ed;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-title {
  font-weight: 500;
}

.task-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.progress-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.failed-text {
  color: #f56c6c;
}

.skipped-text {
  color: #909399;
}

.current-file-section {
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.current-file-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
  font-size: 13px;
}

.current-file-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #409eff;
}

.task-details {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #909399;
}

.stats-section {
  padding: 10px;
  background-color: #fafafa;
  border-radius: 4px;
}

.stats-header {
  font-size: 12px;
  color: #606266;
  margin-bottom: 8px;
  font-weight: 500;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 8px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 6px;
  background-color: #fff;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.stat-type {
  font-size: 11px;
  color: #909399;
}

.stat-count {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.filter-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
  padding: 6px 10px;
  background-color: #f0f9ff;
  border-radius: 4px;
}

.ml-1 {
  margin-left: 4px;
}
</style>
