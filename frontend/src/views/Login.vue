<template>
  <div class="login-page">
    <!-- ===== 星空背景 ===== -->
    <canvas ref="starsCanvas" class="stars-canvas"></canvas>

    <!-- ===== 顶部标题区 ===== -->
    <div class="top-title-bar">
      <div class="title-deco left"></div>
      <div class="title-content">
        <span class="title-text">智能会议</span>
        <span class="title-emblem">◆</span>
        <span class="title-text">助手系统</span>
      </div>
      <div class="title-deco right"></div>
    </div>

    <!-- ===== HUD 外框 ===== -->
    <div class="hud-frame">
      <span class="corner tl"></span>
      <span class="corner tr"></span>
      <span class="corner bl"></span>
      <span class="corner br"></span>
      <!-- 十字准星 -->
      <div class="crosshair ch-left"></div>
      <div class="crosshair ch-right"></div>
      <div class="crosshair ch-bottom"></div>
    </div>

    <!-- ===== 右上角时间日期 ===== -->
    <div class="datetime-display">
      <span class="dt-time">{{ currentTime }}</span>
      <span class="dt-date">{{ currentDate }}</span>
      <span class="dt-week">{{ currentWeek }}</span>
    </div>

    <!-- ===== 左侧装饰面板 ===== -->
    <div class="deco-panel deco-left">
      <div class="deco-label">LOCATION: 127.0.0.1:8001</div>
      <div class="deco-bars">
        <span v-for="n in 6" :key="n" class="bar" :style="{ width: (20 + Math.random() * 60) + '%' }"></span>
      </div>
    </div>

    <!-- ===== 右侧装饰（火箭轮廓） ===== -->
    <div class="deco-panel deco-right">
      <div class="rocket-wireframe">
        <div class="rocket-body"></div>
        <div class="rocket-fin left-fin"></div>
        <div class="rocket-fin right-fin"></div>
        <div class="rocket-nose"></div>
        <div class="rocket-flame"></div>
      </div>
    </div>

    <!-- ===== 地球背景 ===== -->
    <div class="earth-bg">
      <img src="/images/earth-bg.jpg" alt="" />
    </div>

    <!-- ===== 扫描线动画 ===== -->
    <div class="scan-line"></div>

    <!-- ===== 登录卡片 ===== -->
    <div class="login-card">

      <!-- ===== 模式未选择：展示两个入口 ===== -->
      <template v-if="!pageMode">
        <h2 class="login-title">智能会议系统</h2>
        <div class="mode-selector">
          <div class="mode-card admin-card" @click="pageMode = 'admin'">
            <div class="mode-icon">🖥</div>
            <div class="mode-name">管理端</div>
            <div class="mode-desc">登录账号<br/>管理会议、归档、待办</div>
          </div>
          <div class="mode-card terminal-mode-card" @click="router.push('/terminal/auto')">
            <div class="mode-icon">📋</div>
            <div class="mode-name">会议端</div>
            <div class="mode-desc">直接进入<br/>签到、材料、纪要审签</div>
          </div>
        </div>
      </template>

      <!-- ===== 管理端：登录/注册 ===== -->
      <template v-else-if="pageMode === 'admin'">
        <div class="mode-back">
          <el-button text size="small" @click="pageMode = null">← 返回</el-button>
        </div>
        <h2 class="login-title">管理端登录</h2>
        <el-tabs v-model="activeTab" class="login-tabs">
          <el-tab-pane label="账号登录" name="login">
            <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" @submit.prevent="handleLogin">
              <el-form-item prop="username">
                <el-input v-model="loginForm.username" placeholder="请输入账号" prefix-icon="User" size="large" />
              </el-form-item>
              <el-form-item prop="password">
                <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" prefix-icon="Lock" size="large" show-password />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" size="large" class="login-btn" :loading="loading" @click="handleLogin">
                  登录
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="注册账号" name="register">
            <el-form ref="registerFormRef" :model="registerForm" :rules="registerRules" @submit.prevent="handleRegister">
              <el-form-item prop="username">
                <el-input v-model="registerForm.username" placeholder="请输入用户名" prefix-icon="User" size="large" />
              </el-form-item>
              <el-form-item prop="real_name">
                <el-input v-model="registerForm.real_name" placeholder="请输入真实姓名" prefix-icon="UserFilled" size="large" />
              </el-form-item>
              <el-form-item prop="email">
                <el-input v-model="registerForm.email" placeholder="请输入邮箱" prefix-icon="Message" size="large" />
              </el-form-item>
              <el-form-item prop="password">
                <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" prefix-icon="Lock" size="large" show-password />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" size="large" class="login-btn" :loading="loading" @click="handleRegister">
                  注册
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </template>
    </div>

    <!-- ===== 底部装饰 ===== -->
    <div class="bottom-deco">
      <div class="deco-grid">
        <span v-for="n in 12" :key="n" class="grid-cell" :class="{ lit: n % 3 === 0 }"></span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeTab = ref('login')
