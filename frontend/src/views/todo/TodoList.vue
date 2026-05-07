﻿﻿﻿<template>
  <div class="page-container todo-page">

    <!-- 查询区域 -->
    <el-card shadow="never" class="query-card">
      <el-form :model="filters" inline class="query-form">
        <el-form-item label="完成情况">
          <el-select v-model="filters.status" placeholder="全部状态" clearable style="width: 140px">
            <el-option label="待处理" value="pending" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已逾期" value="overdue" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="filters.priority" placeholder="全部优先级" clearable style="width: 140px">
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 260px"
          />
        </el-form-item>
        <el-form-item label="会议名称">
          <el-input v-model="filters.meetingName" placeholder="搜索关联会议" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="事项关键词">
          <el-input v-model="filters.keyword" placeholder="搜索事项描述" prefix-icon="Search" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">
            <el-icon><Search /></el-icon>查询
          </el-button>
          <el-button @click="handleResetQuery">
            <el-icon><RefreshRight /></el-icon>重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 待办列表 -->
    <el-card shadow="never" class="todo-list-card">
      <template #header>
        <div class="list-card-header">
          <span class="list-card-title">待办事项列表</span>
          <el-button type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon>新建待办
          </el-button>
        </div>
      </template>

      <!-- 提醒区（即将会议 + 紧急待办） -->
      <div class="reminder-inline">
        <div class="reminder-inline-header">
          <el-icon class="rp-icon"><Bell /></el-icon>
          <span class="rp-title">我的待办提醒</span>
          <span class="rp-date">{{ todayStr }}</span>
        </div>
        <div class="reminder-body">
          <div class="reminder-block">
            <div class="rb-label"><el-icon><Calendar /></el-icon>即将参加的会议</div>
            <div class="rb-list">
              <div v-for="m in upcomingMeetings" :key="m.id" class="rb-item rb-meeting"
                :class="{ 'rb-item-active': selectedMeeting?.id === m.id }"
                @click="selectMeetingItem(m)" style="cursor:pointer">
                <div class="rbi-left">
                  <div class="rbi-title">{{ m.title }}</div>
                  <div class="rbi-meta">{{ m.time }} · {{ m.location }}</div>
                </div>
                <el-tag :type="m.urgent ? 'danger' : 'warning'" size="small" effect="plain">{{ m.countdown }}</el-tag>
              </div>
              <div v-if="!upcomingMeetings.length" class="rb-empty">今天无会议安排</div>
            </div>
          </div>
          <div class="reminder-block">
            <div class="rb-label"><el-icon><Warning /></el-icon>需要处理的待办</div>
            <div class="rb-list">
              <div v-for="t in urgentTodos" :key="t.id" class="rb-item rb-todo"
                :class="{ 'rb-item-active': selectedTodo?.id === t.id, 'rb-reviewer': t.is_reviewer }"
                @click="selectTodoItem(t)" style="cursor:pointer">
                <div class="rbi-left">
                  <div class="rbi-title">
                    {{ t.title }}
                    <el-tag v-if="t.is_reviewer && t.review_status === 'pending_review'" type="danger" size="small" effect="dark" style="margin-left:6px">待你审核</el-tag>
                    <el-tag v-else-if="!t.is_self_created && !t.acknowledged" type="danger" size="small" style="margin-left:6px">待确认</el-tag>
                    <el-tag v-else-if="t.review_status === 'pending_review'" type="warning" size="small" style="margin-left:6px">审核中</el-tag>
                    <el-tag v-if="t.review_status === 'approved'" type="success" size="small" style="margin-left:6px">已通过</el-tag>
                    <el-tag v-if="t.review_status === 'rejected'" type="danger" size="small" style="margin-left:6px">已驳回</el-tag>
                  </div>
                  <div class="rbi-meta">
                    <template v-if="t.is_reviewer">
                      提交人：{{ t.submitter_name || t.assignee_name }} &nbsp;·&nbsp; {{ t.source }}
                    </template>
                    <template v-else>
                      责任人：{{ t.assignee_name }} &nbsp;·&nbsp; {{ t.source }}
                    </template>
                    <el-tag v-if="t.is_reviewer" size="small" type="danger" style="margin-left:6px">需你审核</el-tag>
                    <el-tag v-else-if="!t.is_self_created" size="small" type="info" style="margin-left:6px">{{ t.creator_name || '他人' }}指派</el-tag>
                    <el-tag v-else size="small" type="success" style="margin-left:6px">自建</el-tag>
                    <el-tag v-if="t.priority" :type="priorityType(t.priority)" size="small" style="margin-left:6px">{{ priorityLabel(t.priority) }}</el-tag>
                  </div>
                </div>
                <el-tag v-if="t.is_reviewer" type="danger" size="small" effect="plain">待审核</el-tag>
                <el-tag v-else :type="t.overdue ? 'danger' : 'warning'" size="small" effect="plain">
                  {{ t.overdue ? '已逾期' : '今日截止' }}
                </el-tag>
              </div>
              <div v-if="!urgentTodos.length" class="rb-empty">暂无紧急待办</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 会议详情展示?-->
      <div v-if="selectedMeeting" class="todo-detail-panel">
        <div class="detail-panel-header">
          <span class="detail-panel-title">会议详情</span>
          <div class="detail-panel-actions">
            <el-button size="small" @click="selectedMeeting = null">
              <el-icon><Close /></el-icon>关闭
            </el-button>
          </div>
        </div>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="会议名称" :span="2">{{ selectedMeeting.title }}</el-descriptions-item>
          <el-descriptions-item label="会议时间">{{ selectedMeeting.time }}</el-descriptions-item>
          <el-descriptions-item label="会议地点">{{ selectedMeeting.location || '未指定' }}</el-descriptions-item>
          <el-descriptions-item label="倒计时">
            <el-tag :type="selectedMeeting.urgent ? 'danger' : 'warning'" size="small">{{ selectedMeeting.countdown }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="参会人员">{{ selectedMeeting.participants || '待确认' }}</el-descriptions-item>
          <el-descriptions-item label="会议议题" :span="2">{{ selectedMeeting.agenda || '暂无议题' }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ selectedMeeting.remark || '无' }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 待办详情展示?-->
      <div v-if="selectedTodo" class="todo-detail-panel">
        <div class="detail-panel-header">
          <span class="detail-panel-title">
            <template v-if="selectedTodo.is_reviewer">审核事项详情</template>
            <template v-else>待办事项详情</template>
          </span>
          <div class="detail-panel-actions">
            <!-- 非自建且未确认：显示确认知晓按钮（不是审核人角色时） -->
            <el-button v-if="!selectedTodo.is_reviewer && !selectedTodo.is_self_created && !selectedTodo.acknowledged" type="warning" size="small" @click="handleAcknowledge(selectedTodo)">
              <el-icon><Check /></el-icon>确认知晓
            </el-button>
            <!-- 自建待办才可编辑 -->
            <el-button v-if="selectedTodo.is_self_created" type="primary" size="small" @click="openDetail(selectedTodo)">
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button size="small" @click="selectedTodo = null">
              <el-icon><Close /></el-icon>关闭
            </el-button>
          </div>
        </div>

        <!-- 审核人角色提?-->
        <el-alert v-if="selectedTodo.is_reviewer && selectedTodo.review_status === 'pending_review'"
          title="该事项已由责任人提交完成审核，请查看证明材料后审核" type="warning" :closable="false" show-icon style="margin-bottom:12px" />

        <!-- 非自建且未确认的提示 -->
        <el-alert v-if="!selectedTodo.is_reviewer && !selectedTodo.is_self_created && !selectedTodo.acknowledged"
          title="此待办事项由上级指派，请确认知晓后方可处理" type="warning" :closable="false" show-icon style="margin-bottom:12px" />

        <el-descriptions :column="2" border>
          <el-descriptions-item label="事项描述" :span="2">{{ selectedTodo.title }}</el-descriptions-item>
          <el-descriptions-item label="详细说明" :span="2">{{ selectedTodo.description || '无' }}</el-descriptions-item>
          <el-descriptions-item label="责任人" prop="assignee_name">{{ selectedTodo.assignee_name || '未指定' }}</el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="priorityType(selectedTodo.priority)" size="small">{{ priorityLabel(selectedTodo.priority) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="截止日期">
            <span :class="{ overdue: isOverdue(selectedTodo) }">{{ selectedTodo.due_date || '未设置' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="当前状态">
            <el-tag :type="statusType(selectedTodo.status)" size="small">{{ statusLabel(selectedTodo.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="来源">
            <el-tag v-if="selectedTodo.is_self_created" type="success" size="small">自建</el-tag>
            <span v-else-if="selectedTodo.is_reviewer">提交人：{{ selectedTodo.submitter_name || selectedTodo.assignee_name }} &nbsp;·&nbsp; {{ selectedTodo.source || '会议关联' }}</span>
            <span v-else>{{ selectedTodo.creator_name || '他人' }}指派（{{ selectedTodo.source || '会议关联' }}）</span>
          </el-descriptions-item>
          <el-descriptions-item label="审核状态">
            <el-tag v-if="!selectedTodo.review_status" type="info" size="small">无需审核</el-tag>
            <el-tag v-else-if="selectedTodo.review_status === 'pending_review'" type="warning" size="small">等待审核</el-tag>
            <el-tag v-else-if="selectedTodo.review_status === 'approved'" type="success" size="small">审核通过</el-tag>
            <el-tag v-else-if="selectedTodo.review_status === 'rejected'" type="danger" size="small">审核驳回</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ selectedTodo.created_at || '--' }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ selectedTodo.updated_at || '--' }}</el-descriptions-item>
        </el-descriptions>

        <!-- 完成操作?-->
        <div class="todo-action-area" v-if="selectedTodo.is_reviewer || selectedTodo.acknowledged || selectedTodo.is_self_created">
          <!-- 审核人角色：显示已提交的证明材料和审核按?-->
          <template v-if="selectedTodo.is_reviewer">
            <div v-if="selectedTodo.need_proof && selectedTodo.proof_files?.length" class="action-section">
              <span class="action-title">证明材料</span>
              <div class="proof-file-list">
                <div v-for="(f, idx) in selectedTodo.proof_files" :key="idx" class="proof-file-item">
                  <el-icon><Document /></el-icon>
                  <span>{{ f.name }}</span>
                </div>
              </div>
            </div>
            <div v-if="selectedTodo.review_status === 'pending_review'" class="action-section review-section">
              <span class="action-title">审核操作</span>
              <div class="review-actions">
                <el-input v-model="reviewComment" type="textarea" :rows="2" placeholder="审核意见（可选）" style="margin-bottom:8px" />
                <div class="review-btns">
                  <el-button type="success" @click="handleReviewApprove(selectedTodo)">
                    <el-icon><Check /></el-icon>审核通过
                  </el-button>
                  <el-button type="danger" @click="handleReviewReject(selectedTodo)">
                    <el-icon><Close /></el-icon>驳回
                  </el-button>
                </div>
              </div>
            </div>
            <div v-else-if="selectedTodo.review_status === 'approved'" class="action-section">
              <span class="action-title">审核结果</span>
              <el-tag type="success" size="small" effect="dark">已审核通过</el-tag>
            </div>
            <div v-else-if="selectedTodo.review_status === 'rejected'" class="action-section">
              <span class="action-title">审核结果</span>
              <el-tag type="danger" size="small" effect="dark">已驳回</el-tag>
            </div>
          </template>

          <!-- 非审核人角色的操作区 -->
          <template v-else>
            <div class="action-section">
            <span class="action-title">完成情况</span>
            <!-- 自建待办：直接切换完成状?-->
            <template v-if="selectedTodo.is_self_created">
              <el-switch
                :model-value="selectedTodo.status === 'completed'"
                @change="(val) => handleToggleComplete(selectedTodo, val)"
                active-text="已完成"
                inactive-text="未完成"
                inline-prompt
                style="--el-switch-on-color: #67c23a; --el-switch-off-color: #909399"
              />
            </template>
            <!-- 他人指派的待办：需要提交审?-->
            <template v-else>
              <template v-if="!selectedTodo.review_status && selectedTodo.status !== 'completed'">
                <el-button type="success" size="small" @click="openSubmitReview(selectedTodo)">
                  <el-icon><Upload /></el-icon>提交完成审核
                </el-button>
              </template>
              <template v-else-if="selectedTodo.review_status === 'pending_review'">
                <el-tag type="warning" size="small" effect="dark" style="margin-right:8px">已提交，等待上级审核</el-tag>
              </template>
              <template v-else-if="selectedTodo.review_status === 'rejected'">
                <el-tag type="danger" size="small" effect="dark" style="margin-right:8px">审核驳回，请重新提交</el-tag>
                <el-button type="warning" size="small" @click="openSubmitReview(selectedTodo)">
                  <el-icon><Upload /></el-icon>重新提交
                </el-button>
              </template>
              <template v-else-if="selectedTodo.review_status === 'approved'">
                <el-tag type="success" size="small" effect="dark">审核通过，事项已完成</el-tag>
              </template>
            </template>
          </div>

          <!-- 上传证明材料区（非自?& 需要上传证?& 不是审核人角色） -->
          <div v-if="!selectedTodo.is_self_created && selectedTodo.need_proof && !selectedTodo.is_reviewer" class="action-section proof-section">
            <span class="action-title">证明材料</span>
            <div class="proof-upload-area">
              <el-upload
                :file-list="selectedTodo.proof_files"
                :auto-upload="false"
                :on-change="(file) => handleProofFileChange(file, selectedTodo)"
                :on-remove="(file) => handleProofFileRemove(file, selectedTodo)"
                accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.xlsx,.xls"
                :limit="5"
              >
                <el-button size="small" type="info" plain>
                  <el-icon><Upload /></el-icon>上传证明文件
                </el-button>
                <template #tip>
                  <div class="upload-tip">支持 PDF/Word/Excel/图片，最多5个文件</div>
                </template>
              </el-upload>
            </div>
          </div>
          </template>
        </div>
      </div>
    </el-card>

    <!-- 新建/编辑待办弹窗 -->
    <el-dialog v-model="showCreateDialog" :title="editingTodo ? '编辑待办' : '新建待办'" width="560px">
      <el-form ref="todoFormRef" :model="todoForm" :rules="todoRules" label-width="80px">
        <el-form-item label="事项描述" prop="title">
          <el-input v-model="todoForm.title" placeholder="请输入待办事项描述" />
        </el-form-item>
        <el-form-item label="详细说明">
          <el-input v-model="todoForm.description" type="textarea" :rows="3" />
        </el-form-item>
          <el-form-item label="责任人" prop="assignee_id">
          <el-select v-model="todoForm.assignee_id" placeholder="选择责任人" filterable style="width: 100%">
            <el-option v-for="u in userOptions" :key="u.id" :label="u.real_name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker v-model="todoForm.due_date" type="date" placeholder="选择截止日期" style="width: 100%" />
        </el-form-item>
          <el-form-item label="优先级">
          <el-radio-group v-model="todoForm.priority">
            <el-radio value="high">高</el-radio>
            <el-radio value="medium">高</el-radio>
            <el-radio value="low">高</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="关联会议">
          <el-select v-model="todoForm.meeting_id" placeholder="选择关联会议(可选)" clearable style="width: 100%">
            <el-option label="项目周例会" :value="1" />
            <el-option label="需求评审会" :value="2" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSaveTodo" :loading="savingTodo">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getTodoList, createTodo, updateTodo } from '@/api/todo'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const todayStr = dayjs().format('YYYY年MM月DD日')

// ─── 提醒数据（实际应从后端获取当前用户数据）───
const upcomingMeetings = ref([
  { id: 1, title: '2026年第二季度计划部署会议', time: '2026-04-02 09:00', location: '行政大楼第一会议室', urgent: true, countdown: '明日 09:00', participants: '王建国、李敏华、张伟东、陈秀芳等8人', agenda: '二季度工作计划部署与分工', remark: '请各科室提前准备汇报材料' },
  { id: 2, title: '信息化系统上线评审', time: '2026-04-04 14:00', location: '技术中心会议室', urgent: false, countdown: '3天后', participants: '张伟东、杨浩然、周婉莹', agenda: '二期系统上线前评审与风险评估', remark: '' },
  { id: 3, title: '预算中期调整专题会', time: '2026-04-07 10:00', location: '财务科会议室', urgent: false, countdown: '6天后', participants: '陈秀芳、刘志强、赵丽娜', agenda: '二季度预算调整方案讨论', remark: '' },
])
const urgentTodos = ref([
  { id: 1, title: '完成二期信息化系统全面部署', assignee_name: '张伟东', source: '2026-03-28季度会议', overdue: false, priority: 'high', due_date: '2026-04-15', status: 'in_progress', description: '完成政务信息化二期系统核心模块开发与部署，确保在4月5日前全部上线', is_self_created: false, acknowledged: false, review_status: null, need_proof: true, proof_files: [], creator_name: '王建国' },
  { id: 2, title: '采购新一批办公设备并完成报批', assignee_name: '周婉莹', source: '2026-03-28季度会议', overdue: true, priority: 'medium', due_date: '2026-03-30', status: 'overdue', description: '采购办公电脑30台、打印机10台，完成报批流程', is_self_created: false, acknowledged: true, review_status: null, need_proof: true, proof_files: [], creator_name: '王建国' },
  { id: 3, title: '提交二季度预算执行计划', assignee_name: '陈秀芳', source: '4月督办事项', overdue: false, priority: 'high', due_date: '2026-04-05', status: 'pending', description: '编制二季度各科室预算执行计划，细化到月度', is_self_created: true, acknowledged: true, review_status: null, need_proof: false, proof_files: [], creator_name: '陈秀芳' },
  { id: 4, title: '会议室智能化改造方案审核', assignee_name: '杨浩然', source: '2026-03-28季度会议', overdue: false, priority: 'medium', due_date: '2026-04-08', status: 'in_progress', description: '杨浩然已提交会议室改造方案，需审核确认方案内容及预算是否合理', is_self_created: false, acknowledged: true, review_status: 'pending_review', need_proof: true, proof_files: [{ name: '会议室改造方案v2.pdf' }], creator_name: '杨浩然', is_reviewer: true, submitter_name: '杨浩然' },
])

const loading = ref(false)
const todoList = ref([])
const showCreateDialog = ref(false)
const editingTodo = ref(null)
const savingTodo = ref(false)
const todoFormRef = ref(null)

const filters = reactive({ status: '', priority: '', keyword: '', dateRange: null, meetingName: '' })
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })

const showDetailDialog = ref(false)
const detailTodo = ref(null)
const selectedTodo = ref(null)
const selectedMeeting = ref(null)

function viewTodoDetail(item) {
  detailTodo.value = item
  showDetailDialog.value = true
}

function selectTodoItem(item) {
  selectedMeeting.value = null
  selectedTodo.value = selectedTodo.value?.id === item.id ? null : item
}

function selectMeetingItem(item) {
  selectedTodo.value = null
  selectedMeeting.value = selectedMeeting.value?.id === item.id ? null : item
}

function handleQuery() {
  pagination.page = 1
  fetchTodos()
}

function handleResetQuery() {
  filters.status = ''
  filters.priority = ''
  filters.keyword = ''
  filters.dateRange = null
  filters.meetingName = ''
  pagination.page = 1
  fetchTodos()
}

const todoForm = reactive({
  title: '',
  description: '',
  assignee_id: null,
  due_date: null,
  priority: 'medium',
  meeting_id: null,
})

const todoRules = {
  title: [{ required: true, message: '请输入事项描述', trigger: 'blur' }],
  assignee_id: [{ required: true, message: '请选择责任人', trigger: 'change' }],
}

// 模拟用户列表
const userOptions = ref([
  { id: 1, real_name: '张三' },
  { id: 2, real_name: '李四' },
  { id: 3, real_name: '王五' },
  { id: 4, real_name: '赵六' },
])

// 模拟待办数据
const sampleTodos = [
  { id: 1, title: '完成模块联调测试', assignee_name: '张三', assignee_id: 1, status: 'in_progress', priority: 'high', due_date: '2026-03-20', meeting_id: 1 },
  { id: 2, title: '协调第三方接口对接', assignee_name: '李四', assignee_id: 2, status: 'completed', priority: 'high', due_date: '2026-03-18', meeting_id: 1 },
  { id: 3, title: '编写测试用例', assignee_name: '王五', assignee_id: 3, status: 'overdue', priority: 'medium', due_date: '2026-03-12', meeting_id: 1 },
  { id: 4, title: '更新部署文档', assignee_name: '赵六', assignee_id: 4, status: 'pending', priority: 'low', due_date: '2026-03-22', meeting_id: null },
  { id: 5, title: '准备上线方案', assignee_name: '张三', assignee_id: 1, status: 'pending', priority: 'medium', due_date: '2026-03-25', meeting_id: 2 },
]


function statusType(s) { return { pending: 'info', in_progress: 'primary', completed: 'success', overdue: 'danger' }[s] || 'info' }
function statusLabel(s) { return { pending: '待处理', in_progress: '进行中', completed: '已完成', overdue: '已逾期' }[s] || s }
function priorityType(p) { return { high: 'danger', medium: 'warning', low: 'info' }[p] || 'info' }
function priorityLabel(p) { return { high: '高', medium: '中', low: '低' }[p] || p }
function formatDate(d) { return d ? dayjs(d).format('MM-DD') : '' }
function isOverdue(item) { return item.due_date && dayjs(item.due_date).isBefore(dayjs(), 'day') && item.status !== 'completed' }

let dragItem = null
function dragStart(item) { dragItem = item }

function openDetail(item) {
  if (!item.is_self_created) {
    ElMessage.warning('此待办由他人指派，不可编辑')
    return
  }
  editingTodo.value = item
  Object.assign(todoForm, {
    title: item.title,
    description: item.description || '',
    assignee_id: item.assignee_id,
    due_date: item.due_date,
    priority: item.priority,
    meeting_id: item.meeting_id,
  })
  showCreateDialog.value = true
}

function openCreateDialog() {
  editingTodo.value = null
  Object.assign(todoForm, {
    title: '',
    description: '',
    assignee_id: null,
    due_date: null,
    priority: 'medium',
    meeting_id: null,
  })
  showCreateDialog.value = true
}

async function fetchTodos() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      status: filters.status || undefined,
      priority: filters.priority || undefined,
      keyword: filters.keyword || undefined,
      meeting_name: filters.meetingName || undefined,
    }
    if (filters.dateRange && filters.dateRange.length === 2) {
      params.start_date = dayjs(filters.dateRange[0]).format('YYYY-MM-DD')
      params.end_date = dayjs(filters.dateRange[1]).format('YYYY-MM-DD')
    }
    const res = await getTodoList(params)
    todoList.value = res.data || sampleTodos
    pagination.total = res.total || sampleTodos.length
  } catch (e) {
    todoList.value = sampleTodos
    pagination.total = sampleTodos.length
  } finally {
    loading.value = false
  }
}

