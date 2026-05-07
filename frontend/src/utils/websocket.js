/**
 * WebSocket 工具类
 * 支持自动重连、心跳检测
 */
export class WebSocketClient {
  constructor(url, options = {}) {
    this.url = url
    this.ws = null
    this.options = {
      reconnect: true,
      reconnectInterval: 3000,
      maxReconnectAttempts: 10,
      heartbeatInterval: 30000,
      ...options,
    }
    this.reconnectAttempts = 0
    this.heartbeatTimer = null
    this.isManualClose = false
    this.listeners = {
      open: [],
      message: [],
      close: [],
      error: [],
    }
  }

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) return

    this.ws = new WebSocket(this.url)
    this.isManualClose = false

    this.ws.onopen = (event) => {
      console.log('[WS] 连接已建立:', this.url)
      this.reconnectAttempts = 0
      this.startHeartbeat()
      this.emit('open', event)
    }

    this.ws.onmessage = (event) => {
      let data = event.data
      try {
        data = JSON.parse(event.data)
      } catch (e) {
        // 非 JSON 数据(如二进制)
      }

      // 处理心跳响应
      if (data?.type === 'pong') return

      this.emit('message', data)
    }

    this.ws.onclose = (event) => {
      console.log('[WS] 连接已关闭:', event.code, event.reason)
      this.stopHeartbeat()
      this.emit('close', event)

      if (!this.isManualClose && this.options.reconnect && this.reconnectAttempts < this.options.maxReconnectAttempts) {
        this.reconnectAttempts++
        console.log(`[WS] ${this.options.reconnectInterval}ms 后第 ${this.reconnectAttempts} 次重连...`)
        setTimeout(() => this.connect(), this.options.reconnectInterval)
      }
    }

    this.ws.onerror = (event) => {
      console.error('[WS] 连接错误:', event)
      this.emit('error', event)
    }
  }

  send(data) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      if (typeof data === 'object' && !(data instanceof ArrayBuffer) && !(data instanceof Blob)) {
        this.ws.send(JSON.stringify(data))
      } else {
        this.ws.send(data)
      }
    } else {
      console.warn('[WS] 连接未就绪，无法发送数据')
    }
  }

  sendBinary(data) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(data)
    }
  }

  close() {
    this.isManualClose = true
    this.stopHeartbeat()
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  on(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event].push(callback)
    }
    return this
  }

  off(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback)
    }
    return this
  }

  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(cb => cb(data))
    }
  }

  startHeartbeat() {
    this.stopHeartbeat()
    this.heartbeatTimer = setInterval(() => {
      this.send({ type: 'ping' })
    }, this.options.heartbeatInterval)
  }

  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  get isConnected() {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

/**
 * 创建会议转写 WebSocket
 */
export function createTranscribeWS(meetingId) {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host
  return new WebSocketClient(`${protocol}//${host}/ws/meeting/${meetingId}/transcribe`)
}

/**
 * 创建 AI 问答 WebSocket
 */
export function createAIQaWS(meetingId) {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host
  return new WebSocketClient(`${protocol}//${host}/ws/meeting/${meetingId}/ai-qa`)
}
