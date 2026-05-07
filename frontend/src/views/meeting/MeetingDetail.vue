<template>
  <div class="detail-page">
    <!-- 顶部标题栏 -->
    <div class="page-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" text @click="router.push('/meeting/list')" />
        <h2 class="page-title">会议详情</h2>
      </div>
      <div class="header-right">
        <el-dropdown v-if="isOrganizer" trigger="click" @command="handleCommand">
          <el-button>
            <el-icon><MoreFilled /></el-icon>管理
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-if="meeting.status === 'pending'" command="edit" :icon="Edit">编辑会议</el-dropdown-item>
              <el-dropdown-item
                v-if="meeting.status === 'processing' || meeting.status === 'finished' || meeting.status === 'archived'"
                command="forceSign"
                :icon="Select"
                style="color:#e6a23c"
              >强制完成审签</el-dropdown-item>
              <el-dropdown-item
                v-if="meeting.status === 'processing' || meeting.status === 'finished' || meeting.status === 'signing' || meeting.status === 'archived'"
                command="issueReview"
                :icon="Tickets"
              >问题审查</el-dropdown-item>
              <el-dropdown-item command="delete" :icon="Delete" style="color:#f56c6c">删除会议</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <!-- 主操作按钮 -->
        <el-button
          v-if="meeting.status === 'in_progress' && isOrganizer"
          type="danger"
          size="large"
          :loading="ending"
          @click="handleEnd"
        >
          <el-icon><CircleClose /></el-icon>结束会议
        </el-button>
        <el-button
          v-if="meeting.status === 'in_progress'"
          type="primary"
          size="large"
          @click="goLive"
        >
          <el-icon><VideoPlay /></el-icon>进入会议
        </el-button>
        <el-button
          v-else-if="meeting.status === 'preparing' && isOrganizer"
          type="success"
          size="large"
          :loading="starting"
          @click="handleStart"
        >
          <el-icon><VideoPlay /></el-icon>开始会议
        </el-button>
        <el-button
          v-else-if="meeting.status === 'preparing' && !isOrganizer"
          type="info"
          size="large"
          @click="goTerminal"
        >
          <el-icon><VideoPlay /></el-icon>进入会议端
        </el-button>
        <el-button
          v-else-if="meeting.status === 'pending' && isOrganizer"
          type="warning"
          size="large"
          :loading="preparingMeeting"
          @click="handlePrepare"
        >
          <el-icon><VideoPlay /></el-icon>会议准备
        </el-button>
        <el-button
          v-else-if="meeting.status === 'pending' && !isOrganizer"
          type="primary"
          size="large"
          disabled
        >
          <el-icon><VideoPlay /></el-icon>等待发起人准备
        </el-button>
        <template v-else-if="meeting.status === 'processing' || meeting.status === 'finished' || meeting.status === 'archived'">
          <el-button class="action-btn" :loading="generatingSummary" @click="doGenerateSummary">
            <el-icon><MagicStick /></el-icon>生成摘要
          </el-button>
          <el-button class="action-btn" :loading="extractingKeypoints" @click="doExtractKeypoints">
            <el-icon><Connection /></el-icon>提取要点
          </el-button>
          <el-button class="action-btn" v-if="meeting.status === 'processing' || meeting.status === 'finished' || meeting.status === 'signing' || meeting.status === 'archived'" @click="router.push(`/meeting/${meetingId}/issue-review`)">
            <el-icon><Tickets /></el-icon>问题审查
          </el-button>
          <el-button class="action-btn" @click="router.push(`/meeting/${meetingId}/minutes`)">
            <el-icon><Document /></el-icon>编写纪要
          </el-button>
        </template>
      </div>
    </div>

    <div v-if="loading" class="loading-wrap">
      <el-skeleton :rows="8" animated />
    </div>

    <div v-else class="detail-body">
      <!-- 基本信息卡片 -->
      <el-card class="info-card" shadow="never">
        <div class="meeting-title-row">
          <span class="meeting-title">{{ meeting.title }}</span>
          <el-tag size="small" class="type-tag">{{ meetingTypeLabel }}</el-tag>
          <el-tag :type="statusTagType(meeting.status)" :class="{ 'processing-tag': meeting.status === 'processing' }" effect="light" size="large" round>
            {{ statusLabel(meeting.status) }}
          </el-tag>
        </div>
        <el-divider />

        <!-- 统计网格 Row 1 -->
        <div class="info-stat-row">
          <div class="info-stat">
            <div class="info-stat-label"><el-icon><Clock /></el-icon> 开始时间</div>
            <div class="info-stat-value">{{ meeting.start_time ? dayjs(meeting.start_time).format('YYYY-MM-DD HH:mm') : '—' }}</div>
          </div>
          <div class="info-stat">
            <div class="info-stat-label"><el-icon><Clock /></el-icon> 结束时间</div>
            <div class="info-stat-value">{{ meeting.end_time ? dayjs(meeting.end_time).format('YYYY-MM-DD HH:mm') : '—' }}</div>
          </div>
          <div class="info-stat">
            <div class="info-stat-label"><el-icon><Timer /></el-icon> 会议时长</div>
            <div class="info-stat-value">
              <span>{{ meetingDuration }}</span>
              <div v-if="meeting.start_time && meeting.end_time" class="duration-bar-wrap">
                <div class="duration-bar"></div>
              </div>
            </div>
          </div>
          <div class="info-stat">
            <div class="info-stat-label"><el-icon><Location /></el-icon> 会议地点</div>
            <div class="info-stat-value">{{ meeting.location || '—' }}</div>
          </div>
        </div>

        <!-- 统计网格 Row 2 -->
        <div class="info-stat-row">
          <div class="info-stat">
            <div class="info-stat-label"><el-icon><User /></el-icon> 参会人数</div>
            <div class="info-stat-value">{{ participants.length }} 人</div>
          </div>
          <div class="info-stat">
            <div class="info-stat-label"><el-icon><Document /></el-icon> 会议材料</div>
            <div class="info-stat-value">{{ attachments.length }} 份</div>
          </div>
          <div class="info-stat">
            <div class="info-stat-label"><el-icon><List /></el-icon> 议程状态</div>
            <div class="info-stat-value">
              <el-tag v-if="meeting.agenda" size="small" type="success" effect="plain">已生成</el-tag>
              <el-tag v-else size="small" type="info" effect="plain">未生成</el-tag>
            </div>
          </div>
          <div class="info-stat">
            <div class="info-stat-label"><el-icon><CircleCheck /></el-icon> 签到状态</div>
            <div class="info-stat-value">
              <span class="checkin-done-num">{{ checkedInCount }}</span>
              <span class="checkin-sep"> / </span>
              <span class="checkin-total-txt">{{ participants.length }} 人已签</span>
            </div>
          </div>
        </div>

        <el-divider />

        <!-- 描述行 -->
        <div class="info-desc-row">
          <span class="info-desc-label"><el-icon><Memo /></el-icon> 会议描述</span>
          <span :class="{ 'empty-val': !meeting.description }" class="info-desc-value">{{ meeting.description || '暂无描述' }}</span>
          <el-button v-if="isOrganizer" link type="primary" size="small" class="add-desc-btn" @click="router.push(`/meeting/${meetingId}/edit`)">+ 添加描述</el-button>
        </div>
      </el-card>

      <!-- 参会人员 — 名牌展示 -->
      <el-card shadow="never" class="participants-card">
        <template #header>
          <div class="card-header">
            <el-icon><User /></el-icon>
            <span>参会人员</span>
            <el-badge :value="participants.length" class="header-badge" />
            <div class="header-actions">
              <template v-if="!isEditingParticipants">
                <el-button
                  v-if="isOrganizer && (meeting.status === 'pending' || meeting.status === 'preparing') && seatSwapOptions.length > 1"
                  size="small"
                  type="warning"
                  plain
                  @click="openSeatSwapDialog"
                >
                  调整座位
                </el-button>

              </template>
              <template v-else>
                <el-button size="small" @click="cancelEditParticipants">取消</el-button>
                <el-button size="small" type="success" :loading="savingOrder" @click="saveParticipantsOrder">
                  <el-icon><Check /></el-icon>保存
                </el-button>
              </template>
            </div>
          </div>
        </template>
        <div v-if="loadingParticipants" class="loading-inner">
          <el-skeleton :rows="3" animated />
        </div>
        <!-- 编辑模式：拖拽列表 -->
        <div v-else-if="isEditingParticipants" class="participant-edit-list">
          <p class="edit-tip">拖拽卡片可调整排列顺序</p>
          <draggable
            v-model="participants"
            item-key="id"
            handle=".drag-handle"
            ghost-class="drag-ghost"
            animation="200"
          >
            <template #item="{ element, index }">
              <div class="participant-edit-row">
                <span class="drag-handle">
                  <el-icon><Rank /></el-icon>
                </span>
                <span class="edit-index">{{ index + 1 }}</span>
                <span class="edit-name">{{ element.real_name }}</span>
                <span class="edit-dept">{{ element.department || element.role || '参会人员' }}</span>
                <el-tag :type="element.checked_in ? 'success' : 'info'" size="small" round>
                  {{ element.checked_in ? '✓ 已签到' : '未签到' }}
                </el-tag>
              </div>
            </template>
          </draggable>
        </div>
        <!-- 展示模式：名牌卡片 -->
        <div v-else class="participant-grid">
          <div v-for="p in participants" :key="p.id" class="name-badge-card">
            <div class="badge-glow"></div>
            <div class="badge-upper">
              <span class="badge-seat" :style="{ opacity: seatMap[p.id] ? 1 : 0 }">{{ seatMap[p.id] || '—' }}</span>
              <span class="badge-name">{{ p.real_name }}</span>
              <el-tag v-if="p.is_leader" type="warning" size="small" class="role-tag leader-tag">组长</el-tag>
              <el-tag v-else-if="p.is_expert_in_meeting" type="success" size="small" class="role-tag expert-tag">专家</el-tag>
            </div>
            <div class="badge-lower">
              <div class="badge-info-group">
                <span class="badge-dept">{{ p.department || p.role || '参会人员' }}</span>
                <span v-if="p.professional_title" class="badge-prof-title">{{ p.professional_title }}</span>
              </div>
              <div class="badge-actions">
                <el-tag :type="p.checked_in ? 'success' : 'info'" size="small" round class="checkin-tag">
                  {{ p.checked_in ? '✓ 已签到' : '未签到' }}
                </el-tag>
                <el-button v-if="p.checked_in && p.signature_status === 'signed'" link type="warning" size="small" @click.stop="handleRollback(p)" style="font-size:12px;padding:0">退回重签</el-button>
                <el-button
                  v-if="meeting.status === 'preparing' && isOrganizer && !p.checked_in"
                  size="small"
                  type="primary"
                  plain
                  style="font-size:12px;padding:1px 6px"
                  @click="openAdminSignDialog(p)"
                >手写签到</el-button>
              </div>
            </div>
          </div>
          <el-empty v-if="participants.length === 0" description="暂无参会人员" :image-size="60" />
        </div>
      </el-card>



      <!-- 会议材料 -->
      <el-card shadow="never" class="attachments-card">
        <template #header>
          <div class="card-header">
            <el-icon><FolderOpened /></el-icon>
            <span>会议材料</span>
            <el-badge :value="attachments.length" class="header-badge" />
          </div>
        </template>
        <div v-if="loadingAttachments" class="loading-inner">
          <el-skeleton :rows="3" animated />
        </div>
        <div v-else>
          <div v-if="attachments.length > 0" class="attach-archive-tip">
            <el-icon style="color:#faad14"><InfoFilled /></el-icon>
            勾选需要归档的材料，点击「保存归档设置」生效
          </div>
          <div v-for="file in attachments" :key="file.id" class="file-row">
            <el-checkbox v-model="file.archiveSelected" class="attach-archive-check" />
            <el-icon :class="['file-icon', file.file_type?.startsWith('image') ? 'file-icon-image' : '']"><Document /></el-icon>
            <div class="file-info">
              <span class="file-name">{{ file.filename }}</span>
              <span class="file-meta">
                {{ file.file_type || '' }}
                {{ file.file_size ? formatFileSize(file.file_size) : '' }}
              </span>
            </div>
            <el-tag v-if="file.archiveSelected" type="success" size="small" effect="plain" style="margin-right:4px">已选归档</el-tag>
            <el-button v-if="canPreview(file)" text type="success" size="small" @click="previewFile(file)">预览</el-button>
            <el-button text type="primary" size="small" @click="downloadFile(file)">下载</el-button>
          </div>
          <div v-if="attachments.length === 0" class="attach-empty-tip"><el-icon><Document /></el-icon> 暂无会议材料</div>
          <div v-if="attachments.length > 0" class="attach-archive-footer">
            <el-button type="primary" size="small" :loading="savingArchive" @click="saveArchiveSelection">
              <el-icon><Check /></el-icon>
              保存归档设置
            </el-button>
            <span class="attach-archive-count">已选 {{ attachments.filter(f => f.archiveSelected).length }} / {{ attachments.length }} 份</span>
          </div>
        </div>
      </el-card>

      <!-- 会后处理流程（会后处理中/已结束/已归档） -->
      <el-card v-if="meeting.status === 'processing' || meeting.status === 'signing' || meeting.status === 'finished' || meeting.status === 'archived'" shadow="never" class="post-flow-card">
        <template #header>
          <div class="card-header">
            <el-icon><Promotion /></el-icon>
            <span>会后处理流程</span>
          </div>
        </template>
        <div class="post-flow-steps">
          <div class="pf-step" :class="{ done: !!aiSummary }">
            <div class="pf-step-num">1</div>
            <div class="pf-step-body">
              <div class="pf-step-title">生成会议摘要</div>
              <el-button size="small" type="warning" :loading="generatingSummary" @click="doGenerateSummary" style="margin-top:8px">
                <el-icon><MagicStick /></el-icon>{{ aiSummary ? '重新生成' : '生成摘要' }}
              </el-button>
            </div>
            <div class="pf-step-tag"><el-tag v-if="aiSummary" type="success" size="small">已完成</el-tag><el-tag v-else type="info" size="small">待处理</el-tag></div>
          </div>
          <div class="pf-step" :class="{ done: aiKeypoints.length > 0 }">
            <div class="pf-step-num">2</div>
            <div class="pf-step-body">
              <div class="pf-step-title">提取关键信息与要点</div>
              <el-button size="small" type="primary" plain :loading="extractingKeypoints" @click="doExtractKeypoints" style="margin-top:8px">
                <el-icon><Connection /></el-icon>{{ aiKeypoints.length ? '重新提取' : '提取要点' }}
              </el-button>
            </div>
            <div class="pf-step-tag"><el-tag v-if="aiKeypoints.length" type="success" size="small">已完成</el-tag><el-tag v-else type="info" size="small">待处理</el-tag></div>
          </div>
          <div class="pf-step">
            <div class="pf-step-num">3</div>
            <div class="pf-step-body">
              <div class="pf-step-title">编写会议纪要</div>
              <el-button size="small" @click="router.push(`/meeting/${meetingId}/minutes`)" style="margin-top:8px">
                <el-icon><Document /></el-icon>前往编写
              </el-button>
            </div>
            <div class="pf-step-tag"><el-tag type="info" size="small">待处理</el-tag></div>
          </div>
          <div class="pf-step" :class="{ done: issueReviewDone }">
            <div class="pf-step-num">4</div>
            <div class="pf-step-body">
              <div class="pf-step-title">问题审查</div>
              <el-button size="small" type="warning" plain @click="router.push(`/meeting/${meetingId}/issue-review`)" style="margin-top:8px">
                <el-icon><Tickets /></el-icon>前往审查
              </el-button>
            </div>
            <div class="pf-step-tag">
              <el-tag :type="issueReviewDone ? 'success' : 'info'" size="small">{{ issueReviewStatusText }}</el-tag>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 会议摘要 -->
      <el-card v-if="aiSummary || meeting.summary" shadow="never" class="summary-card">
        <template #header>
          <div class="card-header">
            <el-icon><Document /></el-icon>
            <span>会议摘要</span>
          </div>
        </template>
        <div class="summary-text">{{ aiSummary || meeting.summary }}</div>
      </el-card>

      <!-- 关键要点 -->
      <el-card v-if="aiKeypoints.length" shadow="never" class="keypoints-card">
        <template #header>
          <div class="card-header">
            <el-icon><List /></el-icon>
            <span>关键信息与要点</span>
          </div>
        </template>
        <div class="kp-list">
          <div v-for="(kp, i) in aiKeypoints" :key="i" class="kp-item" :class="'kp-' + kp.importance">
            <div class="kp-badge">{{ i + 1 }}</div>
            <div class="kp-body">
              <div class="kp-title">{{ kp.title }}</div>
              <div class="kp-content">{{ kp.content }}</div>
            </div>
            <el-tag :type="kp.importance === 'high' ? 'danger' : kp.importance === 'medium' ? 'warning' : 'info'" size="small" effect="plain">{{ kp.importance === 'high' ? '高' : kp.importance === 'medium' ? '中' : '低' }}</el-tag>
          </div>
        </div>
      </el-card>

      <!-- 会议议程 -->
      <el-card v-if="meeting.agenda" shadow="never" class="agenda-card">
        <template #header>
          <div class="card-header">
            <el-icon><List /></el-icon>
            <span>会议议程</span>
          </div>
        </template>
        <div class="rendered-html" v-html="renderedAgenda"></div>
      </el-card>
    </div>

    <el-dialog v-model="seatSwapDialog" title="调整座位" width="600px" destroy-on-close>
      <div style="color:#8bb3d9;margin-bottom:14px;font-size:13px;line-height:1.7">
        点击第一个座位选中，再点击另一座位完成互换。座位调整后，专家/组长权限继续跟随人员。
        <span v-if="seatSwapFirst" style="margin-left:12px;color:#3990f1;font-weight:600">已选中：{{ seatSwapFirst.label }} · {{ seatSwapFirst.userName }}</span>
      </div>
      <div class="seat-visual-grid">
        <div
          v-for="item in seatEditItems"
          :key="item.seatId"
          class="seat-visual-card"
          :class="{ selected: seatSwapFirst?.seatId === item.seatId, empty: !item.userId }"
          @click="handleSeatClick(item)"
        >
          <div class="seat-visual-num">{{ item.label }}</div>
          <div class="seat-visual-name">{{ item.userName || '—' }}</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="seatSwapDialog = false">取消</el-button>
        <el-button type="primary" :loading="swappingSeats" @click="saveSeatLayout">保存调整</el-button>
      </template>
    </el-dialog>

    <!-- 准备阶段手写签到弹窗 -->
    <el-dialog v-model="adminSignDialog" title="手写签到" width="520px" :close-on-click-modal="false" destroy-on-close>
      <div v-if="adminSignTarget" style="text-align:center;margin-bottom:16px">
        <div style="font-size:20px;font-weight:700;color:#00d4ff;letter-spacing:2px">{{ adminSignTarget.real_name }}</div>
        <div style="font-size:14px;color:#8bb3d9;margin-top:4px">
          {{ adminSignTarget.department || '' }}
          <el-tag v-if="adminSignTarget.is_leader" type="danger" size="small" style="margin-left:6px">组长</el-tag>
          <el-tag v-else-if="adminSignTarget.is_expert_in_meeting" type="warning" size="small" style="margin-left:6px">专家</el-tag>
        </div>
      </div>
      <div style="text-align:center;font-size:14px;color:#8bb3d9;margin-bottom:8px">请在下方框内手写签名</div>
      <div style="display:flex;justify-content:center">
        <canvas
          ref="adminSignCanvasRef"
          width="460"
          height="160"
          style="border:1px dashed #2a4d6b;border-radius:6px;background:#0d1e35;cursor:crosshair;touch-action:none;display:block"
          @pointerdown="startAdminSign"
          @pointermove="moveAdminSign"
          @pointerup="endAdminSign"
          @pointerleave="endAdminSign"
        />
      </div>
      <div style="display:flex;justify-content:center;margin-top:8px">
        <el-button size="small" @click="clearAdminSign">清除</el-button>
      </div>
      <template #footer>
        <el-button @click="adminSignDialog = false">取消</el-button>
        <el-button type="primary" :loading="checkingIn" @click="confirmAdminCheckin">确认签到</el-button>
      </template>
    </el-dialog>

    <!-- 文件预览弹窗 -->
    <el-dialog v-model="previewVisible" :title="previewTitle" width="80%" top="5vh" destroy-on-close>
      <div class="preview-body">
        <iframe v-if="previewType === 'pdf'" :src="previewUrl" class="preview-iframe" />
        <img v-else-if="previewType === 'image'" :src="previewUrl" class="preview-image" />
        <div v-else class="preview-unsupported">暂不支持该格式在线预览，请下载查看</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  getMeetingById, startMeeting, prepareMeeting, deleteMeeting,
  getParticipantsStatus, getAttachments, endMeeting, updateParticipantsOrder,
  getTranscripts, signatureRollback, terminalCheckin, updateSeatLayout,
  listMinutesRecords, updateAttachmentArchiveSelection
} from '@/api/meeting'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import {
  ArrowLeft, VideoPlay, Edit, Delete, MoreFilled, Location, Select,
  Clock, Timer, User, Document, FolderOpened, List, CircleClose, CircleCheck,
  Check, Rank, MagicStick, Connection, Promotion, Tickets, Memo, InfoFilled
} from '@element-plus/icons-vue'
import draggable from 'vuedraggable'

