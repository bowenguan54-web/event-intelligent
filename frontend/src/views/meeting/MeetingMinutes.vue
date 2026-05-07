<template>
  <div class="page-container minutes-page">
    <!-- 页面标题栏 -->
    <div class="minutes-page-header">
      <el-button size="small" @click="router.push('/meeting/list')" style="color:#7f99be">
        <el-icon><ArrowLeft /></el-icon>会议管理
      </el-button>
    </div>
    <!-- 状态横幅 -->
    <div v-if="minutesStatus === 'published'" class="status-banner published">
      <el-icon><Promotion /></el-icon>
      纪要已发布，等待会议端审签。发布后内容不可修改，如需修改请等待会议端驳回。
    </div>
    <div v-else-if="minutesStatus === 'reviewing'" class="status-banner published">
      <el-icon><Promotion /></el-icon>
      纪要审签中，等待会议端审签。
    </div>
    <div v-else-if="minutesStatus === 'rejected'" class="status-banner rejected">
      <el-icon><Warning /></el-icon>
      纪要已被会议端驳回，请修改后重新发布。
      <span v-if="rejectReason" style="margin-left:8px;color:#f56c6c">驳回原因：{{ rejectReason }}</span>
    </div>
    <div v-else-if="minutesStatus === 'signed'" class="status-banner signed">
      <el-icon><CircleCheckFilled /></el-icon>
      所有人已完成审签，纪要签署流程已结束。
    </div>
    <!-- 上部：纪要编辑区 + 参考面板 -->
    <div class="minutes-body-layout">
      <div class="minutes-main">    <!-- 上部：纪要编辑区 -->
    <div class="minutes-editor-area">
      <el-card shadow="never" class="editor-card">
        <template #header>
          <div class="editor-header">
            <div class="editor-header-left">
              <span class="card-title">会议纪要编辑</span>
              <el-button link size="small" @click="showRefPanel = !showRefPanel" style="color:#5e8aad;margin-left:14px">
                <el-icon><InfoFilled /></el-icon>{{ showRefPanel ? '隐藏参考' : '显示参考' }}
              </el-button>
            </div>
            <div class="editor-actions">
              <!-- 结束会议按钮 -->
              <el-button v-if="meetingStatus === 'in_progress'" class="btn-nextstep" size="small" :loading="endingMeeting" @click="handleEndMeeting">
                <el-icon><SwitchButton /></el-icon>下一步
              </el-button>
              <!-- 编辑工具栏：仅草稿 / 驳回状态可操作 -->
              <template v-if="isEditable">
                <!-- AI 工具组 -->
                <div class="toolbar-group">
                  <el-button class="btn-ai-gen" size="small" :loading="generating" @click="handleGenerateMinutes">
                    <el-icon><MagicStick /></el-icon>AI 生成
                  </el-button>
                  <el-dropdown @command="applyMinutesTemplate" trigger="click">
                    <el-button class="btn-template" size="small">
                      <el-icon><Document /></el-icon>模板
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="general">通用会议纪要</el-dropdown-item>
                        <el-dropdown-item command="review">评审会议纪要</el-dropdown-item>
                        <el-dropdown-item command="special">专题研讨纪要</el-dropdown-item>
                        <el-dropdown-item command="office">办公会议纪要</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                  <el-button class="btn-polish" size="small" :loading="polishing" @click="handlePolish">
                    <el-icon><EditPen /></el-icon>润色
                  </el-button>
                  <el-button class="btn-tts" size="small" @click="handleTTS" :class="{ 'btn-tts-active': isSpeaking }">
                    <el-icon><Headset /></el-icon>{{ isSpeaking ? '停止' : '播报' }}
                  </el-button>
                </div>
                <!-- 主操作组 -->
                <div class="toolbar-group toolbar-group-primary">
                  <el-button class="btn-save" size="small" @click="saveMinutes" :loading="saving">
                    <el-icon><Check /></el-icon>保存
                  </el-button>
                  <el-button class="btn-publish" size="small" @click="handlePublish" :loading="publishing">
                    <el-icon><Promotion /></el-icon>发布
                  </el-button>
                </div>
              </template>
              <template v-else>
                <el-tag :type="minutesStatus === 'signed' ? 'success' : 'warning'" effect="plain" size="large">
                  {{ minutesStatusLabel }}
                </el-tag>
              </template>
            </div>
          </div>
        </template>

        <div v-if="minutesRecords.length === 0" class="minutes-empty-state">
          <el-icon :size="48" color="#3a5f80"><Document /></el-icon>
          <p style="color:#5e8aad;margin:12px 0 6px;font-size:14px">暂无会议纪要</p>
          <p style="color:#4a6a88;font-size:13px;margin-bottom:16px">点击“新增纪要”开始编写</p>
          <el-button type="primary" :loading="creatingMinutes" @click="createAnotherMinutes"><el-icon><Plus /></el-icon>新增纪要</el-button>
        </div>
        <template v-else>
        <div class="minutes-manage-bar">
          <div class="minutes-manage-left">
            <span class="minutes-manage-label">当前纪要</span>
            <el-select v-model="selectedMinutesId" placeholder="选择纪要" style="width:220px" @change="handleMinutesChange">
              <el-option
                v-for="item in minutesRecords"
                :key="item.id"
                :label="item.title || `纪要 ${item.id}`"
                :value="item.id"
              />
            </el-select>
            <el-input
              v-if="isEditable"
              v-model="minutesTitleInput"
              placeholder="请输入纪要名称"
              maxlength="60"
              style="width:220px"
            />
            <el-tag v-else size="small" effect="plain">{{ selectedMinutesTitle }}</el-tag>
          </div>
          <div class="minutes-manage-right">
            <el-button
              size="small"
              :disabled="issueReviewDone"
              :title="issueReviewDone ? '问题审查已完成或已跳过' : ''"
              @click="goToIssueReview"
            >前往问题审查</el-button>
            <el-button v-if="!minutesReadonlyMode" size="small" :loading="creatingMinutes" @click="createAnotherMinutes"><el-icon><Plus /></el-icon>新增纪要</el-button>
            <el-button
              v-if="selectedMinutesId && !minutesReadonlyMode"
              size="small"
              type="danger"
              plain
              :loading="deletingMinutes"
              @click="handleDeleteMinutes"
            ><el-icon><Delete /></el-icon>删除纪要</el-button>
          </div>
        </div>

        <div v-if="isEditable" class="signer-config-card">
          <div class="signer-config-header">
            <span>指定审签人员</span>
            <div class="minutes-manage-right">
              <el-button link type="primary" @click="signerRows.push({ user_id: null, signer_name: '', signer_unit: '', sign_type: 'review_sign' })"><el-icon><Plus /></el-icon>新增签字人</el-button>
              <el-button v-if="selectedMinutesId" link type="primary" :loading="switchingMinutes" @click="setAsPrimaryMinutes">设为主纪要</el-button>
            </div>
          </div>
          <div v-if="signerRows.length === 0" class="review-empty">未指定时默认仅组长审签</div>
          <div v-for="(row, index) in signerRows" :key="`${index}-${row.user_id || row.signer_name}`" class="signer-config-row">
            <el-select
              v-model="row.user_id"
              clearable
              filterable
              placeholder="选择人员"
              style="width:180px"
              @change="handleSignerUserChange(index, $event)"
            >
              <el-option
                v-for="user in meetingParticipants"
                :key="user.id"
                :label="user.real_name"
                :value="user.id"
              />
            </el-select>
            <el-input v-model="row.signer_name" placeholder="签字人姓名" style="width:150px" />
            <el-input v-model="row.signer_unit" placeholder="单位信息" style="width:180px" />
            <el-select v-model="row.sign_type" style="width:130px">
              <el-option label="组长审签" value="leader_review" />
              <el-option label="审签" value="review_sign" />
            </el-select>
            <el-button link type="danger" @click="signerRows.splice(index, 1)">删除</el-button>
          </div>
        </div>

        <!-- 富文本编辑器 -->
        <div class="editor-wrapper">
          <div ref="editorToolbarRef" class="editor-toolbar" />
          <div ref="editorContainerRef" class="editor-container" :class="{ 'readonly': !isEditable }" />
        </div>
        </template><!-- /v-else minutes exists -->
      </el-card>
    </div>

    <!-- 下部：电子审签区 -->
    <div class="sign-area" v-if="minutesStatus === 'published' || minutesStatus === 'signed' || minutesStatus === 'reviewing'">
      <el-card shadow="never">
        <template #header>
          <div class="sign-header">
            <span class="card-title">电子审签进度</span>
            <div class="sign-header-actions">
              <el-button size="small" @click="refreshSignStatus" :loading="loadingStatus">
                <el-icon><Refresh /></el-icon>刷新进度
              </el-button>
              <el-button v-if="minutesStatus === 'published' || minutesStatus === 'reviewing'" type="danger" size="small" :loading="forcingComplete" @click="handleForceComplete">
                <el-icon><CircleClose /></el-icon>强制结束审签
              </el-button>
            </div>
          </div>
        </template>

        <div class="sign-flow">
          <div class="sign-status-item">
            <el-tag :type="draftSigned ? 'success' : 'info'" size="small">
              {{ draftSigned ? '已签署' : '待签署' }}
            </el-tag>
            <span>{{ draftSignerName || '拟稿人' }}</span>
            <span v-if="draftSignedAt" class="sign-time">{{ draftSignedAt }}</span>
          </div>

          <div class="review-list">
            <div class="review-list-title">指定审签人员</div>
            <div v-if="reviewSignerStatusList.length === 0" class="review-empty">暂无指定审签人员，默认仅组长审签</div>
            <div v-for="item in reviewSignerStatusList" :key="`${item.signer_name}-${item.sign_type}`" class="sign-status-item">
              <el-tag :type="item.signed ? 'success' : 'info'" size="small">
                {{ item.signed ? '已签' : '待签' }}
              </el-tag>
              <span>{{ item.signer_name }}</span>
              <span v-if="item.signer_unit" class="sign-time">{{ item.signer_unit }}</span>
              <span class="sign-time">{{ signTypeLabel(item.sign_type) }}</span>
              <span v-if="item.signed_at" class="sign-time">{{ formatSignTime(item.signed_at) }}</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>
      </div><!-- /minutes-main -->

      <!-- 右侧参考面板 -->
      <div v-if="showRefPanel" class="minutes-ref-panel">
        <div class="ref-panel-header">
          <span class="ref-panel-title">参考信息</span>
          <el-button link size="small" @click="showRefPanel = false"><el-icon><Close /></el-icon></el-button>
        </div>
        <div class="ref-panel-body">
          <template v-if="refData.summary || refData.keypoints?.length">
            <div v-if="refData.summary" class="ref-section">
              <div class="ref-section-title">AI 实时摘要</div>
              <div class="ref-text">{{ refData.summary }}</div>
            </div>
            <div v-if="refData.keypoints?.length" class="ref-section">
              <div class="ref-section-title">关键要点</div>
              <div v-for="(kp, idx) in refData.keypoints" :key="idx" class="ref-kp-item">
                <div class="ref-kp-title">{{ kp.title }}</div>
                <div class="ref-kp-content">{{ kp.content }}</div>
              </div>
            </div>
            <div class="ref-generated-at" v-if="refData.generatedAt">
              生成于 {{ new Date(refData.generatedAt).toLocaleString('zh-CN', { hour12: false }) }}
            </div>
          </template>
          <template v-else>
            <div class="ref-empty">
              <el-icon :size="44" color="#3a5f80"><Document /></el-icon>
              <p style="color:#5e8aad;margin:12px 0 6px;font-size:14px">暂无参考信息</p>
              <p class="ref-empty-tip">会议中生成的摘要与要点会显示在这里，方便编写纪要时对照查看。</p>
            </div>
          </template>
        </div>
      </div>
    </div><!-- /minutes-body-layout -->

    <!-- 签到管理 -->
    <div class="checkin-mgmt-area">
      <el-card shadow="never">
        <template #header>
          <div class="sign-header">
            <span class="card-title">签到管理</span>
            <el-button size="small" @click="loadCheckinParticipants" :loading="loadingCheckin">
              <el-icon><Refresh /></el-icon>刷新
            </el-button>
          </div>
        </template>
        <p class="checkin-mgmt-tip">纪要审签结束后，可在这里补签、回退签到并查看签到签名记录。</p>
          <el-table :data="checkinParticipants" border size="small" style="width:100%;margin-top:12px">
          <el-table-column type="index" label="序号" width="55" align="center" />
          <el-table-column prop="real_name" label="姓名" width="100" />
          <el-table-column prop="department" label="单位" />
          <el-table-column prop="professional_title" label="职称" width="120" />
          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.checked_in ? 'success' : 'info'" size="small">{{ row.checked_in ? '已签到' : '未签到' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="签名" width="110" align="center">
            <template #default="{ row }">
              <img v-if="row.signature_image" :src="row.signature_image" style="height:30px;max-width:90px;object-fit:contain" />
              <span v-else style="color:#909399;font-size:14px">暂无</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" align="center">
            <template #default="{ row }">
              <el-button v-if="row.signature_image || row.checked_in" link type="warning" size="small" @click="rollbackCheckin(row)" :loading="rollbackLoading[row.id]">回退</el-button>
              <el-button v-else link type="primary" size="small" @click="openOfflineSign(row)">签到</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 代签到弹窗 -->
    <el-dialog v-model="offlineSignVisible" :title="`签到-${offlineSignTarget?.real_name || ''}`" width="580px" destroy-on-close>
      <p style="text-align:center;margin:0 0 12px;color:#606266">请 <strong>{{ offlineSignTarget?.real_name }}</strong> 手写签名完成签到</p>
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
        <el-slider v-model="offlineSignPenWidth" :min="1" :max="8" :step="1" style="width:100px" />
        <el-button size="small" @click="undoOfflineSign">撤销</el-button>
        <el-button size="small" @click="clearOfflineSign">清除</el-button>
        <el-button size="small" type="primary" plain @click="openOfflineSignExpand">放大</el-button>
      </div>
      <canvas
        ref="offlineSignCanvasRef"
        width="520"
        height="160"
        class="offline-sign-canvas"
        @pointerdown="startOfflineSign"
        @pointermove="moveOfflineSign"
        @pointerup="endOfflineSign"
        @pointerleave="endOfflineSign"
      />
      <template #footer>
        <el-button @click="offlineSignVisible = false">取消</el-button>
        <el-button type="primary" :loading="submittingOfflineSign" @click="submitOfflineSign">确认签到</el-button>
      </template>
    </el-dialog>

    <!-- 代签到展弢弹窗 -->
    <el-dialog
      v-model="offlineSignExpandVisible"
      :title="`签到（放大）-${offlineSignTarget?.real_name || ''}`"
      width="860px"
      :append-to-body="true"
      destroy-on-close
    >
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
        <el-slider v-model="offlineSignPenWidth" :min="1" :max="8" :step="1" style="width:120px" />
        <el-button size="small" @click="undoOfflineExpandSign">撤销</el-button>
        <el-button size="small" @click="clearOfflineExpandSign">清除</el-button>
      </div>
      <canvas
        ref="offlineSignExpandCanvasRef"
        width="800"
        height="280"
        class="offline-expand-canvas"
        @pointerdown="startOfflineExpandSign"
        @pointermove="moveOfflineExpandSign"
        @pointerup="endOfflineExpandSign"
        @pointerleave="endOfflineExpandSign"
      />
      <template #footer>
        <el-button @click="offlineSignExpandVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmOfflineExpand">确认</el-button>
      </template>
    </el-dialog>

    <!-- 版本历史弹窗 -->
    <el-dialog v-model="showVersions" title="纪要版本历史" width="700px">
      <el-table :data="versionList">
        <el-table-column prop="version" label="版本" width="80" />
        <el-table-column prop="editor" label="编辑人" width="100" />
        <el-table-column prop="created_at" label="时间" width="180" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewVersion(row)">查看</el-button>
            <el-button type="warning" link size="small" @click="rollbackVersion(row)">回滚</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
    <el-dialog v-model="nextStepDialog" title="会议下一步" width="460px" destroy-on-close>
      <div style="color:#8bb3d9;margin-bottom:12px;line-height:1.7">
        会议结束后，可以继续进入问题梳理、纪要编写或评审意见页面，当前选择会自动保存。
      </div>
      <el-radio-group v-model="nextStepValue" class="next-step-options">
        <el-radio label="issues">问题梳理</el-radio>
        <el-radio label="minutes">纪要编写</el-radio>
        <el-radio v-if="meetingType === 'review'" label="review">评审意见</el-radio>
      </el-radio-group>
      <template #footer>
        <el-button @click="nextStepDialog = false">取消</el-button>
        <el-button type="primary" :loading="endingMeeting" @click="confirmNextStep">继续</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import {
  generateMinutes, updateMinutes, signMinutes,
  polishText, getMinutesInfo, publishMinutes, endMeeting, getMeetingById,
  forceCompleteSign, getParticipantsStatus, terminalSign, signatureRollback,
  createMinutesRecord, listMinutesRecords, setPrimaryMinutes, deleteMinutesRecord,
} from '@/api/meeting'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const meetingId = route.params.id