async function handleSaveTodo() {
  const valid = await todoFormRef.value?.validate().catch(() => false)
  if (!valid) return

  savingTodo.value = true
  try {
    if (editingTodo.value) {
      await updateTodo(editingTodo.value.id, todoForm)
      ElMessage.success('更新成功')
    } else {
      await createTodo(todoForm)
      ElMessage.success('创建成功')
    }
    showCreateDialog.value = false
    editingTodo.value = null
    fetchTodos()
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    savingTodo.value = false
  }
}

// ─── 确认知晓 ───
function handleAcknowledge(todo) {
  todo.acknowledged = true
  ElMessage.success('已确认知晓此待办事项')
}

// ─── 手动切换完成（自建待办） ───
function handleToggleComplete(todo, val) {
  todo.status = val ? 'completed' : 'pending'
  ElMessage.success(val ? '已标记为完成' : '已标记为未完成')
}

// ─── 提交完成审核（他人指派） ───
function openSubmitReview(todo) {
  if (todo.need_proof && (!todo.proof_files || todo.proof_files.length === 0)) {
    ElMessage.warning('该待办事项需要上传证明材料后才能提交审核')
    return
  }
  todo.review_status = 'pending_review'
  ElMessage.success('已提交完成审核，等待上级审批')
}

// ─── 证明材料上传 ───
function handleProofFileChange(file, todo) {
  if (!todo.proof_files) todo.proof_files = []
  todo.proof_files.push(file)
}
function handleProofFileRemove(file, todo) {
  if (!todo.proof_files) return
  const idx = todo.proof_files.indexOf(file)
  if (idx >= 0) todo.proof_files.splice(idx, 1)
}

