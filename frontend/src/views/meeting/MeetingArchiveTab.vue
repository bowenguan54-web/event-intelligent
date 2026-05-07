<template>
  <div class="archive-page">
    <!-- 页面标题区 -->
    <div class="page-header">
      <div class="header-info">
        <h2 class="page-title">会后事项管理</h2>
      </div>
    </div>

    <!-- 主体：左列表 + 右详情 -->
    <div class="main-layout">

      <!-- ====== 左侧列表面板 ====== -->
      <div class="left-panel">
        <div class="list-toolbar">
          <el-input v-model="keyword" placeholder="搜索会议..." prefix-icon="Search" clearable size="small"
            @keyup.enter="fetchList(1)" @clear="fetchList(1)" />
          <el-date-picker v-model="dateRange" type="daterange" range-separator="—" start-placeholder="开始"
            end-placeholder="结束" size="small" style="width:220px" @change="fetchList(1)" />
        </div>
        <div class="list-overview">
          <span class="ov-item">共<b>{{ overview.total }}</b> 个归档</span>
          <span class="ov-item">待办 <b>{{ overview.todo_total }}</b></span>
          <span class="ov-item">完成 <b>{{ overview.todo_completed }}</b></span>
          <span class="ov-item" :class="rateClass(overview.completion_rate)">{{ overview.completion_rate }}%</span>
        </div>
        <div class="meeting-list" v-loading="loading">
          <div v-for="m in archiveList" :key="m.id" class="meeting-item"
            :class="{ active: cur?.id === m.id, 'is-demo': m.id === 'demo-1' }" @click="selectMeeting(m)">
            <div class="mi-title">
              {{ m.title }}
              <el-tag v-if="m.id === 'demo-1'" size="small" class="demo-badge">示例</el-tag>
            </div>
            <div class="mi-meta">
              <span>{{ fmtDate(m.start_time) }}</span>
              <span v-if="m.location">· {{ m.location }}</span>
            </div>
            <div class="mi-bottom">
              <span class="mi-people">{{ m.participants_count }}人</span>
              <div v-if="m.todo_total > 0" class="mi-progress">
                <el-progress :percentage="m.completion_rate||0" :stroke-width="4" :show-text="false"
                  :color="progressColor(m.completion_rate)" style="width:60px" />
                <span class="mi-prog-text">{{ m.todo_completed }}/{{ m.todo_total }}</span>
              </div>
              <span v-else class="mi-no-todo">无待办</span>
            </div>
          </div>
          <div v-if="!loading && archiveList.length === 0" class="list-empty">暂无归档会议</div>
        </div>
        <div v-if="pagination.total > pagination.pageSize" class="list-pagination">
          <el-pagination v-model:current-page="pagination.page" :total="pagination.total"
            :page-size="pagination.pageSize" layout="prev,pager,next" small background @current-change="fetchList" />
        </div>
      </div>

      <!-- ====== 右侧详情面板 ====== -->
      <div class="right-panel">
        <div v-if="!cur" class="no-selection">
          <el-empty description="请从左侧选择一个归档会议" />
        </div>
        <div v-else-if="loadingDetail" class="detail-loading">
          <el-icon class="is-loading" :size="32"><Loading /></el-icon>
          <span>加载中..</span>
        </div>

        <template v-else-if="fullData">
          <!-- 会议信息头 -->
          <div class="detail-header">
            <div class="detail-header-top" :class="{ 'is-demo-header': cur?.id === 'demo-1' }">
              <h3 class="detail-title">{{ fullData.title }}</h3>
              <div class="header-actions">
                <el-dropdown trigger="click" @command="handleExport">
                  <el-button size="small"><el-icon><Download /></el-icon>导出会议记录</el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="mp4"><el-icon><VideoCamera /></el-icon>导出音频 (.mp4)</el-dropdown-item>
                      <el-dropdown-item command="docx" divided><el-icon><Document /></el-icon>导出 Word (.docx)</el-dropdown-item>
                      <el-dropdown-item command="pdf"><el-icon><Document /></el-icon>导出 PDF</el-dropdown-item>
                      <el-dropdown-item command="xml"><el-icon><Document /></el-icon>导出 XML</el-dropdown-item>
                      <el-dropdown-item command="txt"><el-icon><Document /></el-icon>导出 纯文本(.txt)</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
                <el-button type="danger" size="small" :loading="deletingMeeting" @click="handleDeleteMeeting">
                  <el-icon><Delete /></el-icon>删除会议
                </el-button>
              </div>
            </div>
            <div class="detail-meta-bar">
              <div class="meta-item"><el-icon><Calendar /></el-icon><span>{{ fmtDate(fullData.start_time) }} — {{ fmtTime(fullData.end_time) }}</span></div>
              <div class="meta-item" v-if="fullData.location"><el-icon><Location /></el-icon><span>{{ fullData.location }}</span></div>
              <div class="meta-item"><el-icon><User /></el-icon><span>{{ fullData.participants.length }}人参会</span></div>
              <el-tag type="success" size="small" effect="plain">已归档</el-tag>
            </div>
          </div>

          <!-- 功能 Tabs -->
          <el-tabs v-model="detailTab" class="detail-tabs">

            <!-- ①会议摘要 -->
            <el-tab-pane label="📊 会议摘要" name="summary">
              <div class="tab-panel">
                <div class="panel-section">
                  <div class="section-title">参会人员</div>
                  <div class="participant-chips">
                    <el-tag v-for="p in fullData.participants" :key="p.id" size="small" effect="plain" class="p-chip"
                      :type="p.is_leader ? 'danger' : (p.is_expert_in_meeting ? 'warning' : '')">
                      <span v-if="p.is_leader" style="font-size:14px;margin-right:2px">组长·</span>
                      <span v-else-if="p.is_expert_in_meeting" style="font-size:14px;margin-right:2px">专家·</span>
                      {{ p.real_name }}<span v-if="p.professional_title" class="chip-dept">·{{ p.professional_title }}</span><span v-else-if="p.department" class="chip-dept">·{{ p.department }}</span>
                    </el-tag>
                  </div>
                </div>
                <div class="panel-section">
                  <div class="section-title-row">
                    <span class="section-title">会议摘要</span>
                    <div class="section-actions">
                      <el-button v-if="!editingSummary" type="info" plain size="small" @click="startEditSummary">
                        <el-icon><Edit /></el-icon>编辑
                      </el-button>
                      <template v-if="editingSummary">
                        <el-button type="primary" size="small" @click="saveSummary">保存</el-button>
                        <el-button size="small" @click="cancelEditSummary">取消</el-button>
                      </template>
                      <el-button type="primary" size="small" :loading="generatingSummary" @click="doGenerateSummary">
                        <el-icon><MagicStick /></el-icon>{{ fullData.summary ? '重新生成' : 'AI 生成摘要' }}
                      </el-button>
                    </div>
                  </div>
                  <el-input v-if="editingSummary" type="textarea" v-model="summaryEditText" :rows="10" class="summary-edit-area" />
                  <template v-else>
                    <div v-if="fullData.summary" class="summary-box">{{ fullData.summary }}</div>
                    <div v-else class="summary-empty">暂无摘要，点击「AI 生成摘要」自动生成</div>
                  </template>
                </div>
              </div>
            </el-tab-pane>

            <!-- ②会议记录（含音频转写） -->
            <el-tab-pane label="📋 会议记录" name="audio-sync">
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
                    <div class="transcript-hint">
                      <el-icon><InfoFilled /></el-icon>
                      点击时间标签可跳转到对应语音位置，直接编辑文字内容即可修改转写结果
                    </div>
                    <!-- 裁剪工具栏 -->
                    <div class="trim-toolbar">
                      <el-button
                        :type="trimMode ? 'danger' : 'warning'"
                        size="small"
                        plain
                        @click="toggleTrimMode"
                      >
                        <el-icon><Scissors /></el-icon>
                        {{ trimMode ? '退出裁剪模式' : '进入裁剪模式' }}
                      </el-button>
                      <template v-if="trimMode">
                        <span class="trim-tip">
                          <el-icon><WarningFilled /></el-icon>
                          点击行右侧「×」标记要删除的段落，已标记 {{ trimMarkedIds.size }} 条
                        </span>
                        <el-button
                          type="danger"
                          size="small"
                          :disabled="trimMarkedIds.size === 0"
                          :loading="trimmingArchive"
                          @click="confirmTrimArchive"
                        >确认裁剪并归档</el-button>
                      </template>
                    </div>
                    <div v-for="(seg, idx) in fullData.transcripts" :key="idx"
                      class="transcript-seg" :class="{ playing: isSegPlaying(seg), 'trim-marked': trimMode && trimMarkedIds.has(seg.segment_id ?? String(idx)) }">
                      <span class="seg-time-tag" @click.stop="seekToSeg(seg)">{{ formatSec(seg.start) }}</span>
                      <span class="seg-speaker-inline" :style="{ color: speakerColor(seg.speaker) }">{{ seg.speaker }}：</span>
                      <div class="seg-text">
                        <el-input type="textarea" :autosize="{ minRows: 1, maxRows: 6 }" v-model="seg.text"
                          :disabled="trimMode"
                          @focus="pauseOnEdit" @blur="onSegBlur(seg, idx)" />
                      </div>
                      <el-button link size="small" v-if="!trimMode" @click.stop="playSegOnly(seg)">
                        <el-icon><VideoPlay /></el-icon>
                      </el-button>
                      <el-button
                        v-if="trimMode"
                        size="small"
                        :type="trimMarkedIds.has(seg.segment_id ?? String(idx)) ? 'danger' : 'default'"
                        circle
                        class="trim-delete-btn"
                        @click.stop="toggleTrimMark(seg.segment_id ?? String(idx))"
                      >
                        <el-icon><Close /></el-icon>
                      </el-button>
                    </div>
                  </div>
              </div>
            </el-tab-pane>

            <!-- 待办分发 -->
            <el-tab-pane label="待办分发" name="todos">
              <div class="tab-panel">
                <div class="todo-toolbar">
                  <el-button type="warning" size="small" :loading="extractingTodos" @click="doAiExtract">
                    <el-icon><MagicStick /></el-icon>AI 智能提取待办
                  </el-button>
                  <el-button type="primary" size="small" @click="openManualTodoDialog">
                    <el-icon><Plus /></el-icon>手动新建待办
                  </el-button>
                  <el-radio-group v-model="todoDensity" size="small" style="margin-left:auto">
                    <el-radio-button value="compact">紧凑</el-radio-button>
                    <el-radio-button value="default">适中</el-radio-button>
                    <el-radio-button value="loose">宽松</el-radio-button>
                  </el-radio-group>
                </div>
                <el-table :data="fullData.todos" class="todo-table" :size="todoDensity === 'loose' ? 'large' : todoDensity === 'compact' ? 'small' : 'default'" :row-style="todoDensity === 'loose' ? { height: '52px' } : {}" style="width:100%">
                  <el-table-column prop="title" label="事项" min-width="180" />
                  <el-table-column prop="assignee_name" label="责任人" width="90" />
                  <el-table-column label="优先级" width="80" align="center">
                    <template #default="{ row }">
                      <el-tag :type="priorityType(row.priority)" size="small" effect="plain">{{ priorityLabel(row.priority) }}</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="状态" width="130" align="center">
                    <template #default="{ row }">
                      <el-tooltip content="状态由关联流程驱动，不可直接修改" placement="top">
                        <el-tag :type="todoStatusType(row.status)" size="small" effect="plain">{{ todoStatusLabel(row.status) }}</el-tag>
                      </el-tooltip>
                      <div v-if="!row.flow_binding_id" class="status-no-flow">未关联流程</div>
                    </template>
                  </el-table-column>
                  <el-table-column prop="due_date" label="截止日期" width="120">
                    <template #default="{ row }"><span style="white-space:nowrap">{{ row.due_date || '未设置' }}</span></template>
                  </el-table-column>
                  <el-table-column label="关联流程" min-width="200" align="center">
                    <template #default="{ row }">
                      <div style="white-space:nowrap">
                      <template v-if="row.flow_binding_id">
                        <el-tag type="success" size="small" effect="plain" style="max-width:90px;overflow:hidden;text-overflow:ellipsis">{{ row.flow_binding_id }}</el-tag>
                        <el-button type="info" link size="small" style="margin-left:4px" @click="openBindFlow(row)">换绑</el-button>
                      </template>
                      <template v-else>
                        <el-button type="primary" link size="small" :loading="row._autoBinding" @click="doAutoBindFlow(row)">
                          <el-icon><Connection /></el-icon>自动匹配
                        </el-button>
                        <el-divider direction="vertical" />
                        <el-button type="info" link size="small" @click="openBindFlow(row)">手动关联</el-button>
                      </template>
                      </div>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-tab-pane>

            <!-- ④进度跟踪 -->
            <el-tab-pane label="📈 进度跟踪" name="track">
              <div class="tab-panel">
                <div class="track-stats">
                  <div class="ts-card ts-total"><span class="ts-num">{{ fullData.todo_stats.total }}</span><span class="ts-label">总计</span></div>
                  <div class="ts-card ts-done"><span class="ts-num">{{ fullData.todo_stats.completed }}</span><span class="ts-label">已完成</span></div>
                  <div class="ts-card ts-prog"><span class="ts-num">{{ fullData.todo_stats.in_progress }}</span><span class="ts-label">进行中</span></div>
                  <div class="ts-card ts-over"><span class="ts-num">{{ fullData.todo_stats.overdue }}</span><span class="ts-label">已逾期</span></div>
                  <div class="ts-card ts-rate">
                    <span class="ts-num" :class="rateClass(fullData.todo_stats.completion_rate)">{{ fullData.todo_stats.completion_rate }}%</span>
                    <span class="ts-label">完成率</span>
                  </div>
                </div>
                <div class="track-chart-row">
                  <div ref="pieChartRef" class="pie-chart"></div>
                  <div class="track-todo-list">
                    <div v-for="t in fullData.todos" :key="t.id" class="tl-row">
                      <span class="tl-title">{{ t.title }}</span>
                      <span class="tl-assignee">{{ t.assignee_name }}</span>
                      <el-tag :type="todoStatusType(t.status)" size="small" effect="plain">{{ todoStatusLabel(t.status) }}</el-tag>
                    </div>
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <!-- ⑤评审结论 -->
            <el-tab-pane label="📝 评审结论" name="review">
              <div class="tab-panel">
                <div v-if="fullData.review_conclusion" class="review-conclusion-box">
                  {{ fullData.review_conclusion }}
                </div>
                <div v-else class="summary-empty">暂无评审结论</div>
              </div>
            </el-tab-pane>

            <!-- ⑥问题清单 -->
            <el-tab-pane label="🔴 问题清单" name="issues">
              <div class="tab-panel">
                <div v-if="fullData.issues?.length" class="issue-list-archive">
                  <div v-for="issue in fullData.issues" :key="issue.id" class="issue-archive-item" :class="issue.status">
                    <!-- 校对状态标记 -->
                    <div class="ia-proofread-bar">
                      <el-tag
                        :type="issue.proofread ? 'success' : 'warning'"
                        size="small"
                        effect="plain"
                      >{{ issue.proofread ? '已校对（锁定）' : '未校对' }}</el-tag>
                    </div>
                    <!-- 编辑模式 -->
                    <template v-if="archiveEditingId === issue.id && !issue.proofread">
                      <el-input v-model="archiveEditingContent" type="textarea" :rows="2" size="small" />
                      <div style="margin-top:6px;display:flex;gap:6px">
                        <el-button type="primary" size="small" @click="saveArchiveIssue(issue)">保存并锁定</el-button>
                        <el-button size="small" @click="archiveEditingId = null">取消</el-button>
                      </div>
                    </template>
                    <!-- 展示模式 -->
                    <template v-else>
                      <div class="ia-content">{{ issue.content }}</div>
                      <div v-if="issue.response" class="ia-response">
                        <el-icon style="font-size:14px;margin-right:4px;vertical-align:middle"><ChatLineRound /></el-icon>{{ issue.response }}
                      </div>
                      <div class="ia-meta">
                        <span>{{ issue.reporter_name }}</span>
                        <el-tag :type="archiveIssueStatusType(issue.status)" size="small" effect="plain">
                          {{ archiveIssueStatusLabel(issue.status) }}
                        </el-tag>
                        <div style="margin-left:auto;display:flex;gap:6px">
                          <!-- 未校对问题可修改一次 -->
                          <el-button
                            v-if="!issue.proofread"
                            size="small" link type="warning"
                            @click="startArchiveEdit(issue)"
                          >
                            <el-icon><Edit /></el-icon>修改
                          </el-button>
                          <el-button
                            size="small" link type="primary"
                            @click="openIssueReply(issue)"
                          >回复/更新</el-button>
                        </div>
                      </div>
                    </template>
                  </div>
                </div>
                <div v-else class="summary-empty">暂无问题记录</div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="会后意见" name="opinions">
              <div class="tab-panel">
                <div class="post-opinion-form">
                  <el-input v-model="postOpinionForm.author_name" placeholder="意见人姓名" style="width:180px" />
                  <el-input v-model="postOpinionForm.author_unit" placeholder="单位信息" style="width:220px" />
                  <el-select v-model="postOpinionForm.author_role" style="width:140px">
                    <el-option label="参会人员" value="participant" />
                    <el-option label="专家" value="expert" />
                    <el-option label="组长" value="leader" />
                  </el-select>
                </div>
                <el-input
                  v-model="postOpinionForm.content"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入会后意见内容"
                  maxlength="500"
                  show-word-limit
                />
                <div style="margin:12px 0 16px">
                  <el-button type="primary" :loading="savingOpinion" @click="submitPostOpinion">录入会后意见</el-button>
                </div>
                <div v-if="fullData.post_opinions?.length" class="issue-list-archive">
                  <div v-for="item in fullData.post_opinions" :key="item.id" class="issue-archive-item">
                    <div class="ia-content">{{ item.content }}</div>
                    <div class="ia-meta">
                      <span>{{ item.author_name }}</span>
                      <el-tag size="small" effect="plain">{{ opinionRoleLabel(item.author_role) }}</el-tag>
                      <span v-if="item.author_unit">{{ item.author_unit }}</span>
                    </div>
                  </div>
                </div>
                <div v-else class="summary-empty">暂无会后意见</div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="归档材料" name="archive-materials">
              <div class="tab-panel">
                <div class="todo-toolbar">
                  <el-button type="primary" size="small" :loading="savingArchiveMaterials" @click="saveArchiveMaterials">保存归档材料</el-button>
                </div>
                <el-table v-if="fullData.attachments?.length" :data="fullData.attachments" size="small">
                  <el-table-column width="60">
                    <template #default="{ row }">
                      <el-checkbox v-model="archivedAttachmentIds" :label="row.id">&nbsp;</el-checkbox>
                    </template>
                  </el-table-column>
                  <el-table-column prop="filename" label="材料名称" min-width="220" />
                  <el-table-column prop="file_type" label="类型" min-width="140" />
                  <el-table-column prop="uploaded_at" label="上传时间" width="180" />
                </el-table>
                <div v-else class="summary-empty">暂无会议材料</div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="电子审签记录" name="esign-records">
              <div class="tab-panel">
                <el-table v-if="fullData.esign_records?.length" :data="fullData.esign_records" size="small">
                  <el-table-column prop="signer_name" label="签字人" min-width="120" />
                  <el-table-column prop="signer_unit" label="单位" min-width="140" />
                  <el-table-column label="环节" width="100">
                    <template #default="{ row }">{{ signStepLabel(row.sign_step) }}</template>
                  </el-table-column>
                  <el-table-column label="类型" width="140">
                    <template #default="{ row }">{{ signTypeLabel(row.sign_type) }}</template>
                  </el-table-column>
                  <el-table-column prop="opinion" label="意见" min-width="180" show-overflow-tooltip />
                  <el-table-column prop="signed_at" label="时间" width="180" />
                </el-table>
                <div v-else class="summary-empty">暂无电子审签记录</div>
              </div>
            </el-tab-pane>



          </el-tabs>
        </template>
      </div>
    </div>

    <!-- ─── 问题回复对话框 ─── -->
    <el-dialog v-model="issueReplyDialog" title="回复/更新问题" width="500px" :destroy-on-close="true">
      <el-form label-width="72px" v-if="issueReplyTarget">
        <el-form-item label="问题">
          <div style="color:#606266;font-size:14px;line-height:1.5">{{ issueReplyTarget.content }}</div>
        </el-form-item>
        <el-form-item label="处理状态">
          <el-select v-model="issueReplyForm.status" style="width:100%">
            <el-option label="解释" value="explained" />
            <el-option label="采纳-未解决" value="adopted_unresolved" />
            <el-option label="采纳-已解决" value="adopted_resolved" />
          </el-select>
        </el-form-item>
        <el-form-item label="回复内容">
          <el-input v-model="issueReplyForm.response" type="textarea" :rows="3" placeholder="请输入回复内容（选填）" maxlength="300" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="issueReplyDialog = false">取消</el-button>
        <el-button type="primary" :loading="savingIssueReply" @click="confirmIssueReply">保存</el-button>
      </template>
    </el-dialog>

    <!-- ─── AI 提取待办对话框 ─── -->
    <el-dialog v-model="aiTodoDialog" title="AI 智能识别待办事项" width="700px" :destroy-on-close="true">
      <div v-if="extractingTodos" class="ai-loading">
        <el-icon class="is-loading" :size="28"><Loading /></el-icon><span>AI 正在分析转写记录...</span>
      </div>
      <div v-else-if="aiSuggestions.length === 0" class="ai-empty">未识别到可提取的待办事项</div>
      <div v-else>
        <p class="ai-hint">AI 从会议记录中识别出以下待办事项，请选择并确认负责人后添加：</p>
        <div v-for="(s, idx) in aiSuggestions" :key="idx" class="suggestion-row"
          :class="{ selected: selectedSuggestions.includes(idx) }" @click="toggleSuggestion(idx)">
          <el-checkbox :model-value="selectedSuggestions.includes(idx)" @change="toggleSuggestion(idx)" />
          <div class="sg-body">
            <div class="sg-title">{{ s.title }}</div>
            <div class="sg-desc" v-if="s.description">{{ s.description }}</div>
            <div class="sg-meta">
              <el-tag :type="priorityType(s.priority)" size="small" effect="plain">{{ priorityLabel(s.priority) }}</el-tag>
              <span class="sg-days" v-if="s.due_days">建议 {{ s.due_days }} 天内完成</span>
            </div>
          </div>
          <div class="sg-assignee" @click.stop>
            <el-select v-model="s._assignee_id" placeholder="指定责任人" size="small" style="width:120px">
              <el-option v-for="p in fullData?.participants||[]" :key="p.id" :label="p.real_name" :value="p.id" />
            </el-select>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="aiTodoDialog=false">取消</el-button>
        <el-button type="primary" :loading="savingSuggestions" :disabled="selectedSuggestions.length===0"
          @click="confirmAddTodos">添加选中 ({{ selectedSuggestions.length }})</el-button>
      </template>
    </el-dialog>

    <!-- 绑定工作流对话框 -->
    <el-dialog v-model="bindFlowDialog" title="关联工作流" width="400px">
      <el-form label-width="80px">
        <el-form-item label="流程 ID">
          <el-input v-model="flowBindInput" placeholder="输入 OA 工作流 ID 或流程编号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bindFlowDialog=false">取消</el-button>
        <el-button type="primary" :loading="bindingFlow" @click="confirmBindFlow">确认绑定</el-button>
      </template>
    </el-dialog>

    <!-- 手动新建待办对话框 -->
    <el-dialog v-model="manualTodoDialog" title="手动新建待办事项" width="560px" :destroy-on-close="true">
      <el-form ref="manualTodoFormRef" :model="manualTodoForm" :rules="manualTodoRules" label-width="80px">
        <el-form-item label="事项描述" prop="title">
          <el-input v-model="manualTodoForm.title" placeholder="请输入待办事项描述" />
        </el-form-item>
        <el-form-item label="详细说明">
          <el-input v-model="manualTodoForm.description" type="textarea" :rows="3" placeholder="可选，输入详细说明" />
        </el-form-item>
        <el-form-item label="责任人" prop="assignee_id">
          <el-select v-model="manualTodoForm.assignee_id" placeholder="选择责任人" filterable style="width: 100%">
            <el-option v-for="p in fullData?.participants||[]" :key="p.id" :label="p.real_name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker v-model="manualTodoForm.due_date" type="date" placeholder="选择截止日期" style="width: 100%" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-radio-group v-model="manualTodoForm.priority">
            <el-radio value="high">高</el-radio>
            <el-radio value="medium">中</el-radio>
            <el-radio value="low">低</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="manualTodoDialog=false">取消</el-button>
        <el-button type="primary" :loading="savingManualTodo" @click="confirmManualTodo">确认创建</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, watch, nextTick, onUnmounted } from 'vue'
