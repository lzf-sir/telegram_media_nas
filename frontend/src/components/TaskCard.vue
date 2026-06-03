<template>
  <div class="task-card glass-card-sm" :class="`task-${task.status}`">
    <!-- 头部 -->
    <div class="card-top">
      <div class="task-meta">
        <span class="badge" :class="`badge-${getStatusBadge(task.status)}`">
          <span class="status-dot" :class="`status-dot-${task.status === 'running' ? 'active' : task.status === 'pending' ? 'pending' : 'inactive'}`"></span>
          {{ getStatusText(task.status) }}
        </span>
        <el-tag v-if="task.task_type === 'bot'" size="small" round>Bot</el-tag>
        <h4 class="task-chat-title">{{ task.chat_title || task.chat_id }}</h4>
      </div>
      <div class="task-actions">
        <el-button v-if="task.status === 'running'" type="warning" size="small" :icon="VideoPause" circle @click="$emit('pause', task.id)" />
        <el-button v-if="task.status === 'paused'" type="success" size="small" :icon="VideoPlay" circle @click="$emit('resume', task.id)" />
        <el-button v-if="task.status === 'running' || task.status === 'pending'" type="danger" size="small" :icon="CircleClose" circle @click="$emit('cancel', task.id)" />
        <el-button v-if="task.status === 'failed'" type="primary" size="small" :icon="RefreshRight" circle @click="$emit('retry', task.id)" />
      </div>
    </div>

    <!-- 进度 -->
    <div class="card-progress">
      <div class="progress-header">
        <span class="font-mono progress-fraction">{{ task.success_count }} / {{ task.total_count }} 文件</span>
        <span class="font-mono progress-pct">{{ progress }}%</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill" :class="`fill-${task.status}`" :style="{ width: `${progress}%` }">
          <div class="progress-shine"></div>
        </div>
      </div>
      <div v-if="task.failed_count || task.skipped_count" class="progress-extra">
        <span v-if="task.failed_count" class="extra-fail">{{ task.failed_count }} 失败</span>
        <span v-if="task.skipped_count" class="extra-skip">{{ task.skipped_count }} 跳过</span>
      </div>
    </div>

    <!-- 当前文件 -->
    <div v-if="task.status === 'running' && task.current_file_name" class="current-file">
      <el-icon class="pulse-icon"><Loading /></el-icon>
      <span class="file-name truncate">{{ task.current_file_name }}</span>
    </div>

    <!-- 下载速度 & ETA -->
    <div v-if="task.status === 'running' && (task.download_speed || task.current_file_progress > 0)" class="speed-eta">
      <span class="speed-text">
        <el-icon><Odometer /></el-icon>
        {{ formatSpeed(task.download_speed || 0) }}
      </span>
      <span v-if="task.eta_seconds > 0" class="eta-text">
        <el-icon><Clock /></el-icon>
        剩余 {{ formatDuration(task.eta_seconds) }}
      </span>
    </div>

    <!-- 详情 -->
    <div class="card-details">
      <div class="detail">
        <el-icon><Files /></el-icon>
        <span class="detail-key">类型</span>
        <span class="detail-val">{{ task.media_types?.join(', ') || '全部' }}</span>
      </div>
      <div class="detail">
        <el-icon><Download /></el-icon>
        <span class="detail-key">大小</span>
        <span class="detail-val font-mono">{{ formatBytes(task.downloaded_bytes || 0) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { VideoPause, VideoPlay, CircleClose, RefreshRight, Files, Download, Loading, Odometer, Clock } from '@element-plus/icons-vue'
import type { Task } from '@/api/tasks'
import { formatBytes } from '@/utils/format'

const props = defineProps<{ task: Task }>()
defineEmits<{ cancel: [id: number]; retry: [id: number]; pause: [id: number]; resume: [id: number] }>()

const progress = computed(() => {
  if (!props.task.total_count) return 0
  return Math.round((props.task.success_count / props.task.total_count) * 100)
})

function getStatusText(s: string) { const m: Record<string,string> = { running:'运行中', pending:'等待中', completed:'已完成', failed:'失败', cancelled:'已取消', paused:'已暂停' }; return m[s]||s }
function getStatusBadge(s: string) { const m: Record<string,string> = { running:'success', completed:'info', failed:'danger', pending:'warning', cancelled:'warning', paused:'warning' }; return m[s]||'info' }

function formatSpeed(bytesPerSec: number): string {
  if (!bytesPerSec || bytesPerSec <= 0) return '--'
  if (bytesPerSec > 1024 * 1024) return `${(bytesPerSec / 1024 / 1024).toFixed(1)} MB/s`
  if (bytesPerSec > 1024) return `${(bytesPerSec / 1024).toFixed(1)} KB/s`
  return `${bytesPerSec.toFixed(1)} B/s`
}
function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}秒`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}分${seconds % 60}秒`
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  return `${h}时${m}分`
}
</script>

<style scoped>
.task-card {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  transition: all var(--transition-normal);
}
.task-card:hover { transform: translateY(-1px); border-color: var(--border-strong); }
.card-top { display: flex; justify-content: space-between; align-items: flex-start; gap: var(--space-2); }
.task-meta { display: flex; align-items: center; gap: var(--space-2); flex-wrap: wrap; min-width: 0; }
.task-chat-title { font-family: var(--font-heading); font-size: 14px; font-weight: 600; color: var(--text-primary); }
.task-actions { display: flex; gap: var(--space-1); flex-shrink: 0; }
.card-progress { display: flex; flex-direction: column; gap: var(--space-1); }
.progress-header { display: flex; justify-content: space-between; }
.progress-fraction { color: var(--text-secondary); font-size: 12px; }
.progress-pct { color: var(--accent); font-size: 13px; font-weight: 600; }
.progress-track {
  height: 6px;
  background: var(--surface-2);
  border-radius: var(--radius-full);
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--transition-slow);
  position: relative;
  overflow: hidden;
}
.fill-running { background: var(--accent-gradient); }
.fill-completed { background: var(--info-gradient); }
.fill-failed { background: var(--danger-gradient); }
.fill-pending { background: var(--warning-gradient); }
.progress-shine {
  position: absolute; inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  animation: shine 2s ease-in-out infinite;
}
@keyframes shine { 0% { transform: translateX(-100%); } 100% { transform: translateX(200%); } }
.progress-extra { display: flex; gap: var(--space-3); font-size: 11px; }
.extra-fail { color: var(--danger); }
.extra-skip { color: var(--warning); }
.current-file {
  display: flex; align-items: center; gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: var(--surface-2); border-radius: var(--radius-md);
  font-size: 12px; color: var(--text-secondary);
}
.pulse-icon { color: var(--accent); animation: spin 1.5s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.card-details { display: flex; flex-direction: column; gap: var(--space-1); }
.detail { display: flex; align-items: center; gap: var(--space-2); font-size: 12px; color: var(--text-secondary); }
.detail-key { width: 40px; color: var(--text-tertiary); flex-shrink: 0; }
.detail-val { color: var(--text-primary); font-weight: 500; }
.font-mono { font-family: var(--font-mono); }

.speed-eta {
  display: flex; gap: var(--space-4); font-size: 12px; color: var(--text-secondary);
  padding-top: var(--space-1);
}
.speed-text, .eta-text { display: flex; align-items: center; gap: 4px; }
.speed-text .el-icon { color: var(--info); }
.eta-text .el-icon { color: var(--accent); }
</style>
