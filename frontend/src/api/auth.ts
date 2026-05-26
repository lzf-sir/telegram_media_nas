/**
 * 认证相关 API
 */
import api from './index'
import type {
  LoginRequest,
  InitRequest,
  TokenResponse,
  User,
  InitStatusResponse,
} from '@/types/user'

/** Token 存储键名 */
const TOKEN_KEY = 'access_token'
const USER_KEY = 'user_info'

/** 认证 API */
export const authApi = {
  /** 获取系统初始化状态 */
  getInitStatus: () =>
    api.get<InitStatusResponse>('/auth/init-status'),

  /** 初始化系统 */
  init: (data: InitRequest) =>
    api.post<TokenResponse>('/auth/init', data),

  /** 登录 */
  login: (data: LoginRequest) =>
    api.post<TokenResponse>('/auth/login', data),

  /** 获取当前用户信息 */
  me: () =>
    api.get<User>('/auth/me'),

  /** 退出登录 */
  logout: () =>
    api.post('/auth/logout'),
}

/** Token 工具函数 */
export const tokenUtil = {
  /** 保存 token */
  saveToken: (token: string, user: User) => {
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  },

  /** 获取 token */
  getToken: () => localStorage.getItem(TOKEN_KEY),

  /** 获取用户信息 */
  getUser: (): User | null => {
    const userStr = localStorage.getItem(USER_KEY)
    if (userStr) {
      try {
        return JSON.parse(userStr)
      } catch {
        return null
      }
    }
    return null
  },

  /** 清除 token 和用户信息 */
  clearToken: () => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  },

  /** 检查是否已登录 */
  isAuthenticated: () => !!localStorage.getItem(TOKEN_KEY),
}
