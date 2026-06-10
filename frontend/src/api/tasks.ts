import api from './index'

// 任务类型枚举
export enum TaskType {
  BOT = 'bot',           // Bot 任务：通过 Bot 命令触发
  ONETIME = 'onetime'    // 一次性任务：通过 Web 面板创建
}

// 任务状态枚举
export enum TaskStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  PAUSED = 'paused',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

// 媒体类型枚举
export enum MediaType {
  AUDIO = 'audio',
  DOCUMENT = 'document',
  PHOTO = 'photo',
  VIDEO = 'video',
  VOICE = 'voice',
  VIDEO_NOTE = 'video_note',
  ANIMATION = 'animation'
}

// 文件扩展名信息
export interface FileExtensionInfo {
  extension: string
  name: string
  media_type: string
  description: string
}

// 可用格式响应
export interface AvailableFormats {
  by_media_type: Record<string, FileExtensionInfo[]>
  all_extensions: string[]
}

// 任务创建请求
export interface TaskCreate {
  chat_id: string
  chat_title?: string
  task_type?: TaskType
  media_types?: string[]
  download_filter?: string
  excluded_extensions?: string[]  // 排除的文件扩展名
  included_extensions?: string[]  // 包含的文件扩展名（优先级更高）
  limit?: number
  offset_id?: number
}

// 任务响应
export interface Task {
  id: number
  chat_id: string
  chat_title: string | null
  task_type: string
  status: string
  total_count: number
  success_count: number
  failed_count: number
  skipped_count: number
  downloaded_bytes: number
  total_bytes: number
  stats_by_type: Record<string, number>
  stats_by_format: Record<string, number>
  current_file_id?: number
  current_file_name?: string
  current_file_size?: number
  current_file_progress: number
  media_types: string[] | null
  download_filter: string | null
  excluded_extensions: string[] | null
  included_extensions: string[] | null
  limit: number
  offset_id: number
  created_at: string | null
  started_at: string | null
  completed_at: string | null
  updated_at: string | null
  progress?: number
  download_speed?: number
  eta_seconds?: number
}

// 任务详情（包含文件列表）
export interface TaskDetail extends Task {
  files: any[]
  summary?: {
    total_files: number
    total_size: number
    by_type: Record<string, number>
    by_format: Record<string, number>
    completion_rate: number
  }
}

// 任务统计
export interface TaskStats {
  task_id: number
  status: string
  progress: {
    total: number
    success: number
    failed: number
    skipped: number
    bytes_downloaded: number
    total_bytes: number
  }
  by_media_type: Array<{
    type: string
    count: number
    total_size: number
  }>
  by_format: Array<{
    extension: string
    count: number
  }>
  current_file?: {
    id: number
    name: string
    size: number
    progress: number
  }
}

export const tasksApi = {
  // 创建任务
  create: (data: TaskCreate) => api.post<Task>('/tasks/', data),

  // 获取任务列表
  list: (params?: { status?: string; task_type?: string; limit?: number; offset?: number }) =>
    api.get<Task[]>('/tasks/', { params }),

  // 获取任务详情
  get: (id: number) => api.get<TaskDetail>(`/tasks/${id}`),

  // 获取任务统计
  getStats: (id: number) => api.get<TaskStats>(`/tasks/${id}/stats`),

  // 获取可用文件格式
  getFormats: () => api.get<AvailableFormats>('/tasks/formats/available'),

  // 取消任务
  cancel: (id: number) => api.delete(`/tasks/${id}`),

  // 重试任务
  retry: (id: number) => api.post(`/tasks/${id}/retry`),

  // 暂停任务
  pause: (id: number) => api.post(`/tasks/${id}/pause`),

  // 恢复任务
  resume: (id: number) => api.post(`/tasks/${id}/resume`),

  // 获取任务文件
  getFiles: (id: number, params?: { media_type?: string; limit?: number; offset?: number }) =>
    api.get(`/tasks/${id}/files`, { params }),
}

// 预定义的文件格式分组（用于 UI 显示）
export const FORMAT_GROUPS = {
  图片: ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.svg', '.ico'],
  视频: ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.ts', '.rmvb'],
  音频: ['.mp3', '.flac', '.aac', '.ogg', '.wav', '.m4a', '.wma', '.opus', '.ape'],
  文档: ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf', '.csv', '.epub', '.mobi'],
  压缩: ['.zip', '.rar', '.7z', '.tar', '.gz'],
  可执行: ['.exe', '.apk', '.dmg', '.iso'],
}

// 常见需要排除的文件格式
export const COMMON_EXCLUDED_FORMATS = [
  '.exe', '.dll', '.so', '.bat', '.sh', '.cmd',  // 可执行文件
  '.tmp', '.temp', '.cache',                      // 临时文件
]
