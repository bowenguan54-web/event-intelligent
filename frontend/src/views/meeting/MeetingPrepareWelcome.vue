<template>
  <div class="prepare-screen">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-glow-tr"></div>
      <div class="bg-glow-bl"></div>
      <div class="bg-glow-center"></div>
      <div class="bg-scan"></div>
    </div>

    <!-- 顶部栏 -->
    <div class="top-bar">
      <div class="logo-area">
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <rect x="2" y="3" width="20" height="14" rx="2"/><polyline points="8 21 12 17 16 21"/>
          </svg>
        </div>
        <span class="logo-text">智能会议系统</span>
      </div>

      <div class="top-bar-center">
        <template v-if="meeting.location">
          <div class="top-center-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
            </svg>
            <strong>{{ meeting.location }}</strong>
          </div>
          <div class="top-center-dot"></div>
        </template>
        <template v-if="meeting.start_time">
          <div class="top-center-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
            </svg>
            <strong>{{ timeRange }}</strong>
          </div>
          <div class="top-center-dot"></div>
        </template>
        <div class="top-center-item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
          参会 <strong>{{ meeting.participants?.length || 0 }} 人</strong>
        </div>
      </div>

      <div class="top-bar-right">
        <div class="live-pill">
          <div class="live-dot"></div>
          <span>会议准备</span>
        </div>
        <div class="top-time">
          <div class="time-clock">{{ clockTime }}</div>
          <div class="time-date-text">{{ clockDate }}</div>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="display-area" v-loading="loading">
      <!-- 会议 Hero -->
      <div class="meeting-hero">
        <div class="meeting-hero-left">
          <div class="meeting-phase">
            <span class="phase-dot"></span>会议准备中
          </div>
          <div class="meeting-title-main">{{ meeting.title || '会议准备中' }}</div>
          <div class="meeting-hero-divider"></div>
        </div>
        <div class="meeting-no-card" v-if="meeting.meeting_code">
          <div class="meeting-no-label">会议号</div>
          <div class="meeting-no-value">{{ meeting.meeting_code }}</div>
          <div class="meeting-no-sub">Conference ID</div>
        </div>
      </div>

      <!-- 两列内容 -->
      <div class="content-cols">
        <!-- 左侧：基础信息列 -->
        <div class="info-col">
          <div class="info-card">
            <div class="info-card-header">
              <div class="info-dot-green"></div>
              <span>会议基础信息</span>
            </div>
            <div class="info-rows">
              <div class="info-row">
                <span class="info-row-label">会议类型</span>
                <span class="info-row-value">
                  <span class="type-badge">{{ meetingTypeLabel }}</span>
                </span>
              </div>
              <div class="info-row">
                <span class="info-row-label">会议时间</span>
                <div>
                  <div class="info-time-main">{{ timeRange }}</div>
                  <div class="info-time-sub">{{ timeDate }}</div>
                </div>
              </div>
              <div class="info-row">
                <span class="info-row-label">会议地点</span>
                <span class="info-row-value">{{ meeting.location || '待定' }}</span>
              </div>
              <div class="info-row">
                <span class="info-row-label">参会人数</span>
                <span class="info-row-value info-row-value--blue">{{ meeting.participants?.length || 0 }} 人</span>
              </div>
            </div>
          </div>
          <div class="notice-strip">
            {{ meeting.description || '请参会人员按座位入席，完成签到后查看材料。' }}
          </div>
        </div>

        <!-- 右侧：欢迎词列 -->
        <div class="welcome-col">
          <div class="welcome-card">
            <div class="welcome-card-header">
              <span class="welcome-card-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="width:14px;height:14px;vertical-align:middle">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
                欢迎词
              </span>
              <span class="welcome-theme-tag">
                <span class="theme-dot"></span>当前主题：{{ themeLabel }}
              </span>
            </div>
            <div class="welcome-card-body">
              <span class="quote-mark">"</span>
              <div class="welcome-text">{{ meeting.welcome_message || defaultWelcome }}</div>
            </div>
            <div class="welcome-card-footer">
              <div class="footer-item">
                <span class="footer-label">当前状态</span>
                <span class="footer-value footer-value--warn">准备中</span>
              </div>
              <div class="footer-divider"></div>
              <div class="footer-item">
                <span class="footer-label">距会议开始</span>
                <span class="footer-value footer-value--accent">{{ countdown }}</span>
              </div>
              <div class="footer-divider"></div>
              <div class="footer-item">
                <span class="footer-label">主持人</span>
                <span class="footer-value">{{ hostName }}</span>
              </div>
              <div class="footer-divider"></div>
              <div class="footer-item">
                <span class="footer-label">会议室</span>
                <span class="footer-value">{{ meeting.location || '—' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import dayjs from 'dayjs'
import { getMeetingById } from '@/api/meeting'
import { ElMessage } from 'element-plus'

const route = useRoute()
const meeting = ref({})
const loading = ref(true)
const clockTime = ref('')
const clockDate = ref('')
const countdown = ref('—')
let clockTimer = null

function updateClock() {
  const now = dayjs()
  clockTime.value = now.format('HH:mm:ss')
  clockDate.value = now.format('YYYY年MM月DD日')
  if (meeting.value?.start_time) {
    const diff = dayjs(meeting.value.start_time).diff(now, 'minute')
    if (diff > 0) {
      countdown.value = diff >= 60
        ? `${Math.floor(diff / 60)} 小时 ${diff % 60} 分钟`
        : `${diff} 分钟`
    } else if (diff >= -5) {
      countdown.value = '即将开始'
    } else {
      countdown.value = '已开始'
    }
  }
}

const typeMap = {
  regular: '例会',
  special: '专题会议',
  decision: '决策会议',
  review: '评审会议',
  other: '其他',
}

const themeMap = {
  aurora: '流光',
  sunrise: '晨曦',
  summit: '峰会',
  harbor: '海岸',
}

const themeKey = computed(() => meeting.value?.welcome_theme || 'aurora')
const themeLabel = computed(() => themeMap[themeKey.value] || '流光')
const meetingTypeLabel = computed(() => typeMap[meeting.value?.meeting_type] || '会议')

const timeRange = computed(() => {
  if (!meeting.value?.start_time) return '待定'
  const start = dayjs(meeting.value.start_time).format('MM月DD日 HH:mm')
  const end = meeting.value.end_time ? dayjs(meeting.value.end_time).format('HH:mm') : ''
  return end ? `${start} ~ ${end}` : start
})

const timeDate = computed(() => {
  if (!meeting.value?.start_time) return ''
  return dayjs(meeting.value.start_time).format('YYYY年MM月DD日')
})

const hostName = computed(() => {
  if (!meeting.value?.participants?.length) return '—'
  const host = meeting.value.participants.find(p => p.role === '主持人' || p.is_host)
  return host?.name || host?.userName || meeting.value.participants[0]?.name || '—'
})

const defaultWelcome = computed(() =>
  `欢迎参加${meeting.value?.title || '本次会议'}，请按照终端提示完成签到并查看会议材料。`
)

onMounted(async () => {
  updateClock()
  clockTimer = setInterval(updateClock, 1000)
  try {
    meeting.value = await getMeetingById(route.params.id)
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '加载会议准备屏失败')
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  if (clockTimer) clearInterval(clockTimer)
})
</script>

<style scoped>
/* ===== 基础 ===== */
.prepare-screen {
  height: 100vh;
  width: 100%;
  background: #03142d;
  color: #dee5f2;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

/* ===== 背景装饰 ===== */
.bg-decoration {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}
.bg-decoration::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(57, 144, 241, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(57, 144, 241, 0.04) 1px, transparent 1px);
  background-size: 60px 60px;
}
.bg-glow-tr {
  position: absolute;
  top: -200px; right: -200px;
  width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(57, 144, 241, 0.12) 0%, transparent 70%);
}
.bg-glow-bl {
  position: absolute;
  bottom: -200px; left: -200px;
  width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(43, 255, 188, 0.08) 0%, transparent 70%);
}
.bg-glow-center {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 1200px; height: 600px;
  background: radial-gradient(ellipse, rgba(57, 144, 241, 0.04) 0%, transparent 60%);
}
.bg-scan {
  position: absolute;
  left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(57, 144, 241, 0.4), transparent);
  animation: scan-move 8s linear infinite;
}
@keyframes scan-move {
  0% { top: 0; }
  100% { top: 100%; }
}

