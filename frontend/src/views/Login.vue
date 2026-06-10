<template>
  <div class="login-container">
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

    <!-- 登录卡片 -->
    <div class="login-card glass-card">
      <!-- Logo -->
      <div class="login-logo">
        <div class="logo-icon">
          <el-icon :size="32"><Platform /></el-icon>
        </div>
        <h1 class="logo-title">Telegram Media NAS</h1>
        <p class="logo-subtitle">现代化媒体下载管理系统</p>
      </div>

      <!-- 登录表单 -->
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            size="large"
            clearable
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password
            clearable
            @keyup.enter="handleLogin"
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
            class="login-btn"
            @click="handleLogin"
          >
            <span v-if="!authStore.loading">登录</span>
            <span v-else>登录中...</span>
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 底部信息 -->
      <div class="login-footer">
        <el-text type="info" size="small">v1.0.0</el-text>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { Platform, User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import ThemeToggle from '@/components/ThemeToggle.vue'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()

const form = reactive({
  username: '',
  password: '',
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
  ],
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    router.push({ name: 'Dashboard' })
  }
})

async function handleLogin() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    const success = await authStore.login({
      username: form.username,
      password: form.password,
    })

    if (success) {
      ElMessage.success('登录成功')
      router.push({ name: 'Dashboard' })
    }
  })
}
</script>

<style scoped>
.login-container {
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
   登录卡片
   ============================================ */
.login-card {
  width: 100%;
  max-width: 420px;
  padding: var(--space-2xl);
  margin: var(--space-lg);
  z-index: 1;
}

/* Logo */
.login-logo {
  text-align: center;
  margin-bottom: var(--space-2xl);
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

/* 表单 */
.login-form {
  margin-bottom: var(--space-xl);
}

:deep(.el-form-item) {
  margin-bottom: var(--space-lg);
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

/* 登录按钮 */
.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  margin-top: var(--space-sm);
}

/* 底部信息 */
.login-footer {
  text-align: center;
  padding-top: var(--space-lg);
  border-top: 1px solid var(--divider-color);
}


</style>