// 会议状态
const meetingStatus = ref('')
const meetingType = ref('')
const endingMeeting = ref(false)
const forcingComplete = ref(false)
const nextStepDialog = ref(false)
const nextStepValue = ref('minutes')
const meetingParticipants = ref([])
const minutesRecords = ref([])
const selectedMinutesId = ref(null)
const minutesTitleInput = ref('')
const publishDialogVisible = ref(false)
const creatingMinutes = ref(false)
const deletingMinutes = ref(false)
const switchingMinutes = ref(false)
const signerRows = ref([])

// 问题审查是否已完成或跳过（仅从后端状态获取，不使用 localStorage 避免过期缓存导致按钮被错误禁用）
const issueReviewDone = ref(false)

// 签到管理
const checkinParticipants = ref([])
const loadingCheckin = ref(false)
const rollbackLoading = ref({})
const offlineSignVisible = ref(false)
const offlineSignTarget = ref(null)
const offlineSignPenWidth = ref(2)
const offlineSignCanvasRef = ref(null)
const submittingOfflineSign = ref(false)
let offlineSignCtx = null
let offlineDrawing = false
let offlinePaths = []
let offlineCurrentPath = []

// 放大签名相关
const offlineSignExpandVisible = ref(false)
const offlineSignExpandCanvasRef = ref(null)
let offlineExpandCtx = null
let offlineExpandDrawing = false
let offlineExpandPaths = []
let offlineExpandCurrentPath = []

