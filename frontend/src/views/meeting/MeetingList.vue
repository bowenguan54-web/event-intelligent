<template>
  <div class="meeting-page">
    <div class="content-frame">
    <!-- 页面标题栏-->
    <div class="page-header">
      <div class="header-info">
        <h2 class="page-title">会议管理</h2>
      </div>
      <el-button type="primary" size="large" @click="$router.push('/meeting/create')" class="create-btn">
        <el-icon><Plus /></el-icon>新建会议
      </el-button>
    </div>

    <!-- 统计概览卡片 -->
    <div class="stats-row">
      <div class="stat-card stat-total" :class="{ active: !filters.status }" @click="quickFilter('')">
        <div class="stat-icon"><el-icon><Calendar /></el-icon></div>
        <div class="stat-body">
          <span class="stat-num">{{ stats.total }}</span>
          <span class="stat-label">全部会议</span>
        </div>
      </div>
      <div class="stat-card stat-pending" :class="{ active: filters.status === 'pending' }" @click="quickFilter('pending')">
        <div class="stat-icon"><el-icon><Clock /></el-icon></div>
        <div class="stat-body">
          <span class="stat-num">{{ stats.pending }}</span>
          <span class="stat-label">待召开</span>
        </div>
      </div>
      <div class="stat-card stat-progress" :class="{ active: filters.status === 'in_progress' }" @click="quickFilter('in_progress')">
        <div class="stat-icon"><el-icon><VideoPlay /></el-icon></div>
        <div class="stat-body">
          <span class="stat-num">{{ stats.in_progress }}</span>
          <span class="stat-label">进行中</span>
        </div>
      </div>
      <div class="stat-card stat-signing" :class="{ active: filters.status === 'processing' }" @click="quickFilter('processing')">
        <div class="stat-icon"><el-icon><EditPen /></el-icon></div>
        <div class="stat-body">
          <span class="stat-num">{{ stats.signing + stats.processing }}</span>
          <span class="stat-label">会后处理中</span>
        </div>
      </div>
    </div>

    <!-- 搜索栏-->
    <div class="toolbar-bar">
      <div class="toolbar-left">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索会议名称..."
          prefix-icon="Search"
          clearable
          style="width: 260px"
          @keyup.enter="fetchList"
          @clear="fetchList"
        />
        <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="width: 260px"
          @change="fetchList"
          :shortcuts="dateShortcuts"
        />
        <el-button v-if="hasFilters" link type="primary" @click="resetFilters">
          <el-icon><RefreshRight /></el-icon>重置
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-radio-group v-model="viewMode" size="small">
          <el-radio-button value="card">
            <el-icon><Grid /></el-icon>
          </el-radio-button>
          <el-radio-button value="table">
            <el-icon><List /></el-icon>
          </el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <!-- 加载中-->
    <div v-if="loading" class="loading-area">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <span>加载中..</span>
    </div>

    <!-- 空状态-->
    <div v-else-if="meetingList.length === 0" class="empty-area">
      <el-empty description="暂无会议记录">
        <el-button type="primary" @click="$router.push('/meeting/create')">
          <el-icon><Plus /></el-icon>创建第一个会议        </el-button>
      </el-empty>
    </div>

    <!-- 卡片视图 -->
    <div v-else-if="viewMode === 'card'" class="card-grid">
      <div v-for="item in meetingList" :key="item.id" class="meeting-card" @click="goToDetail(item)">
        <div class="card-status-bar" :class="'bar-' + item.status"></div>
        <div class="card-body">
          <div class="card-top">
            <el-tag :type="statusTagType(item.status)" :class="statusTagClass(item.status)" size="small" effect="light" round>
              {{ statusLabel(item.status) }}
            </el-tag>
            <el-dropdown trigger="click" @command="(cmd) => handleCommand(cmd, item)">
              <el-icon class="card-more" @click.stop><MoreFilled /></el-icon>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="detail" :icon="Document">查看详情</el-dropdown-item>
                  <el-dropdown-item v-if="item.status === 'pending'" command="edit" :icon="Edit">编辑</el-dropdown-item>
                  <el-dropdown-item v-if="item.status === 'in_progress' || item.status === 'pending'" command="enter" :icon="VideoPlay">进入会议</el-dropdown-item>
                  <el-dropdown-item v-if="item.status !== 'pending'" command="minutes" :icon="Tickets">查看纪要</el-dropdown-item>
                  <el-dropdown-item v-if="['processing', 'finished', 'signing', 'archived'].includes(item.status)" command="issueReview" :icon="Tickets">问题审查</el-dropdown-item>
                  <el-dropdown-item v-if="item.status === 'pending' || item.status === 'finished' || item.status === 'archived'" command="delete" :icon="Delete" divided style="color:#f56c6c">删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          <h3 class="card-title">{{ item.title }}</h3>
          <div class="card-meta">
            <div class="meta-row">
              <el-icon><Clock /></el-icon>
              <span>{{ formatTime(item.start_time) }}</span>
            </div>
            <div class="meta-row" v-if="item.location">
              <el-icon><Location /></el-icon>
              <span>{{ item.location }}</span>
            </div>
          </div>
          <div class="card-footer">
            <div class="card-avatars">
              <el-tooltip v-for="(p, i) in (item.participants || []).slice(0, 5)" :key="i" :content="p.real_name || p.username || ''" placement="top">
                <el-avatar :size="28" class="stack-avatar" :style="{ zIndex: 10 - i, marginLeft: i > 0 ? '-8px' : '0' }">
                  {{ (p.real_name || p.username || '?').charAt(0) }}
                </el-avatar>
              </el-tooltip>
              <span v-if="(item.participants || []).length > 5" class="avatar-more">+{{ item.participants.length - 5 }}</span>
            </div>
            <span class="card-count">{{ (item.participants || []).length }}人</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 表格视图 -->
    <el-card v-else shadow="never" class="table-card">
      <el-table :data="meetingList" stripe style="width: 100%" @row-click="goToMeeting" row-class-name="clickable-row">
        <el-table-column prop="title" label="会议名称" min-width="220">
          <template #default="{ row }">
            <div class="table-title-cell">
              <span class="table-meeting-title">{{ row.title }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="时间" width="170">
          <template #default="{ row }">
            <div class="table-time-cell">
              <span class="time-date">{{ formatDate(row.start_time) }}</span>
              <span class="time-hour">{{ formatHour(row.start_time) }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="地点" width="140" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.location || '' }}
          </template>
        </el-table-column>

        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" :class="statusTagClass(row.status)" size="small" effect="light" round>
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="参会" width="80" align="center">
          <template #default="{ row }">
            <span class="participant-count">{{ row.participants?.length || 0 }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <div class="table-actions" @click.stop>
              <el-button
                v-if="row.status === 'pending' || row.status === 'in_progress'"
                type="primary" link size="small" @click="goToMeeting(row)"
              >进入</el-button>
              <el-button
                v-if="row.status === 'pending'"
                type="warning" link size="small"
                @click="$router.push(`/meeting/${row.id}/edit`)"
              >编辑</el-button>
              <el-button
                v-if="row.status !== 'pending'"
                type="primary" link size="small"
                @click="$router.push(`/meeting/${row.id}/minutes`)"
              >纪要</el-button>
              <el-popconfirm
                v-if="row.status === 'pending'"
                title="确定删除该会议吗？"
                confirm-button-text="删除"
                cancel-button-text="取消"
                confirm-button-type="danger"
                @confirm="handleDelete(row.id)"
              >
                <template #reference>
                  <el-button type="danger" link size="small">删除</el-button>
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 分页 -->
    <div v-if="meetingList.length > 0" class="pagination-bar">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[12, 24, 48]"
        layout="total, sizes, prev, pager, next"
        background
        @size-change="fetchList"
        @current-change="fetchList"
      />
    </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { getMeetingList, deleteMeeting } from '@/api/meeting'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Calendar, Clock, VideoPlay, CircleCheckFilled, MoreFilled,
  Edit, Document, Delete, Location, Loading, Grid, List, RefreshRight, Tickets, EditPen
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const router = useRouter()
const loading = ref(false)
const meetingList = ref([])
const viewMode = ref('card')

const filters = reactive({
  status: '',
  dateRange: null,
  keyword: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 12,
  total: 0,
})

const dateShortcuts = [
  { text: '最近一周', value: () => { const e = new Date(); const s = new Date(); s.setDate(s.getDate() - 7); return [s, e] } },
  { text: '最近一个月', value: () => { const e = new Date(); const s = new Date(); s.setMonth(s.getMonth() - 1); return [s, e] } },
  { text: '本月', value: () => { const s = new Date(); s.setDate(1); return [s, new Date()] } },
]

const hasFilters = computed(() => filters.status || filters.keyword || filters.dateRange)

const stats = reactive({
  total: 0,
  pending: 0,
  in_progress: 0,
  finished: 0,
  signing: 0,
  processing: 0,
})

const statusMap = {
  pending: { label: '待召开', type: 'warning' },
  in_progress: { label: '进行中', type: '' },
  processing: { label: '会后处理中', type: 'processing' },
  finished: { label: '已结束', type: 'success' },
  signing: { label: '会后处理中', type: 'processing' },
  archived: { label: '已归档', type: 'info' },
}

function statusLabel(s) { return statusMap[s]?.label || s }
function statusTagType(s) {
  const t = statusMap[s]?.type
  // 'processing' 是自定义类型（紫色），对 el-tag 使用 '' (default)，配合 CSS 类覆盖
  if (t === 'processing') return ''
  return t || 'info'
}
function statusTagClass(s) {
  return (statusMap[s]?.type === 'processing') ? 'tag-processing' : ''
}
function formatTime(t) { return t ? dayjs(t).format('MM月DD日 HH:mm') : '' }
function formatDate(t) { return t ? dayjs(t).format('MM/DD') : '' }
function formatHour(t) { return t ? dayjs(t).format('HH:mm') : '' }

function quickFilter(status) {
  filters.status = status
  pagination.page = 1
  fetchList()
}

function goToDetail(row) {
  router.push(`/meeting/${row.id}/detail`)
}

function goToMeeting(row) {
  if (row.status === 'pending' || row.status === 'in_progress') {
    router.push(`/meeting/${row.id}/live`)
  } else {
    router.push(`/meeting/${row.id}/minutes`)
  }
}

function handleCommand(cmd, row) {
  switch (cmd) {
    case 'detail': router.push(`/meeting/${row.id}/detail`); break
    case 'edit': router.push(`/meeting/${row.id}/edit`); break
    case 'enter': goToMeeting(row); break
    case 'minutes': router.push(`/meeting/${row.id}/minutes`); break
    case 'issueReview': router.push(`/meeting/${row.id}/issue-review`); break
    case 'delete': confirmDelete(row.id); break
  }
}

async function confirmDelete(id) {
  try {
    await ElMessageBox.confirm('确定删除该会议吗？此操作不可撤销！', '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await handleDelete(id)
  } catch {}
}

async function handleDelete(id) {
  try {
    await deleteMeeting(id)
    ElMessage.success('删除成功')
    fetchList()
  } catch (e) {
    console.error(e)
    ElMessage.error('删除失败')
  }
}

async function fetchList() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      status: filters.status || undefined,
      keyword: filters.keyword || undefined,
    }
    if (filters.dateRange) {
      params.start_date = dayjs(filters.dateRange[0]).format('YYYY-MM-DD')
      params.end_date = dayjs(filters.dateRange[1]).format('YYYY-MM-DD')
    }
    const res = await getMeetingList(params)
    meetingList.value = res.data || []
    pagination.total = res.total || 0
    if (res.status_counts) {
      stats.pending = res.status_counts.pending || 0
      stats.in_progress = res.status_counts.in_progress || 0
      stats.finished = res.status_counts.finished || 0
      stats.signing = res.status_counts.signing || 0
      stats.processing = res.status_counts.processing || 0
      stats.total = stats.pending + stats.in_progress + stats.finished + stats.signing + stats.processing
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.status = ''
  filters.dateRange = null
  filters.keyword = ''
  pagination.page = 1
  fetchList()
}

onMounted(fetchList)
onActivated(() => {
  // 清理从其他页面（如会议纪要）跳转过来时可能残留的 el-overlay，防止按钮无法点击
  document.querySelectorAll('.el-overlay').forEach(el => el.remove())
  document.body.classList.remove('el-popup-parent--hidden')
  document.body.style.overflow = ''
  document.body.style.paddingRight = ''
  fetchList()
})
</script>

<style lang="scss" scoped>
$accent: #3990f1;
$accent-dim: rgba(71,160,235,0.2);
$border: #1e5ca2;
$border-light: rgba(30,92,162,0.4);
$panel: #0e1d38;
$panel2: #14284b;
$text: #dee5f2;
$text-sub: #7f99be;
$icon: #a4ffe6;
$success: #2bffbc;

/* ── 页面容器 ── */
.meeting-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px 20px;
  background: transparent;
}

