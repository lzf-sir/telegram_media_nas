import api from './index'

export interface ActivityLog {
  id: number
  level: string
  log_type: string
  task_id: number | null
  chat_id: string | null
  message_id: number | null
  account_id: number | null
  message: string
  details: string | null
  exception_type: string | null
  exception_message: string | null
  stack_trace: string | null
  created_at: string | null
}

export interface LogListResponse {
  total: number
  limit: number
  offset: number
  logs: ActivityLog[]
}

export interface LogStats {
  by_level: Record<string, number>
  by_type: Record<string, number>
  recent_errors: ActivityLog[]
}

export const logsApi = {
  list: (params?: {
    level?: string
    log_type?: string
    task_id?: number
    chat_id?: string
    limit?: number
    offset?: number
  }) => api.get<LogListResponse>('/logs/', { params }),

  getStats: () => api.get<LogStats>('/logs/stats'),

  deleteOld: (days?: number) => api.delete('/logs/old', { params: { days } }),
}
