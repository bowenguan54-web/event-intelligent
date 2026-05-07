<template>
  <div class="meeting-live">
    <!-- 左栏：会议信息 + AI 问答 -->
    <div class="panel-left" :class="{ collapsed: leftPanelCollapsed }">
      <div v-if="!leftPanelCollapsed" class="panel-left-inner">
      <!-- AI 辅助问答 -->
      <div class="ai-qa-area">
        <el-divider content-position="left">AI 智能问答</el-divider>
        <div class="qa-messages" ref="qaMessagesRef">
          <div v-for="msg in qaMessages" :key="msg.id" :class="['qa-bubble', msg.role]">
            <div class="bubble-content">{{ msg.content }}</div>
            <div v-if="msg.sources?.length" class="bubble-sources">
              <span v-for="s in msg.sources" :key="s.id" class="source-link">📎 {{ s.title }}</span>
            </div>
          </div>
        </div>
        <div class="qa-input">
          <el-input
            v-model="qaInput"
            placeholder="输入问题或点击麦克风语音提问..."
            :disabled="qaLoading"
            @keyup.enter="sendQuestion"
          >
            <template #suffix>
              <el-icon v-if="qaLoading" class="is-loading"><Loading /></el-icon>
              <el-icon v-else class="mic-btn" @click="toggleVoiceInput"><Microphone /></el-icon>
            </template>
          </el-input>
        </div>
      </div>
      </div><!-- /panel-left-inner -->

      <!-- 折叠/展开按钮 -->
      <div class="panel-toggle-btn" @click="leftPanelCollapsed = !leftPanelCollapsed">
        <el-icon v-if="leftPanelCollapsed"><ArrowRight /></el-icon>
        <el-icon v-else><ArrowLeft /></el-icon>
      </div>
    </div>

    <!-- 中栏：实时转写 -->
    <div class="panel-center">
      <!-- 控制栏 -->
      <div class="control-bar">
        <div class="control-left">
          <el-button-group>
            <el-button
              :type="meetingStore.recordingStatus === 'recording' ? 'danger' : 'primary'"
              @click="handleRecord"
            >
              <el-icon><VideoPlay v-if="meetingStore.recordingStatus !== 'recording'" /><VideoPause v-else /></el-icon>
              {{ meetingStore.recordingStatus === 'recording' ? '暂停' : (meetingStore.recordingStatus === 'paused' ? '继续录音' : '开始录音') }}
            </el-button>
            <el-button
              type="danger"
              :disabled="meetingStore.recordingStatus === 'idle'"
              @click="handleStop"
            >
              <el-icon><CircleClose /></el-icon>停止
            </el-button>
          </el-button-group>

          <span class="recording-timer">
            <span :class="['status-dot', meetingStore.recordingStatus]" />
            {{ formatDuration(meetingStore.recordingDuration) }}
          </span>

          <!-- 禁忌词警告 -->
          <el-badge v-if="sensitiveCount > 0" :value="sensitiveCount" class="sensitive-badge">
            <el-button type="danger" link size="small" @click="showSensitiveLog = true">
              <el-icon><Warning /></el-icon>敏感词
            </el-button>
          </el-badge>
        </div>

        <div class="control-right">
          <el-button
            v-if="isOrganizer"
            type="danger"
            size="small"
            :loading="ending"
            @click="handleEndMeeting"
            style="margin-right:8px"
          >下一步</el-button>
          <el-tag :type="meetingStore.wsConnected ? 'success' : 'danger'" size="small">
            {{ meetingStore.wsConnected ? '已连接' : '未连接' }}
          </el-tag>
        </div>
      </div>

      <!-- 会议记录列表（逐字输出模式） -->
      <div class="transcript-list" ref="transcriptListRef" @scroll="onTranscriptScroll">
        <!-- 已完成的行（可编辑、可标注） -->
        <div
          v-for="line in simulatedLines"
          :key="line.id"
          :data-line-id="line.id"
          :class="['transcript-card', 'completed-line', { 'marked-line': line.category, 'mark-hover': markMode && activeCategory, 'locate-highlight': highlightedLineId === line.id }]"
          :style="line.category ? { borderLeft: `3px solid ${getCatColor(line.category)}`, background: getCatBg(line.category) } : {}"
          @click="markLine(line)"
        >
          <div v-if="line.category" class="line-mark-tag">
            <span class="cat-label" :style="{ color: getCatColor(line.category) }">{{ getCatLabel(line.category) }}</span>
            <span class="cat-remove" @click.stop="removeCategory(line)">×</span>
          </div>
          <div
            class="card-text"
            contenteditable="true"
            @blur="handleLineEdit(line, $event)"
            @mouseup.stop="handleTextSelect(line, $event)"
          >{{ line.text }}</div>

          <!-- 局部标注高亮 -->
          <div v-if="getLineAnnotations(line.id).length" class="line-partial-marks">
            <span v-for="ann in getLineAnnotations(line.id)" :key="ann.id" class="partial-mark" :style="{ background: getCatBg(ann.category), color: getCatColor(ann.category), border: `1px solid ${getCatColor(ann.category)}` }">
              {{ ann.text }} <span class="cat-remove" @click.stop="removeCategory(ann)">×</span>
            </span>
          </div>
        </div>

        <!-- 当前正在逐字输出的行 -->
        <div v-if="activeTypingText" class="transcript-card active-typing-line">
          <div class="card-text typing-text">{{ activeTypingText }}<span class="typing-cursor">|</span></div>
        </div>

        <el-empty v-if="simulatedLines.length === 0 && !activeTypingText && meetingStore.recordingStatus === 'idle'" description="等待录音开始.." />
      </div>
    </div>

    <!-- 右栏：辅助工具 -->
    <div class="panel-right">
      <el-tabs v-model="rightTab" class="right-tabs">
        <!-- 问题记录 -->
        <el-tab-pane label="🔴 问题记录" name="issues">
          <div class="issues-panel">
            <div class="issue-input-row">
              <el-input v-model="newIssueContent" placeholder="输入会议中发现的问题..." :rows="2" type="textarea" resize="none" />
              <el-button type="danger" size="small" :disabled="!newIssueContent.trim()" :loading="addingIssue" @click="addIssue" style="margin-top:8px;width:100%">
                <el-icon><Plus /></el-icon>记录问题
              </el-button>
            </div>
            <el-divider style="margin:10px 0" />
            <div class="issue-list">
              <div v-for="issue in meetingIssues" :key="issue.id" class="issue-item" :class="issue.status">
                <!-- 编辑模式 -->
                <template v-if="editingIssueId === issue.id">
                  <el-input v-model="editingIssueContent" type="textarea" :rows="2" size="small" />
                  <div class="issue-edit-actions">
                    <el-button type="primary" size="small" @click="saveEditIssue(issue)">保存</el-button>
                    <el-button size="small" @click="editingIssueId = null">取消</el-button>
                  </div>
                </template>
                <!-- 展示模式 -->
                <template v-else>
                  <div class="issue-content">{{ issue.content }}</div>
                  <div v-if="issue.response" class="issue-response">
                    <el-icon style="font-size:14px;margin-right:3px"><ChatLineRound /></el-icon>{{ issue.response }}
                  </div>
                  <div class="issue-meta">
                    <span class="issue-reporter">{{ issue.reporter_name }}</span>
                    <span class="issue-time">{{ formatIssueTime(issue.created_at) }}</span>
                    <el-tag :type="issueStatusType(issue.status)" size="small">{{ issueStatusLabel(issue.status) }}</el-tag>
                  </div>
                  <!-- 状态操作 -->
                  <div class="issue-actions">
                    <el-dropdown trigger="click" @command="(cmd) => changeIssueStatus(issue, cmd)">
                      <el-button link size="small" type="primary">更改状态</el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item command="explained">📢 解释</el-dropdown-item>
                          <el-dropdown-item command="adopted">采纳</el-dropdown-item>
                          <el-dropdown-item command="adopted_resolved" divided>采纳 已解决</el-dropdown-item>
                          <el-dropdown-item command="adopted_unresolved">采纳 未解决</el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                    <el-button link size="small" @click="startEditIssue(issue)"><el-icon><Edit /></el-icon>编辑</el-button>
                    <el-button link size="small" @click="openReplyIssue(issue)"><el-icon><ChatLineRound /></el-icon>回复</el-button>
                    <el-button link type="danger" size="small" @click="deleteIssue(issue)"><el-icon><Delete /></el-icon></el-button>
                  </div>
                </template>
              </div>
              <el-empty v-if="meetingIssues.length === 0" description="暂无问题记录" :image-size="40" />
            </div>
          </div>
          <!-- 回复弹窗 -->
          <el-dialog v-model="showReplyDialog" title="添加回复/说明" width="420px" :close-on-click-modal="false">
            <el-input v-model="replyContent" type="textarea" :rows="4" placeholder="请输入回复内容.." maxlength="300" show-word-limit />
            <template #footer>
              <el-button @click="showReplyDialog = false">取消</el-button>
              <el-button type="primary" @click="submitReply" :loading="submittingReply">确认</el-button>
            </template>
          </el-dialog>
        </el-tab-pane>

        <!-- 分类标注 -->
        <el-tab-pane label="分类标注" name="category">
          <div class="category-panel">
            <!-- 分类按钮 -->
            <div class="cat-btn-group">
              <button
                v-for="cat in categoryDefs"
                :key="cat.key"
                :class="['cat-btn', { active: activeCategory === cat.key }]"
                :style="{ '--cat-color': cat.color, '--cat-bg': cat.bg }"
                @click="toggleActiveCategory(cat.key)"
              >{{ cat.label }}</button>
            </div>

            <!-- 标注模式开关 -->
            <div :class="['mark-mode-toggle', { active: markMode }]" @click="markMode = !markMode">
              <el-icon v-if="markMode"><EditPen /></el-icon>
              <el-icon v-else><Edit /></el-icon>
              <span>{{ markMode ? '标注模式已开启' : '开启标注模式' }}</span>
            </div>
            <p v-if="markMode" class="mark-mode-tip">
              点击记录行整行标注，或<strong>选中文字</strong>后点击分类按钮进行局部标注
               </p>

            <el-divider style="margin: 10px 0" />

            <!-- 已标注条目列表 -->
            <div class="marked-list">
              <template v-for="cat in categoryDefs" :key="cat.key">
                <div v-if="markedByCat[cat.key]?.length" class="marked-group">
                  <div class="group-header" :style="{ color: cat.color, borderLeft: `3px solid ${cat.color}` }">
                    {{ cat.label }}&nbsp;<span class="group-count">({{ markedByCat[cat.key].length }})</span>
                  </div>
                  <div v-for="item in markedByCat[cat.key]" :key="item.id" class="marked-item">
                    <span class="item-text">{{ item.text }}</span>
                    <span class="item-del" @click="removeCategory(item)">×</span>
                  </div>
                </div>
              </template>
              <el-empty v-if="!hasMarkedItems" description="暂无标注记录" :image-size="50" />
            </div>
          </div>
        </el-tab-pane>

        <!-- 摘要总结 -->
        <el-tab-pane label="📝 摘要总结" name="ai-summary">
          <div class="summary-panel-wrap">
            <!-- 等待状态 -->
            <div v-if="meetingStore.recordingStatus !== 'idle' || simulatedLines.length === 0" class="summary-waiting">
              <el-icon :size="38" color="#3a5f80"><Clock /></el-icon>
              <div class="sw-title">等待会议记录完成</div>
              <div class="sw-desc">录音结束后可一键生成摘要与要点</div>
              <div class="sw-status">
                <template v-if="meetingStore.recordingStatus === 'recording'">
                  <span class="status-dot recording" /> 录音进行中，已记录 {{ simulatedLines.length }} 条                </template>
                <template v-else-if="meetingStore.recordingStatus === 'paused'">
                  <span class="status-dot paused" /> 录音已暂停
                </template>
                <template v-else>
                  <span class="status-dot idle" /> 尚未开始录音
                </template>
              </div>
            </div>

            <!-- 可生成状态 -->
            <div v-else class="summary-ready">
              <div class="summary-ready-tip">
                <el-icon color="#67c23a"><CircleCheckFilled /></el-icon>
                <span>会议记录完成，共 {{ simulatedLines.length }} 条</span>
              </div>
              <el-button type="primary" :loading="generatingSummary" class="gen-btn" @click="generateSummaryNow">
                <el-icon><MagicStick /></el-icon>
                {{ latestSummary ? '重新生成摘要' : '生成 AI 摘要与要点' }}
              </el-button>
              <template v-if="latestSummary">
                <div class="ref-section-title">📝 会议摘要</div>
                <div class="ref-text">{{ latestSummary }}</div>
              </template>
              <template v-if="keypoints.length > 0">
                <div class="ref-section-title" style="margin-top:16px">📌关键要点</div>
                <div v-for="kp in keypoints" :key="kp.id" class="kp-mini">
                  <el-tag :type="importanceType(kp.importance)" size="small" effect="plain">{{ importanceLabel(kp.importance) }}</el-tag>
                  <span class="kp-mini-text">{{ kp.title }}</span>
                </div>
              </template>
              <el-button v-if="latestSummary && keypoints.length === 0" type="warning" size="small"
                class="gen-btn" style="margin-top:10px" :loading="extracting" @click="extractKeypoints">
                <el-icon><Star /></el-icon>提取关键要点
              </el-button>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>

      <el-button type="warning" class="keypoint-btn" @click="keypointDrawer = true">
        <el-icon><Star /></el-icon>查看要点详情
      </el-button>
    </div>

    <!-- 要点抽屉 -->
    <el-drawer v-model="keypointDrawer" title="会议要点" size="400px">
      <div class="keypoint-controls">
        <el-select v-model="keypointStrategy" style="width: 160px" size="small">
          <el-option label="按议题聚合" value="by_topic" />
          <el-option label="按发言人聚合" value="by_speaker" />
          <el-option label="按时间线排列" value="by_timeline" />
        </el-select>
        <el-button type="primary" size="small" :loading="extracting" @click="extractKeypoints">
          自动提取要点
        </el-button>
      </div>

      <div class="keypoint-list">
        <div v-for="kp in keypoints" :key="kp.id" class="keypoint-card">
          <div class="kp-header">
            <el-tag :type="importanceType(kp.importance)" size="small">{{ importanceLabel(kp.importance) }}</el-tag>
            <span class="kp-title">{{ kp.title }}</span>
          </div>
          <p class="kp-content">{{ kp.content }}</p>
          <div class="kp-actions">
            <el-button type="primary" link size="small" @click="locateOriginalText(kp)">定位原文</el-button>
            <el-button type="danger" link size="small">删除</el-button>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="keypointDrawer = false">关闭</el-button>
        <el-dropdown split-button type="primary" @click="exportKeypoints('md')">
          导出 Markdown
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="exportKeypoints('pdf')">导出 PDF</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </template>
    </el-drawer>

    <!-- 敏感词日志弹窗 -->
    <el-dialog v-model="showSensitiveLog" title="敏感词屏蔽日志" width="500px">
      <el-table :data="sensitiveLog">
        <el-table-column prop="time" label="时间" width="120" />
        <el-table-column prop="speaker" label="发言人" width="80" />
        <el-table-column prop="content" label="屏蔽内容" />
      </el-table>
    </el-dialog>

    <!-- 文件预览弹窗 -->
    <el-dialog v-model="attPreviewVisible" :title="attPreviewTitle" width="80%" top="5vh" destroy-on-close>
      <div class="preview-body">
        <iframe v-if="attPreviewType === 'pdf'" :src="attPreviewUrl" class="preview-iframe" />
        <img v-else-if="attPreviewType === 'image'" :src="attPreviewUrl" class="preview-image" />
        <div v-else class="preview-unsupported">暂不支持该格式在线预览，请下载查看</div>
      </div>
    </el-dialog>

    <el-dialog
      v-model="nextStepDialog"
      width="540px"
      :show-close="true"
      destroy-on-close
      class="next-step-dialog"
    >
      <div class="next-step-cards">
        <div
          class="next-step-card"
          :class="{ active: nextStepValue === 'issues' }"
          @click="nextStepValue = 'issues'; confirmNextStep()"
        >
          <div class="next-step-card-icon">🔍</div>
          <div class="next-step-card-info">
            <div class="next-step-card-title">问题审查</div>
            <div class="next-step-card-desc">整理会议中记录的问题，进行归档与跟踪</div>
          </div>
          <el-icon class="next-step-card-arrow"><ArrowRight /></el-icon>
        </div>
        <div
          class="next-step-card"
          :class="{ active: nextStepValue === 'minutes' }"
          @click="nextStepValue = 'minutes'; confirmNextStep()"
        >
          <div class="next-step-card-icon">📝</div>
          <div class="next-step-card-info">
            <div class="next-step-card-title">会议纪要</div>
            <div class="next-step-card-desc">编写并发布会议纪要，完成审签流程</div>
          </div>
          <el-icon class="next-step-card-arrow"><ArrowRight /></el-icon>
        </div>
      </div>
      <div class="next-step-dialog-cancel">
        <el-button text @click="nextStepDialog = false">暂不操作，继续会议</el-button>
      </div>
    </el-dialog>
    <!-- 文字选中标注浮层工具栏 -->
    <Teleport to="body">
      <div v-if="selPopover.visible" class="sel-anno-toolbar" :style="{ left: selPopover.x + 'px', top: selPopover.y + 'px' }" @click.stop>
        <span class="sel-anno-tip">标注选中文字：</span>
        <button v-for="cat in categoryDefs" :key="cat.key" class="sel-anno-btn" :style="{ background: cat.bg, color: cat.color, borderColor: cat.color }" @click="applySelectionAnnotation(cat.key)">
          {{ cat.label }}
        </button>
        <button class="sel-anno-btn-issue" @click="addSelectionAsIssue">🔴 记录问题</button>
        <button class="sel-anno-close" @click="hideSelPopover">×</button>
      </div>
    </Teleport>

    <!-- AI 自动弹出问题提示 -->
    <Teleport to="body">
      <div v-if="aiIssuePop.visible" class="ai-issue-popup" @click.stop>
        <div class="ai-issue-popup-header">
          <span class="ai-issue-popup-icon">🤖</span>
          <span class="ai-issue-popup-title">AI 发现可能问题</span>
          <button class="ai-issue-popup-close" @click="aiIssuePop.visible = false">×</button>
        </div>
        <div class="ai-issue-popup-content">{{ aiIssuePop.content }}</div>
        <div class="ai-issue-popup-actions">
          <button class="ai-issue-confirm" @click="addAiSuggestedIssue">记录此问题</button>
          <button class="ai-issue-dismiss" @click="aiIssuePop.visible = false">忽略</button>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMeetingStore } from '@/stores/meeting'