async function loadCheckinParticipants() {
  loadingCheckin.value = true
  try {
    const res = await getParticipantsStatus(meetingId)
    checkinParticipants.value = Array.isArray(res) ? res : (res?.data || [])
  } catch (e) {
    ElMessage.error('加载参会人员失败')
  } finally {
    loadingCheckin.value = false
  }
}

async function rollbackCheckin(row) {
  try {
    rollbackLoading.value[row.id] = true
    await signatureRollback(meetingId, row.id)
    ElMessage.success(`${row.real_name} 已回退，等待重签`)
    await loadCheckinParticipants()
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '回退失败')
  } finally {
    rollbackLoading.value[row.id] = false
  }
}

function openOfflineSign(row) {
  offlineSignTarget.value = row
  offlinePaths = []
  offlineSignVisible.value = true
  nextTick(() => initOfflineCanvas())
}

function initOfflineCanvas() {
  const canvas = offlineSignCanvasRef.value
  if (!canvas) return
  offlineSignCtx = canvas.getContext('2d')
  offlineSignCtx.strokeStyle = '#000000'
  offlineSignCtx.lineWidth = offlineSignPenWidth.value
  offlineSignCtx.lineCap = 'round'
  offlineSignCtx.lineJoin = 'round'
}

function getOfflineCoords(e) {
  const canvas = offlineSignCanvasRef.value
  if (!canvas) return { x: e.offsetX, y: e.offsetY }
  const rect = canvas.getBoundingClientRect()
  return {
    x: (e.clientX - rect.left) * (canvas.width / rect.width),
    y: (e.clientY - rect.top) * (canvas.height / rect.height),
  }
}

function startOfflineSign(e) {
  if (!offlineSignCtx) initOfflineCanvas()
  offlineDrawing = true
  const { x, y } = getOfflineCoords(e)
  offlineCurrentPath = [{ x, y }]
  offlineSignCtx.beginPath()
  offlineSignCtx.strokeStyle = '#000000'
  offlineSignCtx.lineWidth = offlineSignPenWidth.value
  offlineSignCtx.moveTo(x, y)
}

function moveOfflineSign(e) {
  if (!offlineDrawing) return
  const { x, y } = getOfflineCoords(e)
  offlineCurrentPath.push({ x, y })
  offlineSignCtx.lineTo(x, y)
  offlineSignCtx.stroke()
}

function endOfflineSign() {
  if (!offlineDrawing) return
  offlineDrawing = false
  offlinePaths.push([...offlineCurrentPath])
  offlineCurrentPath = []
}

function clearOfflineSign() {
  if (!offlineSignCtx) return
  offlineSignCtx.clearRect(0, 0, offlineSignCanvasRef.value.width, offlineSignCanvasRef.value.height)
  offlinePaths = []
}

function undoOfflineSign() {
  if (!offlinePaths.length || !offlineSignCtx) return
  offlinePaths.pop()
  const canvas = offlineSignCanvasRef.value
  offlineSignCtx.clearRect(0, 0, canvas.width, canvas.height)
  offlinePaths.forEach(path => {
    if (path.length < 2) return
    offlineSignCtx.beginPath()
    offlineSignCtx.strokeStyle = '#000000'
    offlineSignCtx.lineWidth = offlineSignPenWidth.value
    offlineSignCtx.moveTo(path[0].x, path[0].y)
    path.slice(1).forEach(p => offlineSignCtx.lineTo(p.x, p.y))
    offlineSignCtx.stroke()
  })
}

async function submitOfflineSign() {
  if (!offlinePaths.length) { ElMessage.warning('请先完成手写签名'); return }
  const imageData = offlineSignCanvasRef.value?.toDataURL('image/png') || ''
  submittingOfflineSign.value = true
  try {
    await terminalSign(meetingId, offlineSignTarget.value.id, imageData)
    ElMessage.success(`${offlineSignTarget.value.real_name} 签到成功`)
    offlineSignVisible.value = false
    await loadCheckinParticipants()
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '签到失败')
  } finally {
    submittingOfflineSign.value = false
  }
}

function openOfflineSignExpand() {
  offlineExpandPaths = []
  offlineSignExpandVisible.value = true
  nextTick(() => {
    const canvas = offlineSignExpandCanvasRef.value
    if (!canvas) return
    offlineExpandCtx = canvas.getContext('2d')
    offlineExpandCtx.strokeStyle = '#000000'
    offlineExpandCtx.lineWidth = offlineSignPenWidth.value
    offlineExpandCtx.lineCap = 'round'
    offlineExpandCtx.lineJoin = 'round'
    offlineExpandCtx.clearRect(0, 0, canvas.width, canvas.height)
    // copy small canvas content if any
    if (offlineSignCanvasRef.value) {
      offlineExpandCtx.drawImage(offlineSignCanvasRef.value, 0, 0, canvas.width, canvas.height)
    }
  })
}

