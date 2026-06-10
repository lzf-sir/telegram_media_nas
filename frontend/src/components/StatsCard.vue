<template>
  <div class="stats-card glass-card">
    <div v-if="loading" class="loading-row">
      <div class="skeleton" style="height:48px"></div>
      <div class="skeleton" style="height:48px"></div>
      <div class="skeleton" style="height:48px"></div>
    </div>
    <div v-else class="stats-row">
      <div class="stat-cell">
        <el-icon :size="20" color="var(--info)"><Files /></el-icon>
        <div>
          <span class="font-mono stat-num">{{ stats?.total_files ?? 0 }}</span>
          <span class="stat-sub">总文件</span>
        </div>
      </div>
      <div class="stat-cell">
        <el-icon :size="20" color="var(--accent)"><FolderOpened /></el-icon>
        <div>
          <span class="font-mono stat-num">{{ formatBytes(stats?.total_size ?? 0) }}</span>
          <span class="stat-sub">总大小</span>
        </div>
      </div>
      <div class="stat-cell types-cell">
        <div v-for="(item, type) in stats?.by_media_type" :key="type" class="type-chip">
          <el-tag size="small" round>{{ type }}</el-tag>
          <span class="font-mono">{{ item.count }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Files, FolderOpened } from '@element-plus/icons-vue'
import { formatBytes } from '@/utils/format'
import type { FileStats } from '@/api/files'

defineProps<{ stats: FileStats | null; loading: boolean }>()
</script>

<style scoped>
.stats-card { padding: var(--space-4); }
.loading-row { display: flex; gap: var(--space-4); }
.stats-row { display: flex; gap: var(--space-4); flex-wrap: wrap; align-items: center; }
.stat-cell {
  display: flex; align-items: center; gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: var(--surface-2);
  border-radius: var(--radius-md);
}
.stat-num { font-size: 18px; font-weight: 700; color: var(--text-primary); }
.stat-sub { font-size: 11px; color: var(--text-tertiary); margin-left: var(--space-1); }
.types-cell { display: flex; gap: var(--space-2); flex-wrap: wrap; background: none; padding: 0; }
.type-chip { display: flex; align-items: center; gap: var(--space-1); font-size: 12px; color: var(--text-secondary); }
.font-mono { font-family: var(--font-mono); }
</style>
