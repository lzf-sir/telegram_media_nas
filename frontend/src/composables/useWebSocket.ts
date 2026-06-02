import { ref, onUnmounted } from 'vue'

export interface TaskProgressMessage {
  type: 'progress' | 'complete'
  task_id: number
  status: string
  current: number
  total: number
  success: number
  failed: number
  skipped?: number
  downloaded_bytes: number
  total_bytes: number
  current_file?: string
  progress: number
  isSuccess?: boolean
  message?: string
}

export function useTaskWebSocket(taskId: number) {
  const connected = ref(false)
  const progress = ref<TaskProgressMessage | null>(null)
  const error = ref<string | null>(null)
  let ws: WebSocket | null = null

  const connect = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = import.meta.env.DEV ? 'localhost:8000' : window.location.host
    ws = new WebSocket(`${protocol}//${host}/ws/task/${taskId}`)

    ws.onopen = () => {
      connected.value = true
      error.value = null
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as TaskProgressMessage
        progress.value = data
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }

    ws.onerror = (event) => {
      error.value = 'WebSocket connection error'
      console.error('WebSocket error:', event)
    }

    ws.onclose = () => {
      connected.value = false
    }
  }

  const disconnect = () => {
    if (ws) {
      ws.close()
      ws = null
    }
  }

  const send = (data: unknown) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data))
    }
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    connected,
    progress,
    error,
    connect,
    disconnect,
    send,
  }
}

export function useNotificationsWebSocket() {
  const connected = ref(false)
  const message = ref<unknown>(null)
  let ws: WebSocket | null = null

  const connect = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = import.meta.env.DEV ? 'localhost:8000' : window.location.host
    ws = new WebSocket(`${protocol}//${host}/ws/notifications`)

    ws.onopen = () => {
      connected.value = true
    }

    ws.onmessage = (event) => {
      try {
        message.value = JSON.parse(event.data)
      } catch (e) {
        message.value = event.data
      }
    }

    ws.onclose = () => {
      connected.value = false
    }
  }

  const disconnect = () => {
    if (ws) {
      ws.close()
      ws = null
    }
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    connected,
    message,
    connect,
    disconnect,
  }
}
