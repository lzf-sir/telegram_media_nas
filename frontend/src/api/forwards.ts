import api from './index'

export interface ForwardTask {
  id: number
  source_chat_id: string
  source_chat_title: string | null
  destination_chat_id: string
  destination_chat_title: string | null
  status: string
  total_count: number
  success_count: number
  failed_count: number
  skipped_count: number
  media_types: string[] | null
  download_filter: string | null
  limit: number
  offset_id: number
  forward_with_caption: boolean
  copy_media: boolean
  account_id: number | null
  created_at: string | null
  started_at: string | null
  completed_at: string | null
  updated_at: string | null
}

export interface ForwardTaskCreate {
  source_chat_id: string
  destination_chat_id: string
  source_chat_title?: string
  destination_chat_title?: string
  media_types?: string[]
  download_filter?: string
  limit?: number
  offset_id?: number
  forward_with_caption?: boolean
  copy_media?: boolean
  account_id?: number
}

export const forwardsApi = {
  list: () => api.get<ForwardTask[]>('/forwards/'),
  create: (data: ForwardTaskCreate) => api.post<ForwardTask>('/forwards/', data),
  cancel: (id: number) => api.post(`/forwards/${id}/cancel`),
  retry: (id: number) => api.post(`/forwards/${id}/retry`),
  get: (id: number) => api.get<ForwardTask>(`/forwards/${id}`),
}
