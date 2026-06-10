/**
 * 聊天收藏 API
 */
import api from './index'

export interface FavoriteChat {
  id: number
  chat_id: string
  chat_title: string | null
  note: string | null
  created_at: string | null
}

export const favoritesApi = {
  list: () => api.get<FavoriteChat[]>('/favorites/'),

  create: (data: { chat_id: string; chat_title?: string; note?: string }) =>
    api.post<FavoriteChat>('/favorites/', data),

  delete: (id: number) => api.delete(`/favorites/${id}`),

  deleteByChat: (chatId: string) => api.delete(`/favorites/by-chat/${chatId}`),
}
