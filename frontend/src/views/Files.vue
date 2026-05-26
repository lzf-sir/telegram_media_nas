<template>
  <div class="files-view">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>文件管理</span>
          <div class="header-actions">
            <el-input
              v-model="search"
              placeholder="搜索文件"
              :prefix-icon="Search"
              clearable
              style="width: 200px; margin-right: 10px"
              @input="handleSearch"
            />
            <el-select
              v-model="mediaTypeFilter"
              placeholder="媒体类型"
              clearable
              style="width: 150px; margin-right: 10px"
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
      </template>

      <el-table
        :data="files"
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column label="文件名" prop="file_name" min-width="200">
          <template #default="{ row }">
            <div class="file-name">
              <el-icon>
                <component :is="getMediaTypeIcon(row.media_type)" />
              </el-icon>
              <span>{{ row.file_name || '未命名' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="大小" prop="file_size" width="100">
          <template #default="{ row }">{{ formatBytes(row.file_size) }}</template>
        </el-table-column>
        <el-table-column label="类型" prop="media_type" width="100">
          <template #default="{ row }">{{ row.media_type }}</template>
        </el-table-column>
        <el-table-column label="聊天ID" prop="chat_id" width="150" show-overflow-tooltip />
        <el-table-column label="下载时间" prop="downloaded_at" width="160">
          <template #default="{ row }">{{ formatDateTime(row.downloaded_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
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

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="fetchFiles"
        @size-change="fetchFiles"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

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

onMounted(() => {
  fetchFiles()
  fetchStats()
})
</script>

<style scoped>
.files-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.file-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-name .el-icon {
  font-size: 18px;
  color: #909399;
}
</style>
