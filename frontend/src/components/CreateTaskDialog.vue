<template>
  <el-dialog
    v-model="visible"
    title="创建下载任务"
    width="600px"
    @close="handleClose"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="110px">
      <!-- 聊天ID -->
      <el-form-item label="聊天ID" prop="chat_id">
        <el-input v-model="form.chat_id" placeholder="输入聊天ID或选择已有聊天" clearable />
      </el-form-item>

      <!-- 聊天名称 -->
      <el-form-item label="聊天名称" prop="chat_title">
        <el-input v-model="form.chat_title" placeholder="可选，用于显示" clearable />
      </el-form-item>

      <!-- 任务类型 -->
      <el-form-item label="任务类型" prop="task_type">
        <el-radio-group v-model="form.task_type">
          <el-radio value="onetime">
            <span>一次性任务</span>
            <el-tooltip content="通过 chat_id 一次性下载聊天/频道所有媒体" placement="top">
              <el-icon class="ml-1"><QuestionFilled /></el-icon>
            </el-tooltip>
          </el-radio>
          <el-radio value="bot" disabled>
            <span>Bot 任务</span>
            <el-tooltip content="通过 Telegram Bot 命令触发" placement="top">
              <el-icon class="ml-1"><QuestionFilled /></el-icon>
            </el-tooltip>
          </el-radio>
        </el-radio-group>
      </el-form-item>

      <!-- 媒体类型 -->
      <el-form-item label="媒体类型" prop="media_types">
        <el-checkbox-group v-model="form.media_types">
          <el-checkbox value="audio">音频</el-checkbox>
          <el-checkbox value="video">视频</el-checkbox>
          <el-checkbox value="photo">图片</el-checkbox>
          <el-checkbox value="document">文档</el-checkbox>
          <el-checkbox value="voice">语音</el-checkbox>
          <el-checkbox value="video_note">视频留言</el-checkbox>
        </el-checkbox-group>
        <div class="text-xs text-gray-500 mt-1">
          不选择则下载所有类型
        </div>
      </el-form-item>

      <!-- 文件格式过滤 -->
      <el-form-item label="格式过滤">
        <div class="w-full">
          <el-radio-group v-model="formatFilterMode" class="mb-2">
            <el-radio value="include">仅包含</el-radio>
            <el-radio value="exclude">排除</el-radio>
          </el-radio-group>

          <!-- 格式分组快速选择 -->
          <div class="mb-2">
            <el-button
              v-for="(formats, group) in FORMAT_GROUPS"
              :key="group"
              size="small"
              :type="isGroupSelected(group) ? 'primary' : 'default'"
              @click="toggleGroup(group)"
              class="mr-1 mb-1"
            >
              {{ group }}
            </el-button>
          </div>

          <!-- 格式列表 -->
          <el-scrollbar height="150px">
            <div class="grid grid-cols-4 gap-2">
              <el-checkbox
                v-for="format in allFormats"
                :key="format.extension"
                :model-value="isFormatSelected(format.extension)"
                @change="toggleFormat(format.extension)"
              >
                {{ format.extension }}
              </el-checkbox>
            </div>
          </el-scrollbar>

          <div class="text-xs text-gray-500 mt-1">
            已选择 {{ selectedFormats.size }} 种格式
          </div>
        </div>
      </el-form-item>

      <!-- 数量限制 -->
      <el-form-item label="数量限制">
        <el-input-number v-model="form.limit" :min="0" placeholder="0表示不限制" />
      </el-form-item>

      <!-- 起始ID -->
      <el-form-item label="起始ID">
        <el-input-number v-model="form.offset_id" :min="0" placeholder="从指定消息ID开始" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="submitting">
        创建任务
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'
import { useTaskStore } from '@/stores/task'
import { tasksApi, FORMAT_GROUPS, type FileExtensionInfo, type TaskCreate } from '@/api/tasks'
import type { FormInstance, FormRules } from 'element-plus'

