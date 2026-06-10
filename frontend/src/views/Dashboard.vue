<template>
  <div class="dashboard-view">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <stat-card
        title="运行中"
        :value="runningTasks.length"
        icon="Loading"
        variant="primary"
      />
      <stat-card
        title="已完成"
        :value="completedTasks.length"
        icon="CircleCheck"
        variant="success"
      />
      <stat-card
        title="失败"
        :value="failedTasks.length"
        icon="CircleClose"
        variant="danger"
      />
      <stat-card
        title="总文件"
        :value="totalFiles"
        icon="Files"
        variant="info"
      />
    </div>

    <!-- 内容区域 -->
    <div class="content-grid">
      <!-- 最近任务 -->
      <div class="content-section glass-card">
        <div class="section-header">
          <h3 class="section-title">最近任务</h3>
          <el-button type="primary" size="small" :icon="Plus" @click="goToTasks">
            创建任务
          </el-button>
        </div>
        <task-list :tasks="recentTasks" :loading="loading" @refresh="fetchData" />
      </div>

      <!-- 存储统计 -->
      <div class="content-section glass-card">
        <div class="section-header">
          <h3 class="section-title">存储统计</h3>
        </div>
        <stats-card :stats="stats" :loading="statsLoading" :compact="true" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus } from '@element-plus/icons-vue'
import { useTaskStore } from '@/stores/task'
import { filesApi, type FileStats } from '@/api/files'
import TaskList from '@/components/TaskList.vue'
import StatsCard from '@/components/StatsCard.vue'
import StatCard from '@/components/StatCard.vue'

const router = useRouter()
const taskStore = useTaskStore()

const loading = ref(false)
const statsLoading = ref(false)
const stats = ref<FileStats | null>(null)

const runningTasks = computed(() => taskStore.runningTasks)
const completedTasks = computed(() => taskStore.completedTasks)
const failedTasks = computed(() => taskStore.failedTasks)
const recentTasks = computed(() => taskStore.tasks.slice(0, 5))
const totalFiles = computed(() => stats.value?.total_files || 0)

async function fetchData() {
  loading.value = true
  statsLoading.value = true
  try {
    await Promise.all([
      taskStore.fetchTasks({ limit: 10 }),
      filesApi.getStats().then((data) => {
        stats.value = data
      }),
    ])
  } finally {
    loading.value = false
    statsLoading.value = false
  }
}

function goToTasks() {
  router.push({ name: 'Tasks' })
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.dashboard-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

/* ============================================
   统计卡片网格
   ============================================ */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-lg);
}


/* ============================================
   内容网格
   ============================================ */
.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--space-lg);
}



.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-lg);
  padding-bottom: var(--space-md);
  border-bottom: 1px solid var(--divider-color);
}

.section-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}
</style>
