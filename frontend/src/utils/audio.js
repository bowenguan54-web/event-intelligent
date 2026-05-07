/**
 * 音频采集工具
 * 通过 Web Audio API 采集麦克风音频流
 * 以 PCM 16kHz 采样率分帧(每帧200ms)发送
 */
export class AudioRecorder {
  constructor(options = {}) {
    this.options = {
      sampleRate: 16000,
      frameSize: 200, // ms
      ...options,
    }
    this.stream = null
    this.audioContext = null
    this.processor = null
    this.isRecording = false
    this.onAudioData = null // 回调: (PCM ArrayBuffer) => void
  }

  async start() {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: this.options.sampleRate,
          echoCancellation: true,
          noiseSuppression: true,
        },
      })

      this.audioContext = new AudioContext({ sampleRate: this.options.sampleRate })
      const source = this.audioContext.createMediaStreamSource(this.stream)

      // 使用 ScriptProcessor (兼容性好) 或 AudioWorklet
      const bufferSize = Math.round((this.options.sampleRate * this.options.frameSize) / 1000)
      // 确保 bufferSize 是 2 的幂次
      const adjustedBufferSize = Math.pow(2, Math.ceil(Math.log2(bufferSize)))
      this.processor = this.audioContext.createScriptProcessor(adjustedBufferSize, 1, 1)

      this.processor.onaudioprocess = (event) => {
        if (!this.isRecording) return
        const inputData = event.inputBuffer.getChannelData(0)
        // 转换为 16-bit PCM
        const pcmData = float32ToInt16(inputData)
        if (this.onAudioData) {
          this.onAudioData(pcmData.buffer)
        }
      }

      source.connect(this.processor)
      this.processor.connect(this.audioContext.destination)
      this.isRecording = true

      console.log('[AudioRecorder] 录音已开始')
    } catch (error) {
      console.error('[AudioRecorder] 启动失败:', error)
      throw error
    }
  }

  pause() {
    this.isRecording = false
    console.log('[AudioRecorder] 录音已暂停')
  }

  resume() {
    this.isRecording = true
    console.log('[AudioRecorder] 录音已恢复')
  }

  stop() {
    this.isRecording = false
    if (this.processor) {
      this.processor.disconnect()
      this.processor = null
    }
    if (this.audioContext) {
      this.audioContext.close()
      this.audioContext = null
    }
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop())
      this.stream = null
    }
    console.log('[AudioRecorder] 录音已停止')
  }
}

/**
 * Float32 转 Int16 PCM
 */
function float32ToInt16(float32Array) {
  const int16Array = new Int16Array(float32Array.length)
  for (let i = 0; i < float32Array.length; i++) {
    const s = Math.max(-1, Math.min(1, float32Array[i]))
    int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
  }
  return int16Array
}