function agendaTextToHtml(text) {
  if (!text) return ''
  const lines = text.split('\n')
  let html = ''
  for (let i = 0; i < lines.length; i++) {
    const t = lines[i].trim()
    if (!t) { html += '<div style="height:6px;"></div>'; continue }
    if (i === 0 || (i <= 2 && t.includes('议程'))) {
      html += `<p style="font-size:17px;font-weight:bold;color:#00d4ff;margin:8px 0;">${t}</p>`
    } else if (/^#{1,3}\s/.test(t)) {
      html += `<p style="font-weight:bold;color:#00d4ff;margin:8px 0;">${t.replace(/^#+\s*/, '')}</p>`
    } else if (/^[一二三四五六七八九十\d]+[、．.\s]/.test(t)) {
      html += `<p style="margin:4px 0;padding:3px 0;border-bottom:1px dashed rgba(0,212,255,0.15);color:#c8dff5;">${t}</p>`
    } else {
      html += `<p style="margin:2px 0;color:#c8dff5;">${t}</p>`
    }
  }
  return html
}

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const meetingId = route.params.id

const loading = ref(true)
const loadingParticipants = ref(true)
const loadingAttachments = ref(true)
const savingArchive = ref(false)
const starting = ref(false)
const preparingMeeting = ref(false)
const ending = ref(false)
const forceEnding = ref(false)
const generatingSummary = ref(false)
const extractingKeypoints = ref(false)
const aiSummary = ref('')
const aiKeypoints = ref([])