const loading = ref(false)
const loginFormRef = ref(null)
const registerFormRef = ref(null)
const pageMode = ref(null)  // null | 'admin'

// 会议室布局（含大屏幕位置）
const ROOM_LAYOUTS = {
  '3甲号会议室': {
    roomWidth: 700, roomHeight: 440,
    screen: { x: 8, y: 140, w: 28, h: 160 },
    tables: [{ x: 200, y: 120, w: 300, h: 180, rx: 18, label: '会议桌' }],
    seats: [
      { id: 1, label: '1号', x: 260, y: 90 }, { id: 2, label: '2号', x: 350, y: 90 }, { id: 3, label: '3号', x: 440, y: 90 },
      { id: 4, label: '4号', x: 530, y: 180 }, { id: 5, label: '5号', x: 530, y: 260 },
      { id: 6, label: '6号', x: 440, y: 340 }, { id: 7, label: '7号', x: 350, y: 340 }, { id: 8, label: '8号', x: 260, y: 340 },
      { id: 9, label: '9号', x: 170, y: 260 }, { id: 10, label: '10号', x: 170, y: 180 },
    ]
  },
  '3乙号会议室': {
    roomWidth: 600, roomHeight: 400,
    screen: { x: 8, y: 120, w: 28, h: 160 },
    tables: [{ x: 175, y: 120, w: 250, h: 150, rx: 14, label: '会议桌' }],
    seats: [
      { id: 1, label: '1号', x: 230, y: 90 }, { id: 2, label: '2号', x: 340, y: 90 },
      { id: 3, label: '3号', x: 460, y: 170 }, { id: 4, label: '4号', x: 460, y: 250 },
      { id: 5, label: '5号', x: 340, y: 310 }, { id: 6, label: '6号', x: 230, y: 310 },
      { id: 7, label: '7号', x: 140, y: 250 }, { id: 8, label: '8号', x: 140, y: 170 },
    ]
  },
  '5楼大会议室': {
    roomWidth: 800, roomHeight: 520,
    screen: { x: 8, y: 130, w: 28, h: 260 },
    tables: [{ x: 140, y: 100, w: 520, h: 60, rx: 10, label: '' },
             { x: 140, y: 160, w: 60, h: 240, rx: 10, label: '' },
             { x: 600, y: 160, w: 60, h: 240, rx: 10, label: 'U型桌' }],
    seats: [
      { id: 1, x: 200, y: 70 }, { id: 2, x: 300, y: 70 }, { id: 3, x: 400, y: 70 }, { id: 4, x: 500, y: 70 }, { id: 5, x: 600, y: 70 },
      { id: 6, x: 695, y: 170 }, { id: 7, x: 695, y: 250 }, { id: 8, x: 695, y: 330 }, { id: 9, x: 695, y: 410 },
      { id: 10, x: 600, y: 440 }, { id: 11, x: 500, y: 440 }, { id: 12, x: 400, y: 440 }, { id: 13, x: 300, y: 440 }, { id: 14, x: 200, y: 440 },
      { id: 15, x: 105, y: 410 }, { id: 16, x: 105, y: 330 }, { id: 17, x: 105, y: 250 }, { id: 18, x: 105, y: 170 },
    ]
  },
  '1楼多功能厅': {
    roomWidth: 800, roomHeight: 500,
    screen: { x: 8, y: 120, w: 28, h: 260 },
    tables: [{ x: 300, y: 10, w: 200, h: 60, rx: 10, label: '主席台' }],
    seats: [
      { id: 1, x: 130, y: 140 }, { id: 2, x: 250, y: 140 }, { id: 3, x: 370, y: 140 }, { id: 4, x: 490, y: 140 }, { id: 5, x: 610, y: 140 },
      { id: 6, x: 130, y: 230 }, { id: 7, x: 250, y: 230 }, { id: 8, x: 370, y: 230 }, { id: 9, x: 490, y: 230 }, { id: 10, x: 610, y: 230 },
      { id: 11, x: 130, y: 320 }, { id: 12, x: 250, y: 320 }, { id: 13, x: 370, y: 320 }, { id: 14, x: 490, y: 320 }, { id: 15, x: 610, y: 320 },
      { id: 16, x: 130, y: 410 }, { id: 17, x: 250, y: 410 }, { id: 18, x: 370, y: 410 }, { id: 19, x: 490, y: 410 }, { id: 20, x: 610, y: 410 },
    ]
  },
  '报告厅': {
    roomWidth: 800, roomHeight: 540,
    screen: { x: 8, y: 120, w: 28, h: 300 },
    tables: [{ x: 270, y: 10, w: 260, h: 60, rx: 10, label: '讲台' }],
    seats: [
      { id: 1, x: 100, y: 130 }, { id: 2, x: 210, y: 130 }, { id: 3, x: 320, y: 130 }, { id: 4, x: 430, y: 130 }, { id: 5, x: 540, y: 130 }, { id: 6, x: 650, y: 130 },
      { id: 7, x: 100, y: 210 }, { id: 8, x: 210, y: 210 }, { id: 9, x: 320, y: 210 }, { id: 10, x: 430, y: 210 }, { id: 11, x: 540, y: 210 }, { id: 12, x: 650, y: 210 },
      { id: 13, x: 100, y: 290 }, { id: 14, x: 210, y: 290 }, { id: 15, x: 320, y: 290 }, { id: 16, x: 430, y: 290 }, { id: 17, x: 540, y: 290 }, { id: 18, x: 650, y: 290 },
      { id: 19, x: 100, y: 370 }, { id: 20, x: 210, y: 370 }, { id: 21, x: 320, y: 370 }, { id: 22, x: 430, y: 370 }, { id: 23, x: 540, y: 370 }, { id: 24, x: 650, y: 370 },
      { id: 25, x: 100, y: 450 }, { id: 26, x: 210, y: 450 }, { id: 27, x: 320, y: 450 }, { id: 28, x: 430, y: 450 }, { id: 29, x: 540, y: 450 }, { id: 30, x: 650, y: 450 },
    ]
  },
}

