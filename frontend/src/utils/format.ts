import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'

export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

export function formatSpeed(bytesPerSecond: number): string {
  return formatBytes(bytesPerSecond) + '/s'
}

export function formatRelativeTime(date: string | Date): string {
  return formatDistanceToNow(new Date(date), { addSuffix: true, locale: zhCN })
}

export function formatDateTime(date: string | Date): string {
  return new Date(date).toLocaleString('zh-CN')
}

export function getMediaTypeIcon(type: string): string {
  const icons: Record<string, string> = {
    audio: 'Headset',
    video: 'VideoPlay',
    photo: 'Picture',
    document: 'Document',
    voice: 'Microphone',
    video_note: 'VideoCamera',
    animation: 'Film',
  }
  return icons[type] || 'Files'
}

export function getTaskStatusType(status: string): 'success' | 'warning' | 'danger' | 'info' {
  const types: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    completed: 'success',
    running: 'primary',
    pending: 'info',
    failed: 'danger',
    cancelled: 'warning',
  }
  return types[status] || 'info'
}
