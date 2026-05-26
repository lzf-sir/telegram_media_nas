<template>
  <el-dialog
    v-model="visible"
    title="添加 Telegram 账号"
    width="600px"
    @close="handleClose"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
      <el-divider content-position="left">基本信息</el-divider>

      <el-form-item label="手机号" prop="phone">
        <el-input
          v-model="form.phone"
          placeholder="+8613800138000 (带国家码)"
          :prefix-icon="Phone"
        />
      </el-form-item>

      <el-form-item label="API ID" prop="api_id">
        <el-input v-model.number="form.api_id" type="number" placeholder="从 my.telegram.org 获取" />
      </el-form-item>

      <el-form-item label="API Hash" prop="api_hash">
        <el-input
          v-model="form.api_hash"
          type="password"
          show-password
          placeholder="从 my.telegram.org 获取"
        />
      </el-form-item>

      <el-form-item label="设为默认">
        <el-switch v-model="form.is_default" />
      </el-form-item>

      <el-divider content-position="left">指纹隔离配置</el-divider>

      <el-alert
        title="指纹隔离"
        type="info"
        description="每个账号使用独立的设备指纹，避免被 Telegram 检测为异常行为"
        :closable="false"
        style="margin-bottom: 16px"
      />

      <el-form-item label="设备型号">
        <el-select v-model="form.device_model" placeholder="自动随机" clearable filterable>
          <el-option label="iPhone 14 Pro" value="iPhone 14 Pro" />
          <el-option label="iPhone 14" value="iPhone 14" />
          <el-option label="iPhone 13 Pro" value="iPhone 13 Pro" />
          <el-option label="Samsung Galaxy S23" value="Samsung Galaxy S23" />
          <el-option label="Google Pixel 7" value="Google Pixel 7" />
          <el-option label="Xiaomi 13" value="Xiaomi 13" />
        </el-select>
        <div class="form-tip">留空将自动生成随机设备</div>
      </el-form-item>

      <el-form-item label="系统版本">
        <el-select v-model="form.system_version" placeholder="自动随机" clearable>
          <el-option label="iOS 16.5" value="iOS 16.5" />
          <el-option label="iOS 16.4" value="iOS 16.4" />
          <el-option label="Android 13" value="Android 13" />
          <el-option label="Android 12" value="Android 12" />
          <el-option label="MIUI 14" value="MIUI 14" />
        </el-select>
      </el-form-item>

      <el-form-item label="App 版本">
        <el-select v-model="form.app_version" placeholder="自动随机" clearable>
          <el-option label="10.2.0" value="10.2.0" />
          <el-option label="10.1.0" value="10.1.0" />
          <el-option label="10.0.1" value="10.0.1" />
          <el-option label="9.9.0" value="9.9.0" />
        </el-select>
      </el-form-item>

      <el-divider content-position="left">代理配置（可选）</el-divider>

      <el-form-item label="使用代理">
        <el-switch v-model="proxyEnabled" />
      </el-form-item>

      <template v-if="proxyEnabled">
        <el-form-item label="代理类型">
          <el-radio-group v-model="form.proxy_type">
            <el-radio value="socks5">SOCKS5</el-radio>
            <el-radio value="socks4">SOCKS4</el-radio>
            <el-radio value="http">HTTP</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="代理地址">
          <el-input v-model="form.proxy_host" placeholder="127.0.0.1" />
        </el-form-item>

        <el-form-item label="代理端口">
          <el-input-number v-model="form.proxy_port" :min="1" :max="65535" />
        </el-form-item>
      </template>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="submitting">
        添加账号
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Phone } from '@element-plus/icons-vue'
import { accountsApi, type AccountCreate } from '@/api/accounts'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

const visible = defineModel<boolean>()
const formRef = ref<FormInstance>()
const submitting = ref(false)
const proxyEnabled = ref(false)

const form = reactive<AccountCreate & { proxy_host?: string; proxy_port?: number }>({
  phone: '',
  api_id: 0,
  api_hash: '',
  session_name: undefined,
  is_default: false,
  device_model: undefined,
  system_version: undefined,
  app_version: undefined,
  proxy_type: undefined,
  proxy_host: undefined,
  proxy_port: undefined,
})

const rules: FormRules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^\+\d{10,15}$/, message: '请输入有效的手机号（带国家码）', trigger: 'blur' },
  ],
  api_id: [{ required: true, message: '请输入 API ID', trigger: 'blur' }],
  api_hash: [{ required: true, message: '请输入 API Hash', trigger: 'blur' }],
}

async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      const data: AccountCreate = {
        phone: form.phone,
        api_id: form.api_id,
        api_hash: form.api_hash,
        session_name: form.session_name,
        is_default: form.is_default,
        device_model: form.device_model,
        system_version: form.system_version,
        app_version: form.app_version,
      }

      if (proxyEnabled.value && form.proxy_type && form.proxy_host && form.proxy_port) {
        data.proxy_type = form.proxy_type
        data.proxy_host = form.proxy_host
        data.proxy_port = form.proxy_port
      }

      await accountsApi.create(data)
      ElMessage.success('账号添加成功，请激活')
      emit('added')
      handleClose()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '添加失败')
    } finally {
      submitting.value = false
    }
  })
}

function handleClose() {
  formRef.value?.resetFields()
  form.phone = ''
  form.api_id = 0
  form.api_hash = ''
  form.is_default = false
  form.device_model = undefined
  form.system_version = undefined
  form.app_version = undefined
  proxyEnabled.value = false
}

const emit = defineEmits<{
  added: []
}>()
</script>

<style scoped>
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
