<template>
  <div class="files-view">
    <div class="files-header">
      <div class="header-left">
        <h2 class="page-title-section">文件管理</h2>
        <p class="page-subtitle">管理和搜索已下载的文件</p>
      </div>
      <div class="header-actions">
        <el-input
          v-model="search"
          placeholder="搜索文件"
          :prefix-icon="Search"
          clearable
          class="search-input"
          @input="handleSearch"
        />
        <el-select
          v-model="mediaTypeFilter"
          placeholder="媒体类型"
          clearable
          class="filter-select"
          @change="handleSearch"
        >
          <el-option label="音频" value="audio" />
          <el-option label="视频" value="video" />
          <el-option label="图片" value="photo" />
          <el-option label="文档" value="document" />
        </el-select>
        <el-button
          type="danger"
          :icon="Delete"
          :disabled="selectedFiles.length === 0"
          @click="handleBatchDelete"
        >
          批量删除 ({{ selectedFiles.length }})
        </el-button>
      </div>
    </div>

    <div class="files-content glass-card">
      <el-table
        :data="files"
        v-loading="loading"
        @selection-change="handleSelectionChange"
        class="files-table"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column label="文件名" prop="file_name" min-width="220">
          <template #default="{ row }">
            <div class="file-name">
              <div class="file-icon" :class="`icon-${row.media_type}`">
                <el-icon>
                  <component :is="getMediaTypeIcon(row.media_type)" />
                </el-icon>
              </div>
              <span>{{ row.file_name || '未命名' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="大小" prop="file_size" width="110">
          <template #default="{ row }">{{ formatBytes(row.file_size) }}</template>
        </el-table-column>
        <el-table-column label="类型" prop="media_type" width="100">
          <template #default="{ row }">
            <span class="media-type-badge">{{ getMediaTypeText(row.media_type) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="聊天ID" prop="chat_id" width="140" show-overflow-tooltip />
        <el-table-column label="下载时间" prop="downloaded_at" width="170">
          <template #default="{ row }">{{ formatDateTime(row.downloaded_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button
              type="danger"
              size="small"
              :icon="Delete"
              link
              @click="handleDelete(row)"
            />
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="fetchFiles"
          @size-change="fetchFiles"
        />
      </div>
    </div>

    <stats-card :stats="stats" :loading="statsLoading" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search, Delete } from '@element-plus/icons-vue'
import { filesApi, type FileInfo, type FileStats } from '@/api/files'
import { formatBytes, formatDateTime, getMediaTypeIcon } from '@/utils/format'
import StatsCard from '@/components/StatsCard.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const files = ref<FileInfo[]>([])
const stats = ref<FileStats | null>(null)
const loading = ref(false)
const statsLoading = ref(false)
const search = ref('')
const mediaTypeFilter = ref('')
const selectedFiles = ref<FileInfo[]>([])

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0,
})

async function fetchFiles() {
  loading.value = true
  try {
    const response = await filesApi.list({
      page: pagination.value.page,
      page_size: pagination.value.pageSize,
      search: search.value || undefined,
      media_type: mediaTypeFilter.value || undefined,
    })
    files.value = response.files
    pagination.value.total = response.total
  } catch (error) {
    ElMessage.error('加载文件列表失败')
  } finally {
    loading.value = false
  }
}

async function fetchStats() {
  statsLoading.value = true
  try {
    stats.value = await filesApi.getStats()
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  } finally {
    statsLoading.value = false
  }
}

function handleSearch() {
  pagination.value.page = 1
  fetchFiles()
}

function handleSelectionChange(selection: FileInfo[]) {
  selectedFiles.value = selection
}

async function handleDelete(file: FileInfo) {
  try {
    await ElMessageBox.confirm(`确定要删除文件 "${file.file_name}" 吗？`, '确认删除', {
      type: 'warning',
    })
    await filesApi.delete(file.id)
    ElMessage.success('删除成功')
    fetchFiles()
    fetchStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function handleBatchDelete() {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedFiles.value.length} 个文件吗？`,
      '确认删除',
      { type: 'warning' }
    )
    const ids = selectedFiles.value.map((f) => f.id)
    await filesApi.batchDelete(ids)
    ElMessage.success(`成功删除 ${selectedFiles.value.length} 个文件`)
    selectedFiles.value = []
    fetchFiles()
    fetchStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function getMediaTypeText(type: string): string {
  const texts: Record<string, string> = {
    audio: '音频',
    video: '视频',
    photo: '图片',
    document: '文档',
    voice: '语音',
    video_note: '视频留言',
    animation: '动画',
  }
  return texts[type] || type
}

onMounted(() => {
  fetchFiles()
  fetchStats()
})
</script>

<style scoped>
.files-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

/* ============================================
   头部样式
   ============================================ */
.files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-md);
}

.header-left {
  flex: 1;
}

.page-title-section {
  margin: 0 0 var(--space-xs) 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.page-subtitle {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  flex-wrap: wrap;
}

.search-input {
  width: 200px;
}

.filter-select {
  width: 140px;
}

/* ============================================
   内容区域
   ============================================ */
.files-content {
  padding: var(--space-lg);
  min-height: 400px;
}

:deep(.files-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: transparent;
}

:deep(.files-table .el-table__body-wrapper) {
  background: transparent;
}

:deep(.files-table tr) {
  background: transparent !important;
}

:deep(.files-table th.el-table__cell) {
  background: transparent !important;
  color: var(--text-secondary);
  font-weight: 500;
  border-bottom: 1px solid var(--divider-color);
}

:deep(.files-table td.el-table__cell) {
  border-bottom: 1px solid var(--divider-color);
}

:deep(.files-table .el-table__row:hover td.el-table__cell) {
  background: var(--sidebar-item-hover) !important;
}

/* 文件名 */
.file-name {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.file-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  font-size: 16px;
}

.file-icon.icon-audio {
  background: var(--warning-bg);
  color: var(--warning-color);
}

.file-icon.icon-video {
  background: var(--danger-bg);
  color: var(--danger-color);
}

.file-icon.icon-photo {
  background: var(--success-bg);
  color: var(--success-color);
}

.file-icon.icon-document {
  background: var(--primary-bg);
  color: var(--primary-color);
}

.file-icon.icon-voice {
  background: var(--info-bg);
  color: var(--info-color);
}

.media-type-badge {
  padding: var(--space-xs) var(--space-sm);
  background: var(--glass-bg);
  border-radius: var(--radius-sm);
  font-size: 12px;
  color: var(--text-secondary);
}

/* 分页 */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--space-lg);
  padding-top: var(--space-md);
  border-top: 1px solid var(--divider-color);
}

/* ============================================
   响应式设计
   ============================================ */
@media (max-width: 768px) {
  .files-header {
    flex-direction: column;
    align-items: stretch;
  }

  .page-title-section {
    font-size: 20px;
  }

  .header-actions {
    flex-direction: column;
    width: 100%;
  }

  .search-input,
  .filter-select {
    width: 100%;
  }
}
</style>