// ─── 审核操作 ───
const reviewComment = ref('')

function handleReviewApprove(todo) {
  todo.review_status = 'approved'
  todo.status = 'completed'
  reviewComment.value = ''
  ElMessage.success('审核通过，待办事项已完成')
}
function handleReviewReject(todo) {
  todo.review_status = 'rejected'
  reviewComment.value = ''
  ElMessage.warning('已驳回，待办事项需重新提交')
}

onMounted(fetchTodos)
</script>

<style lang="scss" scoped>
.todo-page {}

/* ─── 提醒面板（内嵌到表格卡片内） ─── */
.reminder-inline {
  background: #14284b;
  border: 1px solid rgba(0,212,255,0.2);
  border-radius: 6px;
  margin-bottom: 16px;
  overflow: hidden;
}
.reminder-inline-header {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 16px;
  background: rgba(0,212,255,0.06);
  border-bottom: 1px solid rgba(0,212,255,0.12);
  .rp-icon { color: #00d4ff; font-size: 16px; }
  .rp-title { font-size: 14px; font-weight: 600; color: #00d4ff; letter-spacing: 1px; }
  .rp-date { margin-left: auto; font-size: 14px; color: #5e8aad; }
}
.reminder-body {
  display: flex; gap: 0;
  .reminder-block {
    flex: 1; padding: 12px 16px;
    &:first-child { border-right: 1px solid rgba(0,212,255,0.1); }
    .rb-label {
      display: flex; align-items: center; gap: 6px;
      font-size: 14px; color: #8aa8c4; font-weight: 600; margin-bottom: 10px;
      text-transform: uppercase; letter-spacing: 0.5px;
      .el-icon { color: #00d4ff; }
    }
  }
}
.rb-list { display: flex; flex-direction: column; gap: 6px; }
.rb-item {
  display: flex; align-items: center; gap: 10px; padding: 8px 10px;
  border-radius: 4px; background: rgba(255,255,255,0.03);
  border: 1px solid rgba(0,212,255,0.08);
  transition: background 0.2s;
  &:hover { background: rgba(0,212,255,0.06); }
  .rbi-left { flex: 1; min-width: 0; }
  .rbi-title { font-size: 14px; color: #e0eef8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .rbi-meta { font-size: 14px; color: #5e8aad; margin-top: 2px; }
}
.rb-meeting { border-left: 3px solid #00d4ff; }
.rb-todo { border-left: 3px solid #e6a23c; }
.rb-reviewer { border-left: 3px solid #f56c6c !important; background: rgba(245,108,108,0.04); }
.rb-empty { font-size: 14px; color: #3a5f80; padding: 8px 0; text-align: center; }

.filter-card { margin-bottom: 16px; }

.query-card {
  margin-bottom: 16px;
  .query-form {
    display: flex;
    flex-wrap: wrap;
    gap: 4px 0;
  }
}

.list-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  .list-card-title { font-size: 15px; font-weight: 600; color: #e0eef8; }
}

.meeting-name { color: #00d4ff; font-size: 14px; }

.todo-list-card { }

.todo-link {
  color: #00d4ff;
  cursor: pointer;
  &:hover { text-decoration: underline; }
}

.text-muted { color: #5e8aad; font-size: 14px; }

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  padding: 16px 0 0;
}

.overdue { color: #f56c6c; }

.rb-item-active {
  background: rgba(0,212,255,0.1) !important;
  border-color: rgba(0,212,255,0.3);
}

/* ─── 详情面板 ─── */
.todo-detail-panel {
  background: #14284b;
  border: 1px solid rgba(0,212,255,0.2);
  border-radius: 6px;
  padding: 16px;
}
.detail-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}
.detail-panel-title {
  font-size: 15px;
  font-weight: 600;
  color: #00d4ff;
}
.detail-panel-actions {
  display: flex;
  gap: 8px;
}

/* ─── 操作?─── */
.todo-action-area {
  margin-top: 16px;
  border: 1px solid rgba(0,212,255,0.15);
  border-radius: 6px;
  background: rgba(0,212,255,0.03);
  padding: 14px 16px;
}
.action-section {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  &:not(:last-child) { margin-bottom: 14px; padding-bottom: 14px; border-bottom: 1px solid rgba(0,212,255,0.1); }
  .action-title {
    flex-shrink: 0;
    font-size: 14px;
    font-weight: 600;
    color: #8aa8c4;
    min-width: 70px;
    line-height: 32px;
  }
}
.proof-section {
  flex-direction: column;
  .proof-upload-area { width: 100%; padding-left: 82px; }
  .upload-tip { font-size: 14px; color: #5e8aad; margin-top: 4px; }
}
.review-section {
  flex-direction: column;
  .review-actions { width: 100%; padding-left: 82px; }
  .review-btns { display: flex; gap: 8px; }
}
.proof-file-list {
  display: flex; flex-direction: column; gap: 6px;
  .proof-file-item {
    display: flex; align-items: center; gap: 6px;
    font-size: 14px; color: #e0eef8;
    padding: 4px 8px; border-radius: 4px;
    background: rgba(0,212,255,0.06);
    .el-icon { color: #00d4ff; }
  }
}
</style>
