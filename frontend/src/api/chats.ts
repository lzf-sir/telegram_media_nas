import api from './index'

export interface Dialog {
  id: string
  title: string
  username: string | null
  type: string
  photo_url: string | null
}

export interface ChatSubscription {
  id: number
  chat_id: string
  chat_title: string
  chat_username: string | null
  chat_type: string
  is_active: boolean
  media_types: string[] | null
  download_filter: string | null
  auto_download: boolean
  last_read_message_id: number
  total_downloaded: number
  created_at: string | null
  updated_at: string | null
}

export interface ChatSubscribe {
  chat_id: string
  chat_title: string
  chat_username?: string
  chat_type: string
  media_types?: string[]
  download_filter?: string
  auto_download?: boolean
}

export const chatsApi = {
  // Get dialogs
  getDialogs: (limit?: number) => api.get<Dialog[]>('/dialogs', { params: { limit } }),

  // List subscriptions
  listSubscriptions: () => api.get<ChatSubscription[]>('/subscriptions'),

  // Subscribe
  subscribe: (data: ChatSubscribe) => api.post<ChatSubscription>('/subscribe', data),

  // Get subscription
  getSubscription: (chat_id: string) => api.get<ChatSubscription>(`/subscriptions/${chat_id}`),

  // Update subscription
  updateSubscription: (chat_id: string, data: Partial<ChatSubscribe>) =>
    api.put<ChatSubscription>(`/subscriptions/${chat_id}`, data),

  // Unsubscribe
  unsubscribe: (chat_id: string) => api.delete(`/subscriptions/${chat_id}`),
}
