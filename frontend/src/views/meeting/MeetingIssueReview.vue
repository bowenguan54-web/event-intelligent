<template>
  <div class="issue-review-page">
    <div class="page-header">
      <el-button :icon="ArrowLeft" text @click="router.push(`/meeting/${meetingId}/detail`)" />
      <h2 class="page-title">问题记录审查</h2>
      <el-tag v-if="issueReviewStatus === 'completed'" type="success" effect="plain">问题审查已完成</el-tag>
      <el-tag v-else-if="issueReviewStatus === 'skipped'" type="info" effect="plain">已跳过问题审查</el-tag>
      <div class="header-actions">
        <el-button @click="goToMinutes">前往会议纪要</el-button>
        <template v-if="!isReadOnly">
          <el-button type="warning" plain :loading="finishing" @click="skipIssueReview">不归档并跳过</el-button>
          <el-button type="primary" :loading="finishing" @click="completeIssueReview">完成问题审查</el-button>
        </template>
      </div>
    </div>

    <el-alert
      v-if="isReadOnly"
      :title="issueReviewStatus === 'skipped' ? '已跳过问题审查，当前为只读状态' : '问题审查已完成，当前为只读状态'"
      type="info"
      show-icon
      :closable="false"
      style="margin: 0 24px 12px"
    />
    <div class="page-body">
      <!-- 左侧：问题列表 -->
      <div class="issues-main">
        <!-- 工具栏 -->
        <div class="toolbar">
          <el-checkbox
            v-model="allSelected"
            :indeterminate="isIndeterminate"
            :disabled="isReadOnly"
            @change="toggleSelectAll"
          >全选</el-checkbox>
          <el-tag size="small" type="info" effect="plain" style="margin-left:8px">
            已选 {{ selectedIds.length }} / 共 {{ issues.length }} 条
          </el-tag>
          <div style="margin-left:auto;display:flex;align-items:center;gap:10px">
            <el-switch
              v-model="requireSign"
              @change="saveDraftState"
              active-text="需要审签"
              inactive-text="无需审签"
              style="--el-switch-on-color:#409eff"
            />
            <el-button
              type="primary"
              :disabled="selectedIds.length === 0 || isReadOnly"
              :loading="archiving"
              @click="handleArchive"
            >
              <el-icon><FolderIcon /></el-icon>
              归档选中问题 ({{ selectedIds.length }})
            </el-button>
          </div>
        </div>

        <el-divider style="margin:10px 0" />

        <!-- 问题列表 -->
        <div v-if="loading" class="loading-state">
          <el-skeleton :rows="5" animated />
        </div>
        <div v-else-if="issues.length === 0" class="empty-state">
          <el-empty description="暂无问题记录" />
        </div>
        <div v-else class="issue-list">
          <div
            v-for="issue in issues"
            :key="issue.id"
            class="issue-card"
            :class="{ 'is-proofread': issue.proofread, 'is-selected': selectedIds.includes(issue.id), 'is-archived': issue.archived }"
          >
            <!-- 勾选 + 校对状态 -->
            <div class="issue-card-left">
              <el-checkbox
                :model-value="selectedIds.includes(issue.id)"
                :disabled="!!issue.archived || isReadOnly"
                @change="toggleSelect(issue.id)"
              />
              <el-tag
                :type="issue.proofread ? 'success' : 'warning'"
                size="small"
                effect="plain"
                class="proofread-tag"
              >
                {{ issue.proofread ? '已校对' : '未校对' }}
              </el-tag>
              <el-tag v-if="issue.archived" type="info" size="small" effect="plain">已归档</el-tag>
            </div>

            <!-- 内容区 -->
            <div class="issue-card-body">
              <!-- 编辑模式 -->
              <template v-if="editingId === issue.id && !issue.proofread">
                <el-input
                  v-model="editingContent"
                  type="textarea"
                  :rows="3"
                  placeholder="修改问题内容..."
                />
                <div class="edit-actions" style="margin-top:8px">
                  <el-button type="primary" size="small" @click="saveEdit(issue)">保存并确认校对</el-button>
                  <el-button size="small" @click="editingId = null">取消</el-button>
                </div>
              </template>
              <!-- 展示模式 -->
              <template v-else>
                <div class="issue-content">{{ issue.content }}</div>
                <div v-if="issue.response" class="issue-response">
                  <el-icon style="font-size:14px;margin-right:4px"><ChatDotRound /></el-icon>
                  {{ issue.response }}
                </div>
                <div class="issue-meta">
                  <el-tag :type="statusType(issue.status)" size="small" effect="plain">{{ statusLabel(issue.status) }}</el-tag>
                  <span v-if="issue.reporter_name" class="reporter">{{ issue.reporter_name }}</span>
                </div>
              </template>
            </div>

            <!-- 操作 -->
            <div class="issue-card-actions">
              <template v-if="!issue.archived && !isReadOnly">
                <!-- 未校对：可修改一次 -->
                <template v-if="!issue.proofread">
                  <el-button
                    v-if="editingId !== issue.id"
                    size="small"
                    type="primary"
                    plain
                    @click="startEdit(issue)"
                  >
                    <el-icon><Edit /></el-icon> 修改
                  </el-button>
                  <el-button
                    size="small"
                    type="success"
                    plain
                    @click="confirmProofread(issue)"
                  >
                    <el-icon><Check /></el-icon> 确认校对
                  </el-button>
                </template>
                <!-- 已校对：只读，显示提示 -->
                <span v-else class="proofread-lock">
                  <el-icon><Lock /></el-icon> 已锁定
                </span>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：统计面板 -->
      <div class="stats-panel">
        <el-card shadow="never" class="stats-card">
          <div class="stats-title">📊 问题统计</div>
          <el-divider style="margin:10px 0" />
          <div class="stats-row">
            <span class="stats-label">总计</span>
            <span class="stats-val">{{ issues.length }}</span>
          </div>
          <div class="stats-row">
            <span class="stats-label">已校对</span>
            <span class="stats-val" style="color:#67c23a">{{ proofreadCount }}</span>
          </div>
          <div class="stats-row">
            <span class="stats-label">未校对</span>
            <span class="stats-val" style="color:#e6a23c">{{ issues.length - proofreadCount }}</span>
          </div>
          <div class="stats-row">
            <span class="stats-label">已归档</span>
            <span class="stats-val" style="color:#909399">{{ archivedCount }}</span>
          </div>
          <el-divider style="margin:10px 0" />
          <div class="stats-sign-tip">
            <div class="stats-sign-label">归档审签设置</div>
            <el-switch v-model="requireSign" size="small" />
            <div class="stats-sign-desc">
              {{ requireSign ? '归档后将触发专家组长在会议端签字确认' : '归档后无需签字，直接完成归档' }}
            </div>
          </div>
        </el-card>

        <el-card shadow="never" class="stats-card" style="margin-top:16px">
          <div class="stats-title">⚠️ 校对说明</div>
          <el-divider style="margin:10px 0" />
          <div class="rule-item">
            <el-tag type="success" size="small" effect="plain">已校对</el-tag>
            <span>会上已确认的问题，内容已锁定不可修改</span>
          </div>
          <div class="rule-item">
            <el-tag type="warning" size="small" effect="plain">未校对</el-tag>
            <span>可修改一次内容，修改后自动锁定</span>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 归档确认弹窗 -->
    <el-dialog v-model="showArchiveDialog" title="确认归档" width="420px" :close-on-click-modal="false">
      <div class="archive-confirm-body">
        <p>即将对 <strong>{{ selectedIds.length }}</strong> 条问题记录进行归档。</p>
        <el-alert
          v-if="requireSign"
          title="已开启审签：归档后将通知专家组长在会议端完成签字确认"
          type="warning"
          :closable="false"
          style="margin-top:12px"
        />
        <el-alert
          v-else
          title="未启用审签：问题将直接归档"
          type="info"
          :closable="false"
          style="margin-top:12px"
        />
        <p style="margin-top:12px;color:#8bb3d9;font-size:14px">归档后问题状态不可再次修改，请确认无误后继续。</p>
      </div>
      <template #footer>
        <el-button @click="showArchiveDialog = false">取消</el-button>
        <el-button type="primary" :loading="archiving" @click="confirmArchive">确认归档</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getMeetingById, getMeetingIssues, updateIssueReviewStatus, updateMeetingIssue } from '@/api/meeting'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Edit, Check } from '@element-plus/icons-vue'