import {
  getArchivedMeetings, getArchivedFull,
  generateMeetingSummary, aiExtractTodos,
  deleteMeeting, updateMeetingIssue, createPostOpinion, updateAttachmentArchiveSelection,
  batchDeleteTranscripts,
} from '@/api/meeting'
import { updateTodo, bindFlow, createTodo } from '@/api/todo'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import dayjs from 'dayjs'

/* ════════════════════════════════════════════════════════════════════════════   示例数据
   ═════════════════════════════════════════════════════════════════════════════*/

const DEMO_PARTICIPANTS = [
  { id: 'd1', real_name: '王建国', department: '局领导', role: '主持人' },
  { id: 'd2', real_name: '李敏华', department: '办公室', role: '记录员' },
  { id: 'd3', real_name: '张伟东', department: '信息中心', role: '汇报人' },
  { id: 'd4', real_name: '陈秀芳', department: '财务科', role: '参会人' },
  { id: 'd5', real_name: '刘志强', department: '综合科', role: '参会人' },
  { id: 'd6', real_name: '赵丽娜', department: '人事科', role: '参会人' },
  { id: 'd7', real_name: '杨浩然', department: '技术科', role: '参会人' },
  { id: 'd8', real_name: '周婉茹', department: '行政科', role: '参会人' },
]

