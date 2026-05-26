<template>
  <el-config-provider :locale="zhCn">
    <div id="app" class="app-container">
      <router-view />
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { provide, onMounted } from 'vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

provide('locale', zhCn)

// 初始化主题
onMounted(() => {
  themeStore.initTheme()
})
</script>

<style>
@import '@/styles/theme.css';
@import '@/styles/global.css';

.app-container {
  height: 100%;
  width: 100%;
  background: var(--bg-gradient);
  position: relative;
  overflow: hidden;
}

/* 背景装饰元素 */
.app-container::before {
  content: '';
  position: fixed;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(
    circle at 20% 20%,
    rgba(79, 172, 254, 0.08) 0%,
    transparent 50%
  );
  pointer-events: none;
  z-index: 0;
}

.app-container::after {
  content: '';
  position: fixed;
  bottom: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(
    circle at 80% 80%,
    rgba(118, 75, 162, 0.06) 0%,
    transparent 50%
  );
  pointer-events: none;
  z-index: 0;
}

/* 确保内容在背景之上 */
#app > div,
#app > div > div {
  position: relative;
  z-index: 1;
}

/* 页面过渡动画 */
.page-enter-active,
.page-leave-active {
  transition: all var(--transition-slow);
}

.page-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* 淡入淡出过渡 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-normal);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 滑动过渡 */
.slide-enter-active,
.slide-leave-active {
  transition: all var(--transition-normal);
}

.slide-enter-from {
  transform: translateX(-20px);
  opacity: 0;
}

.slide-leave-to {
  transform: translateX(20px);
  opacity: 0;
}
</style>
