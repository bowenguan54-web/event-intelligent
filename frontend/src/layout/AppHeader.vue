<template>
  <div class="app-header">
    <!-- 左侧：应用标题 -->
    <div class="header-left">
      <div class="app-title">
        <span class="title-text">智能会议系统</span>
      </div>
    </div>

    <!-- 右侧工具栏 -->
    <div class="header-right">
      <!-- 实时时钟 -->
      <div class="clock-block">
        <div class="clock-time">{{ currentTime }}</div>
        <div class="clock-date">{{ currentDate }}</div>
      </div>

      <!-- 消息通知 -->
      <el-badge :value="notificationCount" :hidden="notificationCount === 0" class="notification-badge">
        <img src="../../image/dingding.png" class="header-icon notification-icon" @click="showNotifications" alt="通知" />
      </el-badge>

      <!-- 用户菜单 -->
      <el-dropdown trigger="click" @command="handleUserCommand">
        <div class="user-info">
          <img src="../../image/user.png" class="user-avatar" alt="用户" />
          <span class="user-name">{{ userInfo?.real_name || '用户' }}</span>
          <el-icon><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>个人信息
            </el-dropdown-item>
            <el-dropdown-item command="settings">
              <el-icon><Setting /></el-icon>系统设置
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 通知抽屉 -->
    <el-drawer v-model="notificationVisible" title="消息通知" size="360px">
      <div class="notification-toolbar">
        <el-button text size="small" @click="fetchReminders" :loading="loadingReminders">刷新</el-button>
      </div>
      <el-empty v-if="notifications.length === 0" description="暂无待办提醒" />
      <div v-else class="notification-list">
        <div v-for="item in notifications" :key="item.id" class="notification-item" @click="goToTodo(item)">
          <el-icon :class="item.type"><Warning v-if="item.type==='overdue'" /><Clock v-else-if="item.type==='upcoming'" /><Bell v-else /></el-icon>
          <div class="notification-content">
            <p class="notification-title">{{ item.title }}</p>
            <p v-if="item.meeting_title" class="notification-meeting">来源会议：{{ item.meeting_title }}</p>
            <p class="notification-time">{{ item.due_date ? `截止：${item.due_date}` : '' }}</p>
          </div>
          <el-tag v-if="item.type==='overdue'" type="danger" size="small">逾期</el-tag>
          <el-tag v-else-if="item.type==='upcoming'" type="warning" size="small">即将到期</el-tag>
          <el-tag v-else type="info" size="small">待办</el-tag>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getReminders } from '@/api/todo'

const router = useRouter()
const userStore = useUserStore()

const userInfo = computed(() => userStore.userInfo)

// 实时时钟
const currentTime = ref('')
const currentDate = ref('')

function updateClock() {
  const now = new Date()
  const h = String(now.getHours()).padStart(2, '0')
  const m = String(now.getMinutes()).padStart(2, '0')
  const s = String(now.getSeconds()).padStart(2, '0')
  currentTime.value = `${h}:${m}:${s}`
  const y = now.getFullYear()
  const mo = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  currentDate.value = `${y}-${mo}-${d}`
}

const notificationCount = ref(0)
const notificationVisible = ref(false)
const loadingReminders = ref(false)
const notifications = ref([])

async function fetchReminders() {
  loadingReminders.value = true
  try {
    const res = await getReminders()
    const data = res?.data || res
    notifications.value = data?.reminders || []
    notificationCount.value = data?.total || 0
  } catch {
    // 未登录或接口异常的静默处理
  } finally {
    loadingReminders.value = false
  }
}

onMounted(() => {
  updateClock()
  setInterval(updateClock, 1000)
  fetchReminders()
  setInterval(fetchReminders, 60000)
})

function handleSearch() {
  // 搜索功能已移至归档查询页面内部
}

function showNotifications() {
  notificationVisible.value = true
  fetchReminders()
}

function goToTodo(item) {
  notificationVisible.value = false
  router.push('/todo')
}

function handleUserCommand(command) {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}
</script>

<style lang="scss" scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  height: 64px;
  padding-right: 5px;
}

/* ===== 左侧标题区 ===== */
.header-left {
  display: flex;
  align-items: center;
  height: 100%;
}

.app-title {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 40px 0 60px;
  min-width: 320px;
}

/* 标题文字，直接叠在背景图上面 */
.title-text {
  font-size: 29px;
  font-weight: 700;
  letter-spacing: 4px;
  white-space: nowrap;
  font-family: '微软雅黑', 'Microsoft YaHei', sans-serif;
  /* 从下到上：浅蓝→深蓝渐变 */
  background: linear-gradient(to top, #7ec8f0, #ffffff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  filter: drop-shadow(0 1px 3px rgba(0,0,0,0.8));
  position: relative;
  z-index: 1;
}

/* ===== 右侧工具栏 ===== */
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;

  .header-icon {
    font-size: 20px;
    cursor: pointer;
    color: #dee5f2;
    &:hover { color: #00d4ff; }
  }

  .notification-badge { cursor: pointer; }
}

/* 通知图标图片 */
.notification-icon {
  width: 22px;
  height: 22px;
  object-fit: contain;
  cursor: pointer;
  opacity: 0.85;
  transition: opacity 0.2s;
  &:hover { opacity: 1; }
}

/* 用户头像图片 */
.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

/* 时钟 */
.clock-block {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  line-height: 1.35;

  .clock-time {
    font-size: 16px;
    font-weight: 500;
    color: #4bb1ff;
    font-family: '微软雅黑', 'Microsoft YaHei', sans-serif;
    letter-spacing: 1px;
  }

  .clock-date {
    font-size: 14px;
    font-weight: 500;
    color: #7f99be;
    font-family: '微软雅黑', 'Microsoft YaHei', sans-serif;
    letter-spacing: 0.5px;
  }
}

/* 用户信息 */
.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 4px;
  transition: all 0.2s;

  &:hover {
    background: rgba(27, 48, 96, 0.35);
  }

  .user-name {
    font-size: 14px;
    font-weight: 550;
    color: #dee5f2;
    font-family: '微软雅黑', 'Microsoft YaHei', sans-serif;
  }

  :deep(.el-avatar) {
    background: #c0392b;
    color: #ffffff;
    font-size: 14px;
    font-weight: 600;
    width: 28px !important;
    height: 28px !important;
  }

  :deep(.el-icon) {
    color: #6b7fa0;
    font-size: 14px;
  }
}

.notification-toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 8px;
}

.notification-list {
  display: flex;
  flex-direction: column;
  gap: 10px;

  .notification-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px;
    border-radius: 6px;
    border: 1px solid rgba(38, 93, 223, 0.15);
    cursor: pointer;
    &:hover { background: rgba(27, 48, 96, 0.4); }

    .el-icon {
      font-size: 18px;
      margin-top: 2px;
      &.overdue { color: #f87171; }
      &.upcoming { color: #fbbf24; }
      &.pending { color: #8092c0; }
    }

    .notification-content {
      flex: 1;
    }

    .notification-title {
      margin: 0;
      font-size: 14px;
      color: #dee5f2;
    }
    .notification-meeting {
      margin: 4px 0 0;
      font-size: 14px;
      color: #8092c0;
    }
    .notification-time {
      margin: 4px 0 0;
      font-size: 14px;
      color: #8092c0;
    }
  }
}
</style>