.content-frame {
  background: $panel;
  border-radius: 6px;
  border: 1px solid $border-light;
  padding: 16px 18px;
}

/* ── 页头 ── */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid $border-light;

  .page-title {
    margin: 0;
    font-size: 22px;
    font-weight: 700;
    color: $text;
    letter-spacing: 2px;
  }
  .page-desc {
    margin: 2px 0 0;
    font-size: 12px;
    color: $text-sub;
  }
  .create-btn {
    height: 32px;
    padding: 0 16px;
    font-size: 13px;
    font-weight: 600;
    background: $border;
    border-color: $border;
    &:hover { background: $accent; border-color: $accent; }
  }
}

/* ── 统计栏 ── */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 12px;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  background: $accent-dim;
  border: 1px solid $border;
  &:hover { border-color: $accent; background: rgba(71,160,235,0.3); transform: translateY(-1px); }
  &.active { border-color: $accent; background: rgba(71,160,235,0.35); }

  .stat-icon {
    width: 32px; height: 32px;
    border-radius: 4px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
  }
  .stat-body { display: flex; flex-direction: column; min-width: 0; }
  .stat-num { font-size: 20px; font-weight: 700; line-height: 1.1; font-family: 'Consolas', monospace; color: $text; }
  .stat-label { font-size: 11px; margin-top: 1px; color: $text-sub; white-space: nowrap; }
}
.stat-total .stat-icon { background: rgba(164,255,230,0.1); color: $icon; }
.stat-pending .stat-icon { background: rgba(251,191,36,0.12); color: #fbbf24; }
.stat-progress .stat-icon { background: rgba(57,144,241,0.15); color: $accent; }
.stat-signing .stat-icon { background: rgba(167,139,250,0.15); color: #a78bfa; }

/* 会后处理中 tag 紫色覆盖 */
:deep(.tag-processing.el-tag) {
  background: rgba(167,139,250,0.15) !important;
  color: #a78bfa !important;
  border-color: rgba(167,139,250,0.35) !important;
}

/* ── 工具栏 ── */
.toolbar-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px 12px;
  background: $panel2;
  border: 1px solid $border-light;
  border-radius: 4px;

  .toolbar-left { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }

  :deep(.el-radio-button__inner) {
    background: $panel;
    border-color: $border-light;
    color: $text-sub;
    padding: 5px 10px;
    &:hover { color: $accent; }
  }
  :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
    background: $border;
    border-color: $border;
    color: #fff;
    box-shadow: none;
  }
}

