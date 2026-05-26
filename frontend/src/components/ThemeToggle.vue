<template>
  <el-dropdown @command="handleCommand" trigger="click">
    <div class="theme-toggle">
      <el-icon :size="20">
        <Sunny v-if="isDark" />
        <Moon v-else />
      </el-icon>
    </div>
    <template #dropdown>
      <el-dropdown-menu class="theme-dropdown">
        <div class="theme-dropdown-header">
          <span>主题切换</span>
        </div>
        <div class="theme-options">
          <div
            class="theme-option"
            :class="{ active: theme === 'dark' }"
            @click="setTheme('dark')"
          >
            <div class="theme-preview dark">
              <el-icon><Moon /></el-icon>
            </div>
            <span>暗色</span>
          </div>
          <div
            class="theme-option"
            :class="{ active: theme === 'light' }"
            @click="setTheme('light')"
          >
            <div class="theme-preview light">
              <el-icon><Sunny /></el-icon>
            </div>
            <span>亮色</span>
          </div>
        </div>
        <div class="theme-dropdown-footer">
          <el-text size="small" type="info">
            跟随系统
          </el-text>
        </div>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { useTheme } from '@/composables/useTheme'
import { Sunny, Moon } from '@element-plus/icons-vue'

const { theme, isDark, setTheme } = useTheme()

function handleCommand(command: string) {
  if (command === 'toggle') {
    setTheme(theme.value === 'light' ? 'dark' : 'light')
  }
}
</script>

<style scoped>
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--text-secondary);
  transition: all var(--transition-normal);
}

.theme-toggle:hover {
  background: var(--sidebar-item-hover);
  color: var(--text-primary);
}

.theme-dropdown {
  background: var(--glass-bg) !important;
  backdrop-filter: var(--glass-blur) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-lg) !important;
  padding: var(--space-sm);
  min-width: 180px !important;
}

.theme-dropdown-header {
  padding: var(--space-sm) var(--space-md);
  font-weight: 500;
  color: var(--text-primary);
  border-bottom: 1px solid var(--divider-color);
  margin-bottom: var(--space-sm);
}

.theme-options {
  display: flex;
  gap: var(--space-sm);
}

.theme-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.theme-option:hover {
  background: var(--sidebar-item-hover);
}

.theme-option.active {
  background: var(--primary-bg);
}

.theme-option.active span {
  color: var(--primary-color);
}

.theme-preview {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  border: 2px solid transparent;
  transition: all var(--transition-normal);
}

.theme-preview.dark {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: #4facfe;
}

.theme-preview.light {
  background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%);
  color: #667eea;
}

.theme-option.active .theme-preview {
  border-color: currentColor;
}

.theme-option span {
  font-size: 12px;
  color: var(--text-secondary);
}

.theme-dropdown-footer {
  padding: var(--space-sm) var(--space-md);
  margin-top: var(--space-sm);
  border-top: 1px solid var(--divider-color);
  text-align: center;
}
</style>
