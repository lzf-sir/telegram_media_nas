<template>
  <div class="init-container">
    <el-card class="init-card">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon"><Setting /></el-icon>
          <span class="header-title">系统初始化</span>
        </div>
      </template>

      <div class="init-content">
        <el-alert
          type="info"
          :closable="false"
          show-icon
          title="欢迎使用 Telegram Media NAS"
          description="首次使用需要创建管理员账户，请设置用户名和密码。"
        />

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="100px"
          class="init-form"
          @submit.prevent="handleSubmit"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名（3-50个字符）"
              maxlength="50"
              show-word-limit
              clearable
              @keyup.enter="handleSubmit"
            >
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码（至少6个字符）"
              maxlength="100"
              show-password
              clearable
              @keyup.enter="handleSubmit"
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="确认密码" prop="password_confirm">
            <el-input
              v-model="form.password_confirm"
              type="password"
              placeholder="请再次输入密码"
              maxlength="100"
              show-password
              clearable
              @keyup.enter="handleSubmit"
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              :loading="authStore.loading"
              class="submit-btn"
              @click="handleSubmit"
            >
              完成初始化
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { Setting, User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 表单引用
const formRef = ref<FormInstance>()

// 表单数据
const form = reactive({
  username: '',
  password: '',
  password_confirm: '',
})

// 验证规则
const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为 3-50 个字符', trigger: 'blur' },
    {
      pattern: /^[a-zA-Z0-9_]+$/,
      message: '用户名只能包含字母、数字和下划线',
      trigger: 'blur',
    },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 100, message: '密码长度至少 6 个字符', trigger: 'blur' },
  ],
  password_confirm: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== form.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

// 提交表单
async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    const success = await authStore.initialize({
      username: form.username,
      password: form.password,
      password_confirm: form.password_confirm,
    })

    if (success) {
      // 初始化成功，跳转到首页
      router.push({ name: 'Dashboard' })
    }
  })
}
</script>

<style scoped>
.init-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.init-card {
  width: 450px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icon {
  font-size: 20px;
  color: #409eff;
}

.header-title {
  font-size: 18px;
  font-weight: 500;
}

.init-content {
  padding: 10px 0;
}

.init-form {
  margin-top: 24px;
}

.submit-btn {
  width: 100%;
}
</style>
