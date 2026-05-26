/**
 * 用户相关类型定义
 */

/** 用户信息 */
export interface User {
  id: number
  username: string
  is_admin: boolean
}

/** 登录请求 */
export interface LoginRequest {
  username: string
  password: string
}

/** 系统初始化请求 */
export interface InitRequest {
  username: string
  password: string
  password_confirm: string
}

/** Token 响应 */
export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

/** 初始化状态响应 */
export interface InitStatusResponse {
  initialized: boolean
}
