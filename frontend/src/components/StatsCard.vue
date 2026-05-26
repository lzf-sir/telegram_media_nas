<template>
  <el-row :gutter="20" class="stats-row">
    <el-col :span="6">
      <el-card shadow="hover">
        <div class="stat-item">
          <el-icon class="stat-icon files"><Files /></el-icon>
          <div class="stat-content">
            <div class="stat-value">{{ stats?.total_files || 0 }}</div>
            <div class="stat-label">总文件数</div>
          </div>
        </div>
      </el-card>
    </el-col>
    <el-col :span="6">
      <el-card shadow="hover">
        <div class="stat-item">
          <el-icon class="stat-icon size"><PieChart /></el-icon>
          <div class="stat-content">
            <div class="stat-value">{{ formatBytes(stats?.total_size || 0) }}</div>
            <div class="stat-label">总大小</div>
          </div>
        </div>
      </el-card>
    </el-col>
    <el-col :span="12">
      <el-card shadow="hover">
        <div class="stat-item inline">
          <div class="media-types">
            <div
              v-for="(item, type) in stats?.by_media_type"
              :key="type"
              class="media-type-item"
            >
              <el-tag size="small">{{ type }}</el-tag>
              <span>{{ item.count }} 个</span>
            </div>
          </div>
        </div>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
import { Files, PieChart } from '@element-plus/icons-vue'
import { formatBytes } from '@/utils/format'
import type { FileStats } from '@/api/files'

defineProps<{
  stats: FileStats | null
  loading: boolean
}>()
</script>

<style scoped>
.stats-row {
  margin-top: 0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-item.inline {
  width: 100%;
}

.stat-icon {
  font-size: 32px;
  color: #409eff;
}

.stat-icon.size {
  color: #67c23a;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.media-types {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  width: 100%;
}

.media-type-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}
</style>