const DEMO_LIST_ITEM = {
  id: 'demo-1',
  title: '会议系统功能示例',
  start_time: '2026-03-28T09:00:00',
  end_time: '2026-03-28T11:30:00',
  location: '行政大楼第一会议室',
  participants_count: 8,
  todo_total: 6,
  todo_completed: 4,
  completion_rate: 66.7,
}

const DEMO_FULL = {
  ...DEMO_LIST_ITEM,
  participants: DEMO_PARTICIPANTS,
  summary: `本次会议由王建国副局长主持，八人参会，历时2.5小时。
会议首先听取了各科室2026年第一季度工作完成情况汇报。信息中心张伟东主任介绍了政务信息化二期系统建设进展，目前核心模块开发完成85%，预计4月中旬完成全部部署。财务科陈秀芳科长通报了一季度预算执行情况，总体执行率达72%，部分专项经费需加快支出进度。
会议重点讨论了第二季度五项重点工作：信息化系统全面上线、预算中期调整、全员业务能力提升培训、会议室智能化改造以及跨部门协作机制优化。
会议决定：各科室于4月5日前提交二季度详细工作计划；信息化项目纳入月度督办，每周报送进度；培训计划由人事科牵头于4月30日前完成方案制定。`,

  keypoints: [
    { id: 'k1', title: '一季度信息化系统建设进展通报', importance: 'high',
      content: '张伟东主任汇报：政务信息化二期项目核心模块开发完成85%，数据库迁移已通过压力测试。移动端适配还需2周，预计4月15日可完成全部署。安全等保三级测评已通过，等待正式发证。建议增加2名运维人员保障上线后系统稳定运行。' },
    { id: 'k2', title: '预算执行与资金使用情况', importance: 'high',
      content: '陈秀芳科长通报：一季度预算总额3200万元，已执行2304万元，执行率72%。其中信息化专项执行率仅58%，需加快招标采购流程。建议对执行率低于60%的科室进行重点督办，并将预算执行情况纳入季度考核指标。' },
    { id: 'k3', title: '全员业务能力提升培训计划', importance: 'medium',
      content: '赵丽娜科长提出分三批组织培训：4月中旬开展信息化应用培训，5月安排公文写作与办公规范培训，6月组织跨部门业务交流。计划邀请外部讲师2名，内部讲师4名，培训费用预算18万元。' },
    { id: 'k4', title: '会议室智能化改造方案', importance: 'medium',
      content: '杨浩然副科长介绍3楼会议室改造方案：包括无纸化会议系统、智能签到终端、高清录播设备和远程视频接入。预算约45万元，改造工期约3周，建议5月启动以不影响日常会议使用。' },
    { id: 'k5', title: '跨部门协作机制优化建议', importance: 'low',
      content: '刘志强科长建议建立月度联席会议制度，设立跨部门项目协调员，使用统一的在线协作平台。计划先在信息化项目上试行，积累经验后推广到其他跨部门项目。' },
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
    { id: 't1', title: '完成二期信息化系统全面部署', assignee_name: '张伟东', priority: 'high', status: 'in_progress', due_date: '2026-04-15', flow_binding_id: 'OA-2026-0328-001' },
    { id: 't2', title: '提交二季度预算调整方案', assignee_name: '陈秀芳', priority: 'high', status: 'completed', due_date: '2026-04-05', completed_at: '2026-04-04', flow_binding_id: null },
    { id: 't3', title: '制定全员业务能力培训计划', assignee_name: '赵丽娜', priority: 'medium', status: 'completed', due_date: '2026-04-10', completed_at: '2026-04-09', flow_binding_id: null },
    { id: 't4', title: '细化会议室智能化改造方案并报批', assignee_name: '杨浩然', priority: 'medium', status: 'completed', due_date: '2026-04-08', completed_at: '2026-04-07', flow_binding_id: 'OA-2026-0328-004' },
    { id: 't5', title: '起草跨部门协作管理办法', assignee_name: '刘志强', priority: 'medium', status: 'completed', due_date: '2026-04-12', completed_at: '2026-04-11', flow_binding_id: null },
    { id: 't6', title: '采购新一批办公设备并完成报批', assignee_name: '周婉茹', priority: 'low', status: 'overdue', due_date: '2026-03-30', flow_binding_id: null },
  ],

  todo_stats: { total: 6, completed: 4, in_progress: 1, overdue: 1, completion_rate: 66.7 },

  review_conclusion: '经专家组审议，与会人员一致认为：一季度各项工作推进有序，信息化二期项目建设进度符合预期。建议二季度重点关注系统上线后的运维保障和预算执行进度督办，确保各项决议按期落实。',

  issues: [
    { id: 'i1', content: '信息化专项经费执行率偏低（58%），采购环节流程较长', reporter_name: '陈秀芳', status: 'adopted_unresolved', response: '已协调采购部加快招标流程，预计5月底前完成。' },
    { id: 'i2', content: '系统上线后运维人员不足，需增加2名专职运维', reporter_name: '张伟东', status: 'adopted_resolved', response: '已完成招聘，2名运维人员已于4月1日到岗。' },
    { id: 'i3', content: '会议室改造预算需进一步细化明确各项开支', reporter_name: '杨浩然', status: 'explained', response: '已补充明细预算表，各项开支均有依据。' },
  ],
}