function getOfflineExpandCoords(e) {
  const canvas = offlineSignExpandCanvasRef.value
  if (!canvas) return { x: e.offsetX, y: e.offsetY }
  const rect = canvas.getBoundingClientRect()
  return {
    x: (e.clientX - rect.left) * (canvas.width / rect.width),
    y: (e.clientY - rect.top) * (canvas.height / rect.height),
  }
}

function startOfflineExpandSign(e) {
  if (!offlineExpandCtx) return
  offlineExpandDrawing = true
  const { x, y } = getOfflineExpandCoords(e)
  offlineExpandCurrentPath = [{ x, y }]
  offlineExpandCtx.beginPath()
  offlineExpandCtx.strokeStyle = '#000000'
  offlineExpandCtx.lineWidth = offlineSignPenWidth.value
  offlineExpandCtx.moveTo(x, y)
}

function moveOfflineExpandSign(e) {
  if (!offlineExpandDrawing) return
  const { x, y } = getOfflineExpandCoords(e)
  offlineExpandCurrentPath.push({ x, y })
  offlineExpandCtx.lineTo(x, y)
  offlineExpandCtx.stroke()
}

function endOfflineExpandSign() {
  if (!offlineExpandDrawing) return
  offlineExpandDrawing = false
  offlineExpandPaths.push([...offlineExpandCurrentPath])
  offlineExpandCurrentPath = []
}

function clearOfflineExpandSign() {
  if (!offlineExpandCtx) return
  offlineExpandCtx.clearRect(0, 0, offlineSignExpandCanvasRef.value.width, offlineSignExpandCanvasRef.value.height)
  offlineExpandPaths = []
}

function undoOfflineExpandSign() {
  if (!offlineExpandPaths.length || !offlineExpandCtx) return
  offlineExpandPaths.pop()
  const canvas = offlineSignExpandCanvasRef.value
  offlineExpandCtx.clearRect(0, 0, canvas.width, canvas.height)
  offlineExpandPaths.forEach(path => {
    if (path.length < 2) return
    offlineExpandCtx.beginPath()
    offlineExpandCtx.strokeStyle = '#000000'
    offlineExpandCtx.lineWidth = offlineSignPenWidth.value
    offlineExpandCtx.moveTo(path[0].x, path[0].y)
    path.slice(1).forEach(p => offlineExpandCtx.lineTo(p.x, p.y))
    offlineExpandCtx.stroke()
  })
}

function confirmOfflineExpand() {
  const expandCanvas = offlineSignExpandCanvasRef.value
  const smallCanvas = offlineSignCanvasRef.value
  if (expandCanvas && smallCanvas) {
    const ctx = smallCanvas.getContext('2d')
    ctx.clearRect(0, 0, smallCanvas.width, smallCanvas.height)
    ctx.drawImage(expandCanvas, 0, 0, smallCanvas.width, smallCanvas.height)
    offlinePaths = [[{ x: 0, y: 0 }]]
    offlineSignCtx = ctx
  }
  offlineSignExpandVisible.value = false
}

async function loadMeetingStatus() {
  try {
    const res = await getMeetingById(meetingId)
    const data = res?.data || res
    meetingStatus.value = data?.status || ''
    meetingType.value = data?.meeting_type || ''
    meetingParticipants.value = data?.participants || []
    // 同步问题审查状态
    if (data?.issue_review_status === 'completed' || data?.issue_review_status === 'skipped') {
      issueReviewDone.value = true
      localStorage.setItem(`issueReviewDone_${meetingId}`, 'true')
    }
    if (!signerRows.value.length) {
      signerRows.value = buildDefaultSignerRows()
    }
  } catch {}
}

function signTypeLabel(type) {
  const map = { leader_review: '组长审签', review_sign: '审签', draft_sign: '拟稿签署' }
  return map[type] || '审签'
}

function buildDefaultSignerRows() {
  const leader = meetingParticipants.value.find(item => item.is_leader)
  const fallback = leader || meetingParticipants.value[0]
  if (!fallback) return []
  return [{
    user_id: fallback.id,
    signer_name: fallback.real_name,
    signer_unit: fallback.department || '',
    sign_type: 'leader_review',
  }]
}

function syncSignerRows(signers = []) {
  if (Array.isArray(signers) && signers.length) {
    signerRows.value = signers.map(item => ({
      user_id: item.user_id || null,
      signer_name: item.signer_name || '',
      signer_unit: item.signer_unit || '',
      sign_type: item.sign_type || 'review_sign',
    }))
    return
  }
  if (!signerRows.value.length) {
    signerRows.value = buildDefaultSignerRows()
  }
}

function normalizeSignerRows() {
  const source = signerRows.value.length ? signerRows.value : buildDefaultSignerRows()
  const rows = source
    .map(item => ({
      user_id: item.user_id || null,
      signer_name: (item.signer_name || '').trim(),
      signer_unit: (item.signer_unit || '').trim(),
      sign_type: item.sign_type || 'review_sign',
    }))
    .filter(item => item.signer_name)
  return rows.filter((item, index) => rows.findIndex(other => other.signer_name === item.signer_name) === index)
}

async function loadMinutesRecords() {
  try {
    const res = await listMinutesRecords(meetingId)
    const list = Array.isArray(res?.data) ? res.data : (Array.isArray(res) ? res : [])
    minutesRecords.value = list
    if (!selectedMinutesId.value) {
      const preferred = minutesRecords.value.find(item => item.is_primary) || minutesRecords.value[0]
      selectedMinutesId.value = preferred?.id || null
    }
    syncMinutesTitle()
  } catch {
    minutesRecords.value = []
  }
  return minutesRecords.value.length
}

async function createAnotherMinutes() {
  creatingMinutes.value = true
  try {
    const order = minutesRecords.value.length + 1
    const res = await createMinutesRecord(meetingId, { title: `纪要 ${order}` })
    const created = res?.data || res
    selectedMinutesId.value = created?.id || null
    await loadMinutesRecords()
    await loadMinutes()
    ElMessage.success('已新增纪要')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '新增纪要失败')
  } finally {
    creatingMinutes.value = false
  }
}

async function setAsPrimaryMinutes() {
  if (!selectedMinutesId.value) return
  switchingMinutes.value = true
  try {
    await setPrimaryMinutes(meetingId, selectedMinutesId.value)
    await loadMinutesRecords()
    ElMessage.success('已设为主纪要')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '设置主纪要失败')
  } finally {
    switchingMinutes.value = false
  }
}

async function handleDeleteMinutes() {
  if (!selectedMinutesId.value) return
  const { ElMessageBox } = await import('element-plus')
  try {
    await ElMessageBox.confirm('确定删除当前纪要？此操作不可恢复。', '删除确认', { type: 'warning', confirmButtonText: '确定删除', cancelButtonText: '取消' })
  } catch {
    return
  }
  deletingMinutes.value = true
  try {
    await deleteMinutesRecord(meetingId, selectedMinutesId.value)
    selectedMinutesId.value = null
    ElMessage.success('纪要已删除')
    const count = await loadMinutesRecords()
    if (count > 0) {
      await loadMinutes()
    } else {
      if (editorContainerRef.value) editorContainerRef.value.innerHTML = ''
      minutesStatus.value = 'none'
    }
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '删除失败')
  } finally {
    deletingMinutes.value = false
  }
}

function handleSignerUserChange(index, userId) {
  const row = signerRows.value[index]
  if (!row) return
  const participant = meetingParticipants.value.find(item => item.id === userId)
  if (!participant) return
  row.signer_name = participant.real_name
  if (!row.signer_unit) row.signer_unit = participant.department || ''
  if (participant.is_leader) row.sign_type = 'leader_review'
}

async function handleMinutesChange() {
  syncMinutesTitle()
  await loadMinutes()
}

