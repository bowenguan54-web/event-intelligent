<template>
  <div class="room-management">
    <div class="page-header">
      <h2>会议室管理</h2>
    </div>

    <!-- 座位布局编辑器 -->
    <div class="room-editor" v-if="editingRoom">
      <div class="editor-toolbar">
        <span class="editor-title">{{ editingRoom.name }} — 座位布局编辑</span>
        <div class="toolbar-right">
          <el-button :disabled="undoStack.length === 0" @click="handleUndo" title="撤销 (Ctrl+Z)">
            ↩ 撤销
          </el-button>
          <el-button :disabled="redoStack.length === 0" @click="handleRedo" title="重做 (Ctrl+Y)">
            ↪ 重做
          </el-button>
          <el-button type="success" @click="addSeat">
            <el-icon><Plus /></el-icon> 添加座位
          </el-button>
          <el-button type="warning" @click="addTable">
            <el-icon><Plus /></el-icon> 添加桌子
          </el-button>
          <el-button type="primary" :loading="saving" @click="saveLayout">
            💾 保存布局
          </el-button>
        </div>
      </div>

      <div class="editor-body">
        <!-- 左侧：可视化画布 -->
        <div class="editor-canvas-wrap">
          <div class="canvas-info">
            画布: {{ editorWidth }} × {{ editorHeight }}px
            &nbsp;|&nbsp; 座位: {{ editorSeats.length }}
            &nbsp;|&nbsp; 桌子: {{ editorTables.length }}
            &nbsp;|&nbsp;
            <el-button text type="primary" size="small" @click="showCanvasDialog = true">修改画布尺寸</el-button>
          </div>
          <div
            class="editor-canvas"
            ref="canvasRef"
            :style="{ width: editorWidth * canvasScale + 'px', height: editorHeight * canvasScale + 'px' }"
            @mousedown="onCanvasMouseDown"
            @mousemove="onCanvasMouseMove"
            @mouseup="onCanvasMouseUp"
          >
            <!-- 屏幕标记 -->
            <div
              v-if="editorScreen"
              class="canvas-screen"
              :class="{ 'is-selected': selectedType === 'screen' }"
              :style="screenStyle"
              @mousedown.stop="startDrag('screen', -1, $event)"
            >大屏幕</div>

            <!-- 桌子 -->
            <div
              v-for="(t, ti) in editorTables"
              :key="'t' + ti"
              class="canvas-table"
              :class="{ 'is-selected': selectedType === 'table' && selectedIndex === ti }"
              :style="tableStyle(t)"
              @mousedown.stop="startDrag('table', ti, $event)"
            >{{ t.label || '桌子' }}
              <!-- 缩放手柄（仅选中时显示） -->
              <template v-if="selectedType === 'table' && selectedIndex === ti">
                <div class="resize-handle rh-n" @mousedown.stop="startResize('n', ti, $event)"></div>
                <div class="resize-handle rh-s" @mousedown.stop="startResize('s', ti, $event)"></div>
                <div class="resize-handle rh-e" @mousedown.stop="startResize('e', ti, $event)"></div>
                <div class="resize-handle rh-w" @mousedown.stop="startResize('w', ti, $event)"></div>
                <div class="resize-handle rh-ne" @mousedown.stop="startResize('ne', ti, $event)"></div>
                <div class="resize-handle rh-nw" @mousedown.stop="startResize('nw', ti, $event)"></div>
                <div class="resize-handle rh-se" @mousedown.stop="startResize('se', ti, $event)"></div>
                <div class="resize-handle rh-sw" @mousedown.stop="startResize('sw', ti, $event)"></div>
              </template>
            </div>

            <!-- 座位 -->
            <div
              v-for="(s, si) in editorSeats"
              :key="'s' + si"
              class="canvas-seat"
              :class="{ 'is-selected': selectedType === 'seat' && selectedIndex === si }"
              :style="seatStyle(s)"
              @mousedown.stop="startDrag('seat', si, $event)"
            >
              <div style="font-weight:bold;font-size:14px">{{ s.id }}</div>
              <div v-if="s.ip" style="font-size:14px;opacity:0.7;line-height:1.2;margin-top:1px">{{ s.ip }}</div>
            </div>

            <!-- 对齐参考线 -->
            <div
              v-for="(g, gi) in guideLines"
              :key="'guide' + gi"
              class="snap-guide"
              :class="g.type === 'v' ? 'snap-guide-v' : 'snap-guide-h'"
              :style="g.type === 'v'
                ? { left: g.pos * canvasScale + 'px', top: 0, height: editorHeight * canvasScale + 'px' }
                : { top: g.pos * canvasScale + 'px', left: 0, width: editorWidth * canvasScale + 'px' }"
            ></div>
          </div>
        </div>

        <!-- 右侧：属性面板 -->
        <div class="editor-props">
          <!-- 屏幕设置 -->
          <div class="props-section">
            <h4>大屏幕位置</h4>
            <div v-if="editorScreen" class="prop-row">
              <span>X:</span><el-input-number v-model="editorScreen.x" :min="0" :max="editorWidth" size="small" />
              <span>Y:</span><el-input-number v-model="editorScreen.y" :min="0" :max="editorHeight" size="small" />
            </div>
            <div v-if="editorScreen" class="prop-row">
              <span>宽</span><el-input-number v-model="editorScreen.w" :min="20" size="small" />
              <span>高</span><el-input-number v-model="editorScreen.h" :min="20" size="small" />
            </div>
            <el-button v-if="!editorScreen" size="small" @click="editorScreen = { x: 8, y: 100, w: 28, h: 160 }">添加屏幕</el-button>
            <el-button v-else size="small" type="danger" @click="editorScreen = null">移除屏幕</el-button>
          </div>

          <el-divider />

          <!-- 选中座位属性 -->
          <div class="props-section" v-if="selectedType === 'seat' && selectedIndex >= 0">
            <h4>座位属性 — #{{ editorSeats[selectedIndex]?.id }}</h4>
            <el-form label-width="60px" size="small">
              <el-form-item label="编号">
                <el-input-number v-model="editorSeats[selectedIndex].id" :min="1" />
              </el-form-item>
              <el-form-item label="标签">
                <el-input v-model="editorSeats[selectedIndex].label" placeholder="如：1号" />
              </el-form-item>
              <el-form-item label="X">
                <el-input-number v-model="editorSeats[selectedIndex].x" :min="0" />
              </el-form-item>
              <el-form-item label="Y">
                <el-input-number v-model="editorSeats[selectedIndex].y" :min="0" />
              </el-form-item>
              <el-form-item label="IP">
                <el-input v-model="editorSeats[selectedIndex].ip" placeholder="如：192.168.1.101" />
              </el-form-item>
              <el-form-item>
                <el-button type="danger" size="small" @click="deleteSeat(selectedIndex)">删除此座位</el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- 选中桌子属性 -->
          <div class="props-section" v-else-if="selectedType === 'table' && selectedIndex >= 0">
            <h4>桌子属性</h4>
            <el-form label-width="60px" size="small">
              <el-form-item label="标签">
                <el-input v-model="editorTables[selectedIndex].label" placeholder="如：会议桌" />
              </el-form-item>
              <el-form-item label="X">
                <el-input-number v-model="editorTables[selectedIndex].x" :min="0" />
              </el-form-item>
              <el-form-item label="Y">
                <el-input-number v-model="editorTables[selectedIndex].y" :min="0" />
              </el-form-item>
              <el-form-item label="宽">
                <el-input-number v-model="editorTables[selectedIndex].w" :min="20" />
              </el-form-item>
              <el-form-item label="高">
                <el-input-number v-model="editorTables[selectedIndex].h" :min="20" />
              </el-form-item>
              <el-form-item label="圆角">
                <el-input-number v-model="editorTables[selectedIndex].rx" :min="0" />
              </el-form-item>
              <el-form-item>
                <el-button type="danger" size="small" @click="deleteTable(selectedIndex)">删除此桌子</el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- 未选中提示 -->
          <div class="props-section" v-else>
            <p class="prop-hint">点击画布中的座位或桌子查看/编辑属性</p>
            <p class="prop-hint">拖拽可移动位置</p>
          </div>

          <el-divider />

          <!-- 座位列表 -->
          <div class="props-section">
            <h4>所有座位 ({{ editorSeats.length }})</h4>
            <div class="seat-list-scroll">
              <div
                v-for="(s, si) in editorSeats"
                :key="si"
                class="seat-list-item"
                :class="{ 'is-active': selectedType === 'seat' && selectedIndex === si }"
                @click="selectedType = 'seat'; selectedIndex = si"
              >
                <span class="seat-id">#{{ s.id }}</span>
                <span class="seat-label">{{ s.label || s.id + '号' }}</span>
                <span class="seat-ip" v-if="s.ip">{{ s.ip }}</span>
                <el-button type="danger" :icon="Delete" circle size="small" @click.stop="deleteSeat(si)" />
              </div>
              <el-empty v-if="editorSeats.length === 0" description="暂无座位" :image-size="40" />
            </div>
          </div>
        </div>
      </div>
    </div>



    <!-- 修改画布尺寸弹窗 -->
    <el-dialog v-model="showCanvasDialog" title="修改画布尺寸" width="380px">
      <el-form label-width="80px">
        <el-form-item label="宽度">
          <el-input-number v-model="editorWidth" :min="300" :max="2000" :step="50" />
        </el-form-item>
        <el-form-item label="高度">
          <el-input-number v-model="editorHeight" :min="200" :max="1500" :step="50" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button type="primary" @click="showCanvasDialog = false">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { getRoomList, createRoom, updateRoom, deleteRoom } from '@/api/room'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'