const meeting = ref({})
const participants = ref([])
const attachments = ref([])
const transcripts = ref([])
const seatSwapDialog = ref(false)
const swappingSeats = ref(false)
const seatSwapForm = ref({ fromSeatId: null, toSeatId: null })
// Visual seat editor state
const seatEditItems = ref([])
const seatSwapFirst = ref(null)

const isEditingParticipants = ref(false)
const savingOrder = ref(false)
let participantsBackup = []

function startEditParticipants() {
  participantsBackup = structuredClone(participants.value)
  isEditingParticipants.value = true
}

function cancelEditParticipants() {
  participants.value = participantsBackup
  isEditingParticipants.value = false
}

async function saveParticipantsOrder() {
  savingOrder.value = true
  try {
    const userIds = participants.value.map(p => p.id)
    await updateParticipantsOrder(meetingId, userIds)
    ElMessage.success('排序已保存')
    isEditingParticipants.value = false
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '保存排序失败')
  } finally {
    savingOrder.value = false
  }
}

async function handleRollback(participant) {
  try {
    await signatureRollback(meetingId, participant.id)
    ElMessage.success('已退回，等待重签')
    participants.value = await getParticipantsStatus(meetingId)
  } catch { ElMessage.error('操作失败') }
}

const isOrganizer = computed(() =>
  meeting.value.creator_id && userStore.userInfo?.id === meeting.value.creator_id
)