async function persistMinutesDraftBeforeJump() {
  if (!isEditable.value) return true
  try {
    const content = editorContainerRef.value?.innerHTML || ''
    await updateMinutes(meetingId, buildMinutesPayload(content, { review_conclusion: reviewConclusion.value }), currentMinutesId.value)
    updateMinutesRecordMeta(currentMinutesId.value, { title: normalizedMinutesTitle.value, status: minutesStatus.value })
    return true
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '自动保存纪要失败')
    return false
  }
}

async function goToIssueReview() {
  const ok = await persistMinutesDraftBeforeJump()
  if (!ok) return
  router.push(`/meeting/${meetingId}/issue-review`)
}

async function handleEndMeeting() {
  nextStepDialog.value = true
}

async function confirmNextStep() {
  endingMeeting.value = true
  try {
    if (meetingStatus.value === 'in_progress') {
      await endMeeting(meetingId)
      meetingStatus.value = 'finished'
    }
    localStorage.setItem(`meeting_next_step_${meetingId}`, nextStepValue.value)
    nextStepDialog.value = false
    if (nextStepValue.value === 'issues') {
      router.push(`/meeting/${meetingId}/issue-review`)
      return
    }
    if (nextStepValue.value === 'review') {
      ElMessage.success('会议已结束，可前往评审意见页面继续处理')
      return
    }
    ElMessage.success('会议已结束，当前流程已保存')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '操作失败')
  } finally {
    endingMeeting.value = false
  }
}

const minutesStatus = ref('none')
const rejectReason = ref('')
const currentMinutesId = computed(() => selectedMinutesId.value || undefined)
const currentMinutesRecord = computed(() => minutesRecords.value.find(item => item.id === selectedMinutesId.value) || null)
const minutesReadonlyMode = computed(() =>
  ['published', 'reviewing', 'signed'].includes(minutesStatus.value) ||
  minutesRecords.value.some(item => ['published', 'reviewing', 'signed'].includes(item.status))
)
const isEditable = computed(() => !minutesReadonlyMode.value && ['draft', 'rejected', 'none'].includes(minutesStatus.value))
const selectedMinutesTitle = computed(() => {
  return currentMinutesRecord.value?.title || minutesTitleInput.value || '未选择纪要'
})
const normalizedMinutesTitle = computed(() => (minutesTitleInput.value || '').trim() || selectedMinutesTitle.value || '未命名纪要')
const minutesStatusLabel = computed(() => {
  const map = { draft: '草稿', published: '待审签', rejected: '已驳回', signed: '已签署', reviewing: '审签中', none: '未创建' }
  return map[minutesStatus.value] || minutesStatus.value
})

const loadingStatus = ref(false)
const draftSignature = ref(null)
const reviewSignatures = ref([])
const totalParticipants = ref(0)

const draftSigned = computed(() => !!draftSignature.value)
const draftSignerName = computed(() => draftSignature.value?.signer_name || '')
const draftSignedAt = computed(() => formatSignTime(draftSignature.value?.signed_at))
const reviewSignerStatusList = computed(() => normalizeSignerRows().map(item => {
  const matched = reviewSignatures.value.find(sig => sig.signer_name === item.signer_name)
  return { ...item, signed: !!matched, signed_at: matched?.signed_at || '' }
}))


async function handleForceComplete() {
  try {
    await import('element-plus').then(({ ElMessageBox }) =>
      ElMessageBox.confirm(
        '强制结束后将直接完成当前审签流程，是否继续？',
        '强制结束审签',
        {
          type: 'warning',
          confirmButtonText: '确认结束',
          cancelButtonText: '取消',
          confirmButtonClass: 'el-button--danger',
        }
      )
    )
  } catch { return }
  forcingComplete.value = true
  try {
    await forceCompleteSign(meetingId, currentMinutesId.value)
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '强制结束审签失败')
    forcingComplete.value = false
    return
  }
  minutesStatus.value = 'signed'
  updateMinutesRecordMeta(currentMinutesId.value, { status: 'signed', title: normalizedMinutesTitle.value })
  if (editorContainerRef.value) {
    editorContainerRef.value.contentEditable = 'false'
  }
  if (signPollTimer) { clearInterval(signPollTimer); signPollTimer = null }
  loadCheckinParticipants()
  ElMessage.success('已强制结束审签')
  forcingComplete.value = false
}

function syncMinutesTitle(title) {
  const nextTitle = (title ?? currentMinutesRecord.value?.title ?? '').trim()
  minutesTitleInput.value = nextTitle
}

function updateMinutesRecordMeta(minutesId, patch = {}) {
  if (!minutesId) return
  minutesRecords.value = minutesRecords.value.map(item => {
    if (item.id !== minutesId) return item
    return { ...item, ...patch }
  })
}

function buildMinutesPayload(content, extra = {}) {
  return {
    title: normalizedMinutesTitle.value,
    content,
    ...extra,
  }
}

const editorToolbarRef = ref(null)
const editorContainerRef = ref(null)
const saving = ref(false)
const generating = ref(false)
const publishing = ref(false)

const showRefPanel = ref(false)
const refData = reactive({ summary: '', keypoints: [], generatedAt: '' })
const reviewConclusion = ref('')

function loadRefData() {
  try {
    const stored = localStorage.getItem(`meeting_ref_${meetingId}`)
    if (stored) {
      const data = JSON.parse(stored)
      refData.summary = data.summary || ''
      refData.keypoints = data.keypoints || []
      refData.generatedAt = data.generatedAt || ''
      if (refData.summary || refData.keypoints.length) showRefPanel.value = true
    }
  } catch {}
}

const showVersions = ref(false)
const versionList = ref([])
const polishing = ref(false)

function formatSignTime(t) {
  if (!t) return ''
  try {
    return new Date(t).toLocaleString('zh-CN', { hour12: false })
  } catch {
    return String(t).replace('T', ' ').slice(0, 19)
  }
}

onMounted(async () => {
  await loadMeetingStatus()
  const recordCount = await loadMinutesRecords()
  if (recordCount > 0) {
    await loadMinutes()
  }
  loadRefData()
  initCanvas()
  startSignPoll()
  loadCheckinParticipants()
})

onUnmounted(() => {
  if (signPollTimer) clearInterval(signPollTimer)
  if (isSpeaking.value) window.speechSynthesis?.cancel()
  // 组件销毁后，等 Element Plus Teleport/PopupManager 自身清理完毕，再强制兜底清理
  // 使用较长延时确保 dialog 关闭动画（~300ms）完成后再清理残留 overlay
  setTimeout(() => {
    document.body.classList.remove('el-popup-parent--hidden')
    document.body.style.overflow = ''
    document.body.style.paddingRight = ''
    document.querySelectorAll('.el-overlay').forEach(el => el.remove())
  }, 350)
})

onBeforeRouteLeave(() => {
  // 离开前关闭所有弹窗 ref，让 Vue/Element Plus 走正常销毁流程
  offlineSignVisible.value = false
  offlineSignExpandVisible.value = false
  nextStepDialog.value = false
  showVersions.value = false
  publishDialogVisible.value = false
  // 关闭全局 ElMessageBox 实例（如删除确认、强制完成确认等弹窗）
  try { ElMessageBox.close() } catch {}
  // 立即清理 body 样式，防止跳转后页面滚动被锁定
  document.body.classList.remove('el-popup-parent--hidden')
  document.body.style.overflow = ''
  document.body.style.paddingRight = ''
})

function initCanvas() {
  const canvas = signatureCanvasRef.value
  if (canvas) {
    ctx = canvas.getContext('2d')
    ctx.strokeStyle = penColor.value
    ctx.lineWidth = penWidth.value
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'
  }
}

