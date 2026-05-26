/**
 * 认证状态管理
 */
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { ElMessage } from 'element-plus'
import { authApi, tokenUtil } from '@/api/auth'
import type { User, LoginRequest, InitRequest } from '@/types/user'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref<User | null>(tokenUtil.getUser())
  const token = ref<string | null>(tokenUtil.getToken())
  const isInitialized = ref<boolean | null>(null)
  const loading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  /**
   * 检查系统初始化状态
   */
  async function checkInitStatus() {
    try {
      const result = await authApi.getInitStatus()
      isInitialized.value = result.initialized
    } catch (error) {
      console.error('Failed to check init status:', error)
      // 如果请求失败，假设未初始化
      isInitialized.value = false
    }
  }

  /**
   * 初始化系统
   */
  async function initialize(data: InitRequest) {
    loading.value = true
    try {
      const response = await authApi.init(data)

      // 保存 token 和用户信息
      token.value = response.access_token
      user.value = response.user
      tokenUtil.saveToken(response.access_token, response.user)

      // 更新初始化状态
      isInitialized.value = true

      ElMessage.success('系统初始化成功')
      return true
    } catch (error: any) {
      const message = error.response?.data?.detail || '初始化失败'
      ElMessage.error(message)
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 登录
   */
  async function login(data: LoginRequest) {
    loading.value = true
    try {
      const response = await authApi.login(data)

      // 保存 token 和用户信息
      token.value = response.access_token
      user.value = response.user
      tokenUtil.saveToken(response.access_token, response.user)

      ElMessage.success('登录成功')
      return true
    } catch (error: any) {
      const message = error.response?.data?.detail || '登录失败'
      ElMessage.error(message)
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 退出登录
   */
  async function logout() {
    try {
      await authApi.logout()
    } catch (error) {
      console.error('Logout API error:', error)
    } finally {
      // 无论 API 是否成功，都清除本地状态
      token.value = null
      user.value = null
      tokenUtil.clearToken()
      ElMessage.success('已退出登录')
    }
  }

  /**
   * 获取当前用户信息
   */
  async function fetchCurrentUser() {
    if (!token.value) {
      return false
    }

    try {
      const currentUser = await authApi.me()
      user.value = currentUser
      tokenUtil.saveToken(token.value, currentUser)
      return true
    } catch (error) {
      // Token 可能已过期，清除本地状态
      token.value = null
      user.value = null
      tokenUtil.clearToken()
      return false
    }
  }

  return {
    // 状态
    user,
    token,
    isInitialized,
    loading,
    // 计算属性
    isAuthenticated,
    // 方法
    checkInitStatus,
    initialize,
    login,
    logout,
    fetchCurrentUser,
  }
})