import { useUserStore } from '@/stores/user'
import { validateTranscripts, generateKeypoints, getAudioSegment, aiQA, getMeetingById, getParticipantsStatus, endMeeting, getMeetingRecordText, getAttachments, getMeetingIssues, createMeetingIssue, updateMeetingIssue, deleteMeetingIssue, createTranscript, updateTranscript } from '@/api/meeting'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import { ArrowLeft, ArrowRight, ChatLineRound, Edit, CircleCheck, Delete } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const meetingStore = useMeetingStore()
const meetingId = route.params.id

// 会议信息
const meetingInfo = ref({
  title: '',
  time: '',
  location: '',
})
const meetingCreatorId = ref(null)

const isOrganizer = computed(() => {
  return meetingCreatorId.value && userStore.userInfo?.id === meetingCreatorId.value
})

const ending = ref(false)
const nextStepDialog = ref(false)
const nextStepValue = ref('issues')

const participants = ref([])

// 左侧面板折叠
const leftPanelCollapsed = ref(false)

// 会议问题记录
const meetingIssues = ref([])
const newIssueContent = ref('')
const addingIssue = ref(false)
const editingIssueId = ref(null)
const editingIssueContent = ref('')
const showReplyDialog = ref(false)
const replyingIssue = ref(null)
const replyContent = ref('')
const submittingReply = ref(false)

