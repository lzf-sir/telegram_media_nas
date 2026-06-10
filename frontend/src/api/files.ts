import api from './index'

export interface FileInfo {
  id: number
  task_id: number
  message_id: number
  chat_id: string
  file_name: string | null
  file_path: string
  file_size: number
  file_unique_id: string | null
  mime_type: string | null
  media_type: string
  duration: number | null
  width: number | null
  height: number | null
  caption: string | null
  thumbnail_path: string | null
  downloaded_at: string | null
}

/** FileInfo 别名，供视图层使用 */
export type FileItem = FileInfo

export interface FileListResponse {
  total: number
  page: number
  page_size: number
  files: FileInfo[]
}

export interface FileStats {
  total_files: number
  total_size: number
  by_media_type: Record<string, { count: number; size: number }>
  by_chat: Record<string, { count: number; size: number }>
}

export const filesApi = {
  // List files
  list: (params?: {
    page?: number
    page_size?: number
    chat_id?: string
    media_type?: string
    search?: string
  }) => api.get<FileListResponse>('/files/', { params }),

  // Get file
  get: (id: number) => api.get<FileInfo>(`/files/${id}`),

  // Delete file
  delete: (id: number) => api.delete(`/files/${id}`),

  // Batch delete
  batchDelete: (file_ids: number[]) => api.delete('/files/batch', { data: file_ids }),

  // Get stats
  getStats: () => api.get<FileStats>('/files/stats'),
}