const meetingTypeLabel = computed(() => {
  const map = { regular: '例会', special: '专题会议', decision: '决策会议', review: '评审会议', other: '其他' }
  return map[meeting.value.meeting_type] || meeting.value.meeting_type || '—'
})

const meetingDuration = computed(() => {
  if (!meeting.value.start_time || !meeting.value.end_time) return '—'
  const diff = dayjs(meeting.value.end_time).diff(dayjs(meeting.value.start_time), 'minute')
  if (diff <= 0) return '—'
  const h = Math.floor(diff / 60)
  const m = diff % 60
  return h > 0 ? (m > 0 ? `${h} 小时 ${m} 分` : `${h} 小时`) : `${m} 分钟`
})

const checkedInCount = computed(() => participants.value.filter(p => p.checked_in).length)

const renderedAgenda = computed(() => agendaTextToHtml(meeting.value.agenda || ''))

// 座位号映射 userId -> seatLabel
const seatMap = computed(() => {
  const map = {}
  if (!meeting.value?.seat_layout) return map
  try {
    const layout = typeof meeting.value.seat_layout === 'string'
      ? JSON.parse(meeting.value.seat_layout)
      : meeting.value.seat_layout
    for (const s of (layout.seats || [])) {
      if (s.userId) map[s.userId] = s.label || String(s.id)
    }
  } catch {}
  return map
})

const seatSwapOptions = computed(() => {
  if (!meeting.value?.seat_layout) return []
  try {
    const layout = typeof meeting.value.seat_layout === 'string'
      ? JSON.parse(meeting.value.seat_layout)
      : meeting.value.seat_layout
    return (layout.seats || [])
      .filter(seat => seat.userId)
      .map(seat => ({
        seatId: seat.id,
        label: seat.label || String(seat.id),
        userId: seat.userId,
        userName: participants.value.find(item => item.id === seat.userId)?.real_name || seat.userName || '未指定',
      }))
  } catch {
    return []
  }
})

function statusLabel(s) {
  const map = { pending: '待开始', preparing: '准备中', in_progress: '进行中', processing: '会后处理中', signing: '审签中', finished: '已结束', archived: '已归档' }
  return map[s] || s
}

function statusTagType(s) {
  const map = { pending: 'info', preparing: 'warning', in_progress: 'success', processing: '', signing: 'info', finished: '', archived: '' }
  return map[s] ?? ''
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}

function downloadFile(file) {
  const url = `/api/meeting/attachment/${file.id}/download`
  window.open(url, '_blank')
}

async function saveArchiveSelection() {
  savingArchive.value = true
  try {
    const selectedIds = attachments.value.filter(f => f.archiveSelected).map(f => f.id)
    await updateAttachmentArchiveSelection(meetingId, selectedIds)
    ElMessage.success('归档设置已保存')
  } catch {
    ElMessage.error('保存失败，请重试')
  } finally {
    savingArchive.value = false
  }
}

// 文件预览
const previewVisible = ref(false)
const previewUrl = ref('')
const previewTitle = ref('')
const previewType = ref('')

function canPreview(file) {
  const name = (file.filename || '').toLowerCase()
  const type = (file.file_type || '').toLowerCase()
  return type.startsWith('image/') || type === 'application/pdf'
    || name.endsWith('.pdf') || /\.(jpg|jpeg|png|gif|webp|bmp|svg)$/.test(name)
}

function previewFile(file) {
  const name = (file.filename || '').toLowerCase()
  const type = (file.file_type || '').toLowerCase()
  previewUrl.value = `/api/meeting/attachment/${file.id}/download`
  previewTitle.value = file.filename
  if (type === 'application/pdf' || name.endsWith('.pdf')) {
    previewType.value = 'pdf'
  } else if (type.startsWith('image/') || /\.(jpg|jpeg|png|gif|webp|bmp|svg)$/.test(name)) {
    previewType.value = 'image'
  } else {
    previewType.value = 'other'
  }
  previewVisible.value = true
}

function goLive() {
  router.push(`/meeting/${meetingId}/live`)
}

function goTerminal() {
  window.open(`/terminal/${meetingId}`, '_blank')
}