async function handleGenerateMinutes() {
  generating.value = true
  try {
    const res = await generateMinutes(meetingId, currentMinutesId.value)
    const content = res?.content || res?.data?.content || ''
    if (content && editorContainerRef.value) {
      editorContainerRef.value.innerHTML = content
      ElMessage.success('AI 纪要生成成功')
    } else {
      ElMessage.warning('生成内容为空，请棢查会议是否有转写记录')
    }
  } catch (e) {
    console.error('纪要生成失败:', e)
    ElMessage.error('AI 纪要生成失败，请稍后重试')
  } finally {
    generating.value = false
  }
}

async function loadMinutes() {
  try {
    const res = await getMinutesInfo(meetingId, currentMinutesId.value)
    const data = res?.data || res
    const content = data?.content
    syncMinutesTitle(data?.title)
    updateMinutesRecordMeta(currentMinutesId.value, {
      title: data?.title || normalizedMinutesTitle.value,
      status: data?.status || 'draft',
      is_primary: data?.is_primary,
    })
    if (editorContainerRef.value) {
      if (content) {
        editorContainerRef.value.innerHTML = content
      } else {
        editorContainerRef.value.innerHTML = ''
      }
    }
    // 载入纪要状态
    minutesStatus.value = data?.status || 'none'
    rejectReason.value = data?.reject_reason || ''
    reviewConclusion.value = data?.review_conclusion || ''
    // 载入签名状态
    const sigs = data?.signatures || []
      syncSignerRows(data?.required_signers || [])
    draftSignature.value = sigs.find(s => s.sign_step === 'draft') || null
    reviewSignatures.value = sigs.filter(s => s.sign_step === 'review')
    // 从后端取与会人数（可选，用于判断“全部已签”）
    if (data?.participant_count != null) {
      totalParticipants.value = data.participant_count
    }
    // 控制编辑器是否只读
    if (editorContainerRef.value) {
      editorContainerRef.value.contentEditable = isEditable.value ? 'true' : 'false'
    }
    // 发布后初始化签名画布
    if (minutesStatus.value === 'published' && !draftSigned.value) {
      setTimeout(() => initCanvas(), 100)
    }
  } catch (e) {
    console.error('加载纪要失败:', e)
    if (editorContainerRef.value) {
      editorContainerRef.value.innerHTML = '<p>纪要加载失败，请刷新页面。</p>'
      editorContainerRef.value.contentEditable = isEditable.value ? 'true' : 'false'
    }
  }
}

/* 模板选择 */
const MINUTES_TEMPLATES = {
  general: '<h1>会议纪要</h1><h2>一、会议概况</h2><p><strong>会议时间：</strong>待填写&nbsp;&nbsp;<strong>会议地点：</strong>待填写</p><p><strong>主持人：</strong>待填写&nbsp;&nbsp;<strong>记录人：</strong>待填写</p><p><strong>参会人员：</strong>待填写</p><h2>二、会议内容</h2><h3>1. 议题研讨</h3><p>待填写</p><h3>2. 主要意见</h3><p>待填写</p><h2>三、会议结论</h2><ol><li>待填写</li></ol><h2>四、会后事项</h2><table><thead><tr><th>事项</th><th>责任人</th><th>完成时限</th></tr></thead><tbody><tr><td>待填写</td><td>待填写</td><td>待填写</td></tr></tbody></table>',
  review: '<h1>评审会议纪要</h1><h2>一、会议概况</h2><p><strong>会议时间：</strong>待填写&nbsp;&nbsp;<strong>会议地点：</strong>待填写</p><p><strong>主持人：</strong>待填写&nbsp;&nbsp;<strong>记录人：</strong>待填写</p><p><strong>参会专家及代表：</strong>待填写</p><h2>二、评审项目概况</h2><p>待填写（项目名称、基本情况、评审目的）</p><h2>三、主要审查意见</h2><ol><li>待填写</li></ol><h2>四、问题清单</h2><ol><li>待填写</li></ol><h2>五、评审结论</h2><p>待填写</p><h2>六、评审建议</h2><p>待填写</p>',
  special: '<h1>专题研讨会纪要</h1><h2>一、会议概况</h2><p><strong>会议时间：</strong>待填写&nbsp;&nbsp;<strong>会议地点：</strong>待填写</p><p><strong>主议题：</strong>待填写</p><p><strong>主持人：</strong>待填写&nbsp;&nbsp;<strong>记录人：</strong>待填写</p><h2>二、情况通报</h2><p>待填写</p><h2>三、主要讨论意见</h2><h3>支持意见</h3><p>待填写</p><h3>待商榷事项</h3><p>待填写</p><h2>四、研讨结论与下一步工作</h2><ol><li>待填写</li></ol>',
  office: '<h1>办公会议纪要</h1><h2>一、基本信息</h2><p><strong>会议时间：</strong>待填写&nbsp;&nbsp;<strong>会议地点：</strong>待填写</p><p><strong>主持人：</strong>待填写&nbsp;&nbsp;<strong>记录人：</strong>待填写</p><p><strong>参会人员：</strong>待填写</p><h2>二、议办事项</h2><h3>1. 事项研讨</h3><p>待填写</p><h3>2. 处理意见</h3><p>待填写</p><h3>3. 决议结果</h3><p>待填写</p><h2>三、其他事项</h2><p>待填写</p><h2>四、散会情况</h2><p>会议于待填写时间散会。</p>',
}

async function applyMinutesTemplate(type) {
  const tpl = MINUTES_TEMPLATES[type]
  if (!tpl || !editorContainerRef.value) return
  const hasContent = editorContainerRef.value.innerHTML?.trim().length > 0
  if (hasContent) {
    const { ElMessageBox } = await import('element-plus')
    try {
      await ElMessageBox.confirm('应用模板将覆盖当前编辑内容，是否继续？', '提示', { type: 'warning', confirmButtonText: '覆盖内容', cancelButtonText: '取消' })
    } catch { return }
  }
  editorContainerRef.value.innerHTML = tpl
}

async function refreshSignStatus() {
  loadingStatus.value = true
  try {
    const res = await getMinutesInfo(meetingId, currentMinutesId.value)
    const data = res?.data || res
    const sigs = data?.signatures || []
    minutesStatus.value = data?.status || minutesStatus.value
    updateMinutesRecordMeta(currentMinutesId.value, {
      title: data?.title || normalizedMinutesTitle.value,
      status: minutesStatus.value,
      is_primary: data?.is_primary,
    })
    draftSignature.value = sigs.find(s => s.sign_step === 'draft') || null
    reviewSignatures.value = sigs.filter(s => s.sign_step === 'review')
    if (data?.participant_count != null) {
      totalParticipants.value = data.participant_count
    }
  } catch {}
  finally { loadingStatus.value = false }
}

function startSignPoll() {
  if (signPollTimer) clearInterval(signPollTimer)
  // 仅在已发布 / 审签中时轮询（等待会议端签署或驳回）
  if (!['published', 'reviewing'].includes(minutesStatus.value)) return
  signPollTimer = setInterval(async () => {
    try {
      const res = await getMinutesInfo(meetingId, currentMinutesId.value)
      const data = res?.data || res
      const newStatus = data?.status || minutesStatus.value
      minutesStatus.value = newStatus
      updateMinutesRecordMeta(currentMinutesId.value, {
        title: data?.title || normalizedMinutesTitle.value,
        status: newStatus,
        is_primary: data?.is_primary,
      })
      const sigs = data?.signatures || []
      draftSignature.value = sigs.find(s => s.sign_step === 'draft') || null
      reviewSignatures.value = sigs.filter(s => s.sign_step === 'review')
      if (data?.participant_count != null) {
        totalParticipants.value = data.participant_count
      }
      // 如果已签署完成或被驳回，停止轮询并更新编辑器状态
      if (newStatus === 'signed' || newStatus === 'rejected') {
        clearInterval(signPollTimer)
        signPollTimer = null
        if (editorContainerRef.value) {
          editorContainerRef.value.contentEditable = isEditable.value ? 'true' : 'false'
        }
        if (newStatus === 'signed') {
          loadCheckinParticipants()
        }
      }
    } catch {}
  }, 4000)
}

