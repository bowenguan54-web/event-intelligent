import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useMeetingStore = defineStore('meeting', () => {
  // 当前会议上下文
  const currentMeeting = ref(null)
  const wsConnected = ref(false)
  const recordingStatus = ref('idle') // idle | recording | paused | stopped
  const recordingDuration = ref(0)
  const transcripts = ref([])
  const keypoints = ref([])

  // WebSocket 实例
  let ws = null
  let timerInterval = null

  // 实时签到事件（供 MeetingLive 监听）
  const lastCheckinEvent = ref(null)

  function setCurrentMeeting(meeting) {
    currentMeeting.value = meeting
  }

  function connectWebSocket(meetingId) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    ws = new WebSocket(`${protocol}//${host}/ws/meeting/${meetingId}/transcribe`)

    ws.onopen = () => {
      wsConnected.value = true
      console.log('WebSocket 已连接')
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleWSMessage(data)
    }

    ws.onclose = () => {
      wsConnected.value = false
      console.log('WebSocket 已断开')
    }

    ws.onerror = (err) => {
      console.error('WebSocket 错误:', err)
    }
  }

  function handleWSMessage(data) {
    switch (data.type) {
      case 'transcript':
        if (data.is_final) {
          transcripts.value.push(data)
        } else {
          // 更新中间结果
          const idx = transcripts.value.findIndex(t => t.segment_id === data.segment_id)
          if (idx >= 0) {
            transcripts.value[idx] = data
          } else {
            transcripts.value.push(data)
          }
        }
        break
      case 'status':
        recordingStatus.value = data.status
        break
      case 'checkin':
        lastCheckinEvent.value = { userId: data.user_id, checkedIn: data.checked_in, ts: Date.now() }
        break
    }
  }

  function sendWSCommand(command) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(command))
    }
  }

  function sendAudioData(audioData) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(audioData)
    }
  }

  function startRecording() {
    recordingStatus.value = 'recording'
    sendWSCommand({ type: 'start' })
    recordingDuration.value = 0
    timerInterval = setInterval(() => {
      recordingDuration.value++
    }, 1000)
  }

  function pauseRecording() {
    recordingStatus.value = 'paused'
    sendWSCommand({ type: 'pause' })
    if (timerInterval) clearInterval(timerInterval)
  }

  function stopRecording() {
    recordingStatus.value = 'stopped'
    sendWSCommand({ type: 'stop' })
    if (timerInterval) clearInterval(timerInterval)
  }

  function disconnectWebSocket() {
    if (ws) {
      ws.close()
      ws = null
    }
    if (timerInterval) clearInterval(timerInterval)
    wsConnected.value = false
  }

  function resetRecordingToIdle() {
    recordingStatus.value = 'idle'
    if (timerInterval) {
      clearInterval(timerInterval)
      timerInterval = null
    }
  }

  function resetState() {
    currentMeeting.value = null
    transcripts.value = []
    keypoints.value = []
    recordingStatus.value = 'idle'
    recordingDuration.value = 0
    disconnectWebSocket()
  }

  return {
    currentMeeting,
    wsConnected,
    recordingStatus,
    recordingDuration,
    transcripts,
    keypoints,
    lastCheckinEvent,
    setCurrentMeeting,
    connectWebSocket,
    disconnectWebSocket,
    sendAudioData,
    startRecording,
    pauseRecording,
    stopRecording,
    resetRecordingToIdle,
    resetState,
  }
})