function openSeatSwapDialog() {
  const layout = typeof meeting.value.seat_layout === 'string'
    ? JSON.parse(meeting.value.seat_layout)
    : (meeting.value.seat_layout || { seats: [] })
  seatEditItems.value = (layout.seats || []).map(s => ({
    seatId: s.id,
    label: s.label || String(s.id),
    userId: s.userId || null,
    userName: participants.value.find(p => p.id === s.userId)?.real_name || s.userName || '',
  }))
  seatSwapFirst.value = null
  seatSwapDialog.value = true
}

function handleSeatClick(item) {
  if (!seatSwapFirst.value) {
    seatSwapFirst.value = { ...item }
  } else {
    if (seatSwapFirst.value.seatId === item.seatId) {
      seatSwapFirst.value = null
      return
    }
    // Swap userId/userName between two seats
    const idx1 = seatEditItems.value.findIndex(s => s.seatId === seatSwapFirst.value.seatId)
    const idx2 = seatEditItems.value.findIndex(s => s.seatId === item.seatId)
    if (idx1 !== -1 && idx2 !== -1) {
      const tmp = { userId: seatEditItems.value[idx1].userId, userName: seatEditItems.value[idx1].userName }
      seatEditItems.value[idx1].userId = seatEditItems.value[idx2].userId
      seatEditItems.value[idx1].userName = seatEditItems.value[idx2].userName
      seatEditItems.value[idx2].userId = tmp.userId
      seatEditItems.value[idx2].userName = tmp.userName
    }
    seatSwapFirst.value = null
  }
}

async function saveSeatLayout() {
  swappingSeats.value = true
  try {
    const layout = typeof meeting.value.seat_layout === 'string'
      ? JSON.parse(meeting.value.seat_layout)
      : JSON.parse(JSON.stringify(meeting.value.seat_layout || { seats: [] }))
    const seats = layout.seats || []
    for (const edited of seatEditItems.value) {
      const seat = seats.find(s => s.id === edited.seatId)
      if (seat) {
        seat.userId = edited.userId
        seat.userName = edited.userName
      }
    }
    const seatLayout = JSON.stringify(layout)
    await updateSeatLayout(meetingId, seatLayout)
    meeting.value.seat_layout = seatLayout
    seatSwapDialog.value = false
    ElMessage.success('座位调整成功')
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '调整座位失败')
  } finally {
    swappingSeats.value = false
  }
}

async function submitSeatSwap() {
  const { fromSeatId, toSeatId } = seatSwapForm.value
  if (!fromSeatId || !toSeatId || fromSeatId === toSeatId) {
    ElMessage.warning('请选择两个不同的座位')
    return
  }
  swappingSeats.value = true
  try {
    const layout = typeof meeting.value.seat_layout === 'string'
      ? JSON.parse(meeting.value.seat_layout)
      : JSON.parse(JSON.stringify(meeting.value.seat_layout || { seats: [] }))
    const seats = layout.seats || []
    const fromSeat = seats.find(item => item.id === fromSeatId)
    const toSeat = seats.find(item => item.id === toSeatId)
    if (!fromSeat || !toSeat) {
      ElMessage.error('座位信息不存在')
      return
    }
    const fromUserId = fromSeat.userId
    const fromUserName = fromSeat.userName
    fromSeat.userId = toSeat.userId
    fromSeat.userName = toSeat.userName
    toSeat.userId = fromUserId
    toSeat.userName = fromUserName
    const seatLayout = JSON.stringify(layout)
    await updateSeatLayout(meetingId, seatLayout)
    meeting.value.seat_layout = seatLayout
    seatSwapDialog.value = false
    ElMessage.success('座位调整成功，权限将继续跟随人员保留')
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '调整座位失败')
  } finally {
    swappingSeats.value = false
  }
}

const adminSignDialog = ref(false)
const adminSignTarget = ref(null)
const adminSignCanvasRef = ref(null)
const checkingIn = ref(false)
let adminSignDrawing = false
let adminSignCtx = null

function openAdminSignDialog(p) {
  adminSignTarget.value = p
  adminSignDialog.value = true
  nextTick(() => {
    const canvas = adminSignCanvasRef.value
    if (!canvas) return
    adminSignCtx = canvas.getContext('2d')
    adminSignCtx.strokeStyle = '#00d4ff'
    adminSignCtx.lineWidth = 2.5
    adminSignCtx.lineCap = 'round'
    adminSignCtx.lineJoin = 'round'
  })
}

function startAdminSign(e) {
  if (!adminSignCtx) return
  adminSignDrawing = true
  adminSignCanvasRef.value.setPointerCapture(e.pointerId)
  const r = adminSignCanvasRef.value.getBoundingClientRect()
  adminSignCtx.beginPath()
  adminSignCtx.moveTo(e.clientX - r.left, e.clientY - r.top)
}

function moveAdminSign(e) {
  if (!adminSignDrawing || !adminSignCtx) return
  const r = adminSignCanvasRef.value.getBoundingClientRect()
  adminSignCtx.lineTo(e.clientX - r.left, e.clientY - r.top)
  adminSignCtx.stroke()
}

function endAdminSign() { adminSignDrawing = false }

function clearAdminSign() {
  if (!adminSignCtx || !adminSignCanvasRef.value) return
  adminSignCtx.clearRect(0, 0, adminSignCanvasRef.value.width, adminSignCanvasRef.value.height)
}

async function confirmAdminCheckin() {
  checkingIn.value = true
  try {
    await terminalCheckin(meetingId, adminSignTarget.value.id)
    adminSignTarget.value.checked_in = true
    ElMessage.success(`${adminSignTarget.value.real_name} 已签到`)
    adminSignDialog.value = false
  } catch {
    ElMessage.error('签到操作失败')
  } finally {
    checkingIn.value = false
  }
}

async function handlePrepare() {
  try {
    preparingMeeting.value = true
    await prepareMeeting(meetingId)
    ElMessage.success('会议进入准备状态，参会者可在终端选择座位')
    meeting.value.status = 'preparing'
    window.open(`/meeting/${meetingId}/prepare-screen`, '_blank')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '操作失败')
  } finally {
    preparingMeeting.value = false
  }
}

async function handleStart() {
  try {
    starting.value = true
    await startMeeting(meetingId)
    ElMessage.success('会议已开始！')
    meeting.value.status = 'in_progress'
    router.push(`/meeting/${meetingId}/live`)
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '开始会议失败')
  } finally {
    starting.value = false
  }
}

async function handleEnd() {
  try {
    await ElMessageBox.confirm('确认结束本次会议？结束后可生成摘要、提取要点，再编写会议纪要。', '结束会议', {
      type: 'warning',
      confirmButtonText: '结束会议',
      cancelButtonText: '取消',
      confirmButtonClass: 'el-button--danger',
    })
  } catch { return }
  ending.value = true
  try {
    await endMeeting(meetingId)
    meeting.value.status = 'finished'
    ElMessage.success('会议已结束，请依次完成会后处理流程')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '结束会议失败')
  } finally {
    ending.value = false
  }
}

async function doGenerateSummary() {
  generatingSummary.value = true
  try {
    await new Promise(r => setTimeout(r, 1200))
    aiSummary.value = `本次会议于${meeting.value.start_time ? dayjs(meeting.value.start_time).format('YYYY年MM月DD日 HH:mm') : '—'} 召开，共 ${participants.value.length} 人参会。会议围绕${meeting.value.title}」主题展开，重点讨论了各科室工作进展与第二季度计划部署，形成多项工作决议，要求各责任人按期落实。`
    ElMessage.success('摘要生成成功')
  } catch {
    ElMessage.error('摘要生成失败')
  } finally {
    generatingSummary.value = false
  }
}