/* ════════════════════════════════════════════════════════════════════════════   响应式状态   ═════════════════════════════════════════════════════════════════════════════*/

const loading = ref(false)
const archiveList = ref([])
const keyword = ref('')
const dateRange = ref(null)
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })
const overview = reactive({ total: 0, todo_total: 0, todo_completed: 0, completion_rate: 0 })

const cur = ref(null)
const fullData = ref(null)
const loadingDetail = ref(false)
const detailTab = ref('summary')
const todoDensity = ref('default')
const savingOpinion = ref(false)
const savingArchiveMaterials = ref(false)
const archivedAttachmentIds = ref([])
const postOpinionForm = reactive({
  author_name: '',
  author_unit: '',
  author_role: 'participant',
  content: '',
})

const generatingSummary = ref(false)
const aiTodoDialog = ref(false)
const aiSuggestions = ref([])
const extractingTodos = ref(false)
const selectedSuggestions = ref([])
const savingSuggestions = ref(false)
const bindFlowDialog = ref(false)
const bindFlowTarget = ref(null)
const flowBindInput = ref('')
const bindingFlow = ref(false)
const pieChartRef = ref(null)
let pieChart = null
// 音字对照
const audioPlaying = ref(false)
const audioCurrentTime = ref(0)
const audioDuration = ref(480)
const audioVolume = ref(70)
let audioTimer = null
const waveHeights = Array.from({ length: 80 }, () => Math.floor(Math.random() * 22) + 4)

// 会议记录裁剪
const trimMode = ref(false)
const trimMarkedIds = ref(new Set())
const trimmingArchive = ref(false)

function toggleTrimMode() {
  trimMode.value = !trimMode.value
  if (!trimMode.value) trimMarkedIds.value = new Set()
}

function toggleTrimMark(segmentId) {
  const s = new Set(trimMarkedIds.value)
  s.has(segmentId) ? s.delete(segmentId) : s.add(segmentId)
  trimMarkedIds.value = s
}

async function confirmTrimArchive() {
  if (trimMarkedIds.value.size === 0) return
  try {
    await ElMessageBox.confirm(
      `将永久删除 ${trimMarkedIds.value.size} 条转写记录，此操作不可恢复，是否继续？`,
      '确认裁剪归档',
      { type: 'warning', confirmButtonText: '确认裁剪', cancelButtonText: '取消' }
    )
  } catch { return }
  trimmingArchive.value = true
  try {
    const segIds = Array.from(trimMarkedIds.value)
    if (cur.value.id !== 'demo-1') {
      await batchDeleteTranscripts(cur.value.id, segIds)
    }
    // 从本地数据移除
    fullData.value.transcripts = fullData.value.transcripts.filter(
      (s, i) => !trimMarkedIds.value.has(s.segment_id ?? String(i))
    )
    trimMarkedIds.value = new Set()
    trimMode.value = false
    ElMessage.success('裁剪归档成功')
  } catch {
    ElMessage.error('操作失败，请重试')
  } finally {
    trimmingArchive.value = false
  }
}