.loading-area {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 10px; padding: 60px 0; color: $text-sub;
}
.empty-area { padding: 40px 0; }

/* ── 卡片网格 ── */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 10px;
}
.meeting-card {
  background: $panel2;
  border-radius: 4px;
  border: 1px solid $border-light;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
  &:hover { border-color: $accent; box-shadow: 0 2px 12px rgba(0,0,0,0.25); transform: translateY(-1px); }

  .card-status-bar { height: 2px;
    &.bar-pending { background: linear-gradient(90deg, #fbbf24, #d4a20a); }
    &.bar-in_progress { background: linear-gradient(90deg, $accent, #1e7fe0); }
    &.bar-finished { background: linear-gradient(90deg, $success, #1bd49a); }
    &.bar-signing { background: linear-gradient(90deg, #a78bfa, #7c6fc4); }
    &.bar-processing { background: linear-gradient(90deg, #a78bfa, #7c6fc4); }
    &.bar-archived { background: linear-gradient(90deg, #5a7088, #3e5568); }
  }
  .card-body { padding: 10px 14px 12px; }
  .card-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
  .card-more { font-size: 15px; color: $text-sub; cursor: pointer; padding: 3px; border-radius: 3px;
    &:hover { color: $accent; background: $accent-dim; }
  }
  .card-title { margin: 0 0 8px; font-size: 14px; font-weight: 600; color: $text; line-height: 1.4; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .card-meta { margin-bottom: 8px;
    .meta-row { display: flex; align-items: center; gap: 5px; font-size: 12px; color: $text-sub; margin-bottom: 2px;
      .el-icon { font-size: 12px; color: $text-sub; }
    }
  }
  .card-footer {
    display: flex; align-items: center; justify-content: space-between;
    padding-top: 8px; border-top: 1px solid $border-light;
    .card-avatars { display: flex; align-items: center;
      .stack-avatar { background: $border; color: #fff; font-size: 11px; border: 1px solid $panel2; }
      .avatar-more { margin-left: 4px; font-size: 12px; color: $text-sub; }
    }
    .card-count { font-size: 12px; color: $text-sub; }
  }
}

/* ── 表格视图 ── */
.table-card {
  border-radius: 4px;
  background: $panel2;
  border: 1px solid $border-light;

  :deep(.el-card__body) { padding: 0; }
  :deep(.clickable-row) { cursor: pointer; }
  :deep(.el-table) { background: transparent; }
  :deep(.el-table tr) { background: transparent; }
  :deep(.el-table th.el-table__cell) { background: $panel; color: $text-sub; font-size: 12px; }
  :deep(.el-table td.el-table__cell) { border-bottom-color: $border-light; }

  .table-title-cell { display: flex; align-items: center; gap: 6px; }
  .table-meeting-title { color: $text; font-weight: 500; font-size: 13px; &:hover { color: $accent; } }
  .table-time-cell { display: flex; flex-direction: column;
    .time-date { font-size: 12px; color: $text; }
    .time-hour { font-size: 11px; color: $text-sub; }
  }
  .participant-count {
    display: inline-flex; align-items: center; justify-content: center;
    min-width: 26px; height: 20px; background: $accent-dim; border-radius: 3px;
    font-size: 12px; color: $accent; font-weight: 600; font-family: 'Consolas', monospace;
  }
  .table-actions { display: flex; align-items: center; justify-content: center; gap: 2px; }
}

/* ── 分页 ── */
.pagination-bar {
  display: flex; justify-content: center; padding: 14px 0 4px;
}

@media (max-width: 768px) {
  .meeting-page { padding: 10px 12px; }
  .stats-row { grid-template-columns: repeat(2, 1fr); }
  .card-grid { grid-template-columns: 1fr; }
  .toolbar-bar { flex-direction: column; align-items: stretch;
    .toolbar-left { flex-direction: column; }
  }
}
</style>
