<template>
  <el-config-provider :locale="zhCn">
    <div id="app-root">
      <!-- 全局背景层 -->
      <div class="bg-layer">
        <div class="bg-orb bg-orb-1"></div>
        <div class="bg-orb bg-orb-2"></div>
        <div class="bg-orb bg-orb-3"></div>
        <div class="bg-grid"></div>
      </div>

      <!-- 路由视图 -->
      <div class="view-layer">
        <router-view v-slot="{ Component, route }">
          <transition :name="(route.meta.transition as string) || 'page'" mode="out-in">
            <keep-alive :include="['Dashboard', 'Tasks', 'Files', 'Forwards', 'Listens', 'Chats', 'Accounts', 'Logs', 'Settings']">
              <component :is="Component" :key="route.path" />
            </keep-alive>
          </transition>
        </router-view>
      </div>
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

onMounted(() => {
  themeStore.initTheme()
})
</script>

<style>
/* 导入设计系统 */
@import '@/styles/theme.css';
@import '@/styles/global.css';

/* ── 根容器 ── */
#app-root {
  position: relative;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: var(--surface-0);
  color: var(--text-primary);
  font-family: var(--font-body);
}

/* ── 背景层 ── */
.bg-layer {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}
.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(var(--border-subtle) 1px, transparent 1px),
    linear-gradient(90deg, var(--border-subtle) 1px, transparent 1px);
  background-size: 64px 64px;
  opacity: 0.4;
}
.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.15;
}
.bg-orb-1 {
  width: 600px;
  height: 600px;
  top: -200px;
  left: -100px;
  background: var(--accent);
  animation: orb-float-1 20s ease-in-out infinite;
}
.bg-orb-2 {
  width: 400px;
  height: 400px;
  bottom: -100px;
  right: -50px;
  background: #8B5CF6;
  animation: orb-float-2 25s ease-in-out infinite;
}
.bg-orb-3 {
  width: 300px;
  height: 300px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: #3B82F6;
  animation: orb-float-3 18s ease-in-out infinite;
}

@keyframes orb-float-1 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(80px, 60px) scale(1.1); }
  66% { transform: translate(-40px, -30px) scale(0.9); }
}
@keyframes orb-float-2 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(-60px, -50px) scale(1.15); }
  66% { transform: translate(30px, 40px) scale(0.85); }
}
@keyframes orb-float-3 {
  0%, 100% { transform: translate(-50%, -50%) scale(1); }
  50% { transform: translate(-50%, -50%) scale(1.2); }
}

/* ── 视图层 ── */
.view-layer {
  position: relative;
  z-index: var(--z-base);
  height: 100%;
  width: 100%;
}
</style>
