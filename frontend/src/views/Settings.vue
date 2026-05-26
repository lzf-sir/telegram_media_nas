<template>
  <div class="settings-view">
    <div class="settings-header">
      <div class="header-left">
        <h2 class="page-title-section">系统设置</h2>
        <p class="page-subtitle">配置系统参数和偏好设置</p>
      </div>
    </div>

    <div class="settings-grid">
      <!-- 界面设置 -->
      <div class="setting-section glass-card">
        <div class="section-header">
          <div class="section-icon" style="background: var(--primary-gradient)">
            <el-icon><Brush /></el-icon>
          </div>
          <div>
            <h3 class="section-title">界面设置</h3>
            <p class="section-description">自定义界面外观</p>
          </div>
        </div>
        <div class="section-content">
          <div class="setting-item">
            <div class="setting-label">
              <span class="label-text">主题模式</span>
              <span class="label-description">选择界面主题</span>
            </div>
            <div class="setting-control">
              <el-segmented v-model="localTheme" :options="themeOptions" @change="handleThemeChange" />
            </div>
          </div>
        </div>
      </div>

      <!-- Telegram 设置 -->
      <div class="setting-section glass-card">
        <div class="section-header">
          <div class="section-icon" style="background: var(--info-gradient)">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div>
            <h3 class="section-title">Telegram 设置</h3>
            <p class="section-description">配置 Telegram API 参数</p>
          </div>
        </div>
        <div class="section-content">
          <div class="setting-item">
            <div class="setting-label">
              <span class="label-text">API ID</span>
            </div>
            <div class="setting-control">
              <el-input v-model="telegramSettings.api_id" placeholder="输入 Telegram API ID" />
            </div>
          </div>
          <div class="setting-item">
            <div class="setting-label">
              <span class="label-text">API Hash</span>
            </div>
            <div class="setting-control">
              <el-input
                v-model="telegramSettings.api_hash"
                type="password"
                placeholder="输入 Telegram API Hash"
                show-password
              />
            </div>
          </div>
          <div class="setting-item">
            <div class="setting-label">
              <span class="label-text">手机号</span>
            </div>
            <div class="setting-control">
              <el-input v-model="telegramSettings.phone" placeholder="输入手机号（带国家码）" />
            </div>
          </div>
          <div class="setting-item">
            <div class="setting-label">
              <span class="label-text">连接状态</span>
            </div>
            <div class="setting-control">
              <span class="status-badge" :class="{ connected: telegramSettings.configured }">
                <span class="status-dot"></span>
                {{ telegramSettings.configured ? '已配置' : '未配置' }}
              </span>
            </div>
          </div>
          <div class="setting-actions">
            <el-button type="primary" @click="saveTelegramSettings">保存设置</el-button>
            <el-button @click="testConnection">测试连接</el-button>
          </div>
        </div>
      </div>

      <!-- 下载设置 -->
      <div class="setting-section glass-card">
        <div class="section-header">
          <div class="section-icon" style="background: var(--success-gradient)">
            <el-icon><Download /></el-icon>
          </div>
          <div>
            <h3 class="section-title">下载设置</h3>
            <p class="section-description">配置文件下载参数</p>
          </div>
        </div>
        <div class="section-content">
          <div class="setting-item">
            <div class="setting-label">
              <span class="label-text">下载路径</span>
              <span class="label-description">文件保存的目录</span>
            </div>
            <div class="setting-control">
              <el-input v-model="downloadSettings.download_path" placeholder="文件保存路径" />
            </div>
          </div>
          <div class="setting-item">
            <div class="setting-label">
              <span class="label-text">并发下载数</span>
              <span class="label-description">同时下载的最大文件数</span>
            </div>
            <div class="setting-control">
              <el-input-number
                v-model="downloadSettings.max_concurrent_downloads"
                :min="1"
                :max="20"
              />
            </div>
          </div>
          <div class="setting-item">
            <div class="setting-label">
              <span class="label-text">超时时间</span>
              <span class="label-description">下载超时时间（秒）</span>
            </div>
            <div class="setting-control">
              <el-input-number
                v-model="downloadSettings.download_timeout"
                :min="30"
                :max="600"
              />
              <span class="unit-label">秒</span>
            </div>
          </div>
          <div class="setting-actions">
            <el-button type="primary" @click="saveDownloadSettings">保存设置</el-button>
          </div>
        </div>
      </div>

      <!-- Bot 安全设置 -->
      <div class="setting-section glass-card">
        <div class="section-header">
          <div class="section-icon" style="background: var(--warning-gradient)">
            <el-icon><Lock /></el-icon>
          </div>
          <div>
            <h3 class="section-title">Bot 安全设置</h3>
            <p class="section-description">配置 Bot 使用限制</p>
          </div>
        </div>
        <div class="section-content">
          <div class="setting-item">
            <div class="setting-label">
              <span class="label-text">每分钟请求限制</span>
              <span class="label-description">0 表示不限制</span>
            </div>
            <div class="setting-control">
              <el-input-number
                v-model="botSettings.rate_limit"
                :min="0"
                :max="1000"
                :step="10"
              />
              <span class="unit-label">次/分钟</span>
            </div>
          </div>
          <div class="setting-item">
            <div class="setting-label">
              <span class="label-text">启用白名单</span>
              <span class="label-description">仅白名单用户可使用 Bot</span>
            </div>
            <div class="setting-control">
              <el-switch v-model="botSettings.whitelist_enabled" />
            </div>
          </div>
          <div class="setting-item full-width">
            <div class="setting-label">
              <span class="label-text">白名单用户</span>
              <span class="label-description">支持 @username 或用户ID</span>
            </div>
            <div class="setting-control">
              <el-select
                v-model="botSettings.whitelist_users"
                multiple
                filterable
                allow-create
                default-first-option
                placeholder="输入用户名（@username）或用户ID"
                class="whitelist-select"
              >
                <el-option
                  v-for="user in botSettings.whitelist_users"
                  :key="user"
                  :label="user"
                  :value="user"
                />
              </el-select>
            </div>
          </div>
          <div class="setting-actions">
            <el-button type="primary" :loading="savingBot" @click="saveBotSettings">
              保存 Bot 设置
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Brush, ChatDotRound, Download, Lock } from '@element-plus/icons-vue'
import { settingsApi, type TelegramSettings, type DownloadSettings, type BotSettings } from '@/api/settings'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'

