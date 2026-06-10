import axios from 'axios'
import type { AxiosInstance } from 'axios'

const api: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if exists
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    console.error('API Error:', message)

    // 处理 401 未授权错误
    if (error.response?.status === 401) {
      // 清除过期的 token
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')

      // 如果不在登录页面，跳转到登录页
      if (window.location.pathname !== '/login' && window.location.pathname !== '/init') {
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export default api