const taskStore = useTaskStore()

const visible = defineModel<boolean>()
const formRef = ref<FormInstance>()
const submitting = ref(false)

// 格式过滤模式：include(仅包含) 或 exclude(排除)
const formatFilterMode = ref<'include' | 'exclude'>('exclude')
const selectedFormats = ref<Set<string>>(new Set())
const allFormats = ref<FileExtensionInfo[]>([])

const form = reactive<TaskCreate>({
  chat_id: '',
  chat_title: '',
  task_type: 'onetime',
  media_types: [],
  excluded_extensions: [],
  included_extensions: [],
  limit: 0,
  offset_id: 0,
})

const rules: FormRules = {
  chat_id: [{ required: true, message: '请输入聊天ID', trigger: 'blur' }],
}

// 加载可用格式
async function loadFormats() {
  try {
    const response = await tasksApi.getFormats()
    allFormats.value = response.data.by_media_type.flat()
  } catch (error) {
    console.error('加载格式列表失败:', error)
  }
}

// 判断格式是否被选中
function isFormatSelected(ext: string): boolean {
  return selectedFormats.value.has(ext)
}

// 切换格式选择
function toggleFormat(ext: string) {
  if (selectedFormats.value.has(ext)) {
    selectedFormats.value.delete(ext)
  } else {
    selectedFormats.value.add(ext)
  }
}

// 判断分组是否全部选中
function isGroupSelected(group: string): boolean {
  const formats = FORMAT_GROUPS[group as keyof typeof FORMAT_GROUPS]
  return formats.every(f => selectedFormats.value.has(f))
}

// 切换分组选择
function toggleGroup(group: string) {
  const formats = FORMAT_GROUPS[group as keyof typeof FORMAT_GROUPS]
  const allSelected = isGroupSelected(group)

  if (allSelected) {
    // 取消选择全部分组
    formats.forEach(f => selectedFormats.value.delete(f))
  } else {
    // 选择全部分组
    formats.forEach(f => selectedFormats.value.add(f))
  }
}

async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      // 根据模式设置包含或排除的格式
      if (selectedFormats.value.size > 0) {
        if (formatFilterMode.value === 'include') {
          form.included_extensions = Array.from(selectedFormats.value)
          form.excluded_extensions = []
        } else {
          form.excluded_extensions = Array.from(selectedFormats.value)
          form.included_extensions = []
        }
      } else {
        form.included_extensions = []
        form.excluded_extensions = []
      }

      await taskStore.createTask({
        chat_id: form.chat_id,
        chat_title: form.chat_title,
        task_type: form.task_type,
        media_types: form.media_types.length > 0 ? form.media_types : undefined,
        limit: form.limit,
        offset_id: form.offset_id,
        excluded_extensions: form.excluded_extensions,
        included_extensions: form.included_extensions,
      })
      ElMessage.success('任务创建成功')
      emit('created')
      handleClose()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '创建任务失败')
    } finally {
      submitting.value = false
    }
  })
}

function handleClose() {
  formRef.value?.resetFields()
  form.chat_id = ''
  form.chat_title = ''
  form.task_type = 'onetime'
  form.media_types = []
  form.limit = 0
  form.offset_id = 0
  form.excluded_extensions = []
  form.included_extensions = []
  selectedFormats.value.clear()
  formatFilterMode.value = 'exclude'
}

const emit = defineEmits<{
  created: []
}>()

onMounted(() => {
  loadFormats()
})
</script>

<style scoped>
.grid {
  display: grid;
  gap: 0.5rem;
}

.grid-cols-4 {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.text-xs {
  font-size: 0.75rem;
}

.text-gray-500 {
  color: rgb(107 114 128);
}

.mt-1 {
  margin-top: 0.25rem;
}

.mb-1 {
  margin-bottom: 0.25rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.mr-1 {
  margin-right: 0.25rem;
}

.ml-1 {
  margin-left: 0.25rem;
}
</style>