import { Lock, FolderOpened as FolderIcon, ChatDotRound } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const meetingId = route.params.id

const issues = ref([])
const loading = ref(true)
const flowLoading = ref(false)
const archiving = ref(false)
const requireSign = ref(false)
const showArchiveDialog = ref(false)
const issueReviewStatus = ref('pending')
const isReadOnly = computed(() => issueReviewStatus.value === 'completed' || issueReviewStatus.value === 'skipped')
const finishing = ref(false)
const issueReviewDraftKey = `meeting_issue_review_draft_${meetingId}`

// 选择状态
const selectedIds = ref([])
const allSelected = computed({
  get: () => issues.value.filter(i => !i.archived).length > 0 && selectedIds.value.length === issues.value.filter(i => !i.archived).length,
  set: () => {}
})
const isIndeterminate = computed(() => selectedIds.value.length > 0 && !allSelected.value)

function toggleSelectAll(val) {
  if (val) {
    selectedIds.value = issues.value.filter(i => !i.archived).map(i => i.id)
  } else {
    selectedIds.value = []
  }
  saveDraftState()
}

function toggleSelect(id) {
  const idx = selectedIds.value.indexOf(id)
  if (idx === -1) {
    selectedIds.value.push(id)
  } else {
    selectedIds.value.splice(idx, 1)
  }
  saveDraftState()
}