/* ===== 顶部栏 ===== */
.top-bar {
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0 32px;
  background: linear-gradient(90deg, #0a1e42 0%, #0d2252 50%, #0a1e42 100%);
  border-bottom: 1px solid rgba(57, 144, 241, 0.3);
  position: relative;
  z-index: 10;
  flex-shrink: 0;
}
.top-bar::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, #3990f1 30%, #2bffbc 70%, transparent);
}
.logo-area {
  display: flex;
  align-items: center;
  gap: 10px;
}
.logo-icon {
  width: 34px; height: 34px;
  border-radius: 8px;
  background: linear-gradient(135deg, #1e5ca2, #3990f1);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 0 12px rgba(57, 144, 241, 0.4);
  flex-shrink: 0;
}
.logo-icon svg {
  width: 18px; height: 18px;
  color: #fff;
}
.logo-text {
  font-size: 16px;
  font-weight: 700;
  background: linear-gradient(90deg, #e0eeff, #3990f1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.05em;
  white-space: nowrap;
}
.top-bar-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
.top-center-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #7f99be;
  padding: 0 16px;
}
.top-center-item svg {
  width: 13px; height: 13px;
  flex-shrink: 0;
}
.top-center-item strong {
  color: #dee5f2;
  font-weight: 500;
}
.top-center-dot {
  width: 4px; height: 4px;
  border-radius: 50%;
  background: #2a4170;
  flex-shrink: 0;
}
.top-bar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.live-pill {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 4px 12px;
  border-radius: 100px;
  background: rgba(43, 255, 188, 0.08);
  border: 1px solid rgba(43, 255, 188, 0.25);
  font-size: 12px;
  color: #2bffbc;
}
.live-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #2bffbc;
  animation: live-pulse 1.5s infinite;
}
@keyframes live-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(43, 255, 188, 0.6); }
  50% { box-shadow: 0 0 0 4px rgba(43, 255, 188, 0); }
}
.top-time {
  text-align: right;
}
.time-clock {
  font-size: 20px;
  font-weight: 700;
  color: #dee5f2;
  letter-spacing: 0.05em;
  line-height: 1.1;
}
.time-date-text {
  font-size: 11px;
  color: #456484;
  margin-top: 1px;
}