const rooms = ref([])
const editingRoom = ref(null)
const saving = ref(false)
const createDialogVisible = ref(false)
const createFormRef = ref(null)
const showCanvasDialog = ref(false)
const canvasRef = ref(null)

// 编辑器数据
const editorWidth = ref(700)
const editorHeight = ref(440)
const editorSeats = ref([])
const editorTables = ref([])
const editorScreen = ref(null)
const canvasScale = 0.85

// 选中状态
const selectedType = ref(null) // 'seat' | 'table' | 'screen'
const selectedIndex = ref(-1)

// 拖拽状态
let dragging = false
let dragType = null
let dragIndex = -1
let dragStartX = 0
let dragStartY = 0
let dragOrigX = 0
let dragOrigY = 0

// 缩放拖拽状态
let resizing = false
let resizeHandle = ''  // 'n','s','e','w','ne','nw','se','sw'
let resizeOrigX = 0
let resizeOrigY = 0
let resizeOrigW = 0
let resizeOrigH = 0

// ===== 撤销/重做 =====
const undoStack = ref([])
const redoStack = ref([])
const MAX_UNDO = 50

function captureState() {
  return {
    seats: JSON.stringify(editorSeats.value),
    tables: JSON.stringify(editorTables.value),
    screen: editorScreen.value ? JSON.stringify(editorScreen.value) : null,
  }
}