// 会议摘要内联编辑
const editingSummary = ref(false)
const summaryEditText = ref('')
// 会议记录关键点编辑
const editingKpId = ref(null)
const kpEditForm = reactive({ title: '', content: '', importance: 'medium' })

// 问题清单回复
const issueReplyDialog = ref(false)
const issueReplyTarget = ref(null)
const issueReplyForm = reactive({ status: 'explained', response: '' })
const savingIssueReply = ref(false)

// 问题编辑（未校对可修改一次）
const archiveEditingId = ref(null)
const archiveEditingContent = ref('')

function startArchiveEdit(issue) {
  archiveEditingId.value = issue.id
  archiveEditingContent.value = issue.content
}

async function saveArchiveIssue(issue) {
  const content = archiveEditingContent.value.trim()
  if (!content) return
  try {
    if (cur.value?.id !== 'demo-1') {
      await updateMeetingIssue(cur.value.id, issue.id, { content, proofread: true })
    }
    issue.content = content
    issue.proofread = true
    archiveEditingId.value = null
    ElMessage.success('已保存并锁定，会上已校对版本')
  } catch {
    ElMessage.error('保存失败')
  }
}

function archiveIssueStatusLabel(status) {
  const map = { open: '待处理', explained: '解释', adopted_unresolved: '采纳-未解决', adopted_resolved: '采纳-已解决', resolved: '已解决' }
  return map[status] || status
}
function archiveIssueStatusType(status) {
  if (status === 'adopted_resolved' || status === 'resolved') return 'success'
  if (status === 'adopted_unresolved') return 'warning'
  if (status === 'explained') return 'info'
  return 'info'
}
function openIssueReply(issue) {
  issueReplyTarget.value = issue
  issueReplyForm.status = issue.status || 'open'
  issueReplyForm.response = issue.response || ''
  issueReplyDialog.value = true
}
async function confirmIssueReply() {
  if (!issueReplyTarget.value || !cur.value) return
  savingIssueReply.value = true
  try {
    let updated
    if (cur.value.id === 'demo-1') {
      updated = { ...issueReplyTarget.value, status: issueReplyForm.status, response: issueReplyForm.response }
    } else {
      updated = await updateMeetingIssue(cur.value.id, issueReplyTarget.value.id, {
        status: issueReplyForm.status,
        response: issueReplyForm.response,
      })
    }
    const idx = fullData.value.issues.findIndex(i => i.id === issueReplyTarget.value.id)
    if (idx >= 0) fullData.value.issues[idx] = { ...fullData.value.issues[idx], ...updated }
    ElMessage.success('已更新')
    issueReplyDialog.value = false
  } catch (e) { ElMessage.error(e?.response?.data?.detail || '保存失败') }
  finally { savingIssueReply.value = false }
}

// 删除会议
const deletingMeeting = ref(false)

async function handleDeleteMeeting() {
  if (!cur.value) return
  const meetingTitle = fullData.value?.title || cur.value.title || ''
  try {
    const { ElMessageBox } = await import('element-plus')
    await ElMessageBox.confirm(
      `确认删除会议「${meetingTitle}」？删除后数据将无法恢复。`,
      '删除会议',
      { type: 'warning', confirmButtonText: '确认删除', cancelButtonText: '取消', confirmButtonClass: 'el-button--danger' }
    )
  } catch { return }
  deletingMeeting.value = true
  try {
    if (cur.value.id !== 'demo-1') {
      await deleteMeeting(cur.value.id)
    }
    const idx = archiveList.value.findIndex(m => m.id === cur.value.id)
    if (idx >= 0) archiveList.value.splice(idx, 1)
    pagination.total = Math.max(0, pagination.total - 1)
    cur.value = null
    fullData.value = null
    ElMessage.success('会议已删除')
    if (archiveList.value.length > 0) {
      selectMeeting(archiveList.value[0])
    }
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '删除失败')
  } finally {
    deletingMeeting.value = false
  }
}


/* ════════════════════════════════════════════════════════════════════════════   列表 & 选择
   ═════════════════════════════════════════════════════════════════════════════*/

async function fetchList(page) {
  if (page) pagination.page = page
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.pageSize, keyword: keyword.value || undefined }
    if (dateRange.value) {
      params.start_date = dayjs(dateRange.value[0]).toISOString()
      params.end_date = dayjs(dateRange.value[1]).toISOString()
    }
    const res = await getArchivedMeetings(params)
    archiveList.value = res.data || []
    pagination.total = res.total || 0
    if (res.overview) Object.assign(overview, res.overview)
  } catch {
    // API 不可用，列表保持不变
  }
  // 始终将示例数据置顶（若不存在则插入）
  if (!archiveList.value.find(m => m.id === 'demo-1')) {
    archiveList.value.unshift(DEMO_LIST_ITEM)
    pagination.total += 1
    if (archiveList.value.length === 1) {
      Object.assign(overview, { total: 1, todo_total: 6, todo_completed: 4, completion_rate: 66.7 })
    }
  }
  loading.value = false
  // 自动选中第一条
  if (!cur.value && archiveList.value.length > 0) {
    selectMeeting(archiveList.value[0])
  }
}

async function selectMeeting(row) {
  if (cur.value?.id === row.id) return
  cur.value = row
  detailTab.value = 'summary'
  editingSummary.value = false
  editingKpId.value = null
  if (pieChart) { pieChart.dispose(); pieChart = null }
  stopAudio()
  loadingDetail.value = true
  try {
    if (row.id === 'demo-1') {
      // 使用示例数据（深拷贝以支持编辑）
      fullData.value = structuredClone(DEMO_FULL)
    } else {
      const res = await getArchivedFull(row.id)
      fullData.value = res.data
    }
    // 确保每条 issue 都有 proofread 字段
    if (fullData.value?.issues) {
      fullData.value.issues = fullData.value.issues.map(i => ({
        ...i,
        proofread: i.proofread ?? (i.status === 'adopted_resolved'),
      }))
    }
    archivedAttachmentIds.value = (fullData.value?.archived_attachments || []).map(item => item.id)
    Object.assign(postOpinionForm, {
      author_name: '',
      author_unit: '',
      author_role: 'participant',
      content: '',
    })
  } catch {
    ElMessage.error('加载详情失败')
    cur.value = null
  } finally {
    loadingDetail.value = false
  }
}
async function submitPostOpinion() {
  if (!cur.value || !fullData.value) return
  if (!postOpinionForm.author_name.trim() || !postOpinionForm.content.trim()) {
    ElMessage.warning('请填写意见人姓名和意见内容')
    return
  }
  savingOpinion.value = true
  try {
    const payload = {
      author_name: postOpinionForm.author_name.trim(),
      author_unit: postOpinionForm.author_unit.trim(),
      author_role: postOpinionForm.author_role,
      content: postOpinionForm.content.trim(),
    }
    if (cur.value.id === 'demo-1') {
      fullData.value.post_opinions = fullData.value.post_opinions || []
      fullData.value.post_opinions.unshift({
        id: 'demo-op-' + Date.now(),
        ...payload,
        created_at: new Date().toISOString(),
      })
    } else {
      const created = await createPostOpinion(cur.value.id, payload)
      fullData.value.post_opinions = fullData.value.post_opinions || []
      fullData.value.post_opinions.unshift(created?.data || created)
    }
    postOpinionForm.content = ''
    ElMessage.success('会后意见已录入')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '会后意见录入失败')
  } finally {
    savingOpinion.value = false
  }
}

async function saveArchiveMaterials() {
  if (!cur.value || !fullData.value) return
  if (cur.value.id === 'demo-1') {
    fullData.value.archived_attachments = (fullData.value.attachments || []).filter(item => archivedAttachmentIds.value.includes(item.id))
    ElMessage.success('归档材料选择已保存')
    return
  }
  savingArchiveMaterials.value = true
  try {
    await updateAttachmentArchiveSelection(cur.value.id, archivedAttachmentIds.value)
    fullData.value.archived_attachments = (fullData.value.attachments || []).filter(item => archivedAttachmentIds.value.includes(item.id))
    ElMessage.success('归档材料已保存')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '归档材料保存失败')
  } finally {
    savingArchiveMaterials.value = false
  }
}