// 统计
const proofreadCount = computed(() => issues.value.filter(i => i.proofread).length)
const archivedCount = computed(() => issues.value.filter(i => i.archived).length)

// 编辑
const editingId = ref(null)
const editingContent = ref('')

function startEdit(issue) {
  editingId.value = issue.id
  editingContent.value = issue.content
  saveDraftState()
}

async function saveEdit(issue) {
  const content = editingContent.value.trim()
  if (!content) return
  try {
    await updateMeetingIssue(meetingId, issue.id, { content, proofread: true })
    issue.content = content
    issue.proofread = true
    editingId.value = null
    saveDraftState()
    ElMessage.success('已保存并标记为已校对')
  } catch {
    ElMessage.error('保存失败')
  }
}

async function confirmProofread(issue) {
  try {
    await updateMeetingIssue(meetingId, issue.id, { proofread: true })
    issue.proofread = true
    saveDraftState()
    ElMessage.success('已标记为已校对')
  } catch {
    ElMessage.error('操作失败')
  }
}

function statusLabel(s) {
  const map = { open: '待处理', explained: '解释', adopted_unresolved: '采纳-未解决', adopted_resolved: '采纳-已解决', adopted: '已采纳' }
  return map[s] || s || '待处理'
}

function statusType(s) {
  const map = { open: 'info', explained: 'warning', adopted_unresolved: 'warning', adopted_resolved: 'success', adopted: 'success' }
  return map[s] || 'info'
}

function handleArchive() {
  if (selectedIds.value.length === 0) return
  showArchiveDialog.value = true
}

async function confirmArchive() {
  archiving.value = true
  try {
    // 批量标记归档（前端本地操作）
    for (const id of selectedIds.value) {
      const issue = issues.value.find(i => i.id === id)
      if (issue) {
        await updateMeetingIssue(meetingId, id, { archived: true })
        issue.archived = true
      }
    }
    const archivedCount = selectedIds.value.length
    selectedIds.value = []
    showArchiveDialog.value = false
    saveDraftState()
    ElMessage.success(`已归档 ${archivedCount} 条问题记录`)
    if (requireSign.value) {
      ElMessage({
        type: 'warning',
        message: '已通知专家组长在会议端完成归档审签',
        duration: 5000,
      })
    }
  } catch {
    ElMessage.error('归档失败')
  } finally {
    archiving.value = false
  }
}