function pushUndo() {
  undoStack.value.push(captureState())
  if (undoStack.value.length > MAX_UNDO) undoStack.value.shift()
  redoStack.value = []
}

function handleUndo() {
  if (undoStack.value.length === 0) return
  redoStack.value.push(captureState())
  const state = undoStack.value.pop()
  editorSeats.value = JSON.parse(state.seats)
  editorTables.value = JSON.parse(state.tables)
  editorScreen.value = state.screen ? JSON.parse(state.screen) : null
}

function handleRedo() {
  if (redoStack.value.length === 0) return
  undoStack.value.push(captureState())
  const state = redoStack.value.pop()
  editorSeats.value = JSON.parse(state.seats)
  editorTables.value = JSON.parse(state.tables)
  editorScreen.value = state.screen ? JSON.parse(state.screen) : null
}

function onKeyDown(e) {
  if (!editingRoom.value) return
  if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
    e.preventDefault()
    handleUndo()
  } else if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) {
    e.preventDefault()
    handleRedo()
  }
}

// ===== 对齐吸附 =====
const SNAP_THRESHOLD = 8
const guideLines = ref([])  // { type: 'v'|'h', pos: number }

function getSnapEdges(excludeType, excludeIndex) {
  const edges = { v: [], h: [] }
  // 桌子
  editorTables.value.forEach((t, i) => {
    if (excludeType === 'table' && excludeIndex === i) return
    edges.v.push(t.x, t.x + t.w / 2, t.x + t.w)
    edges.h.push(t.y, t.y + t.h / 2, t.y + t.h)
  })
  // 座位
  editorSeats.value.forEach((s, i) => {
    if (excludeType === 'seat' && excludeIndex === i) return
    edges.v.push(s.x)
    edges.h.push(s.y)
  })
  // 屏幕
  if (editorScreen.value && excludeType !== 'screen') {
    const sc = editorScreen.value
    edges.v.push(sc.x, sc.x + sc.w / 2, sc.x + sc.w)
    edges.h.push(sc.y, sc.y + sc.h / 2, sc.y + sc.h)
  }
  return edges
}