async function doExtractKeypoints() {
  extractingKeypoints.value = true
  try {
    await new Promise(r => setTimeout(r, 1500))
    aiKeypoints.value = [
      { title: '会议决议事项', content: '各科室须按期提交工作计划，信息化项目纳入月度督办，培训方案由人事科牵头制定。', importance: 'high' },
      { title: '重点工作部署', content: '二季度五项重点工作：信息化系统上线、预算中期调整、全员培训、会议室智能化改造、跨部门协作优化', importance: 'high' },
      { title: '待办行动项', content: '各责任人须在规定时间节点前完成对应工作任务，超期将启动督办程序。', importance: 'medium' },
    ]
    ElMessage.success('要点提取成功')
  } catch {
    ElMessage.error('要点提取失败')
  } finally {
    extractingKeypoints.value = false
  }
}

function copyMeetingCode() {
  const code = meeting.value?.meeting_code
  if (!code) return
  navigator.clipboard.writeText(code).then(() => {
    ElMessage.success('会议号已复制')
  }).catch(() => {
    ElMessage.info(`会议号：${code}`)
  })
}

function handleCommand(cmd) {
  if (cmd === 'edit') {
    router.push(`/meeting/${meetingId}/edit`)
  } else if (cmd === 'issueReview') {
    router.push(`/meeting/${meetingId}/issue-review`)
  } else if (cmd === 'forceSign') {
    ElMessageBox.confirm(
      '当前尚有参会人员未完成审签，是否强制结束签署流程？强制完成后纳入占签记录将标注为「管理员强制完成」',
      '强制完成审签',
      {
        type: 'warning',
        confirmButtonText: '确认强制完成',
        cancelButtonText: '取消',
        confirmButtonClass: 'el-button--warning',
      }
    ).then(async () => {
      forceEnding.value = true
      await new Promise(r => setTimeout(r, 800))
      forceEnding.value = false
      ElMessage.success('审签流程已强制结束，纪要状态已更新为「已完成」')
    }).catch(() => {})
  } else if (cmd === 'delete') {
    ElMessageBox.confirm('确定要删除该会议吗？此操作不可恢复', '确认删除', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      confirmButtonClass: 'el-button--danger',
    }).then(async () => {
      await deleteMeeting(meetingId)
      ElMessage.success('会议已删除')
      router.push('/meeting/list')
    }).catch(() => {})
  }
}

const issueReviewDone = computed(() => ['completed', 'skipped'].includes(meeting.value.issue_review_status))
const issueReviewStatusText = computed(() => {
  const map = {
    completed: '已完成',
    skipped: '已跳过',
    pending: '待处理',
  }
  return map[meeting.value.issue_review_status] || '待处理'
})

const primaryMinutesSigned = ref(false)

onMounted(async () => {
  try {
    meeting.value = await getMeetingById(meetingId)
  } catch {
    ElMessage.error('加载会议信息失败')
  } finally {
    loading.value = false
  }

  try {
    participants.value = await getParticipantsStatus(meetingId)
  } catch {
    participants.value = []
  } finally {
    loadingParticipants.value = false
  }

  try {
    const rawAttachments = await getAttachments(meetingId)
    attachments.value = rawAttachments.map(f => ({ ...f, archiveSelected: !!f.is_archived }))
  } catch {
    attachments.value = []
  } finally {
    loadingAttachments.value = false
  }

  // 加载转写记录（已结束/已归档/会后处理中会议）
  if (['processing', 'signing', 'finished', 'archived', 'in_progress'].includes(meeting.value.status)) {
    try {
      transcripts.value = await getTranscripts(meetingId)
    } catch {
      transcripts.value = []
    }
  }

  // 加载纪要审签状态
  if (['processing', 'signing', 'finished', 'archived'].includes(meeting.value.status)) {
    try {
      const minutesList = await listMinutesRecords(meetingId)
      primaryMinutesSigned.value = Array.isArray(minutesList) && minutesList.some(m => m.status === 'signed')
    } catch {
      primaryMinutesSigned.value = false
    }
  }
})
</script>

<style scoped>
/* ===== Page ===== */
.detail-page {
  min-height: 100vh;
  background: #0a1628;
  padding: 0 0 32px;
}

/* ===== Header ===== */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 24px;
  background: #0e1d38;
  border-bottom: 1px solid rgba(30,92,162,0.45);
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #dee5f2;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Manage dropdown */
.header-right :deep(.el-dropdown .el-button) {
  background: rgba(71,160,235,0.2);
  border-color: #1e5ca2;
  color: #d5e1f5;
}

/* Action buttons (生成摘要/提取要点/问题审查/编写纪要) */
.action-btn {
  background: rgba(71,160,235,0.2) !important;
  border-color: #1e5ca2 !important;
  color: #d5e1f5 !important;
  font-size: 13px;
}
.action-btn:hover {
  background: rgba(71,160,235,0.35) !important;
  border-color: #3990f1 !important;
  color: #dee5f2 !important;
}
.action-btn :deep(.el-icon) {
  color: #dee5f2;
  font-size: 14px;
}

.loading-wrap { padding: 40px 32px; }

/* ===== Body ===== */
.detail-body {
  padding: 14px 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* ===== All cards base ===== */
.info-card,
.participants-card,
.attachments-card,
.agenda-card,
.post-flow-card,
.summary-card,
.keypoints-card,
.checkin-admin-card {
  background: #0e1d38 !important;
  border: 1px solid rgba(30,92,162,0.45) !important;
  border-radius: 6px !important;
}

:deep(.el-card__header) {
  background: #14284b !important;
  border-bottom: 1px solid rgba(30,92,162,0.45) !important;
  padding: 8px 16px;
}

:deep(.el-card__body) {
  padding: 12px 16px;
}

/* ===== Card header ===== */
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #dee5f2;
  font-size: 14px;
  font-weight: 600;
}

.card-header :deep(.el-icon) {
  color: #a4ffe6;
  filter: drop-shadow(0 0 8px rgba(0,234,255,0.64));
}

.header-actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

.header-actions :deep(.el-button--primary) {
  background: rgba(71,160,235,0.2) !important;
  border-color: #1e5ca2 !important;
  color: #d5e1f5 !important;
}
.header-actions :deep(.el-button--warning) {
  background: rgba(217,149,49,0.15) !important;
  border-color: #d99531 !important;
  color: #d99531 !important;
}
.header-actions :deep(.el-button--success) {
  background: rgba(43,255,188,0.12) !important;
  border-color: #2bffbc !important;
  color: #2bffbc !important;
}

/* Badge pill */
.header-badge { margin-left: 2px; }

:deep(.el-badge__content) {
  background: rgba(57,144,241,0.2);
  border: 1px solid #3990f1;
  color: #3990f1;
  box-shadow: none;
}

/* ===== Meeting title area ===== */
.meeting-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.meeting-title {
  font-size: 24px;
  font-weight: 520;
  color: #dee5f2;
  flex: 1;
}

