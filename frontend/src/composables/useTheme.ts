import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme'
import type { Theme } from '@/stores/theme'

export function useTheme() {
  const themeStore = useThemeStore()

  const theme = computed(() => themeStore.theme)
  const isDark = computed(() => theme.value === 'dark')
  const isLight = computed(() => theme.value === 'light')

  function toggleTheme() {
    themeStore.toggleTheme()
  }

  function setTheme(newTheme: Theme) {
    themeStore.setTheme(newTheme)
  }

  return {
    theme,
    isDark,
    isLight,
    toggleTheme,
    setTheme,
  }
}
