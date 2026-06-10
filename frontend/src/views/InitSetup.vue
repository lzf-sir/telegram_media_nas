<template>
  <div class="init-page">
    <div class="init-bg">
      <div class="init-orb init-orb-1"></div>
      <div class="init-orb init-orb-2"></div>
    </div>
    <div class="init-wrapper">
      <div class="init-card glass-card">
        <!-- Logo -->
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none" style="margin-bottom:16px">
          <rect width="48" height="48" rx="14" fill="url(#init-logo)"/>
          <path d="M14 24L22 32L34 16" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
          <defs><linearGradient id="init-logo" x1="0" y1="0" x2="48" y2="48"><stop stop-color="#22C55E"/><stop offset="1" stop-color="#22D3BB"/></linearGradient></defs>
        </svg>
        <h1 class="init-title">系统初始化</h1>
        <p class="init-desc">创建管理员账户以开始使用 Telegram Media NAS</p>

        <el-alert type="info" :closable="false" style="margin:16px 0;text-align:left" show-icon>
          首次使用，请设置管理员账户
        </el-alert>

        <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleSubmit">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="用户名（3-50字符）" size="large" :prefix-icon="User" @keyup.enter="handleSubmit" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="form.password" type="password" placeholder="密码（至少6位）" size="large" show-password :prefix-icon="Lock" @keyup.enter="handleSubmit" />
          </el-form-item>
          <el-form-item prop="confirmPassword">
            <el-input v-model="form.confirmPassword" type="password" placeholder="确认密码" size="large" show-password :prefix-icon="Lock" @keyup.enter="handleSubmit" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" size="large" :loading="authStore.loading" class="init-btn" @click="handleSubmit">
              {{ authStore.loading ? '初始化中...' : '完成初始化' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="init-footer">
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
import type { FormInstance, FormRules } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import ThemeToggle from '@/components/ThemeToggle.vue'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const form = reactive({ username: '', password: '', confirmPassword: '' })

const validateConfirm = (_rule: any, value: string, cb: any) => {
  if (value !== form.password) cb(new Error('两次密码不一致'))
  else cb()
}

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }, { min: 3, max: 50, message: '3-50个字符', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '至少6位', trigger: 'blur' }],
  confirmPassword: [{ required: true, message: '请确认密码', trigger: 'blur' }, { validator: validateConfirm, trigger: 'blur' }],
}

async function handleSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  const success = await authStore.initialize({ username: form.username, password: form.password, password_confirm: form.confirmPassword })
  if (success) router.push('/dashboard')
}
</script>

<style scoped>
<<<<<<< HEAD
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


=======
.init-page { position: relative; height: 100vh; width: 100vw; display: flex; align-items: center; justify-content: center; overflow: hidden; }
.init-bg { position: absolute; inset: 0; pointer-events: none; }
.init-orb { position: absolute; border-radius: 50%; filter: blur(120px); opacity: 0.12; }
.init-orb-1 { width: 500px; height: 500px; top: -150px; right: -100px; background: var(--accent); animation: orbA 15s ease-in-out infinite; }
.init-orb-2 { width: 400px; height: 400px; bottom: -100px; left: -80px; background: #8B5CF6; animation: orbB 18s ease-in-out infinite; }
@keyframes orbA { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(-50px,30px) scale(1.1); } }
@keyframes orbB { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(40px,-20px) scale(1.15); } }
.init-wrapper { position: relative; z-index: 1; }
.init-card { width: 440px; max-width: 90vw; padding: var(--space-10) var(--space-8); border-radius: var(--radius-3xl); text-align: center; }
.init-title { font-family: var(--font-heading); font-size: 24px; font-weight: 700; color: var(--text-primary); }
.init-desc { color: var(--text-tertiary); margin-top: var(--space-2); font-size: 14px; }
.init-btn { width: 100%; height: 44px; font-size: 15px; font-weight: 600; letter-spacing: 4px; margin-top: var(--space-2); }
.init-footer { display: flex; align-items: center; justify-content: center; gap: var(--space-4); margin-top: var(--space-4); }
.version-text { font-family: var(--font-mono); font-size: 12px; color: var(--text-tertiary); }
>>>>>>> 2d69f9af031a6c0fd791c1d47c994b92296ce03a
</style>
