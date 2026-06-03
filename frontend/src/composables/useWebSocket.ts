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
    const host = import.meta.env.DEV ? 'localhost:8741' : window.location.host
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
    const host = import.meta.env.DEV ? 'localhost:8741' : window.location.host
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
/**
 * 全局通知 WebSocket（带心跳和自动重连）
 * 用于 Dashboard 实时统计更新和全局通知
 */
export function useGlobalWebSocket() {
  const connected = ref(false)
  const lastMessage = ref<any>(null)
  const reconnectAttempt = ref(0)
  const maxReconnectAttempts = 10

  let ws: WebSocket | null = null
  let heartbeatTimer: ReturnType<typeof setInterval> | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null

  const buildUrl = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = import.meta.env.DEV ? 'localhost:8741' : window.location.host
    return `${protocol}//${host}/ws/notifications`
  }

  const startHeartbeat = () => {
    stopHeartbeat()
    heartbeatTimer = setInterval(() => {
      if (ws?.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }))
      }
    }, 30000) // 每30秒发送心跳
  }

  const stopHeartbeat = () => {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }

  const scheduleReconnect = () => {
    if (reconnectAttempt.value >= maxReconnectAttempts) {
      console.warn('[WS] 达到最大重连次数，停止重连')
      return
    }

    const delay = Math.min(1000 * Math.pow(2, reconnectAttempt.value), 30000) // 指数退避，最大30秒
    reconnectAttempt.value++

    console.log(`[WS] ${delay / 1000}s 后尝试第 ${reconnectAttempt.value} 次重连...`)
    reconnectTimer = setTimeout(() => {
      connect()
    }, delay)
  }

  const connect = () => {
    // 清理旧的连接
    disconnect(false)

    try {
      ws = new WebSocket(buildUrl())

      ws.onopen = () => {
        connected.value = true
        reconnectAttempt.value = 0
        startHeartbeat()
        console.log('[WS] 已连接')
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          // 忽略心跳响应
          if (data.type === 'pong') return
          lastMessage.value = data
        } catch {
          lastMessage.value = event.data
        }
      }

      ws.onerror = () => {
        console.error('[WS] 连接错误')
      }

      ws.onclose = (event) => {
        connected.value = false
        stopHeartbeat()

        // 非主动关闭时自动重连
        if (event.code !== 1000 && event.code !== 1001) {
          scheduleReconnect()
        }
      }
    } catch (e) {
      console.error('[WS] 创建连接失败:', e)
      scheduleReconnect()
    }
  }

  const disconnect = (permanent = true) => {
    if (permanent) {
      reconnectAttempt.value = maxReconnectAttempts // 阻止重连
    }
    stopHeartbeat()
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    if (ws) {
      ws.close(1000, 'Client disconnect')
      ws = null
    }
    connected.value = false
  }

  onUnmounted(() => {
    disconnect(true)
  })

  return {
    connected,
    lastMessage,
    reconnectAttempt,
    connect,
    disconnect,
  }
}