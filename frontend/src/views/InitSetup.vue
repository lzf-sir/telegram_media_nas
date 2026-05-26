<template>
  <div class="init-container">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-circle bg-circle-1"></div>
      <div class="bg-circle bg-circle-2"></div>
      <div class="bg-circle bg-circle-3"></div>
    </div>

    <!-- 主题切换 -->
    <div class="theme-toggle-wrapper">
      <theme-toggle />
    </div>

    <!-- 初始化卡片 -->
    <div class="init-card glass-card">
      <!-- Logo -->
      <div class="init-logo">
        <div class="logo-icon">
          <el-icon :size="32"><Setting /></el-icon>
        </div>
        <h1 class="logo-title">系统初始化</h1>
        <p class="logo-subtitle">创建管理员账户以开始使用</p>
      </div>

      <!-- 欢迎信息 -->
      <div class="welcome-info">
        <el-icon color="var(--primary-color)" :size="20"><InfoFilled /></el-icon>
        <span>欢迎使用 Telegram Media NAS，请设置管理员账户</span>
      </div>

      <!-- 初始化表单 -->
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="init-form"
        @submit.prevent="handleSubmit"
      >
        <el-form-item prop="username">
          <template #label>
            <span class="form-label">用户名</span>
          </template>
          <el-input
            v-model="form.username"
            placeholder="3-50个字符，支持字母、数字和下划线"
            maxlength="50"
            show-word-limit
            size="large"
            clearable
            @keyup.enter="handleSubmit"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <template #label>
            <span class="form-label">密码</span>
          </template>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="至少6个字符"
            maxlength="100"
            show-password
            size="large"
            clearable
            @keyup.enter="handleSubmit"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password_confirm">
          <template #label>
            <span class="form-label">确认密码</span>
          </template>
          <el-input
            v-model="form.password_confirm"
            type="password"
            placeholder="请再次输入密码"
            maxlength="100"
            show-password
            size="large"
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
            size="large"
            :loading="authStore.loading"
            class="submit-btn"
            @click="handleSubmit"
          >
            <span v-if="!authStore.loading">完成初始化</span>
            <span v-else>初始化中...</span>
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 底部信息 -->
      <div class="init-footer">
        <el-text type="info" size="small">v1.0.0</el-text>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { Setting, User, Lock, InfoFilled } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import ThemeToggle from '@/components/ThemeToggle.vue'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()

const form = reactive({
  username: '',
  password: '',
  password_confirm: '',
})

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
      ElMessage.success('初始化成功')
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
  position: relative;
  overflow: hidden;
}

/* ============================================
   背景装饰
   ============================================ */
.bg-decoration {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
  filter: blur(60px);
}

.bg-circle-1 {
  width: 400px;
  height: 400px;
  background: var(--primary-gradient);
  top: -100px;
  left: -100px;
  animation: float 20s ease-in-out infinite;
}

.bg-circle-2 {
  width: 300px;
  height: 300px;
  background: var(--success-gradient);
  bottom: -50px;
  right: -50px;
  animation: float 15s ease-in-out infinite reverse;
}

.bg-circle-3 {
  width: 250px;
  height: 250px;
  background: var(--info-gradient);
  top: 50%;
  right: 20%;
  animation: float 18s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -30px) scale(1.05);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.95);
  }
}

/* ============================================
   主题切换
   ============================================ */
.theme-toggle-wrapper {
  position: absolute;
  top: var(--space-lg);
  right: var(--space-lg);
  z-index: 10;
}

/* ============================================
   初始化卡片
   ============================================ */
.init-card {
  width: 100%;
  max-width: 460px;
  padding: var(--space-2xl);
  margin: var(--space-lg);
  z-index: 1;
}

/* Logo */
.init-logo {
  text-align: center;
  margin-bottom: var(--space-xl);
}

.logo-icon {
  width: 64px;
  height: 64px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-gradient);
  border-radius: var(--radius-xl);
  color: #fff;
  margin-bottom: var(--space-lg);
  box-shadow: var(--shadow-glow-primary);
}

.logo-title {
  margin: 0 0 var(--space-sm) 0;
  font-size: 24px;
  font-weight: 700;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-subtitle {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
}

/* 欢迎信息 */
.welcome-info {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md);
  background: var(--primary-bg);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-xl);
  font-size: 14px;
  color: var(--text-primary);
}

/* 表单 */
.init-form {
  margin-bottom: var(--space-xl);
}

:deep(.el-form-item) {
  margin-bottom: var(--space-lg);
}

.form-label {
  font-weight: 500;
  color: var(--text-primary);
  display: flex;
  align-items: center;
}

:deep(.el-input__wrapper) {
  padding: 12px 16px;
}

:deep(.el-input__inner) {
  font-size: 15px;
}

:deep(.el-input__prefix) {
  font-size: 18px;
  color: var(--text-tertiary);
}

/* 提交按钮 */
.submit-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  margin-top: var(--space-md);
}

/* 底部信息 */
.init-footer {
  text-align: center;
  padding-top: var(--space-lg);
  border-top: 1px solid var(--divider-color);
}

/* ============================================
   响应式设计
   ============================================ */
@media (max-width: 480px) {
  .init-card {
    padding: var(--space-xl);
    margin: var(--space-md);
  }

  .logo-title {
    font-size: 20px;
  }

  .logo-subtitle {
    font-size: 13px;
  }
}
</style>