const authStore = useAuthStore()
const { theme, setTheme } = useTheme()

const localTheme = ref(theme.value)

const themeOptions = [
  { label: '暗色', value: 'dark' },
  { label: '亮色', value: 'light' },
]

const telegramSettings = reactive<TelegramSettings>({
  api_id: 0,
  api_hash: '',
  phone: '',
  configured: false,
})

const downloadSettings = reactive<DownloadSettings>({
  download_path: './downloads',
  max_concurrent_downloads: 5,
  download_timeout: 300,
})

const botSettings = reactive<BotSettings>({
  rate_limit: 0,
  whitelist_enabled: false,
  whitelist_users: [],
})

const savingBot = ref(false)

function handleThemeChange(value: 'dark' | 'light') {
  setTheme(value)
  ElMessage.success('主题已切换')
}

async function loadSettings() {
  try {
    const [telegram, download] = await Promise.all([
      settingsApi.getTelegramSettings(),
      settingsApi.getDownloadSettings(),
    ])
    Object.assign(telegramSettings, telegram)
    Object.assign(downloadSettings, download)
  } catch (error) {
    console.error('Failed to load settings:', error)
    ElMessage.error('加载设置失败')
  }

  // 单独加载 Bot 设置（需要身份验证）
  if (authStore.isAuthenticated) {
    try {
      const bot = await settingsApi.getBotSettings()
      Object.assign(botSettings, bot)
    } catch (error: any) {
      if (error.response?.status !== 401) {
        console.error('Failed to load bot settings:', error)
      }
    }
  }
}

async function saveTelegramSettings() {
  try {
    await settingsApi.updateTelegramSettings({
      api_id: telegramSettings.api_id,
      api_hash: telegramSettings.api_hash,
      phone: telegramSettings.phone,
    })
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

async function saveDownloadSettings() {
  try {
    await settingsApi.updateDownloadSettings(downloadSettings)
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

async function saveBotSettings() {
  savingBot.value = true
  try {
    await settingsApi.updateBotSettings({
      rate_limit: botSettings.rate_limit,
      whitelist_enabled: botSettings.whitelist_enabled,
      whitelist_users: botSettings.whitelist_users,
    })
    ElMessage.success('Bot 设置保存成功')
  } catch (error: any) {
    const message = error.response?.data?.detail || '保存失败'
    ElMessage.error(message)
  } finally {
    savingBot.value = false
  }
}

function testConnection() {
  ElMessage.info('连接测试功能开发中')
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.settings-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

/* ============================================
   头部样式
   ============================================ */
.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-md);
}

.header-left {
  flex: 1;
}

.page-title-section {
  margin: 0 0 var(--space-xs) 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.page-subtitle {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
}

/* ============================================
   设置网格
   ============================================ */
.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: var(--space-lg);
}

@media (max-width: 768px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
}

/* ============================================
   设置区块
   ============================================ */
.setting-section {
  padding: var(--space-lg);
}

.section-header {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
  padding-bottom: var(--space-md);
  border-bottom: 1px solid var(--divider-color);
}

.section-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  color: #fff;
  font-size: 20px;
  flex-shrink: 0;
}

.section-title {
  margin: 0 0 var(--space-xs) 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.section-description {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
}

.section-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

/* ============================================
   设置项
   ============================================ */
.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-md);
}

.setting-item.full-width {
  flex-direction: column;
  align-items: stretch;
}

.setting-label {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.label-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.label-description {
  font-size: 12px;
  color: var(--text-tertiary);
}

.setting-control {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.unit-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.whitelist-select {
  width: 100%;
}

/* 状态徽章 */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 500;
  background: var(--glass-bg);
  color: var(--text-tertiary);
}

.status-badge .status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-tertiary);
}

.status-badge.connected {
  background: var(--success-bg);
  color: var(--success-color);
}

.status-badge.connected .status-dot {
  background: var(--success-color);
}

/* 设置操作按钮 */
.setting-actions {
  display: flex;
  gap: var(--space-sm);
  padding-top: var(--space-md);
  border-top: 1px solid var(--divider-color);
}

/* ============================================
   响应式设计
   ============================================ */
@media (max-width: 640px) {
  .page-title-section {
    font-size: 20px;
  }

  .setting-item {
    flex-direction: column;
    align-items: stretch;
  }

  .setting-actions {
    flex-direction: column;
  }

  .setting-actions .el-button {
    width: 100%;
  }
}
</style>
