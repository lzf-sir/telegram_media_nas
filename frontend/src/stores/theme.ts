import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export type Theme = 'light' | 'dark'

const THEME_STORAGE_KEY = 'telegram-media-nas-theme'

export const useThemeStore = defineStore(
  'theme',
  () => {
    // 当前主题
    const theme = ref<Theme>('dark')

    // 初始化主题
    function initTheme() {
      // 从 localStorage 读取
      const saved = localStorage.getItem(THEME_STORAGE_KEY)
      if (saved && (saved === 'light' || saved === 'dark')) {
        theme.value = saved
      } else {
        // 检测系统偏好
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
        theme.value = prefersDark ? 'dark' : 'light'
      }
      applyTheme(theme.value)
    }

    // 应用主题
    function applyTheme(newTheme: Theme) {
      document.documentElement.setAttribute('data-theme', newTheme)
    }

    // 切换主题
    function toggleTheme() {
      theme.value = theme.value === 'light' ? 'dark' : 'light'
    }

    // 设置主题
    function setTheme(newTheme: Theme) {
      theme.value = newTheme
    }

    // 监听主题变化，保存到 localStorage 并应用
    watch(theme, (newTheme) => {
      localStorage.setItem(THEME_STORAGE_KEY, newTheme)
      applyTheme(newTheme)
    })

    return {
      theme,
      initTheme,
      toggleTheme,
      setTheme,
    }
  },
  {
    persist: false, // 我们手动处理持久化
  }
)
