import api from './index'

export interface TelegramAccount {
  id: number
  phone: string
  api_id: number
  api_hash: string
  user_id: number | null
  username: string | null
  first_name: string | null
  last_name: string | null
  status: string
  is_default: boolean
  session_name: string
  last_used_at: string | null
  device_model: string
  system_version: string
  app_version: string
  lang_code: string
  proxy_enabled: boolean
  proxy_type: string | null
  last_error: string | null
  created_at: string | null
  updated_at: string | null
}

export interface AccountCreate {
  phone: string
  api_id: number
  api_hash: string
  session_name?: string
  is_default?: boolean
  device_model?: string
  system_version?: string
  app_version?: string
  proxy_type?: string
  proxy_host?: string
  proxy_port?: number
}

export const accountsApi = {
  list: () => api.get<TelegramAccount[]>('/'),
  create: (data: AccountCreate) => api.post<TelegramAccount>('/', data),
  activate: (id: number) => api.post<TelegramAccount>(`/${id}/activate`),
  deactivate: (id: number) => api.post<TelegramAccount>(`/${id}/deactivate`),
  delete: (id: number) => api.delete(`/${id}`),
  getDefault: () => api.get<TelegramAccount>('/default'),
  setDefault: (id: number) => api.post<TelegramAccount>(`/${id}/set-default`),
  updateFingerprint: (id: number, data: {
    device_model?: string
    system_version?: string
    app_version?: string
  }) => api.patch<TelegramAccount>(`/${id}/fingerprint`, data),
}
