<template>
  <div class="dashboard-view">
    <el-row :gutter="20">
      <el-col :span="6">
        <stat-card title="运行中" :value="runningTasks.length" icon="Loading" color="#409eff" />
      </el-col>
      <el-col :span="6">
        <stat-card title="已完成" :value="completedTasks.length" icon="CircleCheck" color="#67c23a" />
      </el-col>
      <el-col :span="6">
        <stat-card title="失败" :value="failedTasks.length" icon="CircleClose" color="#f56c6c" />
      </el-col>
      <el-col :span="6">
        <stat-card title="总文件" :value="totalFiles" icon="Files" color="#e6a23c" />
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card shadow="never">
          <template #header>
            <span>最近任务</span>
          </template>
          <task-list :tasks="recentTasks" :loading="loading" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>
            <span>存储统计</span>
          </template>
          <stats-card :stats="stats" :loading="statsLoading" :compact="true" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useTaskStore } from '@/stores/task'
import { filesApi, type FileStats } from '@/api/files'
import TaskList from '@/components/TaskList.vue'
import StatsCard from '@/components/StatsCard.vue'
import StatCard from '@/components/StatCard.vue'

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

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.dashboard-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
</style>