function issueStatusLabel(status) {
  const map = { open: '待处理', explained: '已解释', adopted: '已采纳', adopted_resolved: '采纳·已解决', adopted_unresolved: '采纳·未解决' }
  return map[status] || status
}
function issueStatusType(status) {
  const map = { open: 'danger', explained: 'warning', adopted: 'success', adopted_resolved: 'success', adopted_unresolved: 'info' }
  return map[status] || 'info'
}
function startEditIssue(issue) {
  editingIssueId.value = issue.id
  editingIssueContent.value = issue.content
}
async function saveEditIssue(issue) {
  if (!editingIssueContent.value.trim()) return
  try {
    await updateMeetingIssue(meetingId, issue.id, { content: editingIssueContent.value })
    editingIssueId.value = null
    await loadIssues()
  } catch { ElMessage.error('编辑失败') }
}
async function changeIssueStatus(issue, status) {
  try {
    await updateMeetingIssue(meetingId, issue.id, { status })
    await loadIssues()
  } catch {}
}
function openReplyIssue(issue) {
  replyingIssue.value = issue
  replyContent.value = issue.response || ''
  showReplyDialog.value = true
}
async function submitReply() {
  if (!replyContent.value.trim()) return
  submittingReply.value = true
  try {
    await updateMeetingIssue(meetingId, replyingIssue.value.id, { response: replyContent.value })
    showReplyDialog.value = false
    await loadIssues()
  } catch { ElMessage.error('回复失败') } finally {
    submittingReply.value = false
  }
}

// 会议材料
const meetingAttachments = ref([])

function downloadAttachment(att) {
  const url = `/api/meeting/attachment/${att.id}/download`
  const a = document.createElement('a')
  a.href = url
  a.download = att.filename || 'file'
  a.click()
}

// 文件预览
const attPreviewVisible = ref(false)
const attPreviewUrl = ref('')
const attPreviewTitle = ref('')
const attPreviewType = ref('')

function canPreviewAtt(att) {
  const name = (att.filename || '').toLowerCase()
  const type = (att.file_type || '').toLowerCase()
  return type.startsWith('image/') || type === 'application/pdf'
    || name.endsWith('.pdf') || /\.(jpg|jpeg|png|gif|webp|bmp|svg)$/.test(name)
}

function previewAttachment(att) {
  const name = (att.filename || '').toLowerCase()
  const type = (att.file_type || '').toLowerCase()
  attPreviewUrl.value = `/api/meeting/attachment/${att.id}/download`
  attPreviewTitle.value = att.filename
  if (type === 'application/pdf' || name.endsWith('.pdf')) {
    attPreviewType.value = 'pdf'
  } else if (type.startsWith('image/') || /\.(jpg|jpeg|png|gif|webp|bmp|svg)$/.test(name)) {
    attPreviewType.value = 'image'
  } else {
    attPreviewType.value = 'other'
  }
  attPreviewVisible.value = true
}