function snapValue(val, targets) {
  let best = null
  let bestDist = SNAP_THRESHOLD + 1
  for (const t of targets) {
    const d = Math.abs(val - t)
    if (d < bestDist) {
      bestDist = d
      best = t
    }
  }
  return best
}

function applySnap(type, index, x, y) {
  const edges = getSnapEdges(type, index)
  const guides = []
  let snappedX = x, snappedY = y

  if (type === 'seat') {
    const sv = snapValue(x, edges.v)
    const sh = snapValue(y, edges.h)
    if (sv !== null) { snappedX = sv; guides.push({ type: 'v', pos: sv }) }
    if (sh !== null) { snappedY = sh; guides.push({ type: 'h', pos: sh }) }
  } else if (type === 'table') {
    const t = editorTables.value[index]
    const w = t.w, h = t.h
    // 检查左、中、右
    const svL = snapValue(x, edges.v)
    const svC = snapValue(x + w / 2, edges.v)
    const svR = snapValue(x + w, edges.v)
    if (svL !== null) { snappedX = svL; guides.push({ type: 'v', pos: svL }) }
    else if (svC !== null) { snappedX = svC - w / 2; guides.push({ type: 'v', pos: svC }) }
    else if (svR !== null) { snappedX = svR - w; guides.push({ type: 'v', pos: svR }) }
    // 检查上、中、下
    const shT = snapValue(y, edges.h)
    const shC = snapValue(y + h / 2, edges.h)
    const shB = snapValue(y + h, edges.h)
    if (shT !== null) { snappedY = shT; guides.push({ type: 'h', pos: shT }) }
    else if (shC !== null) { snappedY = shC - h / 2; guides.push({ type: 'h', pos: shC }) }
    else if (shB !== null) { snappedY = shB - h; guides.push({ type: 'h', pos: shB }) }
  } else if (type === 'screen' && editorScreen.value) {
    const sc = editorScreen.value
    const svL = snapValue(x, edges.v)
    const svR = snapValue(x + sc.w, edges.v)
    if (svL !== null) { snappedX = svL; guides.push({ type: 'v', pos: svL }) }
    else if (svR !== null) { snappedX = svR - sc.w; guides.push({ type: 'v', pos: svR }) }
    const shT = snapValue(y, edges.h)
    const shB = snapValue(y + sc.h, edges.h)
    if (shT !== null) { snappedY = shT; guides.push({ type: 'h', pos: shT }) }
    else if (shB !== null) { snappedY = shB - sc.h; guides.push({ type: 'h', pos: shB }) }
  }

  guideLines.value = guides
  return { x: snappedX, y: snappedY }
}

const createForm = reactive({
  name: '',
  description: '',
  room_width: 700,
  room_height: 440,
})

const createRules = {
  name: [{ required: true, message: '请输入会议室名称', trigger: 'blur' }],
}

function getSeatCount(room) {
  if (!room.seats_data) return 0
  try { return JSON.parse(room.seats_data).length } catch { return 0 }
}

async function loadRooms() {
  try {
    rooms.value = await getRoomList()
  } catch (e) {
    ElMessage.error('加载会议室列表失败')
  }
}