/* ===== 主内容区 ===== */
.display-area {
  flex: 1;
  padding: 28px 40px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: relative;
  z-index: 1;
  overflow: hidden;
}

/* ===== 会议 Hero ===== */
.meeting-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
  flex-shrink: 0;
}
.meeting-hero-left {
  flex: 1;
}
.meeting-phase {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 14px;
  border-radius: 100px;
  background: rgba(57, 144, 241, 0.1);
  border: 1px solid rgba(57, 144, 241, 0.3);
  font-size: 12px;
  color: #3990f1;
  margin-bottom: 14px;
}
.phase-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #3990f1;
  animation: live-pulse 1.5s infinite;
  flex-shrink: 0;
}
.meeting-title-main {
  font-size: 40px;
  font-weight: 800;
  line-height: 1.1;
  background: linear-gradient(90deg, #ffffff 0%, #a8d4ff 50%, #2bffbc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 16px;
}
.meeting-hero-divider {
  width: 60px; height: 3px;
  background: linear-gradient(90deg, #3990f1, #2bffbc);
  border-radius: 2px;
}
.meeting-no-card {
  min-width: 160px;
  padding: 18px 28px;
  background: rgba(14, 29, 56, 0.8);
  border: 1px solid rgba(57, 144, 241, 0.3);
  border-radius: 16px;
  text-align: center;
  backdrop-filter: blur(8px);
  flex-shrink: 0;
}
.meeting-no-label {
  font-size: 11px;
  color: #456484;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 8px;
}
.meeting-no-value {
  font-size: 28px;
  font-weight: 700;
  color: #3990f1;
  letter-spacing: 0.1em;
}
.meeting-no-sub {
  font-size: 10px;
  color: #456484;
  margin-top: 6px;
}

/* ===== 两列内容 ===== */
.content-cols {
  display: flex;
  gap: 20px;
  flex: 1;
  min-height: 0;
}
.info-col {
  width: 340px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.welcome-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* ===== 信息卡 ===== */
.info-card {
  background: rgba(14, 29, 56, 0.7);
  border: 1px solid rgba(32, 64, 130, 0.6);
  border-radius: 16px;
  padding: 18px 20px;
  backdrop-filter: blur(8px);
}
.info-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(57, 144, 241, 0.12);
  font-size: 14px;
  font-weight: 600;
  color: #dee5f2;
}
.info-dot-green {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #2bffbc;
  flex-shrink: 0;
}
.info-rows {
  display: flex;
  flex-direction: column;
}
.info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 9px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}
.info-row:last-child {
  border-bottom: none;
}
.info-row-label {
  font-size: 13px;
  color: #456484;
}
.info-row-value {
  font-size: 13px;
  color: #dee5f2;
  font-weight: 500;
  text-align: right;
}
.info-row-value--blue {
  color: #3990f1;
}
.info-time-main {
  font-size: 13px;
  color: #dee5f2;
  font-weight: 500;
  text-align: right;
}
.info-time-sub {
  font-size: 11px;
  color: #456484;
  text-align: right;
  margin-top: 2px;
}
.type-badge {
  display: inline-flex;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(57, 144, 241, 0.15);
  border: 1px solid rgba(57, 144, 241, 0.3);
  font-size: 12px;
  color: #3990f1;
}
.notice-strip {
  padding: 12px 14px;
  background: rgba(57, 144, 241, 0.06);
  border: 1px solid rgba(57, 144, 241, 0.15);
  border-radius: 10px;
  font-size: 12px;
  color: #7f99be;
  line-height: 1.6;
}

/* ===== 欢迎卡 ===== */
.welcome-card {
  flex: 1;
  background: rgba(14, 29, 56, 0.7);
  border: 1px solid rgba(32, 64, 130, 0.6);
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(8px);
  min-height: 0;
}
.welcome-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 24px;
  border-bottom: 1px solid rgba(57, 144, 241, 0.12);
  flex-shrink: 0;
}
.welcome-card-title {
  font-size: 14px;
  font-weight: 600;
  color: #dee5f2;
  display: flex;
  align-items: center;
  gap: 7px;
}
.welcome-theme-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #456484;
  padding: 3px 10px;
  border-radius: 100px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.theme-dot {
  width: 5px; height: 5px;
  border-radius: 50%;
  background: #3990f1;
  flex-shrink: 0;
}
.welcome-card-body {
  flex: 1;
  padding: 24px 32px;
  position: relative;
  display: flex;
  flex-direction: column;
  overflow: auto;
}
.quote-mark {
  position: absolute;
  top: 10px; left: 18px;
  font-size: 80px;
  line-height: 1;
  color: rgba(57, 144, 241, 0.12);
  font-family: Georgia, serif;
  pointer-events: none;
}
.welcome-text {
  font-size: 22px;
  line-height: 1.8;
  color: #dee5f2;
  white-space: pre-wrap;
  position: relative;
  z-index: 1;
  padding-top: 16px;
}
.welcome-card-footer {
  display: flex;
  align-items: center;
  padding: 12px 24px;
  border-top: 1px solid rgba(57, 144, 241, 0.12);
  background: rgba(57, 144, 241, 0.04);
  flex-shrink: 0;
}
.footer-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  padding: 0 12px;
}
.footer-label {
  font-size: 11px;
  color: #456484;
}
.footer-value {
  font-size: 13px;
  color: #dee5f2;
  font-weight: 500;
}
.footer-value--warn {
  color: #e6a23c;
}
.footer-value--accent {
  color: #3990f1;
}
.footer-divider {
  width: 1px;
  height: 28px;
  background: rgba(57, 144, 241, 0.15);
  flex-shrink: 0;
}
</style>