// 录音状态 — 统一使用 store 中的状态，不再维护本地副本
// 通过 meetingStore.recordingStatus 访问（模板中同样直接引用）

// AI 问答
const qaInput = ref('')
const qaMessages = ref([
  { id: 1, role: 'system', content: '您好！我是AI 助手，可以帮您检索系统数据和历史会议信息。请问有什么需要了解的？', sources: [] },
])
const qaMessagesRef = ref(null)

// 右栏标签
const rightTab = ref('issues')
const validating = ref(false)
const validationResults = ref([])

// 分类
const categories = ref([
  { name: '决策事项', type: 'danger', count: 0 },
  { name: '讨论事项', type: 'warning', count: 0 },
  { name: '通报事项', type: 'primary', count: 0 },
  { name: '其他', type: 'info', count: 0 },
])

// 要点
const keypointDrawer = ref(false)
const keypointStrategy = ref('by_topic')
const extracting = ref(false)
const keypoints = ref([])

// 摘要
const summaryExpanded = ref('')
const latestSummary = ref('')
const generatingSummary = ref(false)

// 敏感词
const sensitiveCount = ref(0)
const showSensitiveLog = ref(false)
const sensitiveLog = ref([])

// 音频播放
const audioPlayerRef = ref(null)

const transcriptListRef = ref(null)
// 定位原文高亮
const highlightedLineId = ref(null)

// 智能滚动：用户手动滚动时暂停自动滚动
const userHasScrolled = ref(false)

function onTranscriptScroll() {
  const el = transcriptListRef.value
  if (!el) return
  // 距离底部小于 60px 认为在底部，恢复自动滚动
  const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 60
  userHasScrolled.value = !atBottom
}

function scrollToBottom() {
  if (userHasScrolled.value) return
  nextTick(() => {
    if (transcriptListRef.value) {
      transcriptListRef.value.scrollTop = transcriptListRef.value.scrollHeight
    }
  })
}

// 录音模拟（逐字输出文件内容）
const simulatedLines = ref([])
const activeTypingText = ref('')
let typingInterval = null
let fileLines = []
let currentLineIdx = 0
let currentCharIdx = 0
let lineIdCounter = 1

// 分类标注
const markMode = ref(false)
const activeCategory = ref(null)
const selectionAnnotations = ref([])   // 局部选中标注: { id, lineId, text, category }
let selAnnotationId = 1

// 文字选中标注浮层
// selPopover: { visible, text, x, y, lineId }
const selPopover = ref({ visible: false, text: '', x: 0, y: 0, lineId: null })

// AI 自动弹出问题
const aiIssuePop = ref({ visible: false, content: '' })
let aiIssueScanTimer = null
let issuesPollTimer = null
let lastScanCount = 0

function hideSelPopover() {
  selPopover.value.visible = false
  window.getSelection()?.removeAllRanges()
}

function applySelectionAnnotation(catKey) {
  if (!selPopover.value.text) return
  selectionAnnotations.value.push({
    id: selAnnotationId++,
    lineId: selPopover.value.lineId,
    text: selPopover.value.text,
    category: catKey,
    isPartial: true,
  })
  window.getSelection()?.removeAllRanges()
  selPopover.value.visible = false
  rightTab.value = 'category'
  ElMessage.success('已标注选中文字')
}

function addSelectionAsIssue() {
  if (!selPopover.value.text) return
  newIssueContent.value = selPopover.value.text
  rightTab.value = 'issues'
  selPopover.value.visible = false
  window.getSelection()?.removeAllRanges()
  ElMessage.info('已填充到问题记录，点击“记录问题”确认')
}

// AI 自动扫描问题
function startAIIssueScan() {
  if (aiIssueScanTimer) return
  aiIssueScanTimer = setInterval(() => {
    const lines = simulatedLines.value
    if (lines.length - lastScanCount >= 10 && lastScanCount < lines.length) {
      const newLines = lines.slice(lastScanCount)
      lastScanCount = lines.length
      tryExtractIssue(newLines.map(l => l.text).join('、'))
    }
  }, 25000)
}

function tryExtractIssue(text) {
  if (!text || text.length < 20) return
  // 基于转写内容简单模拟 AI 问题提取
  const issuePatterns = [
    /存在([^。！？]{4,30})问题/,
    /([^。！？]{4,30})没有[解决完成]/,
    /([^。！？]{4,30})需要进一步'/,
    /([^。！？]{4,30})不符合'/,
    /([^。！？]{4,30})质疑/,
  ]
  for (const pattern of issuePatterns) {
    const match = text.match(pattern)
    if (match) {
      aiIssuePop.value = {
        visible: true,
        content: match[0].length > 60 ? match[0].slice(0, 60) + '…' : match[0],
      }
      return
    }
  }
}

async function addAiSuggestedIssue() {
  const content = aiIssuePop.value.content
  aiIssuePop.value.visible = false
  if (!content) return
  try {
    await createMeetingIssue(meetingId, {
      content: `[AI识别] ${content}`,
      reporter_name: 'AI助手',
    })
    await loadIssues()
    rightTab.value = 'issues'
    ElMessage.success('问题已记录')
  } catch { ElMessage.error('记录失败') }
}

// 关闭选择工具栏 
function onDocMousedown(e) {
  if (!e.target.closest('.sel-anno-toolbar') && !e.target.closest('.transcript-card')) {
    selPopover.value.visible = false
  }
  if (!e.target.closest('.ai-issue-popup')) {
    // 点击其他地方不自动关闭 AI 弹窗（用户需点忽略或确认）
  }
}
const categoryDefs = [
  { key: 'key_point', label: '关键讨论点', color: '#409eff', bg: '#ecf5ff' },
  { key: 'todo', label: '待办事项', color: '#e6a23c', bg: '#fdf6ec' },
  { key: 'decision', label: '决议事项', color: '#f56c6c', bg: '#fef0f0' },
  { key: 'notice', label: '重要说明', color: '#67c23a', bg: '#f0f9eb' },
  { key: 'other', label: '其他', color: '#909399', bg: '#f4f4f5' },
]

const markedByCat = computed(() => {
  const result = {}
  categoryDefs.forEach(cat => { result[cat.key] = [] })
  simulatedLines.value.forEach(line => {
    if (line.category && result[line.category]) {
      result[line.category].push(line)
    }
  })
  // 合并局部标注
  selectionAnnotations.value.forEach(ann => {
    if (result[ann.category]) {
      result[ann.category].push(ann)
    }
  })
  return result
})

const hasMarkedItems = computed(() =>
  categoryDefs.some(cat => markedByCat.value[cat.key]?.length > 0)
)

// 生命周期
onMounted(async () => {
  meetingStore.connectWebSocket(meetingId)
  try {
    const [meeting, pList] = await Promise.all([
      getMeetingById(meetingId),
      getParticipantsStatus(meetingId)
    ])
    meetingInfo.value = {
      title: meeting.title || '会议进行中',
      time: meeting.start_time
        ? `${dayjs(meeting.start_time).format('MM月DD日 HH:mm')} - ${dayjs(meeting.end_time).format('HH:mm')}`
        : '--',
      location: meeting.location || '--',
    }
    meetingCreatorId.value = meeting.creator_id
    participants.value = pList.map(p => ({ ...p, name: p.real_name }))
    // 加载会议材料
    try {
      meetingAttachments.value = await getAttachments(meetingId) || []
    } catch {
      meetingAttachments.value = []
    }
    // 加载问题记录
    await loadIssues()
    issuesPollTimer = setInterval(loadIssues, 5000)
    // 启动全局选择监听与 AI 扫描
    document.addEventListener('mousedown', onDocMousedown)
    startAIIssueScan()
  } catch (e) {
    console.error('加载会议信息失败:', e)
  }
})

