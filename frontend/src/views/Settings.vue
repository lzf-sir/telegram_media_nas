<template>
  <div class="settings-page">
    <div class="page-hero">
      <div class="hero-left">
        <h2 class="page-title">系统设置</h2>
        <p class="page-desc">配置系统参数和偏好</p>
      </div>
    </div>

    <div class="settings-grid">
      <!-- 界面设置 -->
      <div class="setting-section glass-card">
        <div class="section-head">
          <div class="section-icon" style="background: var(--purple-gradient)"><el-icon :size="20"><Brush /></el-icon></div>
          <div><h3>界面设置</h3><p>自定义外观</p></div>
        </div>
        <div class="section-body">
          <div class="setting-row">
            <div class="setting-info"><span>主题模式</span><small>选择深色或亮色界面</small></div>
            <el-segmented v-model="localTheme" :options="themeOpts" @change="handleThemeChange" />
          </div>
        </div>
      </div>

      <!-- Telegram 设置 -->
      <div class="setting-section glass-card">
        <div class="section-head">
          <div class="section-icon" style="background: var(--info-gradient)"><el-icon :size="20"><ChatDotRound /></el-icon></div>
          <div><h3>Telegram 配置</h3><p>API 连接参数</p></div>
        </div>
        <div class="section-body">
          <div class="setting-row">
            <div class="setting-info"><span>API ID</span></div>
            <el-input v-model="tg.api_id" placeholder="输入 API ID" style="max-width:300px" />
          </div>
          <div class="setting-row">
            <div class="setting-info"><span>API Hash</span></div>
            <el-input v-model="tg.api_hash" type="password" show-password placeholder="输入 API Hash" style="max-width:300px" />
          </div>
          <div class="setting-row">
            <div class="setting-info"><span>手机号</span></div>
            <el-input v-model="tg.phone" placeholder="+8613800000000" style="max-width:300px" />
          </div>
          <div class="setting-row">
            <div class="setting-info"><span>状态</span></div>
            <span class="badge" :class="tg.configured ? 'badge-success' : 'badge-warning'">
              <span :class="tg.configured ? 'status-dot-active' : 'status-dot-inactive'" class="status-dot"></span>
              {{ tg.configured ? '已配置' : '未配置' }}
            </span>
          </div>
          <div class="setting-actions">
            <el-button type="primary" @click="saveTg">保存</el-button>
            <el-button @click="testConnection">测试连接</el-button>
          </div>
        </div>
      </div>

      <!-- 下载设置 -->
      <div class="setting-section glass-card">
        <div class="section-head">
          <div class="section-icon" style="background: var(--success-gradient)"><el-icon :size="20"><Download /></el-icon></div>
          <div><h3>下载设置</h3><p>路径和并发控制</p></div>
        </div>
        <div class="section-body">
          <div class="setting-row">
            <div class="setting-info"><span>下载路径</span><small>文件保存位置</small></div>
            <el-input v-model="dl.download_path" placeholder="./downloads" style="max-width:300px" />
          </div>
          <div class="setting-row">
            <div class="setting-info"><span>临时路径</span></div>
            <el-input v-model="dl.temp_path" placeholder="./temp" style="max-width:300px" />
          </div>
          <div class="setting-row">
            <div class="setting-info"><span>最大并发</span><small>同时下载任务数</small></div>
            <el-input-number v-model="dl.max_concurrent" :min="1" :max="20" />
          </div>
          <div class="setting-actions">
            <el-button type="primary" @click="saveDl">保存</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Brush, ChatDotRound, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useThemeStore, type Theme } from '@/stores/theme'
import { settingsApi } from '@/api/settings'

const themeStore = useThemeStore()
const localTheme = ref<Theme>(themeStore.theme)
const themeOpts = [
  { label: '🌙 暗色', value: 'dark' },
  { label: '☀️ 亮色', value: 'light' },
]

const tg = reactive<{ api_id: string | number; api_hash: string; phone: string; configured: boolean }>({ api_id: '', api_hash: '', phone: '', configured: false })
const dl = reactive({ download_path: '', temp_path: '', max_concurrent: 3 })

function handleThemeChange(val: string | number) {
  themeStore.setTheme(val as Theme)
}

async function fetchSettings() {
  try {
    const data: any = await settingsApi.getAll()
    if (data.telegram) Object.assign(tg, data.telegram)
    if (data.download) Object.assign(dl, data.download)
  } catch { /* ignore */ }
}

async function saveTg() {
  try {
    await settingsApi.updateTelegram({ api_id: Number(tg.api_id), api_hash: tg.api_hash, phone: tg.phone })
    ElMessage.success('Telegram 设置已保存')
  } catch { ElMessage.error('保存失败') }
}
async function testConnection() {
  try {
    await settingsApi.testTelegramConnection()
    ElMessage.success('连接测试成功')
    tg.configured = true
  } catch { ElMessage.error('连接测试失败') }
}
async function saveDl() {
  try {
    await settingsApi.updateDownload(dl as any)
    ElMessage.success('下载设置已保存')
  } catch { ElMessage.error('保存失败') }
}

onMounted(fetchSettings)
</script>

<style scoped>
.settings-page { display: flex; flex-direction: column; gap: var(--space-6); }
.page-hero { display: flex; align-items: flex-start; justify-content: space-between; }
.page-title { font-family: var(--font-heading); font-size: 24px; font-weight: 700; }
.page-desc { color: var(--text-tertiary); margin-top: var(--space-1); }
.settings-grid { display: grid; gap: var(--space-4); grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); }
.setting-section { padding: var(--space-6); }
.section-head { display: flex; align-items: center; gap: var(--space-4); margin-bottom: var(--space-6); }
.section-head h3 { font-family: var(--font-heading); font-size: 16px; font-weight: 600; color: var(--text-primary); }
.section-head p { color: var(--text-tertiary); font-size: 13px; }
.section-icon {
  width: 44px; height: 44px; border-radius: var(--radius-lg);
  display: flex; align-items: center; justify-content: center; color: white; flex-shrink: 0;
}
.section-body { display: flex; flex-direction: column; gap: var(--space-4); }
.setting-row { display: flex; align-items: center; justify-content: space-between; gap: var(--space-4); }
.setting-info { display: flex; flex-direction: column; }
.setting-info span { font-weight: 500; color: var(--text-primary); }
.setting-info small { color: var(--text-tertiary); font-size: 12px; }
.setting-actions { display: flex; gap: var(--space-3); padding-top: var(--space-2); }
</style>
