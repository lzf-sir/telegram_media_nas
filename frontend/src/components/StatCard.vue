<template>
  <el-card shadow="hover" class="stat-card">
    <div class="stat-content">
      <el-icon class="stat-icon" :style="{ color: color }">
        <component :is="icon" />
      </el-icon>
      <div class="stat-info">
        <div class="stat-value">{{ value }}</div>
        <div class="stat-label">{{ title }}</div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { defineAsyncComponent } from 'vue'

const props = defineProps<{
  title: string
  value: number
  icon: string
  color: string
}>()

// Dynamic icon component
const icon = defineAsyncComponent(() => {
  return import(`@element-plus/icons-vue`).then((mod) => mod[props.icon])
})
</script>

<style scoped>
.stat-card {
  border: none;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  font-size: 36px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}
</style>