function openCreateDialog() {
  createForm.name = ''
  createForm.description = ''
  createForm.room_width = 700
  createForm.room_height = 440
  createDialogVisible.value = true
}

async function handleCreateRoom() {
  const valid = await createFormRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    await createRoom({
      name: createForm.name,
      description: createForm.description,
      room_width: createForm.room_width,
      room_height: createForm.room_height,
    })
    ElMessage.success('会议室创建成功')
    createDialogVisible.value = false
    await loadRooms()
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '创建失败')
  } finally {
    saving.value = false
  }
}

async function handleDeleteRoom(room) {
  try {
    await ElMessageBox.confirm(`确定删除会议室"${room.name}"？`, '确认删除', { type: 'warning' })
  } catch { return }
  try {
    await deleteRoom(room.id)
    ElMessage.success('已删除')
    await loadRooms()
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '删除失败')
  }
}

function startEditing(room) {
  editingRoom.value = room
  editorWidth.value = room.room_width || 700
  editorHeight.value = room.room_height || 440
  editorTables.value = room.tables_data ? JSON.parse(room.tables_data) : []
  editorSeats.value = room.seats_data ? JSON.parse(room.seats_data) : []
  editorScreen.value = room.screen_data ? JSON.parse(room.screen_data) : null
  selectedType.value = null
  selectedIndex.value = -1
}

function exitEditor() {
  editingRoom.value = null
  selectedType.value = null
  selectedIndex.value = -1
}

function addSeat() {
  pushUndo()
  const maxId = editorSeats.value.reduce((m, s) => Math.max(m, s.id || 0), 0)
  editorSeats.value.push({
    id: maxId + 1,
    label: `${maxId + 1}号`,
    x: editorWidth.value / 2,
    y: editorHeight.value / 2,
    ip: '',
  })
  selectedType.value = 'seat'
  selectedIndex.value = editorSeats.value.length - 1
}

function deleteSeat(idx) {
  pushUndo()
  editorSeats.value.splice(idx, 1)
  if (selectedType.value === 'seat' && selectedIndex.value === idx) {
    selectedType.value = null
    selectedIndex.value = -1
  }
}

function addTable() {
  pushUndo()
  editorTables.value.push({
    x: editorWidth.value / 2 - 75,
    y: editorHeight.value / 2 - 40,
    w: 150,
    h: 80,
    rx: 10,
    label: '桌子',
  })
  selectedType.value = 'table'
  selectedIndex.value = editorTables.value.length - 1
}

function deleteTable(idx) {
  pushUndo()
  editorTables.value.splice(idx, 1)
  if (selectedType.value === 'table' && selectedIndex.value === idx) {
    selectedType.value = null
    selectedIndex.value = -1
  }
}

