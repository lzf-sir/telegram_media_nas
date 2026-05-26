<template>
  <div class="stat-card glass-card" :class="`stat-card-${variant}`">
    <div class="stat-icon-wrapper" :style="{ background: gradientBg }">
      <el-icon class="stat-icon">
        <component :is="iconComponent" />
      </el-icon>
    </div>
    <div class="stat-content">
      <div class="stat-value">{{ value }}</div>
      <div class="stat-label">{{ title }}</div>
    </div>
    <div class="stat-decoration" :style="{ background: gradientBg }"></div>
  </div>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent } from 'vue'

const props = withDefaults(
  defineProps<{
    title: string
    value: number
    icon: string
    color?: string
    variant?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  }>(),
  {
    variant: 'primary',
  }
)

// Dynamic icon component
const iconComponent = defineAsyncComponent(() => {
  return import(`@element-plus/icons-vue`).then((mod) => mod[props.icon])
})

// 渐变背景
const gradientBg = computed(() => {
  const gradients = {
    primary: 'var(--primary-gradient)',
    success: 'var(--success-gradient)',
    warning: 'var(--warning-gradient)',
    danger: 'var(--danger-gradient)',
    info: 'var(--info-gradient)',
  }
  return gradients[props.variant] || gradients.primary
})
</script>

<style scoped>
.stat-card {
  position: relative;
  overflow: hidden;
  padding: var(--space-lg);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-glow-primary);
}

.stat-card.stat-card-success:hover {
  box-shadow: var(--shadow-glow-success);
}

.stat-card.stat-card-danger:hover {
  box-shadow: var(--shadow-glow-danger);
}

.stat-icon-wrapper {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-md);
}

.stat-icon-wrapper .stat-icon {
  font-size: 28px;
  color: #ffffff;
}

.stat-content {
  position: relative;
  z-index: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
  color: var(--text-primary);
  margin-bottom: var(--space-xs);
}

.stat-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-decoration {
  position: absolute;
  right: -20px;
  top: -20px;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  opacity: 0.1;
  transition: all var(--transition-slow);
}

.stat-card:hover .stat-decoration {
  transform: scale(1.5);
  opacity: 0.15;
}
</style>