/* ════════════════════════════════════════════════════════════════════════════   会议摘要内联编辑
   ═════════════════════════════════════════════════════════════════════════════*/

function startEditSummary() {
  summaryEditText.value = fullData.value?.summary || ''
  editingSummary.value = true
}
function saveSummary() {
  if (fullData.value) fullData.value.summary = summaryEditText.value
  editingSummary.value = false
  ElMessage.success('摘要已保存')
}
function cancelEditSummary() {
  editingSummary.value = false
}

/* ════════════════════════════════════════════════════════════════════════════   会议记录关键点编辑   ═════════════════════════════════════════════════════════════════════════════*/

function startEditKp(kp) {
  editingKpId.value = kp.id
  kpEditForm.title = kp.title
  kpEditForm.content = kp.content
  kpEditForm.importance = kp.importance || 'medium'
}
function saveKp(kp) {
  kp.title = kpEditForm.title
  kp.content = kpEditForm.content
  kp.importance = kpEditForm.importance
  editingKpId.value = null
  ElMessage.success('记录已保存')
}
function cancelEditKp() {
  editingKpId.value = null
}

/* ════════════════════════════════════════════════════════════════════════════   会议摘要 & 导出
   ═════════════════════════════════════════════════════════════════════════════*/

async function doGenerateSummary() {
  generatingSummary.value = true
  try {
    if (cur.value.id === 'demo-1') {
      await sleep(800)
      fullData.value.summary = DEMO_FULL.summary
    } else {
      const res = await generateMeetingSummary(cur.value.id)
      fullData.value.summary = res.summary
    }
    ElMessage.success('摘要生成成功')
  } catch { ElMessage.error('摘要生成失败') }
  finally { generatingSummary.value = false }
}

function handleExport(format) {
  if (!fullData.value) return
  if (format === 'mp4') {
    ElMessage.info('音频导出任务已提交，完成后将通过通知下载')
    return
  }
  if (format === 'xml') {
    const xml = [
      '<?xml version="1.0" encoding="UTF-8"?>',
      '<meeting>',
      `  <title>${fullData.value.title}</title>`,
      `  <startTime>${fullData.value.start_time}</startTime>`,
      `  <endTime>${fullData.value.end_time}</endTime>`,
      `  <location>${fullData.value.location || ''}</location>`,
      '  <transcripts>',
      ...fullData.value.transcripts.map(s =>
        `    <segment start="${s.start}" end="${s.end}" speaker="${s.speaker}">${s.text}</segment>`
      ),
      '  </transcripts>',
      '</meeting>',
    ].join('\n')
    downloadText(xml, `${fullData.value.title}.xml`)
    return
  }
  ElMessage.success(`正在导出 ${format.toUpperCase()} 格式...`)
  if (format === 'txt') {
    const lines = [
      fullData.value.title,
      `时间: ${fmtDate(fullData.value.start_time)} — ${fmtTime(fullData.value.end_time)}`,
      `地点: ${fullData.value.location}`,
      `参会人员：${fullData.value.participants.map(p => p.real_name).join('、')}`,
      '', '【会议摘要】', fullData.value.summary || '（暂无）',
      '', '【转写记录】',
      ...fullData.value.transcripts.map(s => `[${formatSec(s.start)}] ${s.speaker}}：${s.text}`),
    ]
    downloadText(lines.join('\n'), `${fullData.value.title}.txt`)
  }
}

function downloadText(text, filename) {
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = filename; a.click()
  URL.revokeObjectURL(url)
}

/* ════════════════════════════════════════════════════════════════════════════   音字对照：模拟播放器
   ═════════════════════════════════════════════════════════════════════════════*/

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
function pauseOnEdit() { stopAudio() }
function onSegBlur() { /* save via API in real mode */ }
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

/* ════════════════════════════════════════════════════════════════════════════   待办 / AI 提取 / 工作流   ═════════════════════════════════════════════════════════════════════════════*/

async function updateTodoStatus(todoId, status) {
  try {
    if (cur.value.id !== 'demo-1') await updateTodo(todoId, { status })
    ElMessage.success('状态已更新')
    recalcStats()
  } catch { ElMessage.error('状态更新失败') }
}
function recalcStats() {
  if (!fullData.value) return
  const s = fullData.value.todo_stats, ts = fullData.value.todos
  s.completed = ts.filter(t => t.status === 'completed').length
  s.in_progress = ts.filter(t => t.status === 'in_progress').length
  s.overdue = ts.filter(t => t.status === 'overdue').length
  s.completion_rate = s.total > 0 ? Math.round(s.completed / s.total * 1000) / 10 : 0
}

async function doAiExtract() {
  extractingTodos.value = true; aiTodoDialog.value = true
  aiSuggestions.value = []; selectedSuggestions.value = []
  try {
    if (cur.value.id === 'demo-1') {
      await sleep(1200)
      aiSuggestions.value = [
        { title: '协调运维人员入职手续', description: '为信息化系统上线后的运维保障招聘2名运维人员', priority: 'high', due_days: 14, suggested_assignee: '赵丽娜', _assignee_id: 'd6' },
        { title: '信息化专项经费加速执行方案', description: '梳理采购流程瓶颈，加快招标进度', priority: 'high', due_days: 7, suggested_assignee: '陈秀芳', _assignee_id: 'd4' },
        { title: '会议室改造施工时间协调', description: '与物业协调5月施工计划，确保不影响日常会议', priority: 'medium', due_days: 20, suggested_assignee: '周婉茹', _assignee_id: 'd8' },
      ]
    } else {
      const res = await aiExtractTodos(cur.value.id)
      const suggestions = res.suggestions || []
      suggestions.forEach(s => {
        s._assignee_id = null
        if (s.suggested_assignee && fullData.value) {
          const match = fullData.value.participants.find(p => p.real_name === s.suggested_assignee)
          if (match) s._assignee_id = match.id
        }
      })
      aiSuggestions.value = suggestions
    }
  } catch { ElMessage.error('AI 提取失败'); aiTodoDialog.value = false }
  finally { extractingTodos.value = false }
}

function toggleSuggestion(idx) {
  const i = selectedSuggestions.value.indexOf(idx)
  if (i >= 0) selectedSuggestions.value.splice(i, 1)
  else selectedSuggestions.value.push(idx)
}

async function confirmAddTodos() {
  const toAdd = selectedSuggestions.value.map(i => aiSuggestions.value[i])
  if (toAdd.some(s => !s._assignee_id)) { ElMessage.warning('请为所有事项指定责任人'); return }
  savingSuggestions.value = true
  try {
    if (cur.value.id === 'demo-1') {
      await sleep(600)
      toAdd.forEach(s => {
        const p = fullData.value.participants.find(x => x.id === s._assignee_id)
        fullData.value.todos.push({
          id: 't-new-' + Date.now() + Math.random(),
          title: s.title, assignee_name: p?.real_name || '', priority: s.priority,
          status: 'pending', due_date: s.due_days ? dayjs().add(s.due_days, 'day').format('YYYY-MM-DD') : null,
          flow_binding_id: null,
        })
      })
      fullData.value.todo_stats.total += toAdd.length
      recalcStats()
    } else {
      for (const s of toAdd) {
        await createTodo({ title: s.title, description: s.description || '', assignee_id: s._assignee_id,
          priority: s.priority || 'medium', due_date: s.due_days ? dayjs().add(s.due_days, 'day').toISOString() : null,
          meeting_id: cur.value.id })
      }
      const res = await getArchivedFull(cur.value.id); fullData.value = res.data
    }
    ElMessage.success(`已添加 ${toAdd.length} 项待办事项`)
    aiTodoDialog.value = false
  } catch { ElMessage.error('添加失败') }
  finally { savingSuggestions.value = false }
}

async function doAutoBindFlow(row) {
  row._autoBinding = true
  try {
    await sleep(1000)
    // 模拟自动匹配：根据待办标题生成流程号
    const autoId = `OA-${dayjs().format('YYYYMMDD')}-${String(row.id).padStart(3, '0')}`
    row.flow_binding_id = autoId
    ElMessage.success(`已自动匹配到流程 ${autoId}`)
  } catch {
    ElMessage.error('自动匹配失败')
  } finally {
    row._autoBinding = false
  }
}

function openBindFlow(row) { bindFlowTarget.value = row; flowBindInput.value = ''; bindFlowDialog.value = true }
async function confirmBindFlow() {
  if (!flowBindInput.value.trim()) { ElMessage.warning('请输入工作流 ID'); return }
  bindingFlow.value = true
  try {
    if (cur.value.id !== 'demo-1') await bindFlow(bindFlowTarget.value.id, { flow_id: flowBindInput.value.trim() })
    bindFlowTarget.value.flow_binding_id = flowBindInput.value.trim()
    bindFlowDialog.value = false; ElMessage.success('工作流绑定成功')
  } catch { ElMessage.error('绑定失败') }
  finally { bindingFlow.value = false }
}

