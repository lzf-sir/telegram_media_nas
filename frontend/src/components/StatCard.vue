<template>
  <div class="stat-card glass-card" :class="[`stat-${variant}`, { interactive: !!clickable }]" @click="clickable && $emit('click')">
    <div class="stat-icon-box" :style="{ background: `var(--${variant}-gradient)` }">
      <el-icon :size="22" color="white"><component :is="icon" /></el-icon>
    </div>
    <div class="stat-body">
      <span class="stat-value font-mono">{{ displayValue }}</span>
      <span class="stat-label">{{ title }}</span>
    </div>
    <div class="stat-bg-glow" :style="{ background: `var(--${variant}-gradient)` }"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  title: string
  value: string | number
  icon: any
  variant?: 'accent' | 'success' | 'warning' | 'danger' | 'info' | 'purple'
  clickable?: boolean
}>(), {
  variant: 'accent',
  clickable: false,
})

defineEmits<{ click: [] }>()

const displayValue = computed(() => {
  if (typeof props.value === 'number' && props.value >= 1000) {
    return props.value.toLocaleString()
  }
  return props.value
})
</script>

<style scoped>
.stat-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5);
  overflow: hidden;
  transition: all var(--transition-normal);
}
.stat-card.interactive { cursor: pointer; }
.stat-card.interactive:hover { transform: translateY(-3px); box-shadow: var(--shadow-glow-sm); }
.stat-icon-box {
  width: 48px; height: 48px;
  border-radius: var(--radius-lg);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.stat-body { display: flex; flex-direction: column; position: relative; z-index: 1; }
.stat-value { font-size: 28px; font-weight: 700; color: var(--text-primary); line-height: 1; }
.stat-label { font-size: 12px; color: var(--text-tertiary); margin-top: var(--space-1); }
.stat-bg-glow {
  position: absolute; right: -20px; bottom: -20px;
  width: 80px; height: 80px; border-radius: 50%;
  opacity: 0.08; filter: blur(30px);
}
.font-mono { font-family: var(--font-mono); }
</style>