async function saveLayout() {
  if (!editingRoom.value) return
  saving.value = true
  try {
    await updateRoom(editingRoom.value.id, {
      room_width: editorWidth.value,
      room_height: editorHeight.value,
      tables_data: JSON.stringify(editorTables.value),
      seats_data: JSON.stringify(editorSeats.value),
      screen_data: editorScreen.value ? JSON.stringify(editorScreen.value) : null,
    })
    ElMessage.success('布局已保存')
    await loadRooms()
    // update editingRoom reference
    const updated = rooms.value.find(r => r.id === editingRoom.value.id)
    if (updated) editingRoom.value = updated
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

// ===== 画布元素样式 =====
const screenStyle = computed(() => {
  if (!editorScreen.value) return {}
  const s = editorScreen.value
  return {
    left: s.x * canvasScale + 'px',
    top: s.y * canvasScale + 'px',
    width: s.w * canvasScale + 'px',
    height: s.h * canvasScale + 'px',
  }
})

function tableStyle(t) {
  return {
    left: t.x * canvasScale + 'px',
    top: t.y * canvasScale + 'px',
    width: t.w * canvasScale + 'px',
    height: t.h * canvasScale + 'px',
    borderRadius: (t.rx || 0) * canvasScale + 'px',
  }
}

function seatStyle(s) {
  const size = 36
  return {
    left: (s.x - size / 2) * canvasScale + 'px',
    top: (s.y - size / 2) * canvasScale + 'px',
    width: size * canvasScale + 'px',
    height: size * canvasScale + 'px',
  }
}

// ===== 拖拽 =====
function startDrag(type, index, e) {
  pushUndo()
  dragging = true
  dragType = type
  dragIndex = index
  dragStartX = e.clientX
  dragStartY = e.clientY
  selectedType.value = type
  selectedIndex.value = index

  if (type === 'seat' && index >= 0) {
    dragOrigX = editorSeats.value[index].x
    dragOrigY = editorSeats.value[index].y
  } else if (type === 'table' && index >= 0) {
    dragOrigX = editorTables.value[index].x
    dragOrigY = editorTables.value[index].y
  } else if (type === 'screen' && editorScreen.value) {
    dragOrigX = editorScreen.value.x
    dragOrigY = editorScreen.value.y
  }
}

// ===== 缩放桌子 =====
function startResize(handle, index, e) {
  e.stopPropagation()
  pushUndo()
  resizing = true
  resizeHandle = handle
  dragIndex = index
  dragStartX = e.clientX
  dragStartY = e.clientY
  const t = editorTables.value[index]
  resizeOrigX = t.x
  resizeOrigY = t.y
  resizeOrigW = t.w
  resizeOrigH = t.h
  selectedType.value = 'table'
  selectedIndex.value = index
}

function onCanvasMouseDown() {
  // Click on empty area deselects
  if (!dragging && !resizing) {
    selectedType.value = null
    selectedIndex.value = -1
  }
}

function onCanvasMouseMove(e) {
  if (resizing) {
    const dx = (e.clientX - dragStartX) / canvasScale
    const dy = (e.clientY - dragStartY) / canvasScale
    const t = editorTables.value[dragIndex]
    const minSize = 20

    if (resizeHandle.includes('e')) {
      t.w = Math.max(minSize, Math.round(resizeOrigW + dx))
    }
    if (resizeHandle.includes('w')) {
      const newW = Math.max(minSize, Math.round(resizeOrigW - dx))
      t.x = Math.round(resizeOrigX + resizeOrigW - newW)
      t.w = newW
    }
    if (resizeHandle.includes('s')) {
      t.h = Math.max(minSize, Math.round(resizeOrigH + dy))
    }
    if (resizeHandle.includes('n')) {
      const newH = Math.max(minSize, Math.round(resizeOrigH - dy))
      t.y = Math.round(resizeOrigY + resizeOrigH - newH)
      t.h = newH
    }
    return
  }

  if (!dragging) return
  const dx = (e.clientX - dragStartX) / canvasScale
  const dy = (e.clientY - dragStartY) / canvasScale

  if (dragType === 'seat' && dragIndex >= 0) {
    const rawX = Math.round(dragOrigX + dx)
    const rawY = Math.round(dragOrigY + dy)
    const snapped = applySnap('seat', dragIndex, rawX, rawY)
    editorSeats.value[dragIndex].x = snapped.x
    editorSeats.value[dragIndex].y = snapped.y
  } else if (dragType === 'table' && dragIndex >= 0) {
    const rawX = Math.round(dragOrigX + dx)
    const rawY = Math.round(dragOrigY + dy)
    const snapped = applySnap('table', dragIndex, rawX, rawY)
    editorTables.value[dragIndex].x = snapped.x
    editorTables.value[dragIndex].y = snapped.y
  } else if (dragType === 'screen' && editorScreen.value) {
    const rawX = Math.round(dragOrigX + dx)
    const rawY = Math.round(dragOrigY + dy)
    const snapped = applySnap('screen', -1, rawX, rawY)
    editorScreen.value.x = snapped.x
    editorScreen.value.y = snapped.y
  }
}

function onCanvasMouseUp() {
  dragging = false
  resizing = false
  guideLines.value = []
}

// ===== 键盘和生命周期 =====
onMounted(async () => {
  await loadRooms()
  if (rooms.value.length > 0) {
    startEditing(rooms.value[0])
  }
  window.addEventListener('keydown', onKeyDown)
})
onUnmounted(() => {
  window.removeEventListener('keydown', onKeyDown)
})
</script>

<style lang="scss" scoped>
/* ===== 深蓝科技风主题变量 ===== */
$bg-deep: #020c1b;
$bg-mid: #0a1929;
$bg-card: #14284b;
$bg-panel: #14284b;
$border-glow: #1e3a5f;
$cyan: #00d4ff;
$cyan-dim: rgba(0,212,255,0.25);
$cyan-faint: rgba(0,212,255,0.08);
$text-primary: #e0f0ff;
$text-secondary: #7eb8da;
$accent-red: #ff4757;
$accent-gold: #ffc048;

.room-management {
  padding: 24px;
  min-height: 100vh;
  background: #0e1d38;
  color: $text-primary;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;

  h2 {
    font-size: 24px;
    font-weight: 700;
    color: $cyan;
    margin: 0;
    text-shadow: 0 0 12px rgba(0,212,255,0.35);
    letter-spacing: 2px;
  }
}

/* ===== 列表表格 ===== */
.room-list {
  :deep(.el-table) {
    background: transparent;
    --el-table-bg-color: transparent;
    --el-table-tr-bg-color: $bg-card;
    --el-table-header-bg-color: $bg-panel;
    --el-table-border-color: $border-glow;
    --el-table-text-color: $text-primary;
    --el-table-header-text-color: $cyan;
    --el-table-row-hover-bg-color: rgba(0,212,255,0.06);

    th.el-table__cell {
      font-weight: 700;
      letter-spacing: 1px;
    }
  }
}

/* ===== 编辑器 ===== */
.room-editor {
  background: $bg-card;
  border-radius: 10px;
  border: 1px solid $border-glow;
  box-shadow: 0 0 30px rgba(0,212,255,0.06), 0 4px 20px rgba(0,0,0,0.4);
  overflow: hidden;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 20px;
  background: $bg-panel;
  border-bottom: 1px solid $border-glow;

  .editor-title {
    font-size: 16px;
    font-weight: 700;
    color: $cyan;
    flex: 1;
    text-shadow: 0 0 8px rgba(0,212,255,0.3);
  }
  .toolbar-right {
    display: flex;
    gap: 8px;
  }
}

.editor-body {
  display: flex;
  height: calc(100vh - 200px);
  min-height: 500px;
}

.editor-canvas-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 12px;
  overflow: auto;
  background: $bg-mid;
}

.canvas-info {
  font-size: 14px;
  color: $text-secondary;
  margin-bottom: 8px;
  padding: 4px 0;
}

.editor-canvas {
  position: relative;
  background: linear-gradient(135deg, #081825, #0c2236);
  border: 2px solid $border-glow;
  border-radius: 8px;
  cursor: crosshair;
  flex-shrink: 0;
  box-shadow: inset 0 0 40px rgba(0,212,255,0.03);

  /* 网格 */
  background-image:
    linear-gradient(rgba(0,212,255,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,212,255,0.04) 1px, transparent 1px);
  background-size: 20px 20px;
}

.canvas-screen {
  position: absolute;
  background: linear-gradient(180deg, $accent-red, #c0392b);
  border: 2px solid $accent-red;
  border-radius: 4px;
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  writing-mode: vertical-lr;
  letter-spacing: 3px;
  cursor: move;
  box-shadow: 0 0 12px rgba(255,71,87,0.4);
  z-index: 3;
  user-select: none;

  &.is-selected {
    box-shadow: 0 0 0 3px rgba(255,71,87,0.5), 0 0 16px rgba(255,71,87,0.4);
  }
}

.canvas-table {
  position: absolute;
  background: $cyan-faint;
  border: 2px solid $cyan-dim;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(0,212,255,0.55);
  font-size: 14px;
  cursor: move;
  user-select: none;
  z-index: 1;
  transition: box-shadow 0.15s;

  &.is-selected {
    border-color: $cyan;
    box-shadow: 0 0 0 3px rgba(0,212,255,0.2), 0 0 16px rgba(0,212,255,0.15);
    background: rgba(0,212,255,0.12);
  }
}

.canvas-seat {
  position: absolute;
  border-radius: 50%;
  background: rgba(0,212,255,0.1);
  border: 2px solid rgba(0,212,255,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  color: $cyan;
  font-size: 14px;
  font-weight: 700;
  cursor: move;
  z-index: 2;
  user-select: none;
  transition: box-shadow 0.15s;

  &.is-selected {
    border-color: $accent-gold;
    background: rgba(255,192,72,0.15);
    color: $accent-gold;
    box-shadow: 0 0 0 3px rgba(255,192,72,0.25), 0 0 10px rgba(255,192,72,0.2);
  }
}

/* ===== 缩放手柄 ===== */
.resize-handle {
  position: absolute;
  width: 10px;
  height: 10px;
  background: $cyan;
  border: 1px solid #fff;
  border-radius: 2px;
  z-index: 10;
  box-shadow: 0 0 6px rgba(0,212,255,0.5);

  &.rh-n  { top: -5px; left: 50%; transform: translateX(-50%); cursor: n-resize; }
  &.rh-s  { bottom: -5px; left: 50%; transform: translateX(-50%); cursor: s-resize; }
  &.rh-e  { right: -5px; top: 50%; transform: translateY(-50%); cursor: e-resize; }
  &.rh-w  { left: -5px; top: 50%; transform: translateY(-50%); cursor: w-resize; }
  &.rh-ne { top: -5px; right: -5px; cursor: ne-resize; }
  &.rh-nw { top: -5px; left: -5px; cursor: nw-resize; }
  &.rh-se { bottom: -5px; right: -5px; cursor: se-resize; }
  &.rh-sw { bottom: -5px; left: -5px; cursor: sw-resize; }
}

/* ===== 吸附参考线 ===== */
.snap-guide-v {
  position: absolute;
  width: 1px;
  background: $accent-gold;
  box-shadow: 0 0 4px rgba(255,192,72,0.6);
  pointer-events: none;
  z-index: 20;
}
.snap-guide-h {
  position: absolute;
  height: 1px;
  background: $accent-gold;
  box-shadow: 0 0 4px rgba(255,192,72,0.6);
  pointer-events: none;
  z-index: 20;
}

/* ===== 属性面板 ===== */
.editor-props {
  width: 320px;
  border-left: 1px solid $border-glow;
  background: $bg-panel;
  overflow-y: auto;
  padding: 16px;
  flex-shrink: 0;
}

.props-section {
  h4 {
    font-size: 14px;
    font-weight: 700;
    color: $cyan;
    margin: 0 0 12px;
    letter-spacing: 1px;
  }
}

.prop-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;

  span {
    font-size: 14px;
    color: $text-secondary;
    white-space: nowrap;
  }

  .el-input-number {
    width: 100px;
  }
}

.prop-hint {
  font-size: 14px;
  color: $text-secondary;
  line-height: 1.8;
}

/* 座位列表 */
.seat-list-scroll {
  max-height: 300px;
  overflow-y: auto;
}

.seat-list-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s;
  font-size: 14px;

  &:hover { background: rgba(0,212,255,0.06); }
  &.is-active { background: rgba(0,212,255,0.1); }

  .seat-id {
    font-weight: 700;
    color: $cyan;
    min-width: 30px;
  }
  .seat-label {
    flex: 1;
    color: $text-primary;
  }
  .seat-ip {
    color: $text-secondary;
    font-size: 14px;
    font-family: 'Consolas', monospace;
  }
}

/* ===== Element Plus 深色覆写 ===== */
:deep(.el-dialog) {
  background: $bg-card;
  border: 1px solid $border-glow;
  box-shadow: 0 0 40px rgba(0,212,255,0.08);

  .el-dialog__title { color: $cyan; }
  .el-dialog__headerbtn .el-dialog__close { color: $text-secondary; }
}

:deep(.el-form-item__label) {
  color: $text-secondary !important;
}

:deep(.el-input__wrapper),
:deep(.el-input-number) {
  background: $bg-mid !important;
  box-shadow: 0 0 0 1px $border-glow inset !important;
}

:deep(.el-input__inner) {
  color: $text-primary !important;
}

:deep(.el-empty__description p) {
  color: $text-secondary;
}

:deep(.el-divider) {
  border-color: $border-glow;
}
</style>
