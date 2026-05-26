<template>
  <el-dialog
    v-model="visible"
    title="订阅聊天"
    width="600px"
    @open="handleOpen"
  >
    <el-tabs v-model="activeTab">
      <el-tab-pane label="从对话列表选择" name="dialogs">
        <div class="dialogs-section">
          <el-input
            v-model="searchQuery"
            placeholder="搜索聊天..."
            :prefix-icon="Search"
            clearable
            style="margin-bottom: 16px"
            @input="handleSearch"
          />
          <el-table
            :data="filteredDialogs"
            v-loading="loading"
            height="300"
            @row-click="handleSelectDialog"
            style="cursor: pointer"
          >
            <el-table-column prop="title" label="名称" min-width="150" />
            <el-table-column prop="username" label="用户名" width="120">
              <template #default="{ row }">
                {{ row.username || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="类型" width="100">
              <template #default="{ row }">{{ getChatTypeText(row.type) }}</template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="手动输入" name="manual">
        <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
          <el-form-item label="聊天ID" prop="chat_id">
            <el-input v-model="form.chat_id" placeholder="输入聊天ID或用户名" />
          </el-form-item>
          <el-form-item label="聊天名称" prop="chat_title">
            <el-input v-model="form.chat_title" placeholder="用于显示的名称" />
          </el-form-item>
          <el-form-item label="聊天类型" prop="chat_type">
            <el-select v-model="form.chat_type" style="width: 100%">
              <el-option label="频道" value="channel" />
              <el-option label="群组" value="supergroup" />
              <el-option label="私聊" value="private" />
            </el-select>
          </el-form-item>
          <el-form-item label="媒体类型">
            <el-checkbox-group v-model="form.media_types">
              <el-checkbox label="audio">音频</el-checkbox>
              <el-checkbox label="video">视频</el-checkbox>
              <el-checkbox label="photo">图片</el-checkbox>
              <el-checkbox label="document">文档</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          <el-form-item label="自动下载">
            <el-switch v-model="form.auto_download" />
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="submitting">
        订阅
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { chatsApi, type Dialog } from '@/api/chats'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

const visible = defineModel<boolean>()
const formRef = ref<FormInstance>()
const activeTab = ref('dialogs')
const loading = ref(false)
const submitting = ref(false)
const searchQuery = ref('')
const dialogs = ref<Dialog[]>([])

const form = reactive({
  chat_id: '',
  chat_title: '',
  chat_username: '',
  chat_type: 'channel',
  media_types: [] as string[],
  auto_download: false,
})

const rules: FormRules = {
  chat_id: [{ required: true, message: '请输入聊天ID', trigger: 'blur' }],
  chat_title: [{ required: true, message: '请输入聊天名称', trigger: 'blur' }],
  chat_type: [{ required: true, message: '请选择聊天类型', trigger: 'change' }],
}

const filteredDialogs = computed(() => {
  if (!searchQuery.value) return dialogs.value
  const query = searchQuery.value.toLowerCase()
  return dialogs.value.filter(
    (d) =>
      d.title?.toLowerCase().includes(query) ||
      d.username?.toLowerCase().includes(query)
  )
})

async function handleOpen() {
  if (activeTab.value === 'dialogs') {
    await loadDialogs()
  }
}

async function loadDialogs() {
  loading.value = true
  try {
    dialogs.value = await chatsApi.getDialogs(100)
  } catch (error) {
    ElMessage.error('加载对话列表失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  // Filter is computed
}

function handleSelectDialog(dialog: Dialog) {
  form.chat_id = dialog.id
  form.chat_title = dialog.title
  form.chat_username = dialog.username || undefined
  form.chat_type = dialog.type
  activeTab.value = 'manual'
}

async function handleSubmit() {
  if (activeTab.value === 'manual') {
    if (!formRef.value) return
    await formRef.value.validate(async (valid) => {
      if (!valid) return

      submitting.value = true
      try {
        await chatsApi.subscribe({
          chat_id: form.chat_id,
          chat_title: form.chat_title,
          chat_username: form.chat_username,
          chat_type: form.chat_type,
          media_types: form.media_types.length > 0 ? form.media_types : undefined,
          auto_download: form.auto_download,
        })
        ElMessage.success('订阅成功')
        emit('subscribed')
        visible.value = false
        resetForm()
      } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || '订阅失败')
      } finally {
        submitting.value = false
      }
    })
  }
}

function resetForm() {
  formRef.value?.resetFields()
  form.chat_id = ''
  form.chat_title = ''
  form.chat_username = ''
  form.chat_type = 'channel'
  form.media_types = []
  form.auto_download = false
}

function getChatTypeText(type: string): string {
  const types: Record<string, string> = {
    private: '私聊',
    group: '群组',
    supergroup: '超级群组',
    channel: '频道',
  }
  return types[type] || type
}

const emit = defineEmits<{
  subscribed: []
}>()
</script>

<style scoped>
.dialogs-section {
  display: flex;
  flex-direction: column;
}

.el-table :deep(.el-table__row) {
  cursor: pointer;
}

.el-table :deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}
</style>
