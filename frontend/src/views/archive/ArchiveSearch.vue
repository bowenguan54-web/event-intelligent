<template>
  <div class="page-container archive-page">
    <!-- 搜索栏 -->
    <el-card shadow="never" class="search-card">
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索会议名称、纪要内容、转写文字.."
          prefix-icon="Search"
          size="large"
          clearable
          @keyup.enter="handleSearch"
          class="search-input"
        />
        <el-button type="primary" size="large" @click="handleSearch" :loading="searching">
          搜索
        </el-button>

        <el-switch
          v-model="isSemanticSearch"
          active-text="语义检索"
          inactive-text="关键词匹配"
          style="margin-left: 16px"
        />
      </div>

      <!-- 高级筛选 -->
      <el-collapse v-model="advancedExpanded" class="advanced-filter">
        <el-collapse-item title="高级筛选" name="advanced">
          <div class="filter-grid">
            <div class="filter-item">
              <label>时间范围</label>
              <el-date-picker
                v-model="filters.dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                style="width: 100%"
              />
            </div>
            <div class="filter-item">
              <label>会议类型</label>
              <el-select v-model="filters.meeting_type" placeholder="全部类型" clearable style="width: 100%">
                <el-option label="例会" value="regular" />
                <el-option label="专题会议" value="special" />
                <el-option label="决策会议" value="decision" />
                <el-option label="评审会议" value="review" />
              </el-select>
            </div>
            <div class="filter-item">
              <label>参会人员</label>
              <el-select v-model="filters.participant_ids" multiple placeholder="选择人员" clearable style="width: 100%">
                <el-option v-for="u in userOptions" :key="u.id" :label="u.name" :value="u.id" />
              </el-select>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
    </el-card>

    <!-- 批量操作栏 -->
    <div v-if="selectedIds.length > 0" class="batch-bar">
      <span>已选择 {{ selectedIds.length }} 条记录</span>
      <el-button type="primary" size="small" @click="handleBatchExport" :loading="exporting">
        <el-icon><Download /></el-icon>批量导出
      </el-button>
    </div>

    <!-- 检索结果列表 -->
    <div v-if="!currentDetail" class="results-area" v-loading="searching">
      <div v-for="item in resultList" :key="item.id" class="result-card">
        <div class="card-checkbox">
          <el-checkbox v-model="item.selected" @change="updateSelection" />
        </div>

        <div class="card-body" @click="openDetail(item)">
          <div class="card-header">
            <h3 class="card-title" v-html="highlightKeyword(item.title)" />
            <div class="card-tags">
              <el-tag size="small" type="info">{{ typeLabel(item.meeting_type) }}</el-tag>
              <span class="card-time">{{ formatTime(item.start_time) }}</span>
            </div>
          </div>

          <div class="card-participants">
            <el-avatar
              v-for="p in item.participants?.slice(0, 5)"
              :key="p.id"
              :size="24"
              class="p-avatar"
            >
              {{ p.real_name?.charAt(0) }}
            </el-avatar>
            <span v-if="item.participants?.length > 5" class="more-count">
              +{{ item.participants.length - 5 }}
            </span>
          </div>

          <p class="card-summary" v-html="highlightKeyword(item.summary || '暂无摘要')" />

          <div class="card-stats" v-if="item.todo_total > 0">
            <span class="cs-item">待办 <b>{{ item.todo_total }}</b></span>
            <span class="cs-item">完成 <b>{{ item.todo_completed }}</b></span>
            <el-progress :percentage="item.completion_rate||0" :stroke-width="4" :show-text="false"
              :color="progressColor(item.completion_rate)" style="width:80px" />
            <span class="cs-rate" :class="rateClass(item.completion_rate)">{{ item.completion_rate }}%</span>
          </div>
        </div>
      </div>

      <el-empty v-if="resultList.length === 0 && !searching" description="暂无检索结果" />

      <!-- 分页 -->
      <div v-if="resultList.length > 0" class="pagination-bar">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          layout="total, prev, pager, next"
          @current-change="handleSearch"
        />
      </div>
    </div>

    <!-- ====== 归档详情视图 ====== -->
    <div v-if="currentDetail" class="detail-view">
      <div class="detail-back-bar">
        <el-button link @click="closeDetail"><el-icon><ArrowLeft /></el-icon>返回检索结果</el-button>
        <span class="detail-back-title">{{ currentDetail.title }}</span>
        <el-dropdown trigger="click" @command="handleExport">
          <el-button size="small"><el-icon><Download /></el-icon>导出</el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="docx"><el-icon><Document /></el-icon>导出 Word</el-dropdown-item>
              <el-dropdown-item command="pdf"><el-icon><Document /></el-icon>导出 PDF</el-dropdown-item>
              <el-dropdown-item command="txt"><el-icon><Document /></el-icon>导出 纯文本</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>

      <div class="detail-meta-bar">
        <div class="meta-item"><el-icon><Calendar /></el-icon><span>{{ formatTime(currentDetail.start_time) }} 至 {{ fmtTime(currentDetail.end_time) }}</span></div>
        <div class="meta-item" v-if="currentDetail.location"><el-icon><Location /></el-icon><span>{{ currentDetail.location }}</span></div>
        <div class="meta-item"><el-icon><User /></el-icon><span>{{ currentDetail.participants?.length || 0 }}人参会</span></div>
        <el-tag type="success" size="small" effect="plain">已归档</el-tag>
      </div>

      <el-tabs v-model="detailTab" class="detail-tabs">

        <!-- 📝 会议纪要 -->
        <el-tab-pane label="📝 会议纪要" name="minutes">
          <div class="tab-panel">
            <div v-if="currentDetail.minutes" class="minutes-box" v-html="currentDetail.minutes"></div>
            <div v-else class="empty-hint">暂无会议纪要</div>
          </div>
        </el-tab-pane>

        <!-- 🎧 会议记录 -->
        <el-tab-pane label="🎧 会议记录" name="records">
          <div class="tab-panel audio-sync-panel">
            <div class="audio-player-bar">
              <div class="ap-controls">
                <el-button :icon="audioPlaying ? 'VideoPause' : 'VideoPlay'" circle size="small"
                  @click="toggleAudioPlay" />
                <span class="ap-time">{{ formatSec(audioCurrentTime) }} / {{ formatSec(audioDuration) }}</span>
                <el-slider v-model="audioCurrentTime" :max="audioDuration" :show-tooltip="false"
                  class="ap-slider" @input="seekAudio" />
                <el-slider v-model="audioVolume" :max="100" :show-tooltip="false" class="ap-volume" />
                <el-icon :size="16"><Microphone /></el-icon>
              </div>
              <div class="ap-waveform">
                <span v-for="i in 80" :key="i" class="wave-bar"
                  :style="{ height: waveHeights[i-1] + 'px', background: (i/80)*audioDuration <= audioCurrentTime ? '#00d4ff' : '#1a3a5c' }" />
              </div>
            </div>

            <div class="transcript-list">
              <div v-for="(seg, idx) in currentDetail.transcripts" :key="idx"
                class="transcript-seg" :class="{ playing: isSegPlaying(seg) }"
                @click="seekToSeg(seg)">
                <div class="seg-left">
                  <div class="seg-time">{{ formatSec(seg.start) }}</div>
                  <div class="seg-speaker" :style="{ color: speakerColor(seg.speaker) }">{{ seg.speaker }}</div>
                </div>
                <div class="seg-text">{{ seg.text }}</div>
                <div class="seg-actions">
                  <el-button link size="small" @click.stop="playSegOnly(seg)">
                    <el-icon><VideoPlay /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 📊 会议摘要 -->
        <el-tab-pane label="📊 会议摘要" name="summary">
          <div class="tab-panel">
            <div class="panel-section">
              <div class="section-title">参会人员</div>
              <div class="participant-chips">
                <el-tag v-for="p in currentDetail.participants" :key="p.id" size="small" effect="plain" class="p-chip">
                  {{ p.real_name }}<span v-if="p.department" class="chip-dept">·{{ p.department }}</span>
                </el-tag>
              </div>
            </div>
            <div class="panel-section">
              <div class="section-title">会议摘要</div>
              <div v-if="currentDetail.summary" class="summary-box">{{ currentDetail.summary }}</div>
              <div v-else class="empty-hint">暂无摘要</div>
            </div>
            <div class="panel-section" v-if="currentDetail.keypoints?.length">
              <div class="section-title">关键讨论点</div>
              <div class="kp-list">
                <div v-for="kp in currentDetail.keypoints" :key="kp.id" class="kp-card" :class="'kp-' + (kp.importance||'medium')">
                  <div class="kp-header">
                    <span class="kp-title">{{ kp.title }}</span>
                    <el-tag :type="importanceType(kp.importance)" size="small" effect="plain">{{ importanceLabel(kp.importance) }}</el-tag>
                  </div>
                  <div class="kp-content">{{ kp.content }}</div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 📋 签到表 -->
        <el-tab-pane label="📋 签到表" name="checkin">
          <div class="tab-panel">
            <!-- 专家签到 -->
            <div v-if="expertCheckins.length > 0" class="checkin-table-wrap">
              <div class="checkin-table-title">一、专家签到表</div>
              <table class="checkin-archive-table">
                <thead>
                  <tr><th>序号</th><th>姓名</th><th>单位</th><th>职称</th><th>签到时间</th><th>签名</th></tr>
                </thead>
                <tbody>
                  <tr v-for="(p, idx) in expertCheckins" :key="p.id">
                    <td>{{ idx + 1 }}</td>
                    <td>
                      {{ p.real_name }}
                      <el-tag v-if="p.is_leader" type="danger" size="small" style="margin-left:4px">组长</el-tag>
                    </td>
                    <td>{{ p.department }}</td>
                    <td>{{ p.professional_title || '—' }}</td>
                    <td>
                      <el-tag :type="p.checked_in ? 'success' : 'info'" size="small">{{ p.checked_in ? (p.checkin_time || '已签到') : '未签到' }}</el-tag>
                    </td>
                    <td>
                      <img v-if="p.signature" :src="p.signature" class="sig-img-table" alt="签名" />
                      <span v-else class="sig-empty">—</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <!-- 其他人员签到 -->
            <div v-if="otherCheckins.length > 0" class="checkin-table-wrap" style="margin-top:20px">
              <div class="checkin-table-title">二、其他人员签到表</div>
              <table class="checkin-archive-table">
                <thead>
                  <tr><th>序号</th><th>姓名</th><th>单位</th><th>职务</th><th>签到时间</th><th>签名</th></tr>
                </thead>
                <tbody>
                  <tr v-for="(p, idx) in otherCheckins" :key="p.id">
                    <td>{{ idx + 1 }}</td>
                    <td>{{ p.real_name }}</td>
                    <td>{{ p.department }}</td>
                    <td>{{ p.position || '—' }}</td>
                    <td>
                      <el-tag :type="p.checked_in ? 'success' : 'info'" size="small">{{ p.checked_in ? (p.checkin_time || '已签到') : '未签到' }}</el-tag>
                    </td>
                    <td>
                      <img v-if="p.signature" :src="p.signature" class="sig-img-table" alt="签名" />
                      <span v-else class="sig-empty">—</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <el-empty v-if="!currentDetail.checkin_records?.length" description="暂无签到记录" />
          </div>
        </el-tab-pane>

        <!-- 📝 评审结论 -->
        <el-tab-pane label="📝 评审结论" name="review">
          <div class="tab-panel">
            <div v-if="currentDetail.review_conclusion" class="review-conclusion-box">
              {{ currentDetail.review_conclusion }}
            </div>
            <div v-else class="empty-hint">暂无评审结论</div>
          </div>
        </el-tab-pane>

        <!-- 🔴 问题清单 -->
        <el-tab-pane label="🔴 问题清单" name="issues">
          <div class="tab-panel">
            <div v-if="currentDetail.issues?.length" class="issue-list-archive">
              <div v-for="issue in currentDetail.issues" :key="issue.id" class="issue-archive-item" :class="issue.status">
                <div class="ia-content">{{ issue.content }}</div>
                <div class="ia-meta">
                  <span class="ia-reporter">{{ issue.reporter_name }}</span>
                  <el-tag :type="issueArchiveStatusType(issue.status)" size="small" effect="plain">
                    {{ issueArchiveStatusLabel(issue.status) }}
                  </el-tag>
                </div>
                <div v-if="issue.response" class="ia-response">
                  <el-icon style="font-size:14px;margin-right:3px;vertical-align:middle"><ChatLineRound /></el-icon>{{ issue.response }}
                </div>
              </div>
            </div>
            <div v-else class="empty-hint">暂无问题记录</div>
          </div>
        </el-tab-pane>

        <!-- 📄 落实报表 -->
        <el-tab-pane label="📄 落实报表" name="impl-report">
          <div class="tab-panel">
            <div class="report-toolbar">
              <el-button type="primary" :loading="generatingReport" @click="doGenerateReport">
                <el-icon><Document /></el-icon>生成落实情况报表
              </el-button>
              <el-button v-if="reportData" @click="printReport"><el-icon><Printer /></el-icon>打印</el-button>
            </div>

            <div v-if="reportData" class="report-preview" id="printable-report">
              <div class="rp-header">
                <h2>{{ reportData.meeting_title }}</h2>
                <div class="rp-subtitle">会议落实情况报表</div>
                <div class="rp-meta">
                  <span>会议时间：{{ reportData.meeting_time }}</span>
                  <span>会议地点：{{ reportData.location }}</span>
                  <span>生成人：{{ reportData.generated_by }}</span>
                  <span>生成时间：{{ reportData.generated_at }}</span>
                </div>
                <div class="rp-participants">参会人员：{{ reportData.participants.join('、') }}</div>
              </div>

              <div class="rp-section">
                <div class="rp-section-title">一、总体落实情况</div>
                <div class="rp-summary-row">
                  <div class="rp-stat" v-for="(val, key) in reportData.todo_summary" :key="key">
                    <span class="rp-stat-val">{{ val }}</span>
                    <span class="rp-stat-key">{{ todoSummaryLabel(key) }}</span>
                  </div>
                </div>
                <div ref="implBarRef" class="impl-bar-chart"></div>
              </div>

              <div class="rp-section">
                <div class="rp-section-title">二、各科室落实明细</div>
                <table class="rp-table">
                  <thead>
                    <tr><th>科室</th><th>任务数</th><th>已完成</th><th>进行中</th><th>逾期</th><th>完成率</th></tr>
                  </thead>
                  <tbody>
                    <tr v-for="d in reportData.dept_breakdown" :key="d.dept">
                      <td>{{ d.dept }}</td><td>{{ d.total }}</td><td>{{ d.completed }}</td>
                      <td>{{ d.in_progress }}</td><td>{{ d.overdue }}</td>
                      <td><span :class="rateClass(d.rate)">{{ d.rate }}%</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div class="rp-section" v-if="reportData.todo_details.length">
                <div class="rp-section-title">三、待办事项明细</div>
                <table class="rp-table">
                  <thead><tr><th>事项</th><th>责任人</th><th>优先级</th><th>状态</th><th>截止日期</th><th>完成时间</th></tr></thead>
                  <tbody>
                    <tr v-for="t in reportData.todo_details" :key="t.id">
                      <td>{{ t.title }}</td><td>{{ t.assignee_name }}</td>
                      <td>{{ priorityLabel(t.priority) }}</td><td>{{ todoStatusLabel(t.status) }}</td>
                      <td>{{ t.due_date || '未设置' }}</td><td>{{ t.completed_at || '—' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div class="rp-section" v-if="reportData.summary_text">
                <div class="rp-section-title">四、会议摘要回顾</div>
                <div class="rp-text">{{ reportData.summary_text }}</div>
              </div>

              <div class="rp-section">
                <div class="rp-section-title">五、落实建议与改进措施</div>
                <div class="rp-recommendation">{{ reportData.recommendations }}</div>
              </div>

              <div class="rp-section">
                <div class="rp-section-title">六、关键时间节点</div>
                <div class="rp-timeline">
                  <div v-for="(ev, idx) in reportData.timeline" :key="idx" class="rt-item">
                    <div class="rt-dot"></div>
                    <div class="rt-date">{{ ev.date }}</div>
                    <div class="rt-content">{{ ev.content }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="report-empty">点击「生成落实情况报表」自动汇总会议决议落实进度并生成 AI 改进建议</div>
          </div>
        </el-tab-pane>

      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { searchArchives, batchExport } from '@/api/archive'
import { getArchivedFull, generateClosureReport } from '@/api/meeting'
import { ElMessage } from 'element-plus'
import { ChatLineRound } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import dayjs from 'dayjs'

const route = useRoute()

/* ═══════════════════════════════════════════════════════   搜索相关
   ══════════════════════════════════════════════════════════════════════════
*/

const searchKeyword = ref(route.query.keyword || '')
const isSemanticSearch = ref(false)
const searching = ref(false)
const exporting = ref(false)
const advancedExpanded = ref('')

const filters = reactive({
  dateRange: null,
  meeting_type: '',
  participant_ids: [],
})

const pagination = reactive({ page: 1, pageSize: 20, total: 0 })

const userOptions = ref([
  { id: 1, name: '张三' }, { id: 2, name: '李四' }, { id: 3, name: '王五' },
])

/* ═══════════════════════════════════════════════════════   示例数据
   ══════════════════════════════════════════════════════════════════════════
*/

const DEMO_PARTICIPANTS = [
  { id: 'd1', real_name: '王建国', department: '局领导', role: '主持人', is_expert: true, is_leader: true, professional_title: '研究员', position: '副局长' },
  { id: 'd2', real_name: '李敏华', department: '办公室', role: '记录人', is_expert: true, is_leader: false, professional_title: '高级工程师', position: '主任' },
  { id: 'd3', real_name: '张伟东', department: '信息中心', role: '汇报人', is_expert: true, is_leader: false, professional_title: '高级工程师', position: '主任' },
  { id: 'd4', real_name: '陈秀芳', department: '财务科', role: '参会人', is_expert: false, is_leader: false, professional_title: '', position: '科长' },
  { id: 'd5', real_name: '刘志强', department: '综合科', role: '参会人', is_expert: false, is_leader: false, professional_title: '', position: '科长' },
  { id: 'd6', real_name: '赵丽娜', department: '人事科', role: '参会人', is_expert: false, is_leader: false, professional_title: '', position: '科长' },
  { id: 'd7', real_name: '杨浩然', department: '技术科', role: '参会人', is_expert: false, is_leader: false, professional_title: '', position: '工程师' },
  { id: 'd8', real_name: '周婉莹', department: '行政科', role: '参会人', is_expert: false, is_leader: false, professional_title: '', position: '科员' },
]

function makeSigSvg(name) {
  const colors = ['#1a5276','#1e8449','#7d3c98','#b9770e','#2e4053','#a93226','#117a65','#6c3483']
  const c = colors[name.codePointAt(0) % colors.length]
  return `data:image/svg+xml,${encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="120" height="40"><text x="8" y="30" font-family="STKaiti,KaiTi,serif" font-size="22" fill="${c}">${name}</text></svg>`
  )}`
}

const DEMO_ARCHIVE_DETAIL = {
  id: 'demo-archive-1',
  title: '会议系统功能示例',
  meeting_type: 'special',
  start_time: '2026-03-28T09:00:00',
  end_time: '2026-03-28T11:30:00',
  location: '行政楼第一会议室',
  participants: DEMO_PARTICIPANTS,
  todo_total: 6,
  todo_completed: 4,
  completion_rate: 66.7,
  summary: `本次会议由王建国副局长主持，8名人参会，历时2.5小时。
会议首先听取了各科室2026年第一季度工作完成情况汇报。信息中心张伟东主任介绍了政务信息化二期系统建设进展，目前核心模块开发完成85%，预计4月中旬完成全部部署。财务科陈秀芳科长通报了一季度预算执行情况，总体执行率达72%，部分专项经费需加快支出进度。
会议重点讨论了第二季度五项重点工作：信息化系统全面上线、预算中期调整、全员业务能力提升培训、会议室智能化改造以及跨部门协作机制优化。
会议决定：各科室于4月5日前提交二季度详细工作计划；信息化项目纳入月度督办，每周报送进度；培训计划由人事科牵头，4月10日前完成方案制定。`,
  minutes: `<h3>2026年第一季度工作总结暨第二季度计划部署会议纪要</h3>
<p><strong>会议时间：</strong>2026年3月18日 上午9:00~11:30</p>
<p><strong>会议地点：</strong>行政楼第一会议室</p>
<p><strong>主持人：</strong>王建国（副局长）</p>
<p><strong>记录人：</strong>李敏华（办公室）</p>
<p><strong>参会人员：</strong>王建国、李敏华、张伟东、陈秀芳、刘志强、赵丽娜、杨浩然、周婉莹</p>
<h4>一、各科室工作汇报</h4>
<p>1. <strong>信息中心（张伟东）</strong>：政务信息化二期核心模块开发完成85%，数据库迁移通过压力测试。移动端适配还需2周，预计4月15日完成全部署。安全等保三级测评通过，等待正式发证。建议增加2名运维人员。</p>
<p>2. <strong>财务科（陈秀芳）</strong>：一季度预算总额3200万元，已执行2304万元，执行率72%。信息化专项执行率仅58%，需加快招标采购。建议执行率低于60%的科室重点督办。</p>
<p>3. <strong>人事科（赵丽娜）</strong>：计划二季度分三批组织全员培训——4月信息化应用培训、5月公文写作培训、6月跨部门业务交流。邀请外部讲师2名、内部讲师4名，预算18万元。</p>
<h4>二、会议决定事项</h4>
<ol>
<li>各科室于4月5日前提交二季度详细工作计划；</li>
<li>信息化项目纳入月度督办，每周报送进度；</li>
<li>培训计划由人事科牵头，4月10日前完成方案制定。</li>
<li>会议室智能化改造方案由杨浩然细化后报办公室。</li>
<li>跨部门协作机制优化由刘志强牵头起草管理办法；</li>
<li>预算督办方案请陈秀芳尽快落实。</li>
</ol>`,

  keypoints: [
    { id: 'k1', title: '一季度信息化系统建设进展通报', importance: 'high',
      content: '张伟东主任汇报：政务信息化二期项目核心模块开发成85%，数据库迁移已通过压力测试。移动端适配还需2周，预计4月5日可完成全部署。安全等保三级测评已通过，等待正式发证。建议增加2名运维人员保障上线后系统稳定运行。' },
    { id: 'k2', title: '预算执行与资金使用情况', importance: 'high',
      content: '陈秀芳科长通报：一季度预算总额3200万元，已执行2304万元，执行率72%。其中信息化专项执行率仅58%，需加快招标采购流程。建议对执行率低于60%的科室进行重点督办，并将预算执行情况纳入季度考核指标。' },
    { id: 'k3', title: '全员业务能力提升培训计划', importance: 'medium',
      content: '赵丽娜科长提出分三批组织培训4月中旬开展信息化应用培训5月安排公文写作与办公规范培训6月组织跨部门业务交流。计划邀请外部讲师2名，内部讲师4名，培训费用预算18万万元。' },
  ],

  transcripts: [
    { start: 0, end: 28, speaker: '王建国', text: '各位同事上午好，今天召开第一季度工作总结暨第二季度计划部署会议。首先请各科室按顺序汇报一季度工作完成情况，先请信息中心张主任。' },
    { start: 30, end: 85, speaker: '张伟东', text: '好的，王局。信息中心一季度主要推进了政务信息化二期项目建设。目前核心模块开发已完成百分之八十五，数据库迁移工作在上周通过了压力测试，各项指标均达标。移动端适配还需要大约两周时间，预计四月十五日可以完成全面部署。' },
    { start: 87, end: 120, speaker: '张伟东', text: '另外，安全等保三级测评已经顺利通过，正在等待正式发证。不过我想提一下，系统上线后运维压力会比较大，建议至少增加两名专职运维人员来保障系统的稳定运行。' },
    { start: 122, end: 140, speaker: '王建国', text: '嗯，信息化建设进度总体不错。运维人员的事情会后和人事科对接一下。接下来请陈科长汇报财务情况。' },
    { start: 142, end: 198, speaker: '陈秀芳', text: '好的。一季度我们的预算总额是三千两百万元，目前已执行两千三百零四万元，总体执行率百分之七十二。需要特别关注的是信息化专项经费执行率只有百分之五十八，主要是采购环节流程较长导致的。建议对执行率低于百分之六十的科室进行重点督办。' },
    { start: 200, end: 230, speaker: '王建国', text: '预算执行要抓紧，特别是专项经费不能沉淀太多。陈科长会后拟一个督办方案。接下来请赵科长汇报人事和培训情况。' },
    { start: 232, end: 290, speaker: '赵丽娜', text: '各位领导好。人事科计划在二季度分三批组织全员业务能力提升培训。第一批四月中旬的信息化应用培训，主要是配合新系统上线；第二批五月份的公文写作培训；第三批六月份的跨部门业务交流。我们计划邀请两名外部讲师、四名内部讲师，培训总预算十八万元。' },
    { start: 292, end: 330, speaker: '杨浩然', text: '我补充一下会议室改造的方案。三楼第一会议室的智能化改造包括四个部分：无纸化会议系统、智能签到终端、高清录播设备和远程视频接入。初步预算大概四十五万元，改造工期约三周，建议五月份启动施工。' },
    { start: 332, end: 365, speaker: '刘志强', text: '我提一个建议，关于跨部门协作的问题。目前几个涉及多科室的项目协调成本比较高，建议我们建立一个月度联席会议制度，设立跨部门项目协调员。可以先在信息化项目上试行。' },
    { start: 367, end: 400, speaker: '王建国', text: '大家的汇报和建议都很好。我总结一下今天的会议精神和工作部署。' },
    { start: 402, end: 440, speaker: '王建国', text: '第一，信息化二期项目继续加快推进，四月十五日前完成部署，纳入月度督办。第二，各科室四月五日前提交二季度详细工作计划。第三，培训方案由人事科牵头，四月十日前定稿。' },
    { start: 442, end: 475, speaker: '王建国', text: '第四，会议室改造方案请杨科长细化后报办公室。第五，协作机制优化由刘科长牵头起草管理办法。另外，预算督办方案请陈科长尽快落实。好，今天的会就开到这里，谢谢大家。' },
    { start: 476, end: 480, speaker: '全体', text: '谢谢王局长' },
  ],

  todos: [
    { id: 't1', title: '完成二期信息化系统全面部署', assignee_name: '张伟东', priority: 'high', status: 'in_progress', due_date: '2026-04-15', completed_at: null },
    { id: 't2', title: '提交二季度预算调整方案', assignee_name: '陈秀芳', priority: 'high', status: 'completed', due_date: '2026-04-05', completed_at: '2026-04-04' },
    { id: 't3', title: '制定全员业务能力培训计划', assignee_name: '赵丽娜', priority: 'medium', status: 'completed', due_date: '2026-04-10', completed_at: '2026-04-09' },
    { id: 't4', title: '细化会议室智能化改造方案并报批', assignee_name: '杨浩然', priority: 'medium', status: 'completed', due_date: '2026-04-08', completed_at: '2026-04-07' },
    { id: 't5', title: '起草跨部门协作管理办法', assignee_name: '刘志强', priority: 'medium', status: 'completed', due_date: '2026-04-12', completed_at: '2026-04-11' },
    { id: 't6', title: '采购新一批办公设备并完成报批', assignee_name: '周婉莹', priority: 'low', status: 'overdue', due_date: '2026-03-30', completed_at: null },
  ],

  checkin_records: DEMO_PARTICIPANTS.map((p, i) => ({
    ...p,
    checked_in: true,
    checkin_time: `08:${(42 + i * 2).toString().padStart(2, '0')}`,
    signature: makeSigSvg(p.real_name),
  })),

  sign_records: [
    { name: '王建国', role: '审签人（主持人）', signed: true, time: '2026-03-29 10:15', comment: '同意，请各科室抓紧落实。', signature_img: makeSigSvg('王建国') },
    { name: '李敏华', role: '审签人（记录人）', signed: true, time: '2026-03-29 11:20', comment: '纪要内容准确无误。', signature_img: makeSigSvg('李敏华') },
    { name: '张伟东', role: '审签人', signed: true, time: '2026-03-29 14:30', comment: '信息化部分表述准确。', signature_img: makeSigSvg('张伟东') },
    { name: '陈秀芳', role: '审签人', signed: true, time: '2026-03-29 15:45', comment: '同意。', signature_img: makeSigSvg('陈秀芳') },
    { name: '刘志强', role: '审签人', signed: true, time: '2026-03-30 09:10', comment: '无异议。', signature_img: makeSigSvg('刘志强') },
    { name: '赵丽娜', role: '审签人', signed: true, time: '2026-03-30 10:00', comment: '培训预算部分确认。', signature_img: makeSigSvg('赵丽娜') },
    { name: '杨浩然', role: '审签人', signed: true, time: '2026-03-30 11:20', comment: '改造方案预算需进一步细化。', signature_img: makeSigSvg('杨浩然') },
    { name: '周婉莹', role: '审签人', signed: true, time: '2026-03-30 14:00', comment: '同意。', signature_img: makeSigSvg('周婉莹') },
  ],

  review_conclusion: '经专家组审议，与会人员一致认为：一季度各项工作推进有序，信息化二期项目建设进度符合预期。建议二季度重点关注系统上线后的运维保障和预算执行进度督办，确保各项决议按期落实。',

  issues: [
    { id: 'i1', content: '信息化专项经费执行率偏低（58%），采购环节流程较长', reporter_name: '陈秀芳', status: 'adopted_unresolved', response: '已协调采购部加快招标流程，预计4月底前完成' },
    { id: 'i2', content: '系统上线后运维人员不足，需增加2名专职运维', reporter_name: '张伟东', status: 'adopted_resolved', response: '已完成招聘，2名运维人员已到岗。' },
    { id: 'i3', content: '会议室改造预算需进一步细化明确各项开支', reporter_name: '杨浩然', status: 'explained', response: '已补充明细预算表，各项开支均有依据' },
  ],
}

const DEMO_REPORT = {
  meeting_title: '会议系统功能示例',
  meeting_time: '2026-03-28 09:00~11:30',
  location: '行政楼第一会议室',
  generated_by: '系统自动生成',
  generated_at: dayjs().format('YYYY-MM-DD HH:mm'),
  participants: DEMO_PARTICIPANTS.map(p => p.real_name),
  todo_summary: { total: 6, completed: 4, in_progress: 1, overdue: 1, completion_rate: '66.7%' },
  dept_breakdown: [
    { dept: '信息中心', total: 1, completed: 0, in_progress: 1, overdue: 0, rate: 0 },
    { dept: '财务科', total: 1, completed: 1, in_progress: 0, overdue: 0, rate: 100 },
    { dept: '人事科', total: 1, completed: 1, in_progress: 0, overdue: 0, rate: 100 },
    { dept: '技术科', total: 1, completed: 1, in_progress: 0, overdue: 0, rate: 100 },
    { dept: '综合科', total: 1, completed: 1, in_progress: 0, overdue: 0, rate: 100 },
    { dept: '行政科', total: 1, completed: 0, in_progress: 0, overdue: 1, rate: 0 },
  ],
  todo_details: DEMO_ARCHIVE_DETAIL.todos,
  summary_text: DEMO_ARCHIVE_DETAIL.summary,
  recommendations: `基于本次会议决议执行情况，AI 分析建议如下：

1. 【重点督办】信息化二期系统部署（负责人：张伟东）目前仍在进行中，建议每周召开项目进度例会，确保4月15日按时上线。2. 【逾期预警】办公设备采购事项（负责人：周婉莹）已超过截止日期，建议立即跟进采购流程瓶颈，必要时启动紧急采购通道。3. 【经验推广】财务科、人事科、技术科、综合科均已按时完成任务，建议在下次会议上分享高效执行的工作方法。4. 【制度建设】跨部门协作管理办法已完成起草，建议尽快安排意见征集并进入审批流程。5. 【培训提醒】全员培训计划已定稿，请尽快发布通知，预留充足报名时间。
总体评估：本次会议6项决议已完成4项（66.7%），总体执行力良好。建议对逾期事项启动督办问责机制。`,
  timeline: [
    { date: '2026-03-28', content: '会议召开，部署6项重点工作' },
    { date: '2026-03-29', content: '会议纪要完成审签（7/8人签署）' },
    { date: '2026-03-30', content: '办公设备采购事项逾期' },
    { date: '2026-04-04', content: '陈秀芳完成二季度预算调整方案' },
    { date: '2026-04-07', content: '杨浩然完成会议室改造方案细化' },
    { date: '2026-04-09', content: '赵丽娜完成全员培训计划制定' },
    { date: '2026-04-11', content: '刘志强完成跨部门协作管理办法' },
    { date: '2026-04-15', content: '信息化系统部署截止日期（进行中）' },
  ],
}

// 模拟结果数据
const resultList = ref([
  {
    id: 'demo-archive-1', title: '会议系统功能示例', meeting_type: 'special',
    start_time: '2026-03-28T09:00:00', end_time: '2026-03-28T11:30:00',
    summary: '本次会议由王建国副局长主持，8名人参会，历时2.5小时。听取了各科室2026年第一季度工作完成情况汇报，重点讨论了第二季度五项重点工作...',
    participants: DEMO_PARTICIPANTS,
    todo_total: 6, todo_completed: 4, completion_rate: 66.7,
    selected: false,
  },
])

const selectedIds = computed(() => resultList.value.filter(r => r.selected).map(r => r.id))

/* ═══════════════════════════════════════════════════════   详情视图
   ══════════════════════════════════════════════════════════════════════════
*/

const currentDetail = ref(null)

const expertCheckins = computed(() =>
  (currentDetail.value?.checkin_records || []).filter(p => p.is_expert || p.is_leader)
)
const otherCheckins = computed(() =>
  (currentDetail.value?.checkin_records || []).filter(p => !p.is_expert && !p.is_leader)
)
const detailTab = ref('minutes')
const loadingDetail = ref(false)

// 落实报表
const generatingReport = ref(false)
const reportData = ref(null)
const implBarRef = ref(null)
let implBarChart = null

// 音字对照
const audioPlaying = ref(false)
const audioCurrentTime = ref(0)
const audioDuration = ref(480)
const audioVolume = ref(70)
let audioTimer = null
const waveHeights = Array.from({ length: 80 }, () => Math.floor(Math.random() * 22) + 4)

async function openDetail(item) {
  detailTab.value = 'minutes'
  reportData.value = null
  stopAudio()
  if (implBarChart) { implBarChart.dispose(); implBarChart = null }

  if (item.id === 'demo-archive-1') {
    currentDetail.value = structuredClone(DEMO_ARCHIVE_DETAIL)
    return
  }

  loadingDetail.value = true
  try {
    const res = await getArchivedFull(item.id)
    currentDetail.value = res.data
  } catch {
    ElMessage.error('加载归档详情失败')
  } finally {
    loadingDetail.value = false
  }
}

function closeDetail() {
  currentDetail.value = null
  stopAudio()
  reportData.value = null
  if (implBarChart) { implBarChart.dispose(); implBarChart = null }
}

/* ═══════════════════════════════════════════════════════   音字对照：模拟播放器
   ══════════════════════════════════════════════════════════════════════════
*/

function toggleAudioPlay() {
  if (audioPlaying.value) { stopAudio() } else { startAudio() }
}
function startAudio() {
  audioPlaying.value = true
  audioTimer = setInterval(() => {
    if (audioCurrentTime.value >= audioDuration.value) { stopAudio(); return }
    audioCurrentTime.value += 1
  }, 1000)
}
function stopAudio() {
  audioPlaying.value = false
  if (audioTimer) { clearInterval(audioTimer); audioTimer = null }
}
function seekAudio(val) { audioCurrentTime.value = val }
function seekToSeg(seg) { audioCurrentTime.value = seg.start; if (!audioPlaying.value) startAudio() }
function playSegOnly(seg) { audioCurrentTime.value = seg.start; startAudio() }
function isSegPlaying(seg) {
  return audioCurrentTime.value >= seg.start && audioCurrentTime.value < seg.end
}
function formatSec(s) {
  const m = Math.floor(s / 60); const sec = Math.floor(s % 60)
  return `${m.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`
}
const SPEAKER_COLORS = {}
function speakerColor(name) {
  if (!SPEAKER_COLORS[name]) {
    const palette = ['#00d4ff', '#67c23a', '#e6a23c', '#f56c6c', '#a78bfa', '#f472b6', '#34d399', '#fbbf24']
    SPEAKER_COLORS[name] = palette[Object.keys(SPEAKER_COLORS).length % palette.length]
  }
  return SPEAKER_COLORS[name]
}

/* ═══════════════════════════════════════════════════════   落实报表
   ══════════════════════════════════════════════════════════════════════════
*/

async function doGenerateReport() {
  generatingReport.value = true
  try {
    if (currentDetail.value.id === 'demo-archive-1') {
      await sleep(1000)
      reportData.value = { ...DEMO_REPORT, generated_at: dayjs().format('YYYY-MM-DD HH:mm') }
    } else {
      const res = await generateClosureReport(currentDetail.value.id)
      reportData.value = res.data
    }
    ElMessage.success('报表生成成功')
    nextTick(() => initImplBarChart())
  } catch { ElMessage.error('报表生成失败') }
  finally { generatingReport.value = false }
}

function initImplBarChart() {
  if (!implBarRef.value || !reportData.value) return
  if (implBarChart) implBarChart.dispose()
  implBarChart = echarts.init(implBarRef.value)
  const depts = reportData.value.dept_breakdown
  implBarChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { data: ['已完成', '进行中', '逾期'], textStyle: { color: '#8aa8c4', fontSize: 11 } },
    grid: { left: 80, right: 20, top: 40, bottom: 20 },
    xAxis: { type: 'value', axisLabel: { color: '#5e8aad' }, splitLine: { lineStyle: { color: 'rgba(0,212,255,0.1)' } } },
    yAxis: { type: 'category', data: depts.map(d => d.dept), axisLabel: { color: '#8aa8c4' } },
    series: [
      { name: '已完成', type: 'bar', stack: 'total', data: depts.map(d => d.completed), itemStyle: { color: '#67c23a' } },
      { name: '进行中', type: 'bar', stack: 'total', data: depts.map(d => d.in_progress), itemStyle: { color: '#409eff' } },
      { name: '逾期', type: 'bar', stack: 'total', data: depts.map(d => d.overdue), itemStyle: { color: '#f56c6c' } },
    ],
  })
}

function printReport() {
  const el = document.getElementById('printable-report')
  if (!el) return
  const w = window.open('', '_blank')
  w.document.write(`<html><head><title>${currentDetail.value?.title}  落实情况报表</title>
  <style>body{font-family:sans-serif;padding:20px;color:#333}h2{color:#1a3a5c}
  table{border-collapse:collapse;width:100%}th,td{border:1px solid #ddd;padding:6px 10px;font-size:14px}
  th{background:#f0f4f8}.rp-meta{color:#666;font-size:14px;margin:6px 0;display:flex;gap:20px}
  .rp-recommendation{background:#f8f9fa;padding:12px;border-radius:4px;border-left:3px solid #409eff}
  .rate-good{color:#2ecc71}.rate-warn{color:#f39c12}.rate-bad{color:#e74c3c}
  </style></head><body>${el.innerHTML}</body></html>`)
  w.document.close(); w.print()
}

/* ═══════════════════════════════════════════════════════   导出
   ══════════════════════════════════════════════════════════════════════════
*/

function handleExport(format) {
  ElMessage.success(`正在导出 ${format.toUpperCase()} 格式...`)
  if (format === 'txt' && currentDetail.value) {
    const lines = [
      currentDetail.value.title,
      `时间: ${formatTime(currentDetail.value.start_time)} 至 ${fmtTime(currentDetail.value.end_time)}`,
      `地点: ${currentDetail.value.location}`,
      `参会人：${currentDetail.value.participants.map(p => p.real_name).join('、')}`,
      '', '【会议摘要】', currentDetail.value.summary || '（暂无）',
      '', '【转写记录人',
      ...currentDetail.value.transcripts.map(s => `[${formatSec(s.start)}] ${s.speaker}: ${s.text}`),
    ]
    const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `${currentDetail.value.title}.txt`; a.click()
    URL.revokeObjectURL(url)
  }
}

/* ═══════════════════════════════════════════════════════   搜索 & 批量导出
   ══════════════════════════════════════════════════════════════════════════
*/

function updateSelection() { /* 选择状态已通过 v-model 更新 */ }

async function handleSearch() {
  searching.value = true
  try {
    const res = await searchArchives({
      keyword: searchKeyword.value,
      search_mode: isSemanticSearch.value ? 'semantic' : 'keyword',
      meeting_type: filters.meeting_type || undefined,
      start_date: filters.dateRange?.[0]?.toISOString(),
      end_date: filters.dateRange?.[1]?.toISOString(),
      participant_ids: filters.participant_ids.length ? filters.participant_ids : undefined,
      page: pagination.page,
      page_size: pagination.pageSize,
    })
    if (res?.data) {
      resultList.value = res.data.map(r => ({ ...r, selected: false }))
      pagination.total = res.total || 0
    }
  } catch {
    // 保持模拟数据
  } finally {
    searching.value = false
  }
}

async function handleBatchExport() {
  exporting.value = true
  try {
    await batchExport({ meeting_ids: selectedIds.value })
    ElMessage.success('导出任务已创建，完成后将通过通知推送下载链接')
  } catch {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

/* ═══════════════════════════════════════════════════════   工具函数
   ══════════════════════════════════════════════════════════════════════════
*/

function sleep(ms) { return new Promise(r => setTimeout(r, ms)) }
function formatTime(t) { return t ? dayjs(t).format('YYYY-MM-DD HH:mm') : '' }
function fmtTime(t) { return t ? dayjs(t).format('HH:mm') : '' }
function typeLabel(t) {
  return { regular: '例会', special: '专题', decision: '决策', review: '评审', other: '其他' }[t] || t
}

function highlightKeyword(text) {
  if (!searchKeyword.value || !text) return text
  const escaped = searchKeyword.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const regex = new RegExp(`(${escaped})`, 'gi')
  return text.replace(regex, '<mark style="background:#fef08a;padding:0 2px">$1</mark>')
}

function progressColor(rate) {
  if (rate >= 80) return '#67c23a'
  if (rate >= 50) return '#e6a23c'
  return '#f56c6c'
}
function rateClass(rate) {
  if (rate >= 80) return 'rate-good'
  if (rate >= 50) return 'rate-warn'
  return 'rate-bad'
}
function importanceLabel(v) { return { high: '高', medium: '中', low: '低' }[v] || v }
function importanceType(v) { return { high: 'danger', medium: 'warning', low: 'info' }[v] || 'info' }
function priorityLabel(v) { return { high: '高优', medium: '中', low: '低' }[v] || v }
function todoStatusLabel(v) { return { pending: '待处理', in_progress: '进行中', completed: '已完成', overdue: '已逾期' }[v] || v }
function todoSummaryLabel(key) { return { total: '总计', completed: '已完成', in_progress: '进行中', overdue: '已逾期', completion_rate: '完成率' }[key] || key }

function issueArchiveStatusLabel(status) {
  const map = { open: '待处理', explained: '解释', adopted: '采纳-已解决', adopted_resolved: '采纳-已解决', adopted_unresolved: '采纳-未解决', resolved: '采纳-已解' }
  return map[status] || status
}
function issueArchiveStatusType(status) {
  if (status === 'adopted_resolved' || status === 'resolved') return 'success'
  if (status === 'adopted_unresolved') return 'warning'
  if (status === 'adopted') return 'success'
  if (status === 'explained') return 'info'
  return 'danger'
}

watch(detailTab, (tab) => {
  if (tab === 'impl-report' && reportData.value) nextTick(() => initImplBarChart())
  if (tab !== 'records') stopAudio()
})

onMounted(() => {
  if (searchKeyword.value) handleSearch()
})

onUnmounted(() => {
  stopAudio()
  if (implBarChart) { implBarChart.dispose(); implBarChart = null }
})
</script>

<style lang="scss" scoped>
$cyan: #00d4ff;
$cyan-dim: rgba(0,212,255,0.15);
$border: rgba(0,212,255,0.2);
$panel: #14284b;
$panel2: #0b1a2e;
$text-main: #e0eef8;
$text-dim: #5e8aad;

.archive-page {}

.search-card { margin-bottom: 16px; }

.search-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  .search-input { flex: 1; max-width: 600px; }
}

.advanced-filter {
  :deep(.el-collapse-item__header) {
    font-size: 14px;
    color: #5e8aad;
  }
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  label {
    display: block;
    font-size: 14px;
    color: #a8c4dc;
    margin-bottom: 6px;
  }
}

.batch-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background: rgba(0,212,255,0.08);
  border: 1px solid rgba(0,212,255,0.15);
  border-radius: 4px;
  margin-bottom: 12px;
  font-size: 14px;
  color: #00d4ff;
}

/* ─── 搜索结果 ─── */
.results-area {
  .result-card {
    display: flex;
    gap: 12px;
    background: $panel;
    border-radius: 4px;
    padding: 16px;
    margin-bottom: 12px;
    border: 1px solid $border;
    transition: all 0.2s;
    &:hover { border-color: rgba(0,212,255,0.3); box-shadow: 0 4px 12px rgba(0,0,0,0.3); }

    .card-checkbox { padding-top: 4px; }

    .card-body {
      flex: 1;
      cursor: pointer;

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 8px;
      }

      .card-title {
        margin: 0;
        font-size: 16px;
        color: #ffffff;
      }

      .card-tags {
        display: flex;
        align-items: center;
        gap: 8px;
        .card-time { font-size: 14px; color: $text-dim; }
      }

      .card-participants {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        .p-avatar { margin-right: -4px; border: 2px solid $panel; }
        .more-count { font-size: 14px; color: $text-dim; margin-left: 8px; }
      }

      .card-summary {
        font-size: 14px;
        color: #a8c4dc;
        line-height: 1.6;
        margin: 0 0 8px;
      }

      .card-stats {
        display: flex; align-items: center; gap: 8px; font-size: 14px; color: $text-dim;
        b { color: #fff; font-family: monospace; }
        .cs-rate { font-weight: 700; }
      }
    }
  }
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  padding: 16px 0;
}

/* ─── 详情视图 ─── */
.detail-view {
  background: $panel;
  border: 1px solid $border;
  border-radius: 4px;
  padding: 20px 24px;
}

.detail-back-bar {
  display: flex; align-items: center; gap: 12px; margin-bottom: 14px; padding-bottom: 12px; border-bottom: 1px solid $border;
  .detail-back-title { flex: 1; font-size: 18px; font-weight: 600; color: #fff; }
}

.detail-meta-bar {
  display: flex; align-items: center; gap: 18px; flex-wrap: wrap; margin-bottom: 16px;
  .meta-item { display: flex; align-items: center; gap: 5px; font-size: 14px; color: $text-dim; .el-icon { color: #3a5f80; font-size: 14px; } }
}

/* ─── Tabs ─── */
.detail-tabs {
  :deep(.el-tabs__item) { color: $text-dim; &.is-active { color: $cyan; } &:hover { color: $cyan; } }
  :deep(.el-tabs__active-bar) { background: $cyan; }
  :deep(.el-tabs__nav-wrap::after) { background: $border; }
}
.tab-panel { padding: 12px 0; }

/* ─── 会议纪要 ─── */
.minutes-box {
  background: $panel2; border: 1px solid $border; border-radius: 4px; padding: 16px 20px;
  color: $text-main; font-size: 14px; line-height: 1.8;
  :deep(h3) { color: $cyan; margin: 0 0 12px; font-size: 16px; }
  :deep(h4) { color: #e0eef8; margin: 16px 0 8px; font-size: 14px; }
  :deep(p) { margin: 6px 0; }
  :deep(hr) { border: none; border-top: 1px solid $border; margin: 12px 0; }
  :deep(ol) { padding-left: 20px; li { margin: 4px 0; } }
}

.empty-hint { color: $text-dim; font-size: 14px; font-style: italic; padding: 20px 0; text-align: center; }

/* ─── 音字对照 ─── */
.audio-sync-panel { padding: 0; }
.audio-player-bar {
  background: $panel2; border: 1px solid $border; border-radius: 6px; padding: 14px 16px; margin-bottom: 16px;
}
.ap-controls {
  display: flex; align-items: center; gap: 12px; margin-bottom: 10px;
  .ap-time { font-size: 14px; color: $text-dim; font-family: monospace; min-width: 90px; }
  .ap-slider { flex: 1; }
  .ap-volume { width: 80px; }
}
.ap-waveform {
  display: flex; align-items: flex-end; gap: 1px; height: 30px;
  .wave-bar { width: 3px; border-radius: 1px; transition: background 0.3s; }
}
.transcript-list { margin-top: 0; }
.transcript-seg {
  display: flex; align-items: flex-start; gap: 12px; padding: 10px 14px;
  border-left: 3px solid transparent; border-bottom: 1px solid rgba($border, 0.3);
  cursor: pointer; transition: all 0.2s;
  &:hover { background: rgba($cyan, 0.03); }
  &.playing { background: rgba($cyan, 0.08); border-left-color: $cyan; }
  .seg-left { flex-shrink: 0; width: 80px;
    .seg-time { font-size: 14px; color: $text-dim; font-family: monospace; }
    .seg-speaker { font-size: 14px; font-weight: 600; margin-top: 2px; }
  }
  .seg-text { flex: 1; font-size: 14px; color: $text-main; line-height: 1.6; }
  .seg-actions { flex-shrink: 0; padding-top: 2px; }
}

/* ─── 摘要 ─── */
.panel-section { margin-bottom: 20px; }
.section-title { font-size: 14px; font-weight: 600; color: $cyan; letter-spacing: 1px; margin-bottom: 8px; }
.participant-chips { display: flex; flex-wrap: wrap; gap: 6px; .chip-dept { color: $text-dim; font-size: 14px; } }
.summary-box { background: $panel2; border: 1px solid $border; border-radius: 4px; padding: 12px 14px; font-size: 14px; color: $text-main; line-height: 1.7; white-space: pre-wrap; }

.kp-list { display: flex; flex-direction: column; gap: 10px; }
.kp-card {
  padding: 12px 14px; border-radius: 4px; border-left: 3px solid #3a5f80; background: $panel2; border: 1px solid $border;
  &.kp-high { border-left-color: #f56c6c; } &.kp-medium { border-left-color: #e6a23c; } &.kp-low { border-left-color: #67c23a; }
  .kp-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; .kp-title { font-size: 14px; font-weight: 600; color: $text-main; } }
  .kp-content { font-size: 14px; color: $text-dim; line-height: 1.6; }
}

/* ─── 签到表 ─── */
.checkin-table-wrap {
  .checkin-table-title {
    font-size: 15px;
    font-weight: 600;
    color: #a8d8f0;
    margin-bottom: 10px;
    padding-left: 4px;
  }
}
.checkin-archive-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  th, td {
    border: 1px solid rgba(0,212,255,0.2);
    padding: 8px 12px;
    text-align: center;
    color: #c8e6f8;
  }
  th {
    background: rgba(0,212,255,0.1);
    color: #00d4ff;
    font-weight: 600;
  }
  tr:hover td {
    background: rgba(0,212,255,0.05);
  }
}
.sig-img-table {
  height: 36px;
  max-width: 100px;
  object-fit: contain;
}
.sig-empty {
  color: #5e8aad;
}

/* ─── 电子审签 ─── */
.sign-flow {
  position: relative; padding-left: 30px;
  .sign-flow-line { position: absolute; left: 14px; top: 10px; bottom: 10px; width: 2px; background: $border; }
}
.sign-node {
  display: flex; gap: 14px; margin-bottom: 16px; position: relative;
  .sn-dot {
    width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-size: 14px; font-weight: 600; flex-shrink: 0; position: relative; z-index: 1;
    background: $panel2; border: 2px solid $border; color: $text-dim;
  }
  &.signed .sn-dot { background: rgba(#67c23a, 0.15); border-color: #67c23a; color: #67c23a; }
  &.rejected .sn-dot { background: rgba(#f56c6c, 0.15); border-color: #f56c6c; color: #f56c6c; }
  .sn-body {
    flex: 1; padding: 6px 12px; background: $panel2; border: 1px solid $border; border-radius: 4px;
    .sn-name { font-size: 14px; color: $text-main; font-weight: 500; .sn-role { font-size: 14px; color: $text-dim; font-weight: 400; } }
    .sn-time { font-size: 14px; color: $text-dim; margin-top: 2px; }
    .sn-comment { font-size: 14px; color: #8ab8d8; margin-top: 4px; padding: 4px 8px; background: rgba($cyan, 0.04); border-radius: 3px; }
    .sn-sig { margin-top: 4px; .sig-img-sm { height: 24px; opacity: 0.85; } }
  }
}

/* ─── 评审结论 ─── */
.review-conclusion-box {
  background: rgba(0,212,255,0.04);
  border: 1px solid rgba(0,212,255,0.15);
  border-radius: 8px;
  padding: 18px 22px;
  font-size: 14px;
  line-height: 1.8;
  color: $text-main;
  white-space: pre-wrap;
}

/* ─── 问题清单 ─── */
.issue-list-archive {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.issue-archive-item {
  background: $panel2;
  border: 1px solid $border;
  border-radius: 6px;
  padding: 12px 16px;
  &.adopted_resolved { border-left: 3px solid #67c23a; }
  &.explained { border-left: 3px solid #909399; }
  &.adopted_unresolved { border-left: 3px solid #e6a23c; }
  .ia-content { font-size: 14px; color: $text-main; line-height: 1.6; margin-bottom: 6px; }
  .ia-response {
    font-size: 14px; color: #8ab8d8; margin-bottom: 6px; padding: 4px 8px;
    background: rgba(0,212,255,0.05); border-radius: 4px; display: flex; align-items: flex-start; gap: 4px;
  }
  .ia-meta { display: flex; align-items: center; gap: 10px; font-size: 14px; color: $text-dim; }
  .ia-reporter { color: $text-dim; }
}

/* ─── 落实报表 ─── */
.report-toolbar { margin-bottom: 14px; display: flex; gap: 10px; }
.report-preview { background: #fff; color: #333; border-radius: 4px; padding: 20px 24px; font-size: 14px; line-height: 1.7; }
.rp-header {
  border-bottom: 1px solid #ddd; padding-bottom: 10px; margin-bottom: 14px;
  h2 { margin: 0 0 4px; font-size: 18px; color: #1a3a5c; }
  .rp-subtitle { font-size: 14px; color: #555; margin-bottom: 6px; }
  .rp-meta { display: flex; flex-wrap: wrap; gap: 14px; color: #666; font-size: 14px; }
  .rp-participants { margin-top: 4px; color: #555; font-size: 14px; }
}
.rp-section {
  margin-bottom: 18px;
  .rp-section-title { font-size: 14px; font-weight: 600; color: #1a3a5c; padding-bottom: 5px; border-bottom: 2px solid #e0eaf4; margin-bottom: 10px; }
}
.rp-summary-row {
  display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 12px;
  .rp-stat {
    display: flex; flex-direction: column; align-items: center; padding: 6px 14px; background: #f5f8fc; border-radius: 4px; min-width: 65px;
    .rp-stat-val { font-size: 16px; font-weight: 700; color: #1a3a5c; font-family: monospace; }
    .rp-stat-key { font-size: 14px; color: #888; margin-top: 2px; }
  }
}
.impl-bar-chart { width: 100%; height: 220px; }
.rp-table {
  width: 100%; border-collapse: collapse; font-size: 14px;
  th, td { border: 1px solid #dce6f0; padding: 5px 8px; }
  th { background: #f0f4fa; font-weight: 600; color: #333; }
  .rate-good { color: #27ae60; font-weight: 600; } .rate-warn { color: #f39c12; font-weight: 600; } .rate-bad { color: #e74c3c; font-weight: 600; }
}
.rp-text { background: #f8f9fb; padding: 8px 12px; border-radius: 4px; color: #444; }
.rp-recommendation { background: #f0f7ff; padding: 10px 14px; border-radius: 4px; border-left: 3px solid #409eff; color: #1b3a6c; white-space: pre-wrap; }
.rp-timeline { padding-left: 20px; position: relative;
  &::before { content: ''; position: absolute; left: 6px; top: 4px; bottom: 4px; width: 2px; background: #d0dce8; }
}
.rt-item {
  display: flex; align-items: flex-start; gap: 12px; margin-bottom: 10px; position: relative;
  .rt-dot { width: 10px; height: 10px; border-radius: 50%; background: #409eff; flex-shrink: 0; margin-top: 4px; position: relative; z-index: 1; }
  .rt-date { font-size: 14px; color: #888; width: 80px; flex-shrink: 0; }
  .rt-content { font-size: 14px; color: #333; flex: 1; }
}
.report-empty { color: $text-dim; font-size: 14px; font-style: italic; padding: 20px 0; text-align: center; }

/* ─── 通用 ─── */
.rate-good { color: #67c23a; font-weight: 700; }
.rate-warn { color: #e6a23c; font-weight: 700; }
.rate-bad { color: #f56c6c; font-weight: 700; }
</style>
