import api from './index'

export interface ListenSubscription {
  id: number
  account_id: number
  chat_id: string
  chat_title: string | null
  status: string
  media_types: string[] | null
  download_filter: string | null
  file_formats: Record<string, string[]> | null
  min_file_size: number | null
  max_file_size: number | null
  auto_forward: boolean
  forward_to_chat_id: string | null
  total_listened: number
  total_downloaded: number
  total_forwarded: number
  last_message_id: number
  last_processed_at: string | null
  created_at: string | null
  updated_at: string | null
}

export interface ListenSubscriptionCreate {
  account_id: number
  chat_id: string
  chat_title?: string
  media_types?: string[]
  download_filter?: string
  auto_forward?: boolean
  forward_to_chat_id?: string
}

export const listensApi = {
  listSubscriptions: () => api.get<ListenSubscription[]>('/subscriptions'),
  create: (data: ListenSubscriptionCreate) => api.post<ListenSubscription>('/subscriptions', data),
  start: (id: number) => api.post(`/subscriptions/${id}/start`),
  stop: (id: number) => api.post(`/subscriptions/${id}/stop`),
  delete: (id: number) => api.delete(`/subscriptions/${id}`),
}
