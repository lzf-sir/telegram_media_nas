<template>
  <div class="login-page">
    <!-- 装饰背景 -->
    <div class="login-bg">
      <div class="login-orb login-orb-1"></div>
      <div class="login-orb login-orb-2"></div>
      <div class="login-grid"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-wrapper">
      <div class="login-card glass-card">
        <!-- Logo -->
        <div class="login-brand">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
            <rect width="48" height="48" rx="14" fill="url(#login-logo-grad)"/>
            <path d="M12 24L20 32L36 16" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            <defs>
              <linearGradient id="login-logo-grad" x1="0" y1="0" x2="48" y2="48">
                <stop stop-color="#22C55E"/><stop offset="1" stop-color="#22D3BB"/>
              </linearGradient>
            </defs>
          </svg>
          <h1 class="brand-name">Telegram Media NAS</h1>
          <p class="brand-desc">现代化媒体下载与管理系统</p>
        </div>

        <!-- 表单 -->
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
              placeholder="用户名"
              size="large"
              :prefix-icon="User"
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="密码"
              size="large"
              show-password
              :prefix-icon="Lock"
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="authStore.loading"
              class="login-btn"
              @click="handleLogin"
            >
              {{ authStore.loading ? '验证中...' : '登 录' }}
            </el-button>
          </el-form-item>
        </el-form>

        <!-- 底部 -->
        <div class="login-footer">
          <ThemeToggle />
          <span class="version-text">v2.0</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { type FormInstance, type FormRules } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import ThemeToggle from '@/components/ThemeToggle.vue'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const form = reactive({ username: '', password: '' })
const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  const success = await authStore.login(form)
  if (success) router.push('/dashboard')
}
</script>

<style scoped>
.login-page {
  position: relative;
  height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.login-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}
.login-grid {
  position: absolute; inset: 0;
  background-image: linear-gradient(var(--border-subtle) 1px, transparent 1px),
                    linear-gradient(90deg, var(--border-subtle) 1px, transparent 1px);
  background-size: 80px 80px;
  opacity: 0.3;
}
.login-orb {
  position: absolute; border-radius: 50%; filter: blur(140px); opacity: 0.12;
}
.login-orb-1 {
  width: 500px; height: 500px;
  top: -150px; left: -100px;
  background: var(--accent);
  animation: orb1 15s ease-in-out infinite;
}
.login-orb-2 {
  width: 400px; height: 400px;
  bottom: -120px; right: -80px;
  background: #8B5CF6;
  animation: orb2 18s ease-in-out infinite;
}
@keyframes orb1 {
  0%,100% { transform: translate(0,0) scale(1); }
  50% { transform: translate(60px,40px) scale(1.15); }
}
@keyframes orb2 {
  0%,100% { transform: translate(0,0) scale(1); }
  50% { transform: translate(-40px,-30px) scale(1.1); }
}

.login-wrapper {
  position: relative;
  z-index: 1;
}
.login-card {
  width: 420px;
  max-width: 90vw;
  padding: var(--space-10) var(--space-8);
  border-radius: var(--radius-3xl);
  text-align: center;
}
.login-brand { margin-bottom: var(--space-8); }
.brand-name {
  font-family: var(--font-heading);
  font-size: 22px;
  font-weight: 700;
  margin-top: var(--space-4);
  color: var(--text-primary);
}
.brand-desc {
  font-size: 13px;
  color: var(--text-tertiary);
  margin-top: var(--space-2);
}
.login-form {
  text-align: left;
  margin-top: var(--space-6);
}
.login-btn {
  width: 100%;
  height: 44px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 4px;
  margin-top: var(--space-2);
}
.login-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-4);
  margin-top: var(--space-6);
}
<<<<<<< HEAD


=======
.version-text {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-tertiary);
}
>>>>>>> 2d69f9af031a6c0fd791c1d47c994b92296ce03a
</style>
