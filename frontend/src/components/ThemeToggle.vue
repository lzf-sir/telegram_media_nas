<template>
  <button class="theme-toggle-btn" @click="toggle" :title="isDark ? '切换到亮色模式' : '切换到暗色模式'">
    <transition name="pop" mode="out-in">
      <el-icon :key="theme" :size="18">
        <Sunny v-if="isDark" />
        <Moon v-else />
      </el-icon>
    </transition>
  </button>
</template>

<script setup lang="ts">
import { useTheme } from '@/composables/useTheme'
import { Sunny, Moon } from '@element-plus/icons-vue'

const { theme, isDark, toggleTheme } = useTheme()

function toggle() {
  toggleTheme()
}
</script>

<style scoped>
.theme-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  border: none;
  background: none;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all var(--transition-fast);
}
.theme-toggle-btn:hover {
  background: var(--glass-bg-hover);
  color: var(--text-primary);
}
</style>