/* ════════════════════════════════════════════════════════════════════════════   手动新建待办
   ═════════════════════════════════════════════════════════════════════════════*/

const manualTodoDialog = ref(false)
const savingManualTodo = ref(false)
const manualTodoFormRef = ref(null)
const manualTodoForm = reactive({ title: '', description: '', assignee_id: null, due_date: null, priority: 'medium' })
const manualTodoRules = {
  title: [{ required: true, message: '请输入事项描述', trigger: 'blur' }],
  assignee_id: [{ required: true, message: '请选择责任人', trigger: 'change' }],
}

function openManualTodoDialog() {
  Object.assign(manualTodoForm, { title: '', description: '', assignee_id: null, due_date: null, priority: 'medium' })
  manualTodoDialog.value = true
}

async function confirmManualTodo() {
  const valid = await manualTodoFormRef.value?.validate().catch(() => false)
  if (!valid) return
  savingManualTodo.value = true
  try {
    if (cur.value.id === 'demo-1') {
      await sleep(400)
      const p = fullData.value.participants.find(x => x.id === manualTodoForm.assignee_id)
      fullData.value.todos.push({
        id: 't-manual-' + Date.now(),
        title: manualTodoForm.title,
        assignee_name: p?.real_name || '',
        priority: manualTodoForm.priority,
        status: 'pending',
        due_date: manualTodoForm.due_date || null,
        flow_binding_id: null,
      })
      fullData.value.todo_stats.total += 1
      recalcStats()
    } else {
      await createTodo({
        title: manualTodoForm.title,
        description: manualTodoForm.description || '',
        assignee_id: manualTodoForm.assignee_id,
        priority: manualTodoForm.priority || 'medium',
        due_date: manualTodoForm.due_date || null,
        meeting_id: cur.value.id,
      })
      const res = await getArchivedFull(cur.value.id)
      fullData.value = res.data
    }
    ElMessage.success('待办事项已创建')
    manualTodoDialog.value = false
  } catch { ElMessage.error('创建失败') }
  finally { savingManualTodo.value = false }
}

/* ════════════════════════════════════════════════════════════════════════════   ECharts 饼图
   ═════════════════════════════════════════════════════════════════════════════*/

function initPieChart(stats) {
  if (!pieChartRef.value || !stats) return
  if (pieChart) pieChart.dispose()
  pieChart = echarts.init(pieChartRef.value)
  const pending = stats.total - stats.completed - stats.in_progress - stats.overdue
  const data = [
    { name: '已完成', value: stats.completed, itemStyle: { color: '#67c23a' } },
    { name: '进行中', value: stats.in_progress, itemStyle: { color: '#409eff' } },
    { name: '已逾期', value: stats.overdue, itemStyle: { color: '#f56c6c' } },
    { name: '待处理', value: Math.max(pending, 0), itemStyle: { color: '#909399' } },
  ].filter(d => d.value > 0)
  pieChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { orient: 'vertical', right: 10, top: 'center', textStyle: { color: '#8aa8c4', fontSize: 12 } },
    series: [{ name: '待办状态', type: 'pie', radius: ['50%', '70%'], center: ['38%', '50%'], data,
      label: { show: stats.total > 0, formatter: '{d}%', color: '#8aa8c4', fontSize: 11 },
      emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.4)' } },
    }],
  })
}

watch(detailTab, (tab) => {
  if (tab === 'track' && fullData.value) nextTick(() => initPieChart(fullData.value.todo_stats))
  if (tab !== 'audio-sync') stopAudio()
})

/* ════════════════════════════════════════════════════════════════════════════   工具函数
   ═════════════════════════════════════════════════════════════════════════════*/

function sleep(ms) { return new Promise(r => setTimeout(r, ms)) }
function fmtDate(t) { return t ? dayjs(t).format('YYYY-MM-DD HH:mm') : '' }
function fmtTime(t) { return t ? dayjs(t).format('HH:mm') : '' }
function opinionRoleLabel(v) { return { participant: '参会人员', expert: '专家', leader: '组长' }[v] || '参会人员' }
function signStepLabel(v) { return { draft: '拟稿', review: '审签' }[v] || v || '-' }
function signTypeLabel(v) { return { draft_sign: '拟稿签署', review_sign: '审签', leader_review: '组长审签' }[v] || v || '-' }
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
function priorityType(v) { return { high: 'danger', medium: 'warning', low: 'info' }[v] || 'info' }
function todoStatusLabel(v) { return { pending: '待处理', in_progress: '进行中', completed: '已完成', overdue: '已逾期' }[v] || v }
function todoStatusType(v) { return { pending: 'info', in_progress: '', completed: 'success', overdue: 'danger' }[v] || 'info' }

onUnmounted(() => {
  stopAudio()
  if (pieChart) { pieChart.dispose(); pieChart = null }
})

fetchList()
</script>

<style lang="scss" scoped>
$cyan: #00d4ff;
$cyan-dim: rgba(0,212,255,0.15);
$cyan-glow: rgba(0,212,255,0.5);
$border: rgba(0,212,255,0.2);
$panel: #14284b;
$panel2: #0b1a2e;
$text-main: #e0eef8;
$text-dim: #5e8aad;