onUnmounted(() => {
  meetingStore.disconnectWebSocket()
  if (aiIssueScanTimer) clearInterval(aiIssueScanTimer)
  if (issuesPollTimer) clearInterval(issuesPollTimer)
  document.removeEventListener('mousedown', onDocMousedown)
})

// ===== 问题记录 =====
async function loadIssues() {
  try {
    const res = await getMeetingIssues(meetingId)
    meetingIssues.value = Array.isArray(res) ? res : (res?.data || [])
  } catch {}
}

async function addIssue() {
  const content = newIssueContent.value.trim()
  if (!content) return
  addingIssue.value = true
  try {
    await createMeetingIssue(meetingId, {
      content,
      reporter_name: userStore.userInfo?.real_name || '管理员',
      submitted: true,
    })
    newIssueContent.value = ''
    await loadIssues()
  } catch (e) {
    ElMessage.error('记录问题失败')
  } finally {
    addingIssue.value = false
  }
}

async function deleteIssue(issue) {
  try {
    await deleteMeetingIssue(meetingId, issue.id)
    await loadIssues()
  } catch {}
}

function formatIssueTime(t) {
  if (!t) return ''
  return dayjs(t).format('HH:mm')
}

async function handleEndMeeting() {
  nextStepDialog.value = true
}

async function confirmNextStep() {
  ending.value = true
  try {
    meetingStore.disconnectWebSocket()
    await endMeeting(meetingId)
    ElMessage.success('会议已结束')
    nextStepDialog.value = false
    if (nextStepValue.value === 'issues') {
      await router.push(`/meeting/${meetingId}/issue-review`)
      return
    }
    await router.push(`/meeting/${meetingId}/minutes`)
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '结束会议失败')
  } finally {
    ending.value = false
  }
}

// 自动滚动到底部（尊重用户手动滚动）
watch(() => simulatedLines.value.length, () => {
  scrollToBottom()
})

// 实时签到：收到 WS checkin 事件时更新参与者状态
watch(() => meetingStore.lastCheckinEvent, (event) => {
  if (!event) return
  const p = participants.value.find(p => p.id === event.userId)
  if (p) p.checked_in = event.checkedIn
})

function handleRecord() {
  if (meetingStore.recordingStatus === 'recording') {
    clearInterval(typingInterval)
    meetingStore.pauseRecording()
  } else if (meetingStore.recordingStatus === 'paused') {
    meetingStore.startRecording()
    if (currentLineIdx < fileLines.length) {
      startTypingNextLine()
    }
  } else {
    // idle → 全新开始
    simulatedLines.value = []
    activeTypingText.value = ''
    lineIdCounter = 1
    meetingStore.startRecording()
    loadAndStartSimulation()
  }
}

function handleStop() {
  clearInterval(typingInterval)
  activeTypingText.value = ''
  meetingStore.resetRecordingToIdle()
}

async function loadAndStartSimulation() {
  try {
    const res = await getMeetingRecordText()
    const content = res?.data?.content || res?.content || ''
    fileLines = content.split('\n').filter(l => l.trim())
  } catch (e) {
    console.error('读取会议记录文件失败:', e)
    fileLines = ['（未找到会议记录文件，请确认 frontend/会议记录.txt 存在。']
  }
  currentLineIdx = 0
  currentCharIdx = 0
  if (fileLines.length > 0 && meetingStore.recordingStatus === 'recording') {
    startTypingNextLine()
  }
}

function startTypingNextLine() {
  clearInterval(typingInterval)
  if (currentLineIdx >= fileLines.length) {
    activeTypingText.value = ''
    recordingStatus.value = 'idle'
    return
  }
  const line = fileLines[currentLineIdx]
  activeTypingText.value = ''
  currentCharIdx = 0
  typingInterval = setInterval(() => {
    if (currentCharIdx < line.length) {
      activeTypingText.value += line[currentCharIdx]
      currentCharIdx++
      scrollToBottom()
    } else {
      clearInterval(typingInterval)
      const lineText = activeTypingText.value
      const segmentId = 'seg_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6)
      const newLine = { id: lineIdCounter++, text: lineText, category: null, segmentId }
      simulatedLines.value.push(newLine)
      activeTypingText.value = ''
      currentLineIdx++
      currentCharIdx = 0
      // 异步持久化到后端，不阻塞打字效果
      createTranscript(meetingId, {
        segment_id: segmentId,
        text: lineText,
        speaker_name: '未识别',
        start_time: new Date().toISOString(),
      }).then(res => {
        // 回写后端返回的 segment_id（通常与前端生成的一致）
        newLine.segmentId = res?.segment_id || segmentId
      }).catch(() => { /* 持久化失败不影响 UI */ })
      if (meetingStore.recordingStatus === 'recording' && currentLineIdx < fileLines.length) {
        setTimeout(startTypingNextLine, 300)
      } else if (currentLineIdx >= fileLines.length) {
        meetingStore.resetRecordingToIdle()
      }
    }
  }, 40)
}

