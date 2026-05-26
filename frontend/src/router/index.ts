import { createRouter, createWebHistory } from 'vue-router'
import routes from './routes'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - Telegram Media NAS`
  }

  // 检查初始化状态（仅在首次访问时）
  if (authStore.isInitialized === null) {
    await authStore.checkInitStatus()
  }

  const isAuthenticated = authStore.isAuthenticated
  const isPublicRoute = to.meta.public === true
  const requiresAuth = to.meta.requiresAuth === true

  // 未初始化 → 强制跳转到初始化页面
  if (authStore.isInitialized === false && to.name !== 'InitSetup') {
    return next({ name: 'InitSetup' })
  }

  // 已初始化但访问初始化页面 → 跳转到登录页
  if (authStore.isInitialized === true && to.name === 'InitSetup') {
    return next({ name: isAuthenticated ? 'Dashboard' : 'Login' })
  }

  // 未登录但访问需要认证的页面 → 跳转到登录页
  if (!isAuthenticated && requiresAuth && !isPublicRoute) {
    return next({ name: 'Login' })
  }

  // 已登录但访问公共页面（登录页）→ 跳转到首页
  if (isAuthenticated && isPublicRoute && to.name === 'Login') {
    return next({ name: 'Dashboard' })
  }

  next()
})

export default router
