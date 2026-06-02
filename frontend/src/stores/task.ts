import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { tasksApi, type Task } from '@/api/tasks'

export const useTaskStore = defineStore('task', () => {
  const tasks = ref<Task[]>([])
  const loading = ref(false)
  const currentTask = ref<Task | null>(null)

  const runningTasks = computed(() =>
    tasks.value.filter((t) => t.status === 'running' || t.status === 'pending')
  )

  const completedTasks = computed(() =>
    tasks.value.filter((t) => t.status === 'completed')
  )

  const failedTasks = computed(() =>
    tasks.value.filter((t) => t.status === 'failed')
  )

  async function fetchTasks(params?: { status?: string; limit?: number }) {
    loading.value = true
    try {
      tasks.value = await tasksApi.list(params) as any
    } catch (error) {
      console.error('Failed to fetch tasks:', error)
    } finally {
      loading.value = false
    }
  }

  async function fetchTask(id: number) {
    loading.value = true
    try {
      currentTask.value = await tasksApi.get(id) as any
      return currentTask.value
    } catch (error) {
      console.error('Failed to fetch task:', error)
    } finally {
      loading.value = false
    }
  }

  async function createTask(data: import('@/api/tasks').TaskCreate) {
    try {
      const task = await tasksApi.create(data) as any
      tasks.value.unshift(task)
      return task
    } catch (error) {
      console.error('Failed to create task:', error)
      throw error
    }
  }

  async function cancelTask(id: number) {
    try {
      await tasksApi.cancel(id)
      const task = tasks.value.find((t) => t.id === id)
      if (task) {
        task.status = 'cancelled'
      }
    } catch (error) {
      console.error('Failed to cancel task:', error)
      throw error
    }
  }

  async function retryTask(id: number) {
    try {
      const newTask = await tasksApi.retry(id) as any
      tasks.value.unshift(newTask)
      return newTask
    } catch (error) {
      console.error('Failed to retry task:', error)
      throw error
    }
  }

  function updateTaskProgress(taskId: number, progress: number) {
    const task = tasks.value.find((t) => t.id === taskId)
    if (task) {
      task.progress = progress
    }
  }

  function updateTaskStatus(taskId: number, status: string) {
    const task = tasks.value.find((t) => t.id === taskId)
    if (task) {
      task.status = status
    }
  }

  return {
    tasks,
    loading,
    currentTask,
    runningTasks,
    completedTasks,
    failedTasks,
    fetchTasks,
    fetchTask,
    createTask,
    cancelTask,
    retryTask,
    updateTaskProgress,
    updateTaskStatus,
  }
})
