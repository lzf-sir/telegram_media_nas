/** @type {import('vue-router').RouterOptions['routes']} */
import MainLayout from '@/layouts/MainLayout.vue'

export default [
  // 公共路由 - 不需要认证
  {
    path: '/init',
    name: 'InitSetup',
    component: () => import('@/views/InitSetup.vue'),
    meta: {
      title: '系统初始化',
      public: true,
    },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: {
      title: '登录',
      public: true,
    },
  },
  // 主路由 - 需要认证
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard',
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表板' },
      },
      {
        path: 'tasks',
        name: 'Tasks',
        component: () => import('@/views/Tasks.vue'),
        meta: { title: '下载任务' },
      },
      {
        path: 'forwards',
        name: 'Forwards',
        component: () => import('@/views/Forwards.vue'),
        meta: { title: '转发任务' },
      },
      {
        path: 'listens',
        name: 'Listens',
        component: () => import('@/views/Listens.vue'),
        meta: { title: '实时监听' },
      },
      {
        path: 'files',
        name: 'Files',
        component: () => import('@/views/Files.vue'),
        meta: { title: '文件管理' },
      },
      {
        path: 'chats',
        name: 'Chats',
        component: () => import('@/views/Chats.vue'),
        meta: { title: '聊天订阅' },
      },
      {
        path: 'accounts',
        name: 'Accounts',
        component: () => import('@/views/Accounts.vue'),
        meta: { title: '账号管理' },
      },
      {
        path: 'logs',
        name: 'Logs',
        component: () => import('@/views/Logs.vue'),
        meta: { title: '操作日志' },
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '系统设置' },
      },
    ],
  },
]