function saveDraftState() {
  localStorage.setItem(issueReviewDraftKey, JSON.stringify({
    selectedIds: selectedIds.value,
    requireSign: requireSign.value,
    editingId: editingId.value,
    editingContent: editingContent.value,
  }))
}

function restoreDraftState() {
  try {
    const raw = localStorage.getItem(issueReviewDraftKey)
    if (!raw) return
    const data = JSON.parse(raw)
    selectedIds.value = Array.isArray(data?.selectedIds) ? data.selectedIds : []
    requireSign.value = !!data?.requireSign
    editingId.value = data?.editingId || null
    editingContent.value = data?.editingContent || ''
  } catch {}
}

async function persistCurrentEditing() {
  if (!editingId.value) return true
  const issue = issues.value.find(item => item.id === editingId.value)
  if (!issue) {
    editingId.value = null
    return true
  }
  if ((editingContent.value || '').trim() === (issue.content || '').trim()) {
    editingId.value = null
    saveDraftState()
    return true
  }
  await saveEdit(issue)
  return editingId.value === null
}

async function loadMeetingFlow() {
  flowLoading.value = true
  try {
    const res = await getMeetingById(meetingId)
    const data = res?.data || res
    issueReviewStatus.value = data?.issue_review_status || 'pending'
    requireSign.value = !!data?.issue_review_require_sign
  } catch {
    issueReviewStatus.value = issueReviewStatus.value || 'pending'
  } finally {
    flowLoading.value = false
  }
}

async function loadIssues() {
  loading.value = true
  try {
    const res = await getMeetingIssues(meetingId)
    const list = Array.isArray(res) ? res : (res?.data || [])
    issues.value = list.map(item => ({
      ...item,
      proofread: item.proofread ?? (item.status === 'adopted_resolved'),
      archived: item.archived ?? false,
    }))
    restoreDraftState()
    selectedIds.value = selectedIds.value.filter(id => issues.value.some(item => item.id === id && !item.archived))
  } catch {
    ElMessage.error('加载问题记录失败')
  } finally {
    loading.value = false
  }
}

async function goToMinutes() {
  const ok = await persistCurrentEditing()
  if (!ok) return
  saveDraftState()
  router.push(`/meeting/${meetingId}/minutes`)
}

async function finalizeIssueReview(nextStatus) {
  const ok = await persistCurrentEditing()
  if (!ok) return
  finishing.value = true
  try {
    const res = await updateIssueReviewStatus(meetingId, {
      issue_review_status: nextStatus,
      issue_review_require_sign: requireSign.value,
    })
    const data = res?.data || res
    issueReviewStatus.value = data?.issue_review_status || nextStatus
    localStorage.removeItem(issueReviewDraftKey)
    // 通知会议纪要页问题审查已完成/跳过
    localStorage.setItem(`issueReviewDone_${meetingId}`, 'true')
    if (data?.status === 'archived') {
      ElMessage.success('会议纪要与问题审查均已完成，会议已归档')
      router.push('/meeting')
      return
    }
    if (nextStatus === 'skipped') {
      ElMessage.success('已跳过问题审查，请继续完成会议纪要审签')
    } else {
      ElMessage.success('问题审查已完成，请继续完成会议纪要审签')
    }
    router.push(`/meeting/${meetingId}/minutes`)
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '保存问题审查状态失败')
  } finally {
    finishing.value = false
  }
}

async function skipIssueReview() {
  await finalizeIssueReview('skipped')
}

async function completeIssueReview() {
  await finalizeIssueReview('completed')
}

