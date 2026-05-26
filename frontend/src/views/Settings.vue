<template>
  <div class="settings-view">
    <!-- Telegram 设置 -->
    <el-card shadow="never">
      <template #header>
        <span>Telegram 设置</span>
      </template>

      <el-form label-width="120px" style="max-width: 600px">
        <el-form-item label="API ID">
          <el-input v-model="telegramSettings.api_id" placeholder="输入 Telegram API ID" />
        </el-form-item>
        <el-form-item label="API Hash">
          <el-input
            v-model="telegramSettings.api_hash"
            type="password"
            placeholder="输入 Telegram API Hash"
            show-password
          />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="telegramSettings.phone" placeholder="输入手机号（带国家码）" />
        </el-form-item>
        <el-form-item label="连接状态">
          <el-tag :type="telegramSettings.configured ? 'success' : 'danger'">
            {{ telegramSettings.configured ? '已配置' : '未配置' }}
          </el-tag>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveTelegramSettings">保存设置</el-button>
          <el-button @click="testConnection">测试连接</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Bot 安全设置 -->
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>Bot 安全设置</span>
          <el-icon class="header-icon"><Lock /></el-icon>
        </div>
      </template>

      <el-alert
        type="info"
        :closable="false"
        show-icon
        title="Bot 安全设置"
        description="配置 Bot 使用的安全限制，防止滥用"
        style="margin-bottom: 20px"
      />

      <el-form label-width="140px" style="max-width: 700px">
        <el-form-item label="每分钟请求限制">
          <el-input-number
            v-model="botSettings.rate_limit"
            :min="0"
            :max="1000"
            :step="10"
          />
          <span class="form-tip">设置为 0 表示不限制</span>
        </el-form-item>

        <el-divider />

        <el-form-item label="启用白名单">
          <el-switch v-model="botSettings.whitelist_enabled" />
          <span class="form-tip">启用后只有白名单用户可以使用 Bot 命令</span>
        </el-form-item>

        <el-form-item label="白名单用户">
          <el-select
            v-model="botSettings.whitelist_users"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入用户名（@username）或用户ID"
            style="width: 100%"
          >
            <el-option
              v-for="user in botSettings.whitelist_users"
              :key="user"
              :label="user"
              :value="user"
            />
          </el-select>
          <div class="form-tip">
            支持格式：<code>@username</code> 或 <code>123456789</code>（用户ID）<br />
            登录的管理员账号始终可以使用 Bot
          </div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="savingBot" @click="saveBotSettings">
            保存 Bot 设置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 下载设置 -->
    <el-card shadow="never">
      <template #header>
        <span>下载设置</span>
      </template>

      <el-form label-width="120px" style="max-width: 600px">
        <el-form-item label="下载路径">
          <el-input v-model="downloadSettings.download_path" placeholder="文件保存路径" />
        </el-form-item>
        <el-form-item label="并发下载数">
          <el-input-number
            v-model="downloadSettings.max_concurrent_downloads"
            :min="1"
            :max="20"
          />
        </el-form-item>
        <el-form-item label="超时时间（秒）">
          <el-input-number
            v-model="downloadSettings.download_timeout"
            :min="30"
            :max="600"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveDownloadSettings">保存设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Lock } from '@element-plus/icons-vue'
import { settingsApi, type TelegramSettings, type DownloadSettings, type BotSettings } from '@/api/settings'
import { useAuthStore } from '@/stores/auth'

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
  const authStore = useAuthStore()
  if (authStore.isAuthenticated) {
    try {
      const bot = await settingsApi.getBotSettings()
      Object.assign(botSettings, bot)
    } catch (error: any) {
      // 如果是 401 错误，说明 token 过期，静默处理
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
  gap: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-icon {
  font-size: 18px;
  color: #409eff;
}

.form-tip {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

.form-tip code {
  padding: 2px 6px;
  background: #f5f7fa;
  border-radius: 3px;
  color: #e6a23c;
}
</style>
