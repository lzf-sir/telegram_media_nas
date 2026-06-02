/**
 * 系统设置 API
 */
import api from './index'

/** Telegram 设置 */
export interface TelegramSettings {
  api_id: number
  api_hash: string
  phone: string
  configured: boolean
}

/** 下载设置 */
export interface DownloadSettings {
  max_concurrent_downloads: number
  download_timeout: number
  download_path: string
}

/** Bot 安全设置 */
export interface BotSettings {
  rate_limit: number          // 每分钟最大请求数，0 表示不限制
  whitelist_enabled: boolean  // 是否启用白名单
  whitelist_users: string[]   // 白名单用户列表
}

/** 系统设置 API */
export const settingsApi = {
  // ==================== Telegram 设置 ====================
  getTelegramSettings: () =>
    api.get<TelegramSettings>('/settings/telegram'),

  updateTelegramSettings: (data: Omit<TelegramSettings, 'configured'>) =>
    api.put('/settings/telegram', data),

  // ==================== 下载设置 ====================
  getDownloadSettings: () =>
    api.get<DownloadSettings>('/settings/download'),

  updateDownloadSettings: (data: DownloadSettings) =>
    api.put('/settings/download', data),

  // ==================== Bot 安全设置 ====================
  getBotSettings: () =>
    api.get<BotSettings>('/settings/bot'),

  updateBotSettings: (data: BotSettings) =>
    api.put('/settings/bot', data),

  // ==================== 通用设置 ====================
  getAllSettings: () =>
    api.get<Record<string, unknown>>('/settings/all'),

  /** @deprecated 使用 getAllSettings */
  getAll: () =>
    api.get<{ telegram?: TelegramSettings; download?: DownloadSettings }>('/settings/all'),

  /** @deprecated 使用 updateTelegramSettings */
  updateTelegram: (data: Omit<TelegramSettings, 'configured'>) =>
    api.put('/settings/telegram', data),

  /** 测试 Telegram 连接 */
  testTelegramConnection: () =>
    api.post('/settings/telegram/test'),

  /** @deprecated 使用 updateDownloadSettings */
  updateDownload: (data: DownloadSettings) =>
    api.put('/settings/download', data),

  getSetting: (key: string) =>
    api.get<{ key: string; value: string; value_type: string }>(`/settings/${key}`),

  updateSetting: (key: string, value: string, valueType?: string) =>
    api.put(`/settings/${key}`, { value, value_type: valueType }),
}