.archive-page { max-width: 1440px; margin: 0 auto; padding: 24px; background: #0e1d38; }

/* ─── 页头 ─── */
.page-header {
  margin-bottom: 20px; padding-bottom: 14px; border-bottom: 1px solid $border;
  .page-title { margin: 0; font-size: 20px; font-weight: 700; color: $cyan; letter-spacing: 3px; text-shadow: 0 0 12px $cyan-glow; }
  .page-desc { margin: 4px 0 0; font-size: 14px; color: $text-dim; }
}

/* ─── 主体 ─── */
.main-layout { display: flex; gap: 20px; min-height: calc(100vh - 160px); }

/* ─── 左侧 ─── */
.left-panel { width: 320px; flex-shrink: 0; display: flex; flex-direction: column; background: $panel; border: 1px solid $border; border-radius: 4px; overflow: hidden; }
.list-toolbar { display: flex; flex-direction: column; gap: 8px; padding: 12px; border-bottom: 1px solid $border; }
.list-overview {
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 8px 12px; border-bottom: 1px solid $border; font-size: 14px; color: $text-dim;
  .ov-item b { color: #fff; font-family: monospace; }
  .rate-good { color: #67c23a; font-weight: 700; }
  .rate-warn { color: #e6a23c; font-weight: 700; }
  .rate-bad { color: #f56c6c; font-weight: 700; }
}
.meeting-list { flex: 1; overflow-y: auto; padding: 4px 0; }
.meeting-item {
  padding: 12px 14px; cursor: pointer; border-bottom: 1px solid rgba($border, 0.4); transition: all 0.2s;
  &:hover { background: rgba($cyan, 0.04); }
  &.active { background: rgba($cyan, 0.08); border-left: 3px solid $cyan; padding-left: 11px; }
  &.is-demo { border-left: 2px solid rgba($cyan, 0.35); }
  .mi-title { font-size: 14px; font-weight: 500; color: $text-main; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-bottom: 4px; display: flex; align-items: center; gap: 6px; }
  .demo-badge { flex-shrink: 0; font-size: 14px; padding: 0 5px; height: 16px; line-height: 16px; border-color: rgba($cyan, 0.5); color: $cyan; background: rgba($cyan, 0.08); }
  .mi-meta { font-size: 14px; color: $text-dim; margin-bottom: 4px; span + span { margin-left: 2px; } }
  .mi-bottom {
    display: flex; align-items: center; justify-content: space-between;
    .mi-people { font-size: 14px; color: $text-dim; background: rgba($cyan, 0.08); padding: 1px 6px; border-radius: 3px; }
    .mi-progress { display: flex; align-items: center; gap: 6px; .mi-prog-text { font-size: 14px; color: $text-dim; } }
    .mi-no-todo { font-size: 14px; color: #5a7088; }
  }
}
.list-empty { padding: 40px 0; text-align: center; color: $text-dim; font-size: 14px; }
.list-pagination { padding: 8px 12px; display: flex; justify-content: center; border-top: 1px solid $border; }

/* ─── 右侧 ─── */
.right-panel { flex: 1; min-width: 0; background: $panel; border: 1px solid $border; border-radius: 4px; padding: 20px 24px; overflow-y: auto; }
.no-selection { display: flex; align-items: center; justify-content: center; height: 400px; }
.detail-loading { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; padding: 80px 0; color: $text-dim; }

.detail-header {
  margin-bottom: 16px; padding-bottom: 14px; border-bottom: 1px solid $border;
  .detail-header-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
  .is-demo-header { border-left: 3px solid rgba($cyan, 0.5); padding-left: 10px; }
  .detail-title { margin: 0 0 8px; font-size: 18px; font-weight: 600; color: #fff; }
  .header-actions { flex-shrink: 0; }
}
.detail-meta-bar {
  display: flex; align-items: center; gap: 18px; flex-wrap: wrap;
  .meta-item { display: flex; align-items: center; gap: 5px; font-size: 14px; color: $text-dim; .el-icon { color: #3a5f80; font-size: 14px; } }
}

/* ─── Tabs ─── */
.detail-tabs {
  :deep(.el-tabs__item) { color: $text-dim; &.is-active { color: $cyan; } &:hover { color: $cyan; } }
  :deep(.el-tabs__active-bar) { background: $cyan; }
  :deep(.el-tabs__nav-wrap::after) { background: $border; }
}
.tab-panel { padding: 12px 0; }
.post-opinion-form {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

/* ─── 摘要 ─── */
.panel-section { margin-bottom: 20px; }
.section-title { font-size: 14px; font-weight: 600; color: $cyan; letter-spacing: 1px; margin-bottom: 8px; }
.section-title-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.participant-chips { display: flex; flex-wrap: wrap; gap: 6px; .chip-dept { color: $text-dim; font-size: 14px; } }
.summary-box { background: $panel2; border: 1px solid $border; border-radius: 4px; padding: 12px 14px; font-size: 14px; color: $text-main; line-height: 1.7; white-space: pre-wrap; }
.summary-empty { color: $text-dim; font-size: 14px; font-style: italic; padding: 14px 0; }

/* ─── 讨论记录 ─── */
.kp-list { display: flex; flex-direction: column; gap: 10px; }
.kp-card {
  padding: 12px 14px; border-radius: 4px; border-left: 3px solid #3a5f80; background: $panel2; border: 1px solid $border;
  &.kp-high { border-left-color: #f56c6c; } &.kp-medium { border-left-color: #e6a23c; } &.kp-low { border-left-color: #67c23a; }
  &.kp-editing { border-left-color: $cyan; border-color: rgba($cyan, 0.4); }
  .kp-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; .kp-title { font-size: 14px; font-weight: 600; color: $text-main; } }
  .kp-header-right { display: flex; align-items: center; flex-shrink: 0; }
  .kp-content { font-size: 14px; color: $text-dim; line-height: 1.6; }
  .kp-edit-form { display: flex; flex-direction: column; gap: 0; }
  .kp-edit-row { display: flex; align-items: center; }
  .kp-edit-actions { display: flex; gap: 8px; margin-top: 10px; }
}
.kp-empty { padding: 30px 0; }
.section-actions { display: flex; align-items: center; gap: 8px; }
.summary-edit-area { margin-top: 8px; }

/* ─── 音字对照 ─── */
.audio-sync-panel { /* container */ padding: 0; }
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
.transcript-list { /* container */ margin-top: 0; }
.transcript-hint {
  display: flex; align-items: center; gap: 6px; font-size: 14px; color: $text-dim;
  padding: 8px 12px; background: rgba($cyan, 0.05); border-radius: 4px; margin-bottom: 10px;
}
.transcript-seg {
  display: flex; align-items: baseline; gap: 8px; padding: 8px 14px;
  border-left: 3px solid transparent; border-bottom: 1px solid rgba($border, 0.3);
  transition: all 0.2s;
  &:hover { background: rgba($cyan, 0.03); }
  &.playing { background: rgba($cyan, 0.08); border-left-color: $cyan; }
  &.trim-marked { background: rgba(#f56c6c, 0.08); border-left-color: #f56c6c; opacity: 0.55; text-decoration: line-through; }
  .seg-time-tag { flex-shrink: 0; font-size: 14px; color: $text-dim; font-family: monospace; min-width: 42px; cursor: pointer; &:hover { color: $cyan; } }
  .seg-speaker-inline { flex-shrink: 0; font-size: 14px; font-weight: 700; white-space: nowrap; }
  .seg-text { flex: 1; :deep(.el-textarea__inner) { background: transparent; border: 1px solid transparent; color: $text-main; font-size: 14px; line-height: 1.7; padding: 2px 6px; &:focus { border-color: $cyan; background: rgba($panel2, 0.6); } } }
  .trim-delete-btn { flex-shrink: 0; margin-left: 4px; }
}
.trim-toolbar {
  display: flex; align-items: center; gap: 10px; padding: 8px 12px;
  background: rgba(#e6a23c, 0.06); border: 1px solid rgba(#e6a23c, 0.2); border-radius: 4px; margin-bottom: 10px;
  .trim-tip { display: flex; align-items: center; gap: 4px; font-size: 13px; color: #e6a23c; flex: 1; }
}

/* ─── 待办 ─── */
.todo-toolbar { margin-bottom: 10px; }
.todo-table { border: 1px solid $border; border-radius: 4px; }
.status-no-flow { font-size: 14px; color: #5e8aad; margin-top: 2px; }

/* ─── 进度跟踪 ─── */
.track-stats { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }
.ts-card {
  display: flex; flex-direction: column; align-items: center; padding: 8px 14px; background: $panel2; border: 1px solid $border; border-radius: 4px; min-width: 65px;
  .ts-num { font-size: 18px; font-weight: 700; font-family: monospace; } .ts-label { font-size: 14px; color: $text-dim; margin-top: 2px; }
}
.ts-total .ts-num { color: #fff; } .ts-done .ts-num { color: #67c23a; } .ts-prog .ts-num { color: $cyan; } .ts-over .ts-num { color: #f56c6c; }
.ts-rate .ts-num { &.rate-good { color: #67c23a; } &.rate-warn { color: #e6a23c; } &.rate-bad { color: #f56c6c; } }
.track-chart-row { display: flex; gap: 16px; align-items: flex-start; }
.pie-chart { width: 280px; height: 220px; flex-shrink: 0; }
.track-todo-list {
  flex: 1; max-height: 220px; overflow-y: auto;
  .tl-row {
    display: flex; align-items: center; gap: 8px; padding: 5px 0; border-bottom: 1px solid rgba($border, 0.5);
    .tl-title { flex: 1; font-size: 14px; color: $text-main; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .tl-assignee { font-size: 14px; color: $text-dim; width: 60px; text-align: right; flex-shrink: 0; }
  }
}

/* ─── AI 对话框 ─── */
.ai-loading { display: flex; align-items: center; gap: 12px; padding: 40px 0; justify-content: center; color: $text-dim; }
.ai-empty { padding: 24px 0; text-align: center; color: $text-dim; }
.ai-hint { font-size: 14px; color: $text-dim; margin-bottom: 10px; }
.suggestion-row {
  display: flex; align-items: flex-start; gap: 10px; padding: 8px 10px; margin-bottom: 6px;
  border: 1px solid $border; border-radius: 4px; cursor: pointer; transition: background 0.2s;
  &:hover, &.selected { background: $cyan-dim; border-color: $cyan; }
  .sg-body { flex: 1;
    .sg-title { font-size: 14px; color: $text-main; font-weight: 500; }
    .sg-desc { font-size: 14px; color: $text-dim; margin-top: 2px; }
    .sg-meta { display: flex; align-items: center; gap: 8px; margin-top: 5px; } .sg-days { font-size: 14px; color: $text-dim; }
  }
  .sg-assignee { flex-shrink: 0; }
}

/* ─── 响应式 ─── */
@media (max-width: 900px) {
  .main-layout { flex-direction: column; }
  .left-panel { width: 100%; max-height: 300px; }
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
  display: flex; flex-direction: column; gap: 10px;
}
.issue-archive-item {
  background: $panel2; border: 1px solid $border; border-radius: 6px; padding: 12px 16px;
  &.resolved { opacity: 0.6; }
  .ia-proofread-bar {
    display: flex; align-items: center; gap: 6px; margin-bottom: 6px;
    .ia-edit-row { display: flex; align-items: flex-start; gap: 8px; width: 100%; }
    .ia-locked-row { display: flex; align-items: center; gap: 6px; font-size: 14px; color: $text-dim; }
  }
  .ia-content { font-size: 14px; color: $text-main; line-height: 1.6; margin-bottom: 6px; }
  .ia-meta { display: flex; align-items: center; gap: 10px; font-size: 14px; color: $text-dim; }
}
</style>