/* Processing status tag override */
:deep(.processing-tag.el-tag) {
  background: rgba(43,255,188,0.1) !important;
  border-color: #2bffbc !important;
  color: #2bffbc !important;
}

/* Type tag */
.type-tag {
  background: rgba(57,144,241,0.12) !important;
  border-color: #1e5ca2 !important;
  color: #3990f1 !important;
}

/* Divider */
:deep(.el-divider) {
  border-top-color: #163153 !important;
  margin: 10px 0;
}

/* ===== Info stat grid ===== */
.info-stat-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0;
  margin: 4px 0;
}

.info-stat {
  padding: 10px 14px;
  border-right: 1px solid rgba(30,92,162,0.25);
}
.info-stat:last-child { border-right: none; }

.info-stat-label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #7f99be;
  margin-bottom: 6px;
}
.info-stat-label :deep(.el-icon) { color: #a4ffe6; filter: drop-shadow(0 0 5px rgba(0,234,255,0.5)); font-size: 14px; }

.info-stat-value {
  font-size: 14px;
  color: #dee5f2;
  font-weight: 500;
}

.duration-bar-wrap {
  margin-top: 5px;
  height: 3px;
  background: rgba(57,144,241,0.15);
  border-radius: 2px;
  overflow: hidden;
  width: 80%;
}
.duration-bar {
  height: 100%;
  width: 60%;
  background: linear-gradient(90deg, #3990f1, #2bffbc);
  border-radius: 2px;
}

.checkin-done-num { font-size: 16px; font-weight: 600; color: #2bffbc; }
.checkin-sep { color: #456484; margin: 0 2px; }
.checkin-total-txt { font-size: 13px; color: #7f99be; }

/* Agenda status tag in stat grid */
.info-stat-value :deep(.el-tag--success) {
  background: rgba(43,255,188,0.1) !important;
  border-color: #2bffbc !important;
  color: #2bffbc !important;
}
.info-stat-value :deep(.el-tag--info) {
  background: rgba(100,120,150,0.1) !important;
  border-color: #456484 !important;
  color: #7f99be !important;
}

/* Description row */
.info-desc-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 14px 4px;
  flex-wrap: wrap;
}
.info-desc-label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #7f99be;
  white-space: nowrap;
}
.info-desc-label :deep(.el-icon) { color: #a4ffe6; font-size: 14px; }
.info-desc-value { flex: 1; font-size: 13px; color: #dee5f2; }
.add-desc-btn { color: #3990f1 !important; font-size: 12px; white-space: nowrap; }

.empty-val {
  color: #456484;
  font-style: italic;
}

/* ===== Code bar ===== */
.meeting-code-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
  padding: 6px 12px;
  background: rgba(57,144,241,0.08);
  border: 1px solid rgba(57,144,241,0.25);
  border-radius: 4px;
  width: fit-content;
}
.code-label { font-size: 13px; color: #7f99be; }
.code-value { font-size: 20px; font-weight: 700; letter-spacing: 4px; color: #3990f1; font-family: 'Courier New', monospace; }
.copy-btn { color: #7f99be !important; }
.copy-btn:hover { color: #3990f1 !important; }

/* ===== Name badge grid ===== */
.participant-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 8px;
  padding: 2px 0;
  align-items: stretch;
}

.name-badge-card {
  position: relative;
  border-radius: 6px;
  border: 1px solid #204082;
  background: #14284b;
  overflow: hidden;
  transition: all 0.2s;
  cursor: default;
  display: flex;
  flex-direction: column;
}

.name-badge-card:hover {
  border-color: #3990f1;
  box-shadow: 0 0 12px rgba(57,144,241,0.2);
}

.badge-glow { display: none; }

.badge-upper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 14px 12px 10px;
  position: relative;
  gap: 4px;
  flex: 1;
}

.badge-name {
  font-size: 20px;
  font-weight: 520;
  color: #dee5f2;
  letter-spacing: 4px;
  text-align: center;
  line-height: 1.3;
}

.badge-seat {
  font-size: 12px;
  font-weight: 600;
  color: #3990f1;
  letter-spacing: 2px;
  margin-bottom: 2px;
}

/* Role tags */
.role-tag {
  font-size: 12px !important;
  padding: 0 6px !important;
}
:deep(.leader-tag.el-tag--warning) {
  background: rgba(217,149,49,0.15) !important;
  border-color: #d99531 !important;
  color: #d99531 !important;
}
:deep(.expert-tag.el-tag--success) {
  background: rgba(43,255,188,0.12) !important;
  border-color: #2bffbc !important;
  color: #2bffbc !important;
}

/* Lower section */
.badge-lower {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 4px;
  padding: 8px 12px;
  border-top: 1px solid #163153;
  background: rgba(0,0,0,0.12);
}

.badge-info-group {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.badge-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.badge-dept {
  font-size: 12px;
  color: #7f99be;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
}

.badge-prof-title {
  font-size: 12px;
  color: #7f99be;
  margin-left: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 60px;
}

/* Visual seat grid */
.seat-visual-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 10px;
}

.seat-visual-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px 8px;
  background: #14284b;
  border: 1px solid #204082;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
  min-height: 72px;

  &:hover { border-color: #3990f1; background: rgba(57,144,241,0.1); }
  &.selected { border-color: #3990f1; background: rgba(57,144,241,0.2); box-shadow: 0 0 10px rgba(57,144,241,0.4); }
  &.empty { opacity: 0.5; }
}

.seat-visual-num {
  font-size: 11px;
  color: #3990f1;
  font-weight: 600;
  letter-spacing: 1px;
}

.seat-visual-name {
  font-size: 14px;
  font-weight: 600;
  color: #dee5f2;
  text-align: center;
  letter-spacing: 2px;
}

.checkin-tag { flex-shrink: 0; }

:deep(.checkin-tag.el-tag--success) {
  background: rgba(0,255,180,0.1) !important;
  border-color: #00ffb4 !important;
  color: #00ffb4 !important;
}
:deep(.checkin-tag.el-tag--info) {
  background: transparent !important;
  border-color: #7f99be !important;
  color: #7f99be !important;
}

/* ===== File rows ===== */
.file-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: #14284b;
  border-radius: 4px;
  border: 1px solid #204082;
  margin-bottom: 6px;
  transition: border-color 0.15s;
}
.file-row:last-child { margin-bottom: 0; }
.file-row:hover { border-color: #3990f1; }

.attach-empty-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 4px;
  color: #5e8aad;
  font-size: 13px;
}
.attach-archive-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #7f99be;
  background: rgba(250,173,20,0.06);
  border: 1px solid rgba(250,173,20,0.15);
  border-radius: 6px;
  padding: 7px 12px;
  margin-bottom: 10px;
}
.attach-archive-check {
  flex-shrink: 0;
}
.attach-archive-footer {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255,255,255,0.06);
}
.attach-archive-count {
  font-size: 12px;
  color: #7f99be;
}

.file-icon {
  font-size: 18px;
  color: #3990f1;
  flex-shrink: 0;
}
.file-icon-image { color: #2bffbc !important; }

.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.file-name { font-size: 13px; color: #dee5f2; }
.file-meta { font-size: 12px; color: #7f99be; }

.file-row :deep(.el-button--success) {
  background: rgba(43,255,188,0.1) !important;
  border-color: rgba(43,255,188,0.4) !important;
  color: #2bffbc !important;
}
.file-row :deep(.el-button--primary) {
  background: rgba(71,160,235,0.15) !important;
  border-color: #1e5ca2 !important;
  color: #d5e1f5 !important;
}

/* ===== Post-flow ===== */
.post-flow-steps {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.pf-step {
  flex: 1;
  min-width: 140px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 12px 10px;
  border-radius: 6px;
  border: 1px solid #204082;
  background: #14284b;
  transition: all 0.2s;
}
.pf-step.done {
  border-color: rgba(43,255,188,0.4);
  background: rgba(43,255,188,0.04);
}

.pf-step-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(57,144,241,0.15);
  border: 1px solid #3990f1;
  color: #3990f1;
  font-weight: 700;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
  flex-shrink: 0;
}
.pf-step.done .pf-step-num {
  background: rgba(43,255,188,0.15);
  border-color: #2bffbc;
  color: #2bffbc;
}

.pf-step-title {
  font-size: 14px;
  font-weight: 520;
  color: #dee5f2;
  margin-bottom: 4px;
}

.pf-step-desc {
  font-size: 12px;
  color: #7f99be;
  line-height: 1.5;
  margin-bottom: 4px;
}

.pf-step-tag { margin-top: 6px; }

.pf-step :deep(.el-button) {
  background: rgba(71,160,235,0.15) !important;
  border-color: #1e5ca2 !important;
  color: #d5e1f5 !important;
  font-size: 12px;
}
.pf-step :deep(.el-button:hover) {
  background: rgba(71,160,235,0.3) !important;
  border-color: #3990f1 !important;
}
.pf-step :deep(.el-tag--info) {
  background: transparent !important;
  border-color: #456484 !important;
  color: #456484 !important;
}
.pf-step :deep(.el-tag--success) {
  background: rgba(43,255,188,0.1) !important;
  border-color: #2bffbc !important;
  color: #2bffbc !important;
}

/* ===== Summary ===== */
.summary-text {
  font-size: 14px;
  line-height: 1.8;
  color: #dee5f2;
  white-space: pre-wrap;
}

/* ===== Rendered HTML ===== */
.rendered-html { color: #dee5f2 !important; line-height: 1.7; }
.rendered-html :deep(h1),
.rendered-html :deep(h2),
.rendered-html :deep(h3) { color: #3990f1 !important; margin: 12px 0 6px; }
.rendered-html :deep(p),
.rendered-html :deep(li) { color: #dee5f2 !important; }
.rendered-html :deep(ul),
.rendered-html :deep(ol) { padding-left: 20px; }

/* ===== Keypoints ===== */
.kp-list { display: flex; flex-direction: column; gap: 8px; }
.kp-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 4px;
  background: #14284b;
  border-left: 3px solid #1e5ca2;
}
.kp-item.kp-high { border-left-color: #f56c6c; }
.kp-item.kp-medium { border-left-color: #d99531; }
.kp-item.kp-low { border-left-color: #2bffbc; }
.kp-badge {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(57,144,241,0.15);
  color: #3990f1;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}
.kp-body { flex: 1; }
.kp-title { font-size: 13px; font-weight: 600; color: #dee5f2; margin-bottom: 3px; }
.kp-content { font-size: 12px; color: #7f99be; line-height: 1.6; }

/* ===== Edit mode ===== */
.loading-inner { padding: 12px 0; }
.participant-edit-list { display: flex; flex-direction: column; gap: 0; }
.edit-tip {
  color: #7f99be;
  font-size: 13px;
  margin: 0 0 10px;
  padding: 5px 10px;
  background: rgba(57,144,241,0.06);
  border-radius: 4px;
  border-left: 3px solid rgba(57,144,241,0.4);
}
.participant-edit-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: #14284b;
  border: 1px solid rgba(30,92,162,0.45);
  border-radius: 4px;
  margin-bottom: 6px;
  transition: all 0.2s;
}
.participant-edit-row:hover {
  background: rgba(57,144,241,0.06);
  border-color: #3990f1;
}
.drag-handle {
  cursor: grab;
  color: #7f99be;
  font-size: 16px;
  display: flex;
  align-items: center;
  padding: 4px;
  border-radius: 4px;
  transition: color 0.2s;
}
.drag-handle:hover { color: #3990f1; }
.drag-handle:active { cursor: grabbing; }
.edit-index {
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(57,144,241,0.15);
  color: #3990f1;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}
.edit-name { font-size: 14px; font-weight: 600; color: #dee5f2; letter-spacing: 1px; min-width: 60px; }
.edit-dept { font-size: 13px; color: #7f99be; flex: 1; }
.drag-ghost {
  opacity: 0.4;
  background: rgba(57,144,241,0.1) !important;
  border-color: rgba(57,144,241,0.5) !important;
}

/* ===== Preview ===== */
.preview-body { min-height: 400px; display: flex; align-items: center; justify-content: center; }
.preview-iframe { width: 100%; height: 75vh; border: none; }
.preview-image { max-width: 100%; max-height: 75vh; object-fit: contain; }
.preview-unsupported { color: #7f99be; font-size: 13px; }

/* ===== Dark dialog overrides ===== */
:deep(.el-overlay-dialog .el-dialog) {
  background: #0a1828;
  border: 1px solid rgba(30,92,162,0.55);
  border-radius: 6px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.6);
}

:deep(.el-overlay-dialog .el-dialog__header) {
  background: #0d1e35;
  border-bottom: 1px solid rgba(30,92,162,0.4);
  padding: 12px 18px;
  margin-right: 0;
}

:deep(.el-overlay-dialog .el-dialog__title) {
  color: #dee5f2;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 1px;
}

:deep(.el-overlay-dialog .el-dialog__headerbtn) {
  top: 12px;
  right: 14px;
  .el-icon {
    color: #7f99be;
    &:hover { color: #dee5f2; }
  }
}

:deep(.el-overlay-dialog .el-dialog__body) {
  background: #0a1828;
  color: #dee5f2;
  padding: 18px 20px;
}

:deep(.el-overlay-dialog .el-dialog__footer) {
  background: #0a1828;
  border-top: 1px solid rgba(30,92,162,0.4);
  padding: 10px 20px;
}

/* Form elements inside dark dialogs */
:deep(.el-overlay-dialog .el-form-item__label) {
  color: #dee5f2;
}

:deep(.el-overlay-dialog .el-select .el-input__wrapper) {
  background: #14284b;
  border: 1px solid #204082;
  box-shadow: none;
  &:hover, &.is-focus { border-color: #3990f1; }
}

:deep(.el-overlay-dialog .el-select .el-input__inner) {
  color: #dee5f2;
  &::placeholder { color: #456484; }
}

:deep(.el-overlay-dialog .el-button--default) {
  background: rgba(71,160,235,0.15);
  border-color: #1e5ca2;
  color: #d5e1f5;
  &:hover { background: rgba(71,160,235,0.3); border-color: #3990f1; }
}

:deep(.el-overlay-dialog .el-button--primary) {
  background: rgba(57,144,241,0.25);
  border-color: #3990f1;
  color: #dee5f2;
  &:hover { background: rgba(57,144,241,0.5); }
}
</style>
