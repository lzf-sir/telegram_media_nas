<template>
  <el-dialog
    v-model="visible"
    title="创建转发任务"
    width="600px"
    @close="handleClose"
  >
    <el-form :model="form" label-width="120px">
      <el-form-item label="源聊天ID">
        <el-input v-model="form.sourceChatId" placeholder="输入源聊天ID" />
      </el-form-item>
      <el-form-item label="目标聊天ID">
        <el-input v-model="form.destinationChatId" placeholder="输入目标聊天ID" />
      </el-form-item>
      <el-form-item label="媒体类型">
        <el-checkbox-group v-model="form.mediaTypes">
          <el-checkbox label="photo">图片</el-checkbox>
          <el-checkbox label="video">视频</el-checkbox>
          <el-checkbox label="audio">音频</el-checkbox>
          <el-checkbox label="document">文档</el-checkbox>
        </el-checkbox-group>
      </el-form-item>
      <el-form-item label="数量限制">
        <el-input-number v-model="form.limit" :min="0" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleConfirm">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface ForwardForm {
  sourceChatId: string
  destinationChatId: string
  mediaTypes: string[]
  limit: number
}

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm', value: ForwardForm): void
}>()

const visible = ref(false)
const form = ref<ForwardForm>({
  sourceChatId: '',
  destinationChatId: '',
  mediaTypes: [],
  limit: 0
})

watch(() => props.modelValue, (val) => {
  visible.value = val
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const handleClose = () => {
  visible.value = false
}

const handleConfirm = () => {
  emit('confirm', form.value)
  handleClose()
}
</script>