function formatDuration(seconds) {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

function formatTimestamp(ts) {
  return ts ? dayjs(ts).format('HH:mm:ss') : ''
}

function getCategoryColor(category) {
  const colors = {
    '决策事项': '#fef0f0',
    '讨论事项': '#fdf6ec',
    '通报事项': '#f0f9ff',
  }
  return colors[category] || 'transparent'
}

function categoryTagType(cat) {
  const types = { '决策事项': 'danger', '讨论事项': 'warning', '通报事项': 'primary' }
  return types[cat] || 'info'
}

function handleTextEdit(item, event) {
  const newText = event.target.innerText
  if (newText !== item.text) {
    item.text = newText
    // TODO: 调用 updateTranscript API
  }
}

function handleLineEdit(line, event) {
  const newText = event.target.innerText.trim()
  if (newText !== line.text) {
    line.text = newText
    // 持久化文本修改到后端
    if (line.segmentId) {
      updateTranscript(meetingId, line.segmentId, { text: newText }).catch(() => { /* 静默失败 */ })
    }
  }
}

function getCatColor(key) {
  return categoryDefs.find(c => c.key === key)?.color || '#909399'
}

function getCatBg(key) {
  return categoryDefs.find(c => c.key === key)?.bg || 'transparent'
}

function getCatLabel(key) {
  return categoryDefs.find(c => c.key === key)?.label || key
}

function toggleActiveCategory(key) {
  activeCategory.value = activeCategory.value === key ? null : key
}

function markLine(line) {
  if (markMode.value && activeCategory.value) {
    // 先尝试局部选中标注
    const sel = window.getSelection()
    const selectedText = sel?.toString()?.trim()
    if (selectedText && selectedText.length > 0 && selectedText !== line.text?.trim()) {
      selectionAnnotations.value.push({
        id: selAnnotationId++,
        lineId: line.id,
        text: selectedText,
        category: activeCategory.value,
        isPartial: true,
      })
      sel.removeAllRanges()
      return
    }
    // 否则整行标注
    const newCategory = line.category === activeCategory.value ? null : activeCategory.value
    line.category = newCategory
    // 持久化分类标注到后端
    if (line.segmentId) {
      updateTranscript(meetingId, line.segmentId, { category: newCategory }).catch(() => { /* 静默失败 */ })
    }
  }
}

function handleTextSelect(line, e) {
  const sel = window.getSelection()
  const selectedText = sel?.toString()?.trim()
  if (!selectedText || selectedText.length < 2) {
    // 没有有效选区，关闭小工具栏
    selPopover.value.visible = false
    return
  }
  // markMode 已开启且已选分类：直接应用特定分类
  if (markMode.value && activeCategory.value && selectedText !== line.text?.trim()) {
    selectionAnnotations.value.push({
      id: selAnnotationId++,
      lineId: line.id,
      text: selectedText,
      category: activeCategory.value,
      isPartial: true,
    })
    sel.removeAllRanges()
    selPopover.value.visible = false
    return
  }
  // 展示浮层工具条，允许用户选择标注类型
  const range = sel.getRangeAt(0).getBoundingClientRect()
  selPopover.value = {
    visible: true,
    text: selectedText,
    x: Math.max(0, range.left + window.scrollX),
    y: range.bottom + window.scrollY + 8,
    lineId: line.id,
  }
}

function getLineAnnotations(lineId) {
  return selectionAnnotations.value.filter(a => a.lineId === lineId)
}

function removeCategory(item) {
  if (item.isPartial) {
    selectionAnnotations.value = selectionAnnotations.value.filter(a => a.id !== item.id)
  } else {
    item.category = null
  }
}

// AI 问答
const qaLoading = ref(false)

async function sendQuestion() {
  if (!qaInput.value.trim()) return
  const question = qaInput.value
  qaMessages.value.push({ id: Date.now(), role: 'user', content: question, sources: [] })
  qaInput.value = ''
  qaLoading.value = true

  try {
    const res = await aiQA({ question, meeting_id: meetingId })
    const answer = res?.answer || res?.data?.answer || '抱歉，暂时无法回答该问题'
    qaMessages.value.push({
      id: Date.now() + 1,
      role: 'assistant',
      content: answer,
      sources: res?.data?.sources || res?.sources || [],
    })
  } catch (e) {
    console.error('AI问答失败:', e)
    qaMessages.value.push({
      id: Date.now() + 1,
      role: 'assistant',
      content: '抱歉，AI服务暂时不可用，请稍后重试。',
      sources: [],
    })
  } finally {
    qaLoading.value = false
    // 滚动到底部
    nextTick(() => {
      if (qaMessagesRef.value) {
        qaMessagesRef.value.scrollTop = qaMessagesRef.value.scrollHeight
      }
    })
  }
}

function toggleVoiceInput() {
  ElMessage.info('语音输入功能开发中')
}

// 智能校验
async function runValidation() {
  validating.value = true
  try {
    const res = await validateTranscripts(meetingId)
    validationResults.value = res?.data || []
  } catch (e) {
    // 使用模拟数据
    validationResults.value = [
      { id: 1, segment_id: 'seg_001', original_text: '玩成任务', suggested_text: '完成任务', reason: '同音字误识别', confidence: 0.95 },
    ]
  } finally {
    validating.value = false
  }
}

function acceptSuggestion(item) {
  validationResults.value = validationResults.value.filter(v => v.id !== item.id)
  ElMessage.success('已采纳修改建议')
}

function ignoreSuggestion(item) {
  validationResults.value = validationResults.value.filter(v => v.id !== item.id)
}

function autoClassify() {
  ElMessage.success('AI 自动分类已触发')
}

// 音频回放
function playAudio(segmentId) {
  const url = getAudioSegment(meetingId, segmentId)
  if (audioPlayerRef.value) {
    audioPlayerRef.value.src = url
    audioPlayerRef.value.play()
  }
}

// 要点提取
async function extractKeypoints() {
  extracting.value = true
  try {
    const res = await generateKeypoints(meetingId, { strategy: keypointStrategy.value })
    keypoints.value = res || []
  } catch (e) {
    keypoints.value = [
      { id: 1, title: '项目进度确认', content: '各模块开发进度整合85%', importance: 'high', sort_order: 1 },
      { id: 2, title: '风险预警', content: '第三方接口对接存在延期风险', importance: 'high', sort_order: 2 },
    ]
  } finally {
    extracting.value = false
  }
}

function importanceType(imp) {
  return { high: 'danger', medium: 'warning', low: 'primary', normal: 'info' }[imp] || 'info'
}

function importanceLabel(imp) {
  return { high: '重要', medium: '一般', low: '次要', normal: '普通' }[imp] || imp
}

function exportKeypoints(format) {
  ElMessage.success(`要点导出(${format})功能开发中`)
}

function locateOriginalText(kp) {
  // 先尝试通过 source_segment_ids 定位
  let targetLine = null
  if (kp.source_segment_ids) {
    try {
      const ids = JSON.parse(kp.source_segment_ids)
      if (Array.isArray(ids) && ids.length > 0) {
        targetLine = simulatedLines.value.find(l => ids.includes(l.segmentId))
      }
    } catch {}
  }
  // 回退：文本相似度搜索（取要点 title/content 中的关键词）
  if (!targetLine) {
    const kw = (kp.title || '') + ' ' + (kp.content || '')
    const words = kw.split(/[\s，。、；：,.\s]+/).filter(w => w.length >= 2)
    let bestScore = 0
    for (const line of simulatedLines.value) {
      const score = words.filter(w => line.text.includes(w)).length
      if (score > bestScore) { bestScore = score; targetLine = line }
    }
  }
  if (!targetLine) { ElMessage.warning('未找到对应原文'); return }

  // 关闭抽屉后滚动到目标行并高亮
  keypointDrawer.value = false
  nextTick(() => {
    const el = transcriptListRef.value?.querySelector(`[data-line-id="${targetLine.id}"]`)
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    highlightedLineId.value = targetLine.id
    setTimeout(() => { highlightedLineId.value = null }, 2500)
  })
}

async function generateSummaryNow() {
  if (simulatedLines.value.length === 0) { ElMessage.warning('暂无会议记录，无法生成摘要'); return }
  generatingSummary.value = true
  latestSummary.value = ''
  try {
    const transcriptText = simulatedLines.value.map(l => l.text).join('\n')
    const res = await aiQA({
      question: `请对以下完整会议记录生成专业会议摘要（300字以内），重点提取核心议题、决策结论和待办事项：\n${transcriptText}`,
      meeting_id: meetingId,
    })
    latestSummary.value = res?.data?.answer || res?.answer || '摘要生成完成，请参阅详细记录。'
    // 同步提取要点
    await extractKeypoints()
    // 持久化供纪要页参考
    try {
      localStorage.setItem(`meeting_ref_${meetingId}`, JSON.stringify({
        summary: latestSummary.value,
        keypoints: keypoints.value,
        generatedAt: new Date().toISOString(),
      }))
    } catch {}
    ElMessage.success('摘要与要点已生成，可在纪要编辑页查看参考资料')
  } catch {
    latestSummary.value = '（AI 服务暂时不可用，请在纪要页面重新生成）'
    ElMessage.warning('AI 服务暂时不可用')
  } finally {
    generatingSummary.value = false
  }
}

async function refreshSummary() {
  await generateSummaryNow()
}
</script>

<style lang="scss" scoped>
.meeting-live {
  display: flex;
  height: 100%;
  overflow: hidden;
  box-sizing: border-box;
}

// 左栏
.panel-left {
  width: 25%;
  min-width: 280px;
  border-right: 1px solid rgba(0,212,255,0.15);
  display: flex;
  flex-direction: column;
  background: #0d2137;
  overflow: hidden;
  position: relative;
  transition: width 0.3s, min-width 0.3s;

  &.collapsed {
    width: 40px;
    min-width: 40px;
  }

  .panel-left-inner {
    display: flex;
    flex-direction: column;
    flex: 1;
    overflow: hidden;
  }

  .panel-toggle-btn {
    position: absolute;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 24px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0,212,255,0.15);
    border-radius: 0 6px 6px 0;
    cursor: pointer;
    color: #00d4ff;
    z-index: 5;
    &:hover { background: rgba(0,212,255,0.3); }
  }

  .ai-qa-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 0 16px 16px;
    overflow: hidden;

    .qa-messages {
      flex: 1;
      overflow-y: auto;
      padding: 8px 0;

      .qa-bubble {
        margin-bottom: 12px;

        &.user .bubble-content {
          background: #00d4ff; color: #0a1a38;
          margin-left: 40px; border-radius: 12px 12px 0 12px;
        }
        &.assistant .bubble-content, &.system .bubble-content {
          background: #0b1a2e; color: #a8c4dc;
          margin-right: 40px; border-radius: 12px 12px 12px 0;
        }

        .bubble-content {
          padding: 10px 14px; font-size: 14px; line-height: 1.5;
        }
        .bubble-sources {
          margin-top: 4px;
          .source-link {
            font-size: 14px; color: #00d4ff; cursor: pointer;
            &:hover { text-decoration: underline; }
          }
        }
      }
    }

    .qa-input {
      .mic-btn { cursor: pointer; font-size: 18px; &:hover { color: #00d4ff; } }
    }
  }
}

// 中栏
.panel-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #070e1a;

  .control-bar {
    display: flex; justify-content: space-between; align-items: center;
    padding: 12px 16px;
    background: #0d2137;
    border-bottom: 1px solid rgba(0,212,255,0.15);

    .control-left {
      display: flex; align-items: center; gap: 16px;
    }

    .recording-timer {
      font-family: 'Consolas', monospace;
      font-size: 16px;
      color: #ffffff;
      display: flex; align-items: center; gap: 6px;

      .status-dot {
        width: 8px; height: 8px; border-radius: 50%;
        &.recording { background: #f56c6c; animation: pulse 1s infinite; }
        &.paused { background: #e6a23c; }
        &.stopped, &.idle { background: #909399; }
      }
    }
  }

  .transcript-list {
    flex: 1;
    overflow-y: auto;
    padding: 16px;

    .transcript-card {
      background: #0d2137;
      border-radius: 8px;
      padding: 12px 16px;
      margin-bottom: 12px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.2);
      transition: background 0.3s;

      &.is-interim { opacity: 0.7; }
      &.is-interrupted { border-left: 3px dashed #e6a23c; }

      .interrupt-marker {
        display: flex; align-items: center; gap: 8px;
        margin-bottom: 8px; color: #e6a23c; font-size: 14px;
        .interrupt-line { flex: 1; height: 1px; border-top: 1px dashed #e6a23c; }
      }

      .card-header {
        display: flex; align-items: center; gap: 8px; margin-bottom: 8px;
        .speaker-info { flex: 1; }
        .speaker-name { font-weight: 600; font-size: 14px; color: #ffffff; }
        .speak-time { font-size: 14px; color: #5e8aad; margin-left: 8px; }
      }

      .card-text {
        font-size: 14px; line-height: 1.8; color: #a8c4dc;
        outline: none;
        &:focus { background: rgba(0,212,255,0.05); border-radius: 12px; padding: 4px; }
      }

      .sensitive-hint {
        margin-top: 6px; font-size: 14px; color: #f56c6c;
      }
      // 逐字输出相关
      &.completed-line {
        cursor: default;
        &.mark-hover { cursor: pointer; }
        &.marked-line { border-radius: 6px; }
        &.locate-highlight {
          animation: locateFlash 2.5s ease-out;
        }
      }

      @keyframes locateFlash {
        0%, 30% { background: rgba(0, 212, 255, 0.25); box-shadow: 0 0 8px rgba(0, 212, 255, 0.5); }
        100% { background: transparent; box-shadow: none; }
      }

      &.active-typing-line {
        background: #070e1a;
        border: 1px dashed rgba(0,212,255,0.3);

        .typing-text { color: #ffffff; }
        .typing-cursor {
          display: inline-block;
          color: #00d4ff;
          animation: blink 0.7s step-start infinite;
          margin-left: 1px;
        }
      }

      .line-mark-tag {
        display: flex;
        align-items: center;
        gap: 4px;
        margin-bottom: 4px;

        .cat-label { font-size: 14px; font-weight: 600; }
        .cat-remove {
          cursor: pointer;
          font-size: 14px;
          color: #5e8aad;
          line-height: 1;
          &:hover { color: #f56c6c; }
        }
      }

      .line-partial-marks {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 6px;

        .partial-mark {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          font-size: 14px;
          padding: 2px 8px;
          border-radius: 4px;

          .cat-remove {
            cursor: pointer;
            font-size: 14px;
            line-height: 1;
            &:hover { color: #f56c6c; }
          }
        }
      }
    }
  }

  .summary-bar {
    display: none;
  }
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

// 右栏
.panel-right {
  width: 28%;
  min-width: 300px;
  border-left: 1px solid rgba(0,212,255,0.15);
  background: #0d2137;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .right-tabs {
    flex: 1;
    overflow: hidden;
    :deep(.el-tabs__content) {
      height: calc(100% - 50px);
      overflow-y: auto;
      padding: 0 16px;
    }
  }

  .issues-panel {
    padding: 8px 0;

    .issue-list {
      .issue-item {
        padding: 8px 10px;
        margin-bottom: 6px;
        background: rgba(14,36,64,0.6);
        border: 1px solid rgba(0,212,255,0.15);
        border-radius: 6px;
        &.resolved { opacity: 0.6; }
        .issue-content { font-size: 14px; color: #d8f0ff; line-height: 1.6; }
        .issue-meta {
          display: flex; align-items: center; gap: 8px;
          margin-top: 6px; font-size: 14px; color: #5e8aad;
        }
      }
    }
  }

  .category-panel {
    padding: 8px 0;

    .cat-btn-group {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 10px;

      .cat-btn {
        padding: 5px 10px;
        border-radius: 14px;
        border: 1px solid var(--cat-color, #909399);
        background: transparent;
        color: var(--cat-color, #909399);
        font-size: 14px;
        cursor: pointer;
        transition: all 0.2s;

        &:hover { background: var(--cat-bg, #f4f4f5); }
        &.active {
          background: var(--cat-color, #909399);
          color: #fff;
        }
      }
    }

    .mark-mode-toggle {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 600;
      color: #5e8aad;
      background: rgba(0,212,255,0.06);
      border: 1.5px dashed rgba(0,212,255,0.2);
      transition: all 0.25s;
      margin-bottom: 6px;

      &:hover {
        background: rgba(0,212,255,0.12);
        border-color: rgba(0,212,255,0.4);
        color: #a8c4dc;
      }

      &.active {
        background: rgba(0,212,255,0.18);
        border: 1.5px solid #00d4ff;
        color: #00d4ff;
        box-shadow: 0 0 12px rgba(0,212,255,0.15);
      }
    }

    .mark-mode-tip {
      font-size: 14px;
      color: #5e8aad;
      margin: 0 0 6px;
      line-height: 1.5;
      strong { color: #00d4ff; }
    }

    .marked-list {
      overflow-y: auto;
      max-height: calc(100% - 160px);

      .marked-group {
        margin-bottom: 12px;

        .group-header {
          font-size: 14px;
          font-weight: 600;
          padding: 4px 8px;
          margin-bottom: 6px;
          background: rgba(255,255,255,0.04);
          border-radius: 0 4px 4px 0;

          .group-count { font-weight: 400; opacity: 0.7; }
        }

        .marked-item {
          display: flex;
          align-items: flex-start;
          gap: 6px;
          padding: 6px 8px;
          font-size: 14px;
          color: #a8c4dc;
          border-bottom: 1px solid rgba(0,212,255,0.06);

          .item-text { flex: 1; line-height: 1.5; word-break: break-all; }
          .item-del {
            flex-shrink: 0;
            cursor: pointer;
            font-size: 14px;
            color: #5e8aad;
            line-height: 1.5;
            &:hover { color: #f56c6c; }
          }
        }
      }
    }
  }

  .keypoint-btn {
    margin: 12px 16px;
  }
}

// 要点抽屉
.keypoint-controls {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

// 摘要总结面板
.summary-panel-wrap {
  padding: 8px 0;
}
.summary-waiting {
  text-align: center;
  padding: 30px 12px;
  .sw-title { font-size: 15px; font-weight: 600; color: #a8c4dc; margin: 12px 0 6px; }
  .sw-desc { font-size: 14px; color: #5e8aad; line-height: 1.5; margin-bottom: 14px; }
  .sw-status {
    font-size: 14px; color: #5e8aad;
    display: flex; align-items: center; gap: 6px; justify-content: center;
  }
}
.summary-ready {
  .summary-ready-tip {
    display: flex; align-items: center; gap: 6px; font-size: 14px; color: #67c23a;
    background: rgba(103,194,58,0.08); padding: 8px 12px; border-radius: 4px; margin-bottom: 12px;
  }
  .gen-btn { width: 100%; margin-bottom: 14px; }
  .ref-section-title { font-size: 14px; font-weight: 700; color: #5e8aad; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px; }
  .ref-text {
    font-size: 14px; color: #a8c4dc; line-height: 1.7;
    background: #070e1a; padding: 10px 12px; border-radius: 4px;
    border-left: 2px solid rgba(0,212,255,0.3);
  }
  .kp-mini {
    display: flex; align-items: flex-start; gap: 8px; margin-bottom: 8px;
    .kp-mini-text { font-size: 14px; color: #a8c4dc; line-height: 1.4; flex: 1; }
  }
}

.keypoint-list {
  .keypoint-card {
    border: 1px solid rgba(0,212,255,0.12);
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 10px;

    .kp-header {
      display: flex; align-items: center; gap: 8px;
      .kp-title { font-weight: 600; font-size: 14px; color: #ffffff; }
    }
    .kp-content { font-size: 14px; color: #a8c4dc; margin: 8px 0; }
    .kp-actions { display: flex; gap: 8px; }
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.preview-body {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.preview-iframe {
  width: 100%;
  height: 75vh;
  border: none;
}
.preview-image {
  max-width: 100%;
  max-height: 75vh;
  object-fit: contain;
}
.preview-unsupported {
  color: #909399;
  font-size: 14px;
}

/* ===== 文字选中标注工具栏 ===== */
.sel-anno-toolbar {
  position: fixed;
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  background: #1a2f4a;
  border: 1px solid rgba(0,212,255,0.35);
  border-radius: 8px;
  padding: 6px 10px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.5);
  max-width: 500px;
}
.sel-anno-tip {
  font-size: 14px;
  color: #8bb3d9;
  white-space: nowrap;
}
.sel-anno-btn {
  font-size: 14px;
  padding: 3px 8px;
  border-radius: 4px;
  border: 1px solid;
  cursor: pointer;
  white-space: nowrap;
  transition: opacity 0.15s;
}
.sel-anno-btn:hover { opacity: 0.8; }
.sel-anno-btn-issue {
  font-size: 14px;
  padding: 3px 8px;
  border-radius: 4px;
  border: 1px solid #f56c6c;
  background: rgba(245,108,108,0.12);
  color: #f56c6c;
  cursor: pointer;
}
.sel-anno-btn-issue:hover { background: rgba(245,108,108,0.22); }
.sel-anno-close {
  font-size: 14px;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid rgba(255,255,255,0.15);
  background: transparent;
  color: #8bb3d9;
  cursor: pointer;
  margin-left: 4px;
}
.sel-anno-close:hover { color: #e0efff; }

/* ===== 下一步弹窗 ===== */
:deep(.next-step-dialog) {
  .el-dialog {
    background: #0e1d38;
    border: 1px solid rgba(0,212,255,0.3);
    border-radius: 10px;
    padding: 0;
  }
  .el-dialog__header {
    padding: 0;
    margin: 0;
  }
  .el-dialog__body {
    padding: 20px 24px 16px;
  }
}

.next-step-dialog-header {
  display: flex;
  align-items: baseline;
  gap: 10px;
  padding: 16px 20px;
  background: linear-gradient(90deg, #163153 0%, #0d2137 100%);
  border-radius: 10px 10px 0 0;
  border-bottom: 1px solid rgba(0,212,255,0.2);
  position: relative;
}
.next-step-dialog-title {
  font-size: 16px;
  font-weight: 700;
  color: #dee5f2;
  letter-spacing: 1px;
}
.next-step-dialog-sub {
  font-size: 13px;
  color: #7f99be;
}
.next-step-dialog-close {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #456484;
  font-size: 20px;
  cursor: pointer;
  line-height: 1;
  &:hover { color: #dee5f2; }
}

.next-step-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.next-step-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px 20px;
  background: #14284b;
  border: 1px solid rgba(57,144,241,0.3);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: #3990f1;
    background: rgba(57,144,241,0.12);
    transform: translateX(4px);
  }

  &.active {
    border-color: #2bffbc;
    background: rgba(43,255,188,0.08);
  }
}

.next-step-card-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.next-step-card-info {
  flex: 1;
}

.next-step-card-title {
  font-size: 15px;
  font-weight: 600;
  color: #dee5f2;
  margin-bottom: 4px;
}

.next-step-card-desc {
  font-size: 13px;
  color: #7f99be;
  line-height: 1.5;
}

.next-step-card-arrow {
  color: #456484;
  font-size: 16px;
  flex-shrink: 0;
}

.next-step-dialog-cancel {
  margin-top: 16px;
  text-align: center;
  :deep(.el-button) {
    color: #456484;
    font-size: 13px;
    &:hover { color: #7f99be; }
  }
}

/* ===== AI 自动弹出问题提示 ===== */
.ai-issue-popup {
  position: fixed;
  bottom: 80px;
  right: 32px;
  z-index: 9998;
  background: #1a2f4a;
  border: 1px solid rgba(0,212,255,0.35);
  border-radius: 12px;
  padding: 16px;
  width: 320px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.5);
  animation: slideInRight 0.3s ease;
}
@keyframes slideInRight {
  from { transform: translateX(100px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
.ai-issue-popup-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}
.ai-issue-popup-icon { font-size: 18px; }
.ai-issue-popup-title {
  font-size: 14px;
  font-weight: 600;
  color: #00d4ff;
  flex: 1;
}
.ai-issue-popup-close {
  background: transparent;
  border: none;
  color: #8bb3d9;
  cursor: pointer;
  font-size: 16px;
  padding: 0 4px;
}
.ai-issue-popup-close:hover { color: #e0efff; }
.ai-issue-popup-content {
  font-size: 14px;
  color: #c8dff5;
  line-height: 1.6;
  padding: 8px 10px;
  background: rgba(255,255,255,0.04);
  border-radius: 6px;
  margin-bottom: 12px;
}
.ai-issue-popup-actions {
  display: flex;
  gap: 8px;
}
.ai-issue-confirm {
  flex: 1;
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid rgba(0,212,255,0.4);
  background: rgba(0,212,255,0.1);
  color: #00d4ff;
  font-size: 14px;
  cursor: pointer;
}
.ai-issue-confirm:hover { background: rgba(0,212,255,0.2); }
.ai-issue-dismiss {
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.1);
  background: transparent;
  color: #8bb3d9;
  font-size: 14px;
  cursor: pointer;
}
.ai-issue-dismiss:hover { background: rgba(255,255,255,0.05); }
</style>
