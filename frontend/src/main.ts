/**
 * Telegram Media NAS v2.0 — 应用入口
 * 霓虹微光 · 玻璃拟态 · Fira 字体系统
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

import App from './App.vue'
import router from './router'

const app = createApp(App)

// 状态管理
app.use(createPinia())

// 路由
app.use(router)

// UI 框架 — 仅按需注册核心组件，其余由 unplugin 自动导入
app.use(ElementPlus, { locale: zhCn })

// 全局错误处理
app.config.errorHandler = (err, _instance, info) => {
  console.error(`[App Error] ${info}:`, err)
}

app.mount('#app')
