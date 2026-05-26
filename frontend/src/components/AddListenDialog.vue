<template>
  <el-dialog
    v-model="visible"
    title="添加监听订阅"
    width="600px"
    @close="handleClose"
  >
    <el-form :model="form" label-width="120px">
      <el-form-item label="账号">
        <el-select v-model="form.accountId" placeholder="选择账号">
          <el-option
            v-for="account in accounts"
            :key="account.id"
            :label="account.phone"
            :value="account.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="聊天ID">
        <el-input v-model="form.chatId" placeholder="输入要监听的聊天ID" />
      </el-form-item>
      <el-form-item label="媒体类型">
        <el-checkbox-group v-model="form.mediaTypes">
          <el-checkbox label="photo">图片</el-checkbox>
          <el-checkbox label="video">视频</el-checkbox>
          <el-checkbox label="audio">音频</el-checkbox>
          <el-checkbox label="document">文档</el-checkbox>
        </el-checkbox-group>
      </el-form-item>
      <el-form-item label="自动转发">
        <el-switch v-model="form.autoForward" />
      </el-form-item>
      <el-form-item label="转发到" v-if="form.autoForward">
        <el-input v-model="form.forwardToChatId" placeholder="输入目标聊天ID" />
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

interface Account {
  id: number
  phone: string
}

interface ListenForm {
  accountId: number
  chatId: string
  mediaTypes: string[]
  autoForward: boolean
  forwardToChatId: string
}

const props = defineProps<{
  modelValue: boolean
  accounts: Account[]
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm', value: ListenForm): void
}>()

const visible = ref(false)
const form = ref<ListenForm>({
  accountId: 0,
  chatId: '',
  mediaTypes: [],
  autoForward: false,
  forwardToChatId: ''
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
