<template>
  <div class="files-page">
    <div class="page-hero">
      <div class="hero-left">
        <h2 class="page-title">文件管理</h2>
        <p class="page-desc">搜索和管理已下载的 {{ stats?.total_files ?? 0 }} 个文件</p>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar glass-card-sm">
      <div class="search-row">
        <el-input
          v-model="search"
          placeholder="搜索文件名..."
          :prefix-icon="Search"
          clearable
          size="large"
          class="search-input"
          @input="debouncedSearch"
        />
        <el-select v-model="mediaTypeFilter" placeholder="媒体类型" clearable size="large" style="width:140px" @change="fetchFiles">
          <el-option label="图片" value="photo" />
          <el-option label="视频" value="video" />
          <el-option label="音频" value="audio" />
          <el-option label="文档" value="document" />
        </el-select>
        <el-button
          v-if="selectedFiles.length"
          type="danger"
          :icon="Delete"
          @click="handleBatchDelete"
        >
          批量删除 ({{ selectedFiles.length }})
        </el-button>
      </div>
    </div>

    <!-- 文件表格 -->
    <div class="files-table-wrapper glass-card">
      <el-table
        :data="files"
        v-loading="loading"
        @selection-change="onSelectionChange"
        class="files-table"
        row-key="id"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column label="文件名" min-width="240">
          <template #default="{ row }">
            <div class="file-name-cell">
              <div class="file-type-icon" :class="`type-${row.media_type}`">
                <el-icon :size="18"><component :is="getMediaTypeIcon(row.media_type)" /></el-icon>
              </div>
              <div class="file-name-body">
                <span class="file-name-text truncate">{{ row.file_name || '未命名' }}</span>
                <span class="file-name-meta font-mono">{{ row.chat_id }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="大小" width="100" align="right">
          <template #default="{ row }">
            <span class="font-mono">{{ formatBytes(row.file_size) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="80">
          <template #default="{ row }">
            <span class="badge" :class="`badge-${getMediaBadge(row.media_type)}`">{{ getMediaTypeText(row.media_type) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="MD5" width="120">
          <template #default="{ row }">
            <code class="md5-hash" :title="row.md5_hash">{{ row.md5_hash?.slice(0, 12) }}</code>
          </template>
        </el-table-column>
        <el-table-column label="下载时间" width="160">
          <template #default="{ row }">{{ formatDateTime(row.downloaded_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-popconfirm title="确认删除此文件？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button type="danger" size="small" :icon="Delete" link />
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="table-footer" v-if="pagination.total > 0">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @current-change="fetchFiles"
          @size-change="fetchFiles"
        />
      </div>
    </div>

    <!-- 存储统计 -->
    <div class="storage-bar glass-card-sm" v-if="stats">
      <div class="storage-item">
        <el-icon><Picture /></el-icon>
        <span>图片</span>
        <strong class="font-mono">{{ stats.by_media_type?.photo?.count ?? 0 }}</strong>
      </div>
      <div class="storage-item">
        <el-icon><VideoPlay /></el-icon>
        <span>视频</span>
        <strong class="font-mono">{{ stats.by_media_type?.video?.count ?? 0 }}</strong>
      </div>
      <div class="storage-item">
        <el-icon><Headset /></el-icon>
        <span>音频</span>
        <strong class="font-mono">{{ stats.by_media_type?.audio?.count ?? 0 }}</strong>
      </div>
      <div class="storage-item">
        <el-icon><Document /></el-icon>
        <span>文档</span>
        <strong class="font-mono">{{ stats.by_media_type?.document?.count ?? 0 }}</strong>
      </div>
      <div class="storage-item total">
        <el-icon><FolderOpened /></el-icon>
        <span>总大小</span>
        <strong class="font-mono gradient-text">{{ formatBytes(stats.total_size) }}</strong>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import {
  Search, Delete, Picture, VideoPlay, Headset, Document, FolderOpened,
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { filesApi, type FileItem, type FileStats } from '@/api/files'
import { formatBytes, formatDateTime, getMediaTypeIcon } from '@/utils/format'
import { useDebounceFn } from '@vueuse/core'

const loading = ref(false)
const files = ref<FileItem[]>([])
const stats = ref<FileStats | null>(null)
const search = ref('')
const mediaTypeFilter = ref('')
const selectedFiles = ref<FileItem[]>([])

const pagination = reactive({ page: 1, pageSize: 20, total: 0 })

const debouncedSearch = useDebounceFn(() => { pagination.page = 1; fetchFiles() }, 300)

async function fetchFiles() {
  loading.value = true
  try {
    const data: any = await filesApi.list({
      page: pagination.page,
      page_size: pagination.pageSize,
      search: search.value || undefined,
      media_type: mediaTypeFilter.value || undefined,
    })
    files.value = data.files ?? data.items ?? []
    pagination.total = data.total ?? 0
  } catch { ElMessage.error('加载文件列表失败') }
  finally { loading.value = false }
}

async function fetchStats() {
  try { stats.value = await filesApi.getStats() as any }
  catch { /* 静默处理 */ }
}

function onSelectionChange(items: FileItem[]) { selectedFiles.value = items }

async function handleDelete(row: FileItem) {
  try { await filesApi.delete(row.id); ElMessage.success('已删除'); fetchFiles(); fetchStats() }
  catch { ElMessage.error('删除失败') }
}

async function handleBatchDelete() {
  try {
    await ElMessageBox.confirm(`确认删除选中的 ${selectedFiles.value.length} 个文件？`, '批量删除', { type: 'warning' })
    await filesApi.batchDelete(selectedFiles.value.map(f => f.id))
    ElMessage.success('批量删除成功')
    fetchFiles()
    fetchStats()
  } catch { /* 取消 */ }
}

function getMediaTypeText(type: string) {
  const m: Record<string, string> = { photo: '图片', video: '视频', audio: '音频', document: '文档', voice: '语音', animation: '动画' }
  return m[type] || type
}
function getMediaBadge(type: string) {
  const m: Record<string, string> = { photo: 'accent', video: 'info', audio: 'accent', document: 'warning' }
  return m[type] || 'info'
}

onMounted(() => { fetchFiles(); fetchStats() })
</script>

<style scoped>
.files-page { display: flex; flex-direction: column; gap: var(--space-4); }
.page-hero { display: flex; align-items: flex-start; justify-content: space-between; }
.page-title { font-family: var(--font-heading); font-size: 24px; font-weight: 700; color: var(--text-primary); }
.page-desc { color: var(--text-tertiary); margin-top: var(--space-1); font-size: 14px; }

.search-bar { padding: var(--space-4); }
.search-row { display: flex; gap: var(--space-3); align-items: center; }
.search-input { flex: 1; }

.files-table-wrapper { padding: var(--space-4); flex: 1; }
.file-name-cell { display: flex; align-items: center; gap: var(--space-3); }
.file-type-icon {
  width: 36px; height: 36px; border-radius: var(--radius-md);
  display: flex; align-items: center; justify-content: center;
  color: white; flex-shrink: 0;
}
.file-type-icon.type-photo { background: var(--accent-gradient); }
.file-type-icon.type-video { background: var(--info-gradient); }
.file-type-icon.type-audio { background: var(--purple-gradient); }
.file-type-icon.type-document { background: var(--warning-gradient); }
.file-name-body { display: flex; flex-direction: column; min-width: 0; }
.file-name-text { font-weight: 500; color: var(--text-primary); }
.file-name-meta { font-size: 11px; color: var(--text-tertiary); }
.md5-hash { font-size: 11px; color: var(--text-tertiary); background: var(--surface-2); padding: 2px 6px; border-radius: var(--radius-xs); }
.table-footer { padding: var(--space-4) 0 0; display: flex; justify-content: flex-end; }

.storage-bar {
  display: flex; gap: var(--space-2); padding: var(--space-4);
  flex-wrap: wrap;
}
.storage-item {
  display: flex; align-items: center; gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  background: var(--surface-2);
  font-size: 13px; color: var(--text-secondary);
  flex: 1; min-width: 120px;
}
.storage-item.total { background: var(--glass-bg); }
.storage-item strong { color: var(--text-primary); margin-left: auto; }
.font-mono { font-family: var(--font-mono); }
</style>