onMounted(async () => {
  // 清理可能残留的 el-overlay（如从会议纪要页跳转过来时遗留的弹窗遮罩）
  document.querySelectorAll('.el-overlay').forEach(el => el.remove())
  document.body.classList.remove('el-popup-parent--hidden')
  document.body.style.overflow = ''
  document.body.style.paddingRight = ''
  await Promise.all([loadMeetingFlow(), loadIssues()])
})

watch(requireSign, () => saveDraftState())
</script>

<style scoped>
.issue-review-page {
  min-height: 100vh;
  background: #0a1628;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 24px;
  background: #0e1d38;
  border-bottom: 1px solid rgba(30,92,162,0.45);
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #dee5f2;
}

.header-tip {
  font-size: 12px;
  color: #7f99be;
  margin-left: 6px;
}

.page-body {
  display: flex;
  gap: 14px;
  padding: 14px 24px;
  flex: 1;
}

.issues-main {
  flex: 1;
  min-width: 0;
}

.toolbar {
  display: flex;
  align-items: center;
  padding: 7px 12px;
  background: #14284b;
  border: 1px solid rgba(30,92,162,0.45);
  border-radius: 4px;
}

.issue-list {
  display: flex;
  flex-direction: column;
  gap: 7px;
  margin-top: 8px;
}

.issue-card {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 12px;
  background: #0e1d38;
  border: 1px solid rgba(30,92,162,0.45);
  border-radius: 6px;
  transition: all 0.15s;
}

.issue-card:hover {
  border-color: #3990f1;
  background: rgba(57,144,241,0.05);
}

.issue-card.is-proofread {
  border-left: 3px solid rgba(43,255,188,0.5);
}

.issue-card.is-selected {
  border-color: rgba(57,144,241,0.5);
  background: rgba(57,144,241,0.06);
}

.issue-card.is-archived {
  opacity: 0.55;
  border-style: dashed;
}

.issue-card-left {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  flex-shrink: 0;
  padding-top: 2px;
}

.proofread-tag { font-size: 13px; }

.issue-card-body {
  flex: 1;
  min-width: 0;
}

.issue-content {
  font-size: 13px;
  color: #dee5f2;
  line-height: 1.6;
  margin-bottom: 4px;
}

.issue-response {
  font-size: 12px;
  color: #7f99be;
  display: flex;
  align-items: center;
  margin-bottom: 4px;
}

.issue-meta {
  display: flex;
  align-items: center;
  gap: 6px;
}

.reporter {
  font-size: 12px;
  color: #7f99be;
}

.issue-card-actions {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex-shrink: 0;
  align-items: flex-end;
}

.proofread-lock {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  color: #7f99be;
}

/* 统计面板 */
.stats-panel {
  width: 200px;
  flex-shrink: 0;
}

.stats-card {
  background: #0e1d38 !important;
  border: 1px solid rgba(30,92,162,0.45) !important;
  border-radius: 6px !important;
  color: #dee5f2;
}

.stats-title {
  font-size: 13px;
  font-weight: 600;
  color: #dee5f2;
}

.stats-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 0;
}

.stats-label {
  font-size: 12px;
  color: #7f99be;
}

.stats-val {
  font-size: 18px;
  font-weight: 700;
  color: #dee5f2;
}

.stats-sign-tip {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stats-sign-label {
  font-size: 12px;
  color: #7f99be;
}

.stats-sign-desc {
  font-size: 12px;
  color: #7f99be;
  line-height: 1.5;
}

.rule-item {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 4px 0;
  font-size: 12px;
  color: #7f99be;
  line-height: 1.5;
}

.loading-state, .empty-state {
  padding: 32px 0;
  text-align: center;
}

.archive-confirm-body p {
  color: #dee5f2;
  font-size: 13px;
}

:deep(.el-card__body) {
  padding: 10px 12px;
}

:deep(.el-card__header) {
  background: #14284b !important;
  border-bottom: 1px solid rgba(30,92,162,0.45) !important;
  padding: 8px 12px
}
</style>
