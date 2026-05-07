<template>
  <div class="signature-pad-wrapper">
    <div class="pad-controls">
      <span class="label">画笔粗细:</span>
      <el-slider v-model="lineWidth" :min="1" :max="8" :step="1" style="width: 100px" />
      <span class="label">颜色:</span>
      <el-color-picker v-model="strokeColor" :predefine="predefineColors" size="small" />
      <el-button size="small" @click="undo"><el-icon><RefreshLeft /></el-icon>撤销</el-button>
      <el-button size="small" @click="clear"><el-icon><Delete /></el-icon>清除</el-button>
    </div>
    <canvas
      ref="canvasRef"
      :width="width"
      :height="height"
      class="signature-canvas"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
      @pointerleave="onPointerUp"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

const props = defineProps({
  width: { type: Number, default: 400 },
  height: { type: Number, default: 160 },
})

const emit = defineEmits(['change'])

const canvasRef = ref(null)
const lineWidth = ref(2)
const strokeColor = ref('#ffffff')
const predefineColors = ['#ffffff', '#00d4ff', '#67c23a', '#e6a23c']

let ctx = null
let isDrawing = false
let paths = []       // 所有已完成笔画
let currentPath = [] // 当前正在绘制的笔迹

onMounted(() => {
  const canvas = canvasRef.value
  if (canvas) {
    ctx = canvas.getContext('2d')
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'
  }
})

watch(lineWidth, (val) => {
  if (ctx) ctx.lineWidth = val
})

watch(strokeColor, (val) => {
  if (ctx) ctx.strokeStyle = val
})

function onPointerDown(e) {
  isDrawing = true
  const { offsetX, offsetY } = e
  currentPath = [{ x: offsetX, y: offsetY }]
  ctx.beginPath()
  ctx.strokeStyle = strokeColor.value
  ctx.lineWidth = lineWidth.value
  ctx.moveTo(offsetX, offsetY)
}

function onPointerMove(e) {
  if (!isDrawing) return
  const { offsetX, offsetY } = e
  currentPath.push({ x: offsetX, y: offsetY })

  // 贝塞尔曲线平滑
  if (currentPath.length >= 3) {
    const len = currentPath.length
    const p0 = currentPath[len - 3]
    const p1 = currentPath[len - 2]
    const p2 = currentPath[len - 1]
    const midX = (p1.x + p2.x) / 2
    const midY = (p1.y + p2.y) / 2
    ctx.quadraticCurveTo(p1.x, p1.y, midX, midY)
    ctx.stroke()
  } else {
    ctx.lineTo(offsetX, offsetY)
    ctx.stroke()
  }
}

function onPointerUp() {
  if (!isDrawing) return
  isDrawing = false
  if (currentPath.length > 0) {
    paths.push({
      points: [...currentPath],
      color: strokeColor.value,
      width: lineWidth.value,
    })
    currentPath = []
    emit('change', paths.length > 0)
  }
}

function redrawAll() {
  ctx.clearRect(0, 0, props.width, props.height)
  for (const path of paths) {
    if (path.points.length < 2) continue
    ctx.beginPath()
    ctx.strokeStyle = path.color
    ctx.lineWidth = path.width
    ctx.moveTo(path.points[0].x, path.points[0].y)
    for (let i = 1; i < path.points.length; i++) {
      ctx.lineTo(path.points[i].x, path.points[i].y)
    }
    ctx.stroke()
  }
}

function undo() {
  if (paths.length === 0) return
  paths.pop()
  redrawAll()
  emit('change', paths.length > 0)
}

function clear() {
  paths = []
  ctx.clearRect(0, 0, props.width, props.height)
  emit('change', false)
}

function toDataURL(type = 'image/png') {
  return canvasRef.value?.toDataURL(type) || ''
}

function isEmpty() {
  return paths.length === 0
}

defineExpose({ toDataURL, clear, undo, isEmpty })
</script>

<style lang="scss" scoped>
.signature-pad-wrapper {
  .pad-controls {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
    .label { font-size: 14px; color: #606266; }
  }

  .signature-canvas {
    border: 2px dashed rgba(0,212,255,0.25);
    border-radius: 8px;
    cursor: crosshair;
    display: block;
    touch-action: none;
    background: #0b1a2e;
    &:hover { border-color: #00d4ff; }
  }
}
</style>