async function saveMinutes() {
  saving.value = true
  try {
    const content = editorContainerRef.value?.innerHTML || ''
    await updateMinutes(meetingId, buildMinutesPayload(content, { review_conclusion: reviewConclusion.value }), currentMinutesId.value)
    // 保存后如果是 rejected 状，后端会自动重置为 draft
    if (minutesStatus.value === 'rejected') {
      minutesStatus.value = 'draft'
    }
    updateMinutesRecordMeta(currentMinutesId.value, { title: normalizedMinutesTitle.value, status: minutesStatus.value })
    ElMessage.success('保存成功')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function handlePublish() {
  const content = editorContainerRef.value?.innerHTML || ''
  // 先保存再发布
  publishing.value = true
  try {
    await updateMinutes(meetingId, buildMinutesPayload(content), currentMinutesId.value)
    await publishMinutes(meetingId, { minutes_id: currentMinutesId.value, required_signers: normalizeSignerRows() })
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '发布失败')
    publishing.value = false
    return
  }
  minutesStatus.value = 'published'
  updateMinutesRecordMeta(currentMinutesId.value, { title: normalizedMinutesTitle.value, status: 'published' })
  if (editorContainerRef.value) {
    editorContainerRef.value.contentEditable = 'false'
  }
  ElMessage.success('纪要已发布，等待会议端审签')
  setTimeout(() => {
    try { initCanvas() } catch {}
  }, 100)
  startSignPoll()
  publishing.value = false
}

async function handlePolish() {
  const content = editorContainerRef.value?.innerHTML || ''
  if (!content || content === '<p>纪要内容加载失败，请刷新页面。</p>') {
    ElMessage.warning('请先编辑纪要内容')
    return
  }

  // 如果有选中文本，则只润色选中部分；否则润色全文
  const selection = window.getSelection()
  const selectedText = selection.toString()
  const textToPolish = selectedText || editorContainerRef.value?.innerText || ''

  polishing.value = true
  try {
    const res = await polishText({ text: textToPolish, meeting_id: meetingId })
    const polishedText = res?.data?.polished || res?.polished || res?.data?.answer || res?.answer

    if (polishedText) {
      if (selectedText) {
        // 替换选中文本
        document.execCommand('insertText', false, polishedText)
        ElMessage.success('AI 润色已应用到选中文本')
      } else {
        // 替换全文
        editorContainerRef.value.innerHTML = polishedText
        ElMessage.success('AI 润色已应用到全文')
      }
    } else {
      ElMessage.warning('润色结果为空，请重试')
    }
  } catch (e) {
    console.error('润色失败:', e)
    ElMessage.error('AI 润色失败，请稍后重试')
  } finally {
    polishing.value = false
  }
}

// 语音播报 (Web Speech Synthesis)
const isSpeaking = ref(false)
let speechUtterance = null

function handleTTS() {
  if (!('speechSynthesis' in window)) {
    ElMessage.warning('当前浏览器不支持语音播报，请使用 Chrome 或 Edge')
    return
  }

  if (isSpeaking.value) {
    window.speechSynthesis.cancel()
    isSpeaking.value = false
    return
  }

  const text = editorContainerRef.value?.innerText?.trim()
  if (!text) {
    ElMessage.warning('暂无可播报内容')
    return
  }

  const chunks = []
  const maxLen = 200
  let remaining = text
  while (remaining.length > 0) {
    if (remaining.length <= maxLen) {
      chunks.push(remaining)
      break
    }
    let splitIdx = remaining.lastIndexOf('。', maxLen)
    if (splitIdx < 0) splitIdx = remaining.lastIndexOf('，', maxLen)
    if (splitIdx < 0) splitIdx = remaining.lastIndexOf(' ', maxLen)
    if (splitIdx < 0) splitIdx = maxLen
    chunks.push(remaining.slice(0, splitIdx + 1))
    remaining = remaining.slice(splitIdx + 1)
  }

  isSpeaking.value = true
  let idx = 0

  function speakNext() {
    if (idx >= chunks.length || !isSpeaking.value) {
      isSpeaking.value = false
      return
    }
    const utt = new SpeechSynthesisUtterance(chunks[idx])
    utt.lang = 'zh-CN'
    utt.rate = 1.0
    utt.pitch = 1.0
    utt.onend = () => { idx++; speakNext() }
    utt.onerror = () => { isSpeaking.value = false }
    speechUtterance = utt
    window.speechSynthesis.speak(utt)
  }

  speakNext()
}

// Canvas 签名
function startSign(e) {
  isDrawing = true
  currentPath = [{ x: e.offsetX, y: e.offsetY }]
  ctx.beginPath()
  ctx.strokeStyle = penColor.value
  ctx.lineWidth = penWidth.value
  ctx.moveTo(e.offsetX, e.offsetY)
}

function moveSign(e) {
  if (!isDrawing) return
  currentPath.push({ x: e.offsetX, y: e.offsetY })
  ctx.lineTo(e.offsetX, e.offsetY)
  ctx.stroke()
}

function endSign() {
  if (!isDrawing) return
  isDrawing = false
  signPaths.push([...currentPath])
  currentPath = []
}

function clearSignature() {
  ctx.clearRect(0, 0, signatureCanvasRef.value.width, signatureCanvasRef.value.height)
  signPaths = []
}

function undoSignature() {
  if (signPaths.length === 0) return
  signPaths.pop()
  ctx.clearRect(0, 0, signatureCanvasRef.value.width, signatureCanvasRef.value.height)
  // 重绘剩余路径
  signPaths.forEach(path => {
    if (path.length < 2) return
    ctx.beginPath()
    ctx.moveTo(path[0].x, path[0].y)
    path.slice(1).forEach(p => ctx.lineTo(p.x, p.y))
    ctx.stroke()
  })
}

async function submitSignature() {
  if (signPaths.length === 0) {
    ElMessage.warning('请先完成手写签名')
    return
  }

  signing.value = true
  try {
    const canvas = signatureCanvasRef.value
    const signatureImage = canvas.toDataURL('image/png')

    await signMinutes(meetingId, {
      signature_image: signatureImage,
      sign_step: 'draft',
    }, currentMinutesId.value)

    clearSignature()
    ElMessage.success('拟稿签署成功')
    await refreshSignStatus()
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '签署失败')
  } finally {
    signing.value = false
  }
}

function viewVersion(row) {
  ElMessage.info('版本查看功能开发中')
}

function rollbackVersion(row) {
  ElMessage.info('版本回滚功能开发中')
}
</script>

<style lang="scss" scoped>
$panel: #0e1d38;
$panel2: #14284b;
$border: rgba(30,92,162,0.45);
$accent: #3990f1;
$text: #dee5f2;
$text-sub: #7f99be;
$icon: #a4ffe6;
$success: #2bffbc;

.minutes-page {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.minutes-page-header {
  display: flex;
  align-items: center;
  padding: 4px 0;
}

.minutes-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 20px;
}

/* ── 分栏布局 ── */
.minutes-body-layout {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}
.minutes-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.minutes-ref-panel {
  width: 260px;
  flex-shrink: 0;
  background: $panel;
  border: 1px solid $border;
  border-radius: 4px;
  overflow: hidden;
  position: sticky;
  top: 60px;
  max-height: calc(100vh - 100px);
  overflow-y: auto;

  .ref-panel-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 8px 12px;
    background: $panel2;
    border-bottom: 1px solid $border;
    .ref-panel-title { font-size: 13px; font-weight: 600; color: $text; }
  }
  .ref-panel-body { padding: 10px 12px; }

  .ref-section {
    margin-bottom: 12px;
    .ref-section-title { font-size: 11px; font-weight: 700; color: $text-sub; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
    .ref-text { font-size: 12px; color: $text; line-height: 1.6; background: $panel2; padding: 7px 10px; border-radius: 4px; border-left: 2px solid $accent; }
  }
  .ref-kp-item {
    padding: 6px 8px; margin-bottom: 6px;
    background: $panel2; border-radius: 4px; border-left: 2px solid $border;
    .ref-kp-title { font-size: 12px; font-weight: 600; color: $text; margin-bottom: 2px; }
    .ref-kp-content { font-size: 11px; color: $text-sub; line-height: 1.4; }
  }
  .ref-empty {
    text-align: center; padding: 20px 10px;
    .ref-empty-tip { font-size: 12px; color: $text-sub; line-height: 1.5; }
  }
  .ref-generated-at { font-size: 11px; color: $text-sub; margin-top: 6px; text-align: right; }
}
.editor-header-left { display: flex; align-items: center; }