const loginForm = reactive({ username: '', password: '' })
const registerForm = reactive({ username: '', real_name: '', email: '', password: '' })

// ===== 星空绘制 =====
const starsCanvas = ref(null)
function initStars() {
  const canvas = starsCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const dpr = window.devicePixelRatio || 1
  const w = window.innerWidth
  const h = window.innerHeight
  canvas.width = w * dpr
  canvas.height = h * dpr
  canvas.style.width = w + 'px'
  canvas.style.height = h + 'px'
  ctx.scale(dpr, dpr)

  // 深蓝渐变底色
  const bg = ctx.createRadialGradient(w * 0.35, h * 0.45, 80, w * 0.5, h * 0.5, w * 0.9)
  bg.addColorStop(0, '#0c1e40')
  bg.addColorStop(0.4, '#060f28')
  bg.addColorStop(1, '#020810')
  ctx.fillStyle = bg
  ctx.fillRect(0, 0, w, h)

  // ---- 银河带：一条倾斜的密集星云带 ----
  ctx.save()
  ctx.translate(w * 0.5, h * 0.5)
  ctx.rotate(-0.45) // 倾斜约45°  // 多层叠加产生银河质感
  for (let layer = 0; layer < 6; layer++) {
    const spreadX = 400 + layer * 120
    const spreadY = 60 + layer * 30
    const milky = ctx.createRadialGradient(0, 0, 0, 0, 0, spreadX)
    const opacity = 0.04 - layer * 0.004
    const hue = 210 + layer * 8
    milky.addColorStop(0, `hsla(${hue}, 40%, 60%, ${opacity + 0.02})`)
    milky.addColorStop(0.3, `hsla(${hue}, 35%, 40%, ${opacity})`)
    milky.addColorStop(0.7, `hsla(${hue + 20}, 30%, 25%, ${opacity * 0.5})`)
    milky.addColorStop(1, 'transparent')
    ctx.fillStyle = milky
    ctx.beginPath()
    ctx.ellipse(0, (Math.random() - 0.5) * 20, spreadX, spreadY, 0, 0, Math.PI * 2)
    ctx.fill()
  }
  // 银河带中密集微星
  for (let i = 0; i < 1200; i++) {
    const angle = Math.random() * Math.PI * 2
    const rx = (Math.random() - 0.5) * 900
    const ry = (Math.random() - 0.5) * 100 * (1 + Math.random())
    const r = Math.random() * 0.8 + 0.1
    const alpha = Math.random() * 0.5 + 0.2
    const colors = ['220,230,255', '255,240,220', '200,215,255', '255,250,240']
    const c = colors[Math.floor(Math.random() * colors.length)]
    ctx.beginPath()
    ctx.arc(rx, ry, r, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(${c}, ${alpha})`
    ctx.fill()
  }
  ctx.restore()

  // ---- 大面积星云雾气 ----
  const nebulaConfigs = [
    { x: w * 0.15, y: h * 0.3, r: 300, hue: 30, sat: 40, light: 35, a: 0.05 },   // 左侧暖色星云
    { x: w * 0.8,  y: h * 0.6, r: 250, hue: 240, sat: 40, light: 30, a: 0.04 },   // 右下蓝紫星云
    { x: w * 0.5,  y: h * 0.35,r: 350, hue: 215, sat: 30, light: 40, a: 0.035 },   // 中心淡蓝
    { x: w * 0.3,  y: h * 0.7, r: 200, hue: 260, sat: 35, light: 25, a: 0.03 },   // 左下紫色
    { x: w * 0.7,  y: h * 0.2, r: 220, hue: 200, sat: 45, light: 35, a: 0.04 },   // 右上青蓝
  ]
  for (const n of nebulaConfigs) {
    const g = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r)
    g.addColorStop(0, `hsla(${n.hue}, ${n.sat}%, ${n.light}%, ${n.a})`)
    g.addColorStop(0.5, `hsla(${n.hue}, ${n.sat - 10}%, ${n.light - 10}%, ${n.a * 0.5})`)
    g.addColorStop(1, 'transparent')
    ctx.fillStyle = g
    ctx.fillRect(0, 0, w, h)
  }

  // ---- 散布星星（远景） ----
  for (let i = 0; i < 600; i++) {
    const x = Math.random() * w
    const y = Math.random() * h
    const r = Math.random() * 1.2 + 0.2
    const alpha = Math.random() * 0.6 + 0.15
    // 色温随机：冷蓝 / 暖黄 / 纯白
    const temp = Math.random()
    let rgb
    if (temp < 0.4) rgb = '200,215,255'       // 冷蓝
    else if (temp < 0.6) rgb = '255,240,210'   // 暖黄
    else if (temp < 0.75) rgb = '255,200,180'  // 橙红（远星）
    else rgb = '240,245,255'                    // 白
    ctx.beginPath()
    ctx.arc(x, y, r, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(${rgb}, ${alpha})`
    ctx.fill()
  }

  // ---- 亮星（带柔光晕） ----
  for (let i = 0; i < 30; i++) {
    const x = Math.random() * w
    const y = Math.random() * h
    const r = Math.random() * 1.5 + 1
    const alpha = Math.random() * 0.5 + 0.5
    // 柔和圆形光晕，不是十字
    const glow = ctx.createRadialGradient(x, y, 0, x, y, r * 6)
    glow.addColorStop(0, `rgba(220, 235, 255, ${alpha})`)
    glow.addColorStop(0.15, `rgba(200, 220, 255, ${alpha * 0.5})`)
    glow.addColorStop(0.4, `rgba(150, 190, 255, ${alpha * 0.12})`)
    glow.addColorStop(1, 'transparent')
    ctx.fillStyle = glow
    ctx.beginPath()
    ctx.arc(x, y, r * 6, 0, Math.PI * 2)
    ctx.fill()
    // 星芯
    ctx.beginPath()
    ctx.arc(x, y, r * 0.6, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(240, 248, 255, ${alpha})`
    ctx.fill()
  }
}

// ===== 实时时钟 =====
const now = ref(new Date())
let timer = null
onMounted(() => {
  timer = setInterval(() => { now.value = new Date() }, 1000)
  initStars()
  window.addEventListener('resize', initStars)
})
onUnmounted(() => {
  clearInterval(timer)
  window.removeEventListener('resize', initStars)
})

const pad = (n) => String(n).padStart(2, '0')
const currentTime = computed(() => `${pad(now.value.getHours())}:${pad(now.value.getMinutes())}:${pad(now.value.getSeconds())}`)
const currentDate = computed(() => `${now.value.getFullYear()}-${pad(now.value.getMonth()+1)}-${pad(now.value.getDate())}`)
const weekMap = ['星期日','星期一','星期二','星期三','星期四','星期五','星期六']
const currentWeek = computed(() => weekMap[now.value.getDay()])

const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const registerRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  real_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }, { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码不少于6位', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await loginFormRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await userStore.doLogin(loginForm)
    ElMessage.success('登录成功')
    router.push(route.query.redirect || '/')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '登录失败')
  } finally { loading.value = false }
}

async function handleRegister() {
  const valid = await registerFormRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await userStore.doRegister(registerForm)
    ElMessage.success('注册成功')
    router.push('/')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '注册失败')
  } finally { loading.value = false }
}

async function enterTerminal() {
  if (!currentMeeting.value) {
    ElMessage.warning('未找到进行中的会议，请稍候重试')
    return
  }
  stopTerminalPoll()
  loading.value = true
  try {
    router.push(`/terminal/${currentMeeting.value.id}?seat=1`)
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
/* ============================================================
   深蓝科幻军事风 — 复刻登录页   ============================================================ */

// ===== 颜色变量（仅本页）=====
$bg-deep:    #020c1b;
$bg-mid:     #071a36;
$bg-panel:   #0a1e3d;
$cyan:       #00d4ff;
$cyan-dim:   rgba(0,212,255,0.25);
$cyan-glow:  rgba(0,212,255,0.6);
$blue:       #2080e0;
$blue-bright:#3ca8ff;
$text-main:  #d8f0ff;
$text-dim:   #6aa0c8;
$border-hud: rgba(0,212,255,0.35);

/* ===== 星空canvas ===== */
.stars-canvas {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

/* ===== 全屏容器 ===== */
.login-page {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background: #020810;
  color: $text-main;
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;

  /* 网格底纹 */
  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
      linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none;
    z-index: 1;
  }
}

/* ===== 顶部标题区 ===== */
.top-title-bar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 54px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 20;
  background: linear-gradient(180deg, rgba(10,40,90,0.95), rgba(5,20,50,0.7));
  border-bottom: 1px solid $border-hud;

  .title-deco {
    flex: 1;
    height: 2px;
    max-width: 320px;
    &.left {
      background: linear-gradient(90deg, transparent, $cyan-glow);
      margin-right: 20px;
    }
    &.right {
      background: linear-gradient(90deg, $cyan-glow, transparent);
      margin-left: 20px;
    }
  }

  .title-content {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .title-text {
    font-size: 26px;
    font-weight: 700;
    letter-spacing: 6px;
    color: $cyan;
    text-shadow: 0 0 20px rgba(0,212,255,0.5), 0 0 40px rgba(0,212,255,0.2);
  }

  .title-emblem {
    font-size: 20px;
    color: #ff6060;
    text-shadow: 0 0 12px rgba(255,80,80,0.6);
    animation: emblem-pulse 2s ease-in-out infinite;
  }
}

@keyframes emblem-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* ===== HUD 外框 ===== */
.hud-frame {
  position: absolute;
  inset: 60px 24px 24px;
  border: 1px solid $border-hud;
  pointer-events: none;
  z-index: 1;

  .corner {
    position: absolute;
    width: 50px;
    height: 50px;
    border: 2px solid $cyan;
    filter: drop-shadow(0 0 8px $cyan-glow);
    &.tl { top: -1px; left: -1px; border-right: none; border-bottom: none; }
    &.tr { top: -1px; right: -1px; border-left: none; border-bottom: none; }
    &.bl { bottom: -1px; left: -1px; border-right: none; border-top: none; }
    &.br { bottom: -1px; right: -1px; border-left: none; border-top: none; }
  }
}

/* 十字准星 */
.crosshair {
  position: absolute;
  width: 18px;
  height: 18px;
  z-index: 2;
  pointer-events: none;
  &::before, &::after {
    content: '';
    position: absolute;
    background: $cyan;
  }
  &::before { width: 18px; height: 1px; top: 50%; left: 0; transform: translateY(-50%); }
  &::after  { width: 1px; height: 18px; left: 50%; top: 0; transform: translateX(-50%); }

  &.ch-left   { left: 80px;  top: 50%; }
  &.ch-right  { right: 80px; top: 50%; }
  &.ch-bottom { left: 50%;   bottom: 100px; }
}

/* ===== 右上角时间日期 ===== */
.datetime-display {
  position: absolute;
  top: 72px;
  right: 52px;
  z-index: 10;
  text-align: right;
  pointer-events: none;

  .dt-time {
    display: block;
    font-size: 28px;
    font-weight: 300;
    font-family: 'Consolas', 'Courier New', monospace;
    color: $text-main;
    letter-spacing: 2px;
  }
  .dt-date {
    display: inline;
    font-size: 16px;
    color: $text-dim;
    margin-right: 12px;
    font-family: 'Consolas', monospace;
  }
  .dt-week {
    display: block;
    font-size: 14px;
    color: $text-dim;
    margin-top: 2px;
  }
}

/* ===== 左侧装饰面板 ===== */
.deco-panel.deco-left {
  position: absolute;
  left: 42px;
  top: 80px;
  z-index: 5;
  pointer-events: none;

  .deco-label {
    font-size: 14px;
    color: $text-dim;
    font-family: 'Consolas', monospace;
    margin-bottom: 10px;
    letter-spacing: 1px;
  }
  .deco-bars {
    display: flex;
    flex-direction: column;
    gap: 4px;
    .bar {
      height: 3px;
      background: linear-gradient(90deg, $cyan-dim, transparent);
      border-radius: 1px;
    }
  }
}

/* ===== 右侧火箭装饰 ===== */
.deco-panel.deco-right {
  position: absolute;
  right: 60px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 5;
  pointer-events: none;
}

.rocket-wireframe {
  width: 60px;
  height: 280px;
  position: relative;

  .rocket-body {
    position: absolute;
    left: 50%;
    top: 40px;
    transform: translateX(-50%);
    width: 20px;
    height: 160px;
    border: 1px solid $cyan;
    border-radius: 10px 10px 4px 4px;
    box-shadow: 0 0 12px $cyan-dim, inset 0 0 8px rgba(0,212,255,0.08);
  }
  .rocket-nose {
    position: absolute;
    left: 50%;
    top: 10px;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 10px solid transparent;
    border-right: 10px solid transparent;
    border-bottom: 30px solid $cyan;
    filter: drop-shadow(0 0 8px $cyan-glow);
    opacity: 0.8;
  }
  .rocket-fin {
    position: absolute;
    bottom: 75px;
    width: 0;
    height: 0;
    border-top: 20px solid transparent;
    border-bottom: 10px solid transparent;
    &.left-fin {
      left: 6px;
      border-right: 14px solid rgba(0,212,255,0.4);
    }
    &.right-fin {
      right: 6px;
      border-left: 14px solid rgba(0,212,255,0.4);
    }
  }
  .rocket-flame {
    position: absolute;
    left: 50%;
    bottom: 50px;
    transform: translateX(-50%);
    width: 14px;
    height: 30px;
    background: linear-gradient(180deg, rgba(0,212,255,0.5), rgba(32,128,224,0.3), transparent);
    border-radius: 0 0 7px 7px;
    animation: flame-flicker 1.5s ease-in-out infinite;
  }
}

@keyframes flame-flicker {
  0%, 100% { opacity: 0.5; height: 30px; }
  50% { opacity: 1; height: 40px; }
}

/* ===== 地球全屏背景 ===== */
.earth-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;

  img {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    min-width: 100%;
    min-height: 100%;
    width: auto;
    height: 100%;
    object-fit: cover;
    opacity: 0.7;
    animation: earth-breathe 80s ease-in-out infinite;
  }
}

@keyframes earth-breathe {
  0%   { transform: translate(-50%, -50%) scale(1); }
  50%  { transform: translate(-50%, -50%) scale(1.03); }
  100% { transform: translate(-50%, -50%) scale(1); }
}

/* ===== 扫描线 ===== */
.scan-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent 5%, $cyan-dim 30%, $cyan-dim 70%, transparent 95%);
  z-index: 3;
  pointer-events: none;
  animation: scan-move 6s linear infinite;
  opacity: 0.4;
}

@keyframes scan-move {
  0%   { top: 10%; }
  100% { top: 90%; }
}

/* ===== 登录卡片 ===== */
.login-card {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 440px;
  padding: 30px 36px 28px;
  z-index: 10;
  background: linear-gradient(160deg, rgba(8,30,65,0.88), rgba(5,18,45,0.92));
  border: 1px solid rgba(0,212,255,0.3);
  border-radius: 4px;
  backdrop-filter: blur(12px);
  box-shadow:
    0 0 0 1px rgba(0,212,255,0.1) inset,
    0 20px 60px rgba(0,0,0,0.4),
    0 0 40px rgba(30,120,220,0.15);

  &.login-card-wide {
    width: 880px;
    transition: width 0.3s ease;
  }
}

.login-title {
  text-align: center;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 8px;
  margin: 0 0 24px;
  color: #ffffff;
  text-shadow: 0 0 16px rgba(0,212,255,0.3);
}

.login-btn {
  width: 100%;
  height: 46px;
  border: none !important;
  font-size: 20px;
  letter-spacing: 1em;
  text-indent: 1em;
  border-radius: 4px;
  background: linear-gradient(90deg, $blue, $blue-bright) !important;
  box-shadow: 0 8px 24px rgba(32,128,224,0.4), 0 0 16px rgba(60,168,255,0.2);
  color: #ffffff !important;
  &:hover {
    background: linear-gradient(90deg, lighten($blue, 5%), lighten($blue-bright, 5%)) !important;
    box-shadow: 0 8px 32px rgba(32,128,224,0.5), 0 0 24px rgba(60,168,255,0.3);
  }
}

/* Tab 样式覆盖 */
.login-tabs {
  :deep(.el-tabs__header) { margin-bottom: 16px; }
  :deep(.el-tabs__nav-wrap::after) { background: rgba(0,212,255,0.15); }
  :deep(.el-tabs__item) {
    color: $text-dim !important;
    font-size: 14px;
    &.is-active { color: #ffffff !important; }
    &:hover { color: $cyan !important; }
  }
  :deep(.el-tabs__active-bar) {
    background-color: $cyan !important;
    box-shadow: 0 0 10px $cyan-glow;
  }

  :deep(.el-input__wrapper) {
    border-radius: 4px;
    background: rgba(5,20,50,0.7) !important;
    border: 1px solid rgba(0,212,255,0.3) !important;
    box-shadow: none !important;
    &:hover { border-color: rgba(0,212,255,0.5) !important; }
    &.is-focus {
      border-color: $cyan !important;
      box-shadow: 0 0 0 2px rgba(0,212,255,0.15) !important;
    }
  }
  :deep(.el-input__inner) {
    color: #ffffff !important;
    font-size: 14px;
    &::placeholder { color: $text-dim !important; }
  }
  :deep(.el-input__prefix .el-icon) { color: $cyan !important; font-size: 18px; }
  :deep(.el-form-item__error) { color: #ff6b6b; }
}

/* ===== 模式选择 ===== */
.mode-back {
  margin-bottom: 8px;
  :deep(.el-button) { color: rgba(0,212,255,0.7); padding: 0; }
}

.mode-selector {
  display: flex;
  gap: 16px;
  margin-top: 12px;
}

.mode-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 12px;
  border-radius: 10px;
  border: 1px solid rgba(0,212,255,0.25);
  background: rgba(5,20,50,0.5);
  cursor: pointer;
  transition: all 0.25s;

  .mode-icon { font-size: 40px; margin-bottom: 10px; }
  .mode-name { font-size: 18px; font-weight: 700; color: #fff; margin-bottom: 6px; }
  .mode-desc { font-size: 14px; color: rgba(170,210,255,0.7); text-align: center; line-height: 1.6; }

  &:hover {
    border-color: $cyan;
    background: rgba(30,80,180,0.35);
    box-shadow: 0 0 20px rgba(0,212,255,0.2);
    transform: translateY(-2px);
  }
  &.terminal-mode-card { border-color: rgba(120,80,220,0.35); }
  &.terminal-mode-card:hover {
    border-color: #a67cec;
    background: rgba(80,40,160,0.35);
    box-shadow: 0 0 20px rgba(140,80,240,0.2);
  }
}

.terminal-hint {
  color: rgba(170,210,255,0.7);
  font-size: 14px;
  margin: -8px 0 16px;
  text-align: center;
}

/* 会议端自动关联样式 */
.terminal-auto-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px 0;
  color: rgba(160, 200, 255, 0.8);
  font-size: 14px;
}

.terminal-loading-icon {
  font-size: 32px;
  animation: spin 1s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.terminal-no-meeting { color: rgba(200, 150, 150, 0.9); }

.terminal-meeting-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  margin: 12px 0 8px;
}

.terminal-meeting-title {
  font-size: 18px;
  font-weight: 700;
  color: #c8e6ff;
  letter-spacing: 1px;
  text-align: center;
}

.terminal-seat-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  margin: 12px 0 16px;
  padding: 16px 32px;
  background: rgba(0, 40, 80, 0.5);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 12px;
  backdrop-filter: blur(6px);
  min-width: 180px;
}

.seat-preview-label {
  font-size: 14px;
  color: rgba(0, 212, 255, 0.7);
  letter-spacing: 2px;
  text-transform: uppercase;
}

.seat-preview-name {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 2px;
}

.seat-preview-loading {
  font-size: 14px;
  color: rgba(160, 200, 255, 0.6);
}

.seat-preview-empty {
  font-size: 14px;
  color: rgba(200, 150, 150, 0.8);
}

.terminal-room-preview {
  flex-shrink: 0;
  width: 480px;
  padding: 12px;
  background: rgba(0,16,40,0.5);
  border: 1px solid rgba(0,212,255,0.2);
  border-radius: 8px;
}

.room-preview-title {
  text-align: center;
  font-size: 14px;
  color: rgba(0,212,255,0.8);
  margin-bottom: 10px;
  letter-spacing: 1px;
}

.room-preview-map {
  position: relative;
  margin: 0 auto;
  background: rgba(0,10,28,0.7);
  border: 1px solid rgba(0,212,255,0.15);
  border-radius: 6px;
  overflow: hidden;
}

.room-screen-marker {
  position: absolute;
  background: linear-gradient(180deg, #e74c3c, #c0392b);
  border: 1px solid #e74c3c;
  border-radius: 3px;
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  writing-mode: vertical-lr;
  letter-spacing: 4px;
  box-shadow: 0 0 8px rgba(231,76,60,0.4);
  z-index: 2;
}

.room-mini-table {
  position: absolute;
  background: rgba(0,212,255,0.06);
  border: 1px solid rgba(0,212,255,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(0,212,255,0.4);
  font-size: 14px;
  pointer-events: none;
}

.room-mini-seat {
  position: absolute;
  border-radius: 50%;
  background: rgba(100,160,220,0.15);
  border: 1px solid rgba(100,160,220,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(160,200,240,0.6);
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;

  &.is-highlight {
    background: rgba(0,212,255,0.3);
    border-color: #00d4ff;
    color: #00d4ff;
    box-shadow: 0 0 10px rgba(0,212,255,0.4);
    font-weight: 700;
    font-size: 14px;
  }
}

/* ===== 底部装饰格子 ===== */
.bottom-deco {
  position: absolute;
  right: 60px;
  bottom: 42px;
  z-index: 5;
  pointer-events: none;
}

.deco-grid {
  display: grid;
  grid-template-columns: repeat(4, 14px);
  gap: 4px;

  .grid-cell {
    width: 14px;
    height: 14px;
    border: 1px solid rgba(0,212,255,0.2);
    &.lit {
      background: rgba(0,212,255,0.2);
      box-shadow: 0 0 6px rgba(0,212,255,0.3);
    }
  }
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .login-card { width: 92vw; padding: 24px 20px; }
  .deco-panel { display: none; }
  .earth-container { width: 300px; height: 300px; }
  .top-title-bar .title-text { font-size: 18px; letter-spacing: 3px; }
  .hud-frame { inset: 56px 12px 12px; }
}
</style>