.status-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;

  .el-icon { font-size: 16px; }

  &.published {
    background: rgba(57, 144, 241, 0.1);
    border: 1px solid rgba(57, 144, 241, 0.3);
    color: $accent;
  }
  &.rejected {
    background: rgba(230, 162, 60, 0.1);
    border: 1px solid rgba(230, 162, 60, 0.3);
    color: #e6a23c;
  }
  &.signed {
    background: rgba(43, 255, 188, 0.08);
    border: 1px solid rgba(43, 255, 188, 0.3);
    color: $success;
  }
}

.minutes-editor-area { flex: 0 0 auto; }

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title { font-size: 14px; font-weight: 600; color: $text; }

.editor-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

// 工具栏按钮组
.toolbar-group {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 0 8px;
  border-right: 1px solid rgba(57,144,241,0.2);

  &:last-child { border-right: none; padding-right: 0; }
}

.toolbar-group-primary {
  padding-left: 8px;
}

// AI 工具类按钮（辅助）
.btn-ai-gen {
  background: rgba(57,144,241,0.15) !important;
  border: 1px solid rgba(57,144,241,0.4) !important;
  color: #5aaaf7 !important;
  &:hover { background: rgba(57,144,241,0.3) !important; }
  :deep(.el-icon) { color: #5aaaf7; }
}

.btn-template {
  background: rgba(57,144,241,0.08) !important;
  border: 1px solid rgba(57,144,241,0.25) !important;
  color: #7f99be !important;
  &:hover { background: rgba(57,144,241,0.2) !important; color: #bee0ff !important; }
}

.btn-polish {
  background: rgba(160,120,255,0.1) !important;
  border: 1px solid rgba(160,120,255,0.3) !important;
  color: #b088ff !important;
  &:hover { background: rgba(160,120,255,0.25) !important; }
}

.btn-tts {
  background: rgba(100,150,190,0.08) !important;
  border: 1px solid rgba(100,150,190,0.5) !important;
  color: #7f99be !important;
  &:hover { border-color: #bee0ff !important; color: #dee5f2 !important; background: rgba(100,150,190,0.18) !important; }
}

.btn-tts-active {
  background: rgba(242,75,85,0.1) !important;
  border-color: rgba(242,75,85,0.5) !important;
  color: #f24b55 !important;
}

// 保存按钮（蓝色实心）
.btn-save {
  background: rgba(57,144,241,0.25) !important;
  border: 1px solid #3990f1 !important;
  color: #dee5f2 !important;
  font-weight: 600 !important;
  &:hover { background: rgba(57,144,241,0.5) !important; }
}

// 发布按钮（绿色主色 - 最重要操作）
.btn-publish {
  background: rgba(43,255,188,0.15) !important;
  border: 1px solid rgba(43,255,188,0.6) !important;
  color: #2bffbc !important;
  font-weight: 700 !important;
  box-shadow: 0 0 8px rgba(43,255,188,0.2);
  &:hover { background: rgba(43,255,188,0.3) !important; box-shadow: 0 0 14px rgba(43,255,188,0.4); }
  :deep(.el-icon) { color: #2bffbc; }
}

// 下一步按钮（橙色警告）
.btn-nextstep {
  background: rgba(230,162,60,0.15) !important;
  border: 1px solid rgba(230,162,60,0.5) !important;
  color: #e6a23c !important;
  &:hover { background: rgba(230,162,60,0.3) !important; }
}

.minutes-manage-bar {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.minutes-manage-left,
.minutes-manage-right {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.minutes-manage-label {
  color: $text-sub;
  font-size: 12px;
}

.signer-config-card {
  margin-bottom: 10px;
  padding: 10px 12px;
  border: 1px solid $border;
  border-radius: 4px;
  background: $panel2;
}

.signer-config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  color: $text;
  font-size: 13px;
  font-weight: 600;
}

.signer-config-row {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.editor-wrapper {
  border: 1px solid $border;
  border-radius: 4px;
  overflow: hidden;
}

.review-conclusion-section {
  margin-top: 12px;
  padding: 12px 14px;
  background: $panel2;
  border: 1px solid $border;
  border-radius: 4px;

  .conclusion-title {
    margin: 0 0 8px 0;
    font-size: 13px;
    font-weight: 600;
    color: $accent;
  }
}

.editor-toolbar {
  border-bottom: 1px solid $border;
  padding: 6px 8px;
  background: $panel2;
}

.editor-container {
  min-height: 300px;
  max-height: 460px;
  overflow-y: auto;
  padding: 14px 16px;
  font-size: 13px;
  line-height: 1.8;
  outline: none;
  color: $text;
  background: $panel;

  &.readonly {
    opacity: 0.85;
    cursor: default;
    user-select: text;
    background: $panel2;
  }

  &:focus {
    box-shadow: inset 0 0 0 2px rgba(57,144,241,0.15);
  }

  :deep(h1) { font-size: 20px; margin: 14px 0 6px; color: $text; }
  :deep(h2) { font-size: 16px; margin: 12px 0 5px; color: $text; }
  :deep(table) { width: 100%; border-collapse: collapse; margin: 10px 0; }
  :deep(td), :deep(th) { border: 1px solid $border; padding: 6px 8px; font-size: 12px; }
}

.sign-area { flex: 0 0 auto; }
.checkin-mgmt-area { margin-top: 14px; }
.checkin-mgmt-tip {
  font-size: 12px;
  color: $text-sub;
  margin: 0 0 4px;
}
.offline-sign-canvas {
  display: block;
  width: 100%;
  border: 2px dashed $border;
  border-radius: 4px;
  cursor: crosshair;
  touch-action: none;
  background: #fff;
}
.offline-expand-canvas {
  display: block;
  width: 100%;
  border: 2px dashed $accent;
  border-radius: 4px;
  cursor: crosshair;
  touch-action: none;
  background: #fff;
}
.sign-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.sign-header-actions {
  display: flex;
  gap: 6px;
  align-items: center;
}

.review-list {
  margin-top: 6px;
}

.review-list-title {
  font-size: 12px;
  color: $text-sub;
  margin-bottom: 6px;
  font-weight: 500;
}

.review-empty {
  color: $text-sub;
  font-size: 12px;
  padding: 6px 0;
  font-style: italic;
}

.all-signed-tip {
  margin-top: 10px;
  padding: 6px 0;
}

.draft-done {
  text-align: center;
  padding: 20px 0;
}
.sign-flow {
  .sign-status-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 0;
    border-bottom: 1px solid $border;

    .sign-time {
      margin-left: auto;
      font-size: 12px;
      color: $text-sub;
    }
  }
}

.draft-sign-inline {
  margin-top: 10px;
  padding: 12px 14px;
  border: 1px solid $border;
  border-radius: 4px;
  background: $panel2;

  .canvas-controls {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
  }

  .signature-canvas {
    border: 2px dashed rgba(57,144,241,0.3);
    border-radius: 4px;
    cursor: crosshair;
    display: block;
    touch-action: none;
    background: #0b1a2e;

    &:hover {
      border-color: $accent;
    }
  }
}
</style>
