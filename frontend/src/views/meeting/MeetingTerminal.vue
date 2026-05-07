<template>
  <div class="terminal-page">
    <!-- ===== 顶部全局栏 ===== -->
    <div class="global-bar">
      <div class="back-btn" @click="router.push('/login')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="15 18 9 12 15 6"/></svg>
        返回
      </div>
      <div class="divider-v"></div>
      <svg class="terminal-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><polyline points="9 11 12 14 15 11"/><line x1="12" y1="8" x2="12" y2="14"/></svg>
      <span class="meeting-type-label">会议终端</span>
      <template v-if="meeting.title">
        <div class="divider-v"></div>
        <div class="global-bar-title-group">
          <div class="meeting-name">{{ meeting.title }}</div>
          <div class="meeting-meta-bar">
            <div class="meta-item" v-if="meeting.start_time">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              {{ formatTime(meeting.start_time) }} ~ {{ formatTime(meeting.end_time) }}
            </div>
            <div class="meta-item" v-if="meeting.location">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
              {{ meeting.location }}
            </div>
          </div>
        </div>
      </template>
      <div v-else-if="loading" class="global-bar-title-group">
        <el-skeleton :rows="1" animated style="width:200px" />
      </div>
      <div v-if="meeting.status" class="status-badge">
        <div class="status-dot" :class="meeting.status"></div>{{ statusLabel(meeting.status) }}
      </div>
      <div class="global-bar-right">
        <div class="icon-btn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg>
        </div>
      </div>
    </div>

    <!-- ===== 加载/错误状态 ===== -->
    <div v-if="loading" class="state-center">
      <el-icon class="loading-icon"><Loading /></el-icon>
      <p>加载会议信息…</p>
    </div>
    <div v-else-if="notFound" class="state-center">
      <el-icon style="font-size:48px;color:#f56c6c"><CircleClose /></el-icon>
      <p>未找到该会议</p>
    </div>

    <!-- ===== 待开始：当前时段无会议 ===== -->
    <div v-else-if="meeting.status === 'pending'" class="bigscreen">
      <div class="bigscreen-content">
        <div class="bs-no-meeting-icon">⌛</div>
        <div class="bs-no-meeting-title">当前时段无会议</div>
        <div class="bs-no-meeting-sub">请等待发起人开启会议准备</div>
      </div>
    </div>

    <!-- ===== 准备中：参会者选座（未选座时显示） ===== -->
    <div v-else-if="meeting.status === 'preparing' && !terminalEntered" class="preparing-screen">
      <div class="preparing-content">
        <div class="bs-title">{{ meeting.title }}</div>

        <!-- 已选座位：显示姓名+身份信息 -->
        <template v-if="seatId && seatPerson && seatPerson.userName">
          <div class="seat-display">
            <div class="seat-display-badge">座位 {{ seatPerson.seatLabel || seatId }}</div>
            <div class="seat-display-name">{{ seatPerson.userName }}</div>
            <div class="seat-display-dept" v-if="seatPerson.department">{{ seatPerson.department }}</div>
            <div class="seat-display-title" v-if="seatPerson.professionalTitle">{{ seatPerson.professionalTitle }}</div>
            <div class="seat-display-tags">
              <el-tag v-if="seatPerson.isLeader" type="danger" size="small" effect="dark">专家组长</el-tag>
              <el-tag v-else-if="seatPerson.isExpert" type="warning" size="small" effect="dark">专家</el-tag>
            </div>
          </div>
          <div class="bs-waiting">
            <span class="waiting-dot" /><span class="waiting-dot delay1" /><span class="waiting-dot delay2" />
            <span class="waiting-text">等待会议开始</span>
          </div>
          <el-button type="primary" style="margin-top:20px;padding:10px 28px;font-size:15px" @click="terminalEntered = true">
            进入会议端查看材料
          </el-button>
          <el-button size="small" text style="margin-top:12px;color:#5e8aad" @click="seatId = null; seatPerson = null">
            重新选择座位
          </el-button>
        </template>

        <!-- 座位加载中 -->
        <template v-else-if="seatId && seatLoading">
          <div class="seat-display-loading">加载座位信息…</div>
        </template>

        <!-- 未选座位：显示选座网格 -->
        <template v-else>
          <div class="preparing-hint">请点击您的座位号完成签到准备</div>
          <div v-if="seatList.length > 0" class="seat-select-grid">
            <div
              v-for="seat in seatList"
              :key="seat.id"
              class="seat-select-card"
              @click="selectSeat(seat.id)"
            >
              <div class="seat-select-num">{{ seat.label || seat.id }}</div>
              <div class="seat-select-name" v-if="seat.userName">{{ seat.userName }}</div>
              <div class="seat-select-sub" v-if="getParticipantByUserId(seat.userId)">
                <span v-if="getParticipantByUserId(seat.userId)?.department">{{ getParticipantByUserId(seat.userId).department }}</span>
                <span v-if="getParticipantByUserId(seat.userId)?.professional_title" style="margin-left:4px">{{ getParticipantByUserId(seat.userId).professional_title }}</span>
              </div>
            </div>
          </div>
          <div v-else class="bs-empty">
            <p>暂未设置座位，等待会议开始…</p>
          </div>
          <div class="bs-waiting" style="margin-top:24px">
            <span class="waiting-dot" /><span class="waiting-dot delay1" /><span class="waiting-dot delay2" />
            <span class="waiting-text">等待发起人开始会议</span>
          </div>
        </template>
      </div>
    </div>

    <!-- ===== 准备中/进行中/已结束：主界面 ===== -->
    <div v-else class="terminal-body">
      <!-- 准备阶段提示横幅 -->
      <div v-if="meeting.status === 'preparing'" class="preparing-notice-bar">
        <el-icon><InfoFilled /></el-icon>
        <span>会议准备中，管理员尚未正式开始会议。您可以提前查看会议材料和议程，签到请等待会议开始。</span>
      </div>
      <!-- 自定义导航栏 -->
      <div class="nav-bar">
        <div class="seg-control">
          <div class="tab-item" :class="{ active: activeTab === 'checkin' }" @click="activeTab = 'checkin'">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            签到
          </div>
          <div class="tab-item" :class="{ active: activeTab === 'materials' }" @click="activeTab = 'materials'">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
            会议材料
          </div>
          <div class="tab-item" :class="{ active: activeTab === 'people' }" @click="activeTab = 'people'">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
            参会人员
            <span v-if="participants.length > 0" class="tab-badge">{{ participants.length }}</span>
          </div>
          <div class="tab-item" :class="{ active: activeTab === 'issues' }" @click="activeTab = 'issues'">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            问题记录
          </div>
          <div class="tab-item" :class="{ active: activeTab === 'qa' }" @click="activeTab = 'qa'">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            智能问答
          </div>
          <div class="tab-item" :class="{ active: activeTab === 'summary' }" @click="activeTab = 'summary'">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            实时摘要
          </div>
          <div class="tab-item" :class="{ active: activeTab === 'esign' }" @click="activeTab = 'esign'">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="9" y1="15" x2="15" y2="15"/></svg>
            会议纪要
          </div>
          <div v-if="(seatPerson?.isExpert || seatPerson?.isLeader) && meeting?.has_review_fee" class="tab-item" :class="{ active: activeTab === 'fee' }" @click="activeTab = 'fee'">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
            评审费
          </div>
        </div>
        <div class="nav-bar-right">
          <button class="nav-action-btn btn-ghost">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            会议信息
          </button>
        </div>
      </div>

      <!-- 内容区域 -->
      <div class="content-area">

        <!-- 签到 -->
        <div v-show="activeTab === 'checkin'" class="tab-section">
          <div class="checkin-section">
            <!-- 有座位绑定时：只显示本人 -->
            <template v-if="seatId && seatPerson && seatPerson.userId">
              <!-- 已签到成功 -->
              <div v-if="selfChecked" class="self-signed-done-card">
                <el-icon class="ssd-check-icon"><CircleCheckFilled /></el-icon>
                <div class="ssd-text">签到成功</div>
                <div class="ssd-name">{{ seatPerson.userName }}</div>
                <div class="ssd-dept" v-if="seatPerson.department">{{ seatPerson.department }}</div>
              </div>
              <!-- 未签到：左右分栏布局 -->
              <div v-else class="self-checkin-split-layout">
                <!-- 左侧：身份确认 -->
                <div class="identity-confirm-panel">
                  <div class="icp-title">身份确认</div>
                  <div class="icp-card">
                    <div class="icp-avatar">{{ seatPerson.userName?.charAt(0) }}</div>
                    <div class="icp-name">{{ seatPerson.userName }}</div>
                    <div class="icp-dept" v-if="seatPerson.department">{{ seatPerson.department }}</div>
                    <div class="icp-confirm-badge">
                      <el-icon><Check /></el-icon>
                      <span>已识别</span>
                    </div>
                  </div>
                  <el-button
                    size="small"
                    class="icp-reidentify-btn"
                    @click="seatId = null; seatPerson = null; router.replace({ query: {} })"
                  >
                    不是本人？重新识别
                  </el-button>
                </div>
                <!-- 右侧：手写签名 -->
                <div class="sign-input-panel">
                  <div class="sip-header">
                    <span class="sip-title">手写签名</span>
                    <div class="sip-tools">
                      <el-button size="small" text @click="undoCheckinSign">← 撤销</el-button>
                      <el-button size="small" text @click="clearCheckinSign">✕ 清除</el-button>
                    </div>
                  </div>
                  <div class="sip-canvas-wrap">
                    <canvas
                      ref="checkinCanvasRef"
                      width="800"
                      height="320"
                      class="sip-canvas"
                      @pointerdown="startCheckinSign"
                      @pointermove="moveCheckinSign"
                      @pointerup="endCheckinSign"
                      @pointerleave="endCheckinSign"
                    />
                    <div v-if="!checkinHasDrawn" class="sip-placeholder">
                      <el-icon class="sip-ph-icon"><Edit /></el-icon>
                      <span>请在此处手写签名</span>
                    </div>
                  </div>
                  <div class="sip-footer">
                    <span class="sip-tip">请使用触控笔或手指在上方区域完成签名</span>
                    <el-button
                      type="primary"
                      class="sip-confirm-btn"
                      :loading="checkingIn"
                      @click="handleSelfCheckinWithSign"
                    >
                      <el-icon><Check /></el-icon> 确认签到
                    </el-button>
                  </div>
                </div>
              </div>
              <!-- 签到统计 -->
              <div class="checkin-stats" style="margin-top:24px">
                <el-statistic title="应到人数" :value="participants.length" />
                <el-statistic title="已签到" :value="checkedCount" />
                <el-statistic title="未签到" :value="participants.length - checkedCount" />
              </div>
            </template>

            <!-- 无座位绑定时：表格显示全部参会人员 -->
            <template v-else>
              <div class="checkin-stats">
                <el-statistic title="应到人数" :value="participants.length" />
                <el-statistic title="已签到" :value="checkedCount" />
                <el-statistic title="未签到" :value="participants.length - checkedCount" />
              </div>
              <!-- 专家签到表 -->
              <div v-if="expertParticipants.length > 0" class="checkin-table-section">
                <div class="checkin-table-title">一、专家签到表</div>
                <el-table :data="expertParticipants" border size="small" style="width:100%">
                  <el-table-column type="index" label="序号" width="60" align="center" />
                  <el-table-column prop="real_name" label="姓名" width="100" />
                  <el-table-column prop="department" label="单位" />
                  <el-table-column prop="professional_title" label="职称" width="120" />
                  <el-table-column label="身份" width="90">
                    <template #default="{ row }">
                      <el-tag v-if="row.is_leader" type="danger" size="small">组长</el-tag>
                      <el-tag v-else type="warning" size="small">专家</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="签到状态" width="100">
                    <template #default="{ row }">
                      <el-tag :type="row.checked_in ? 'success' : 'info'" size="small" @click="openCheckinSign(row)" style="cursor:pointer">
                        {{ row.checked_in ? '已签到' : '点击签到' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="签名" width="80">
                    <template #default="{ row }">
                      <el-image v-if="row.signature_image" :src="row.signature_image" style="width:60px;height:28px" fit="contain" />
                      <span v-else class="text-muted">—</span>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
              <!-- 其他人员签到表 -->
              <div v-if="otherParticipants.length > 0" class="checkin-table-section" style="margin-top:16px">
                <div class="checkin-table-title">二、其他人员签到表</div>
                <el-table :data="otherParticipants" border size="small" style="width:100%">
                  <el-table-column type="index" label="序号" width="60" align="center" />
                  <el-table-column prop="real_name" label="姓名" width="100" />
                  <el-table-column prop="department" label="单位" />
                  <el-table-column prop="position" label="职务" width="120" />
                  <el-table-column label="签到状态" width="100">
                    <template #default="{ row }">
                      <el-tag :type="row.checked_in ? 'success' : 'info'" size="small" @click="openCheckinSign(row)" style="cursor:pointer">
                        {{ row.checked_in ? '已签到' : '点击签到' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="签名" width="80">
                    <template #default="{ row }">
                      <el-image v-if="row.signature_image" :src="row.signature_image" style="width:60px;height:28px" fit="contain" />
                      <span v-else class="text-muted">—</span>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
              <el-empty v-if="participants.length === 0" description="暂无参会人员" />

              <!-- 评审费签名表 -->
              <div v-if="meeting?.has_review_fee && expertParticipants.length > 0" class="checkin-table-section" style="margin-top:16px">
                <div class="checkin-table-title">三、评审费签名</div>
                <el-table :data="expertParticipants" border size="small" style="width:100%">
                  <el-table-column type="index" label="序号" width="60" align="center" />
                  <el-table-column prop="real_name" label="姓名" width="100" />
                  <el-table-column prop="department" label="单位" />
                  <el-table-column prop="professional_title" label="职称" width="120" />
                  <el-table-column label="签名状态" width="120">
                    <template #default="{ row }">
                      <el-tag :type="row.fee_signature_image ? 'success' : 'info'" size="small">
                        {{ row.fee_signature_image ? '已签名' : '未签名' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="120">
                    <template #default="{ row }">
                      <el-button
                        size="small"
                        :type="row.fee_signature_image ? 'success' : 'primary'"
                        plain
                        @click="openFeeSign(row)"
                      >
                        {{ row.fee_signature_image ? '重新签名' : '评审费签名' }}
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </template>
          </div>
        </div>

        <!-- 评审费（仅专家且已选座，且会议设置了评审费） -->
        <div v-if="(seatPerson?.isExpert || seatPerson?.isLeader) && meeting?.has_review_fee" v-show="activeTab === 'fee'" class="tab-section">
          <div class="fee-manage-section">
            <!-- 未选座位 -->
            <div v-if="!seatId || !seatPerson?.userId" class="fee-notice-card">
              <el-icon style="font-size:40px;color:#5e8aad"><InfoFilled /></el-icon>
              <p>请先在"签到"标签中选择您的座位，方可填写评审费信息</p>
            </div>
            <template v-else>
              <!-- 头部信息栏 -->
              <div class="fee-manage-header">
                <div class="fee-manage-header-left">
                  <div class="fee-manage-title">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="width:18px;height:18px;flex-shrink:0"><rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>
                    评审费管理
                  </div>
                  <div class="fee-manage-subtitle">请专家完成身份信息填写与手写签名，以确认收取评审费</div>
                </div>
                <div class="fee-manage-stats">
                  <div class="fee-stat-item">
                    <div class="fee-stat-num">{{ expertParticipants.length }}</div>
                    <div class="fee-stat-label">专家总数</div>
                  </div>
                  <div class="fee-stat-item fee-stat-signed">
                    <div class="fee-stat-num">{{ expertParticipants.filter(p => p.fee_signature_image).length }}</div>
                    <div class="fee-stat-label">已签名</div>
                  </div>
                  <div class="fee-stat-item fee-stat-pending">
                    <div class="fee-stat-num">{{ expertParticipants.filter(p => !p.fee_signature_image).length }}</div>
                    <div class="fee-stat-label">待签名</div>
                  </div>
                </div>
              </div>
              <!-- 进度条 -->
              <div class="fee-progress-row">
                <span class="fee-progress-label">签名进度</span>
                <div class="progress-bar-track" style="flex:1">
                  <div class="progress-bar-fill" :style="{ width: (expertParticipants.length > 0 ? Math.round(expertParticipants.filter(p => p.fee_signature_image).length / expertParticipants.length * 100) : 0) + '%' }"></div>
                </div>
                <span class="fee-progress-frac">{{ expertParticipants.filter(p => p.fee_signature_image).length }} / {{ expertParticipants.length }}</span>
              </div>
              <!-- 专家列表 -->
              <div class="fee-group-label">
                <svg viewBox="0 0 24 24" fill="none" stroke="#b37feb" stroke-width="1.8" stroke-linecap="round" style="width:15px;height:15px;flex-shrink:0"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2z"/></svg>
                评审专家 {{ expertParticipants.length }}人
              </div>
              <div class="fee-expert-list">
                <div v-for="p in expertParticipants" :key="p.id" class="fee-expert-item">
                  <div class="fee-expert-avatar" :style="{ background: p.is_leader ? 'linear-gradient(135deg,#7c3aed,#a855f7)' : 'linear-gradient(135deg,#1d4ed8,#3b82f6)' }">
                    {{ (p.real_name || '?').charAt(0) }}
                  </div>
                  <div class="fee-expert-info">
                    <div class="fee-expert-name">
                      {{ p.real_name }}
                      <el-tag v-if="p.is_leader" type="danger" size="small" effect="dark" style="margin-left:6px">专家组长</el-tag>
                    </div>
                    <div class="fee-expert-meta">
                      <span v-if="p.department"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="width:12px;height:12px;vertical-align:middle"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg> {{ p.department }}</span>
                      <span v-if="p.professional_title || p.role_label"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="width:12px;height:12px;vertical-align:middle"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg> {{ p.professional_title || p.role_label }}</span>
                      <span v-if="meeting?.review_fee_amount"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="width:12px;height:12px;vertical-align:middle"><rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg> 评审费：¥{{ Number(meeting.review_fee_amount).toLocaleString() }}</span>
                    </div>
                  </div>
                  <div class="fee-expert-right">
                    <div class="fee-expert-status" :class="p.fee_signature_image ? 'status-signed' : 'status-pending'">
                      <span class="fee-status-dot"></span>
                      {{ p.fee_signature_image ? '已签名' : '待签名' }}
                    </div>
                    <!-- 仅本人显示按钮 -->
                    <button
                      v-if="selfParticipant && p.id === selfParticipant.id"
                      class="fee-sign-btn"
                      @click="openFeeSign(p)"
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="width:13px;height:13px"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                      {{ p.fee_signature_image ? '重新签名' : '填写并签名' }}
                    </button>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </div>

        <!-- 会议材料 -->
        <div v-show="activeTab === 'materials'" class="tab-section">
          <div class="materials-section">
            <template v-if="canAccessMeetingContent">
              <template v-if="attachments.length > 0">
                <!-- 工具栏 -->
                <div class="mat-toolbar">
                  <div style="display:flex;align-items:center;gap:10px;">
                    <div class="search-box">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                      <input v-model="materialSearch" type="text" placeholder="搜索文件名…" />
                    </div>
                    <div class="filter-group">
                      <button
                        v-for="f in [{ label: '全部', key: 'all' }, { label: 'Word', key: 'word' }, { label: 'PDF', key: 'pdf' }, { label: 'PPT', key: 'ppt' }]"
                        :key="f.key"
                        class="filter-btn"
                        :class="{ active: materialTypeFilter === f.key }"
                        @click="materialTypeFilter = f.key"
                      >{{ f.label }}{{ f.key === 'all' ? ' ' + attachments.length : '' }}</button>
                    </div>
                  </div>
                  <div class="toolbar-right">
                    <div class="view-toggle">
                      <div class="view-btn" :class="{ active: materialViewMode === 'list' }" @click="materialViewMode = 'list'">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
                      </div>
                      <div class="view-btn" :class="{ active: materialViewMode === 'grid' }" @click="materialViewMode = 'grid'">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
                      </div>
                    </div>
                  </div>
                </div>
                <!-- 列表视图 -->
                <div v-if="materialViewMode === 'list'" class="file-list">
                  <div v-for="att in filteredAttachments" :key="att.id" class="file-item">
                    <div class="file-icon" :class="getFileTypeCategory(att)" :style="{ background: getFileTypeInfo(att).bg, color: getFileTypeInfo(att).color }">
                      {{ getFileTypeInfo(att).label }}
                    </div>
                    <div class="file-info">
                      <div class="file-name">{{ att.filename }}</div>
                      <div class="file-meta">
                        <div class="file-meta-item" v-if="att.file_size">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                          {{ formatSize(att.file_size) }}
                        </div>
                        <div class="file-meta-item" v-if="att.uploaded_at || att.created_at">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                          {{ formatUploadTime(att.uploaded_at || att.created_at) }}上传
                        </div>
                        <div class="file-meta-item" v-if="att.uploader_name">上传者：{{ att.uploader_name }}</div>
                      </div>
                    </div>
                    <div class="file-actions">
                      <button v-if="canPreview(att)" class="file-btn file-btn-preview" @click="previewFile(att)">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                        预览
                      </button>
                      <button class="file-btn file-btn-download" @click="downloadFile(att)">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                        下载
                      </button>
                    </div>
                  </div>
                  <div v-if="filteredAttachments.length === 0" class="empty-state">
                    <div class="empty-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></div>
                    <div class="empty-title">没有匹配的文件</div>
                  </div>
                </div>
                <!-- 网格视图 -->
                <div v-else class="mat-grid">
                  <div v-for="att in filteredAttachments" :key="att.id" class="mat-grid-item">
                    <div class="mat-grid-type-icon" :style="{ background: getFileTypeInfo(att).bg, color: getFileTypeInfo(att).color }">
                      {{ getFileTypeInfo(att).label }}
                    </div>
                    <div class="file-name" style="text-align:center">{{ att.filename }}</div>
                    <div class="file-meta-item" v-if="att.file_size" style="justify-content:center">{{ formatSize(att.file_size) }}</div>
                    <div class="file-actions" style="justify-content:center">
                      <button v-if="canPreview(att)" class="file-btn file-btn-preview" @click="previewFile(att)">预览</button>
                      <button class="file-btn file-btn-download" @click="downloadFile(att)">下载</button>
                    </div>
                  </div>
                  <div v-if="filteredAttachments.length === 0" class="empty-state">
                    <div class="empty-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></div>
                    <div class="empty-title">没有匹配的文件</div>
                  </div>
                </div>
                <!-- 底部统计 -->
                <div class="materials-stats">
                  <div class="stat-item"><strong>{{ filteredAttachments.length }}</strong> 份文件</div>
                  <div class="divider-v"></div>
                  <div class="stat-item">共 <strong>{{ totalAttachmentSize }}</strong></div>
                  <template v-if="lastUpdatedAt">
                    <div class="divider-v"></div>
                    <div class="stat-item">最近更新：<strong>{{ lastUpdatedAt }}</strong></div>
                  </template>
                </div>
              </template>
              <el-empty v-else description="暂无会议材料" />
            </template>
            <el-empty v-else description="请先完成签到，再查看会议材料" :image-size="52" />
          </div>
        </div>

        <!-- 参会人员 -->
        <div v-show="activeTab === 'people'" class="tab-section">
          <div class="people-section">
            <template v-if="canAccessMeetingContent">
              <!-- 5个统计卡片 -->
              <div class="people-stat-cards">
                <div class="psc-card psc-total">
                  <div class="psc-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                  </div>
                  <div class="psc-num">{{ participants.length }}</div>
                  <div class="psc-label">参会总人数</div>
                </div>
                <div class="psc-card psc-expert">
                  <div class="psc-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2z"/></svg>
                  </div>
                  <div class="psc-num">{{ expertParticipants.length }}</div>
                  <div class="psc-label">专家人数</div>
                </div>
                <div class="psc-card psc-other">
                  <div class="psc-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
                  </div>
                  <div class="psc-num">{{ otherParticipants.length }}</div>
                  <div class="psc-label">其他人员</div>
                </div>
                <div class="psc-card psc-checked-in">
                  <div class="psc-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                  </div>
                  <div class="psc-num">{{ checkedCount }}</div>
                  <div class="psc-label">已签到</div>
                </div>
                <div class="psc-card psc-unchecked">
                  <div class="psc-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
                  </div>
                  <div class="psc-num">{{ participants.length - checkedCount }}</div>
                  <div class="psc-label">未签到</div>
                </div>
              </div>
              <!-- 签到进度条 -->
              <div class="people-progress-wrap">
                <div class="progress-bar-label">签到进度</div>
                <div class="progress-bar-track">
                  <div class="progress-bar-fill" :style="{ width: (participants.length > 0 ? Math.round(checkedCount / participants.length * 100) : 0) + '%' }"></div>
                </div>
                <div class="progress-bar-frac">{{ checkedCount }} / {{ participants.length }}</div>
              </div>
              <!-- 专家表格 -->
              <div v-if="expertParticipants.length > 0" class="people-group-block">
                <div class="people-group-header-bar">
                  <span class="pgb-dot pgb-expert-dot"></span>
                  <span>专家（{{ expertParticipants.length }}人）</span>
                </div>
                <el-table :data="expertParticipants" size="small" style="width:100%" class="people-table">
                  <el-table-column type="index" label="序号" width="60" align="center" />
                  <el-table-column prop="real_name" label="姓名" min-width="100" />
                  <el-table-column prop="department" label="单位" />
                  <el-table-column prop="professional_title" label="职称" width="120" />
                  <el-table-column label="是否组长" width="90" align="center">
                    <template #default="{ row }">
                      <el-tag v-if="row.is_leader" type="danger" size="small" effect="dark">组长</el-tag>
                      <span v-else style="color:#5e8aad">—</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="签到状态" width="100" align="center">
                    <template #default="{ row }">
                      <el-tag v-if="row.checked_in" type="success" size="small">已签到</el-tag>
                      <el-tag v-else type="warning" size="small">未签到</el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
              <!-- 其他人员表格 -->
              <div v-if="otherParticipants.length > 0" class="people-group-block" style="margin-top:16px">
                <div class="people-group-header-bar">
                  <span class="pgb-dot pgb-other-dot"></span>
                  <span>其他人员（{{ otherParticipants.length }}人）</span>
                </div>
                <el-table :data="otherParticipants" size="small" style="width:100%" class="people-table">
                  <el-table-column type="index" label="序号" width="60" align="center" />
                  <el-table-column prop="real_name" label="姓名" min-width="100" />
                  <el-table-column prop="department" label="单位" />
                  <el-table-column prop="position" label="职务" width="120" />
                  <el-table-column label="签到状态" width="100" align="center">
                    <template #default="{ row }">
                      <el-tag v-if="row.checked_in" type="success" size="small">已签到</el-tag>
                      <el-tag v-else type="warning" size="small">未签到</el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </template>
            <el-empty v-else description="请先完成签到，再查看参会人员信息" :image-size="52" />
          </div>
        </div>

        <!-- 问题记录 -->
        <div v-show="activeTab === 'issues'" class="tab-section">
          <div class="issues-section">
            <template v-if="canAccessMeetingContent">
              <!-- 工具栏 -->
              <div class="issues-toolbar">
                <div class="issue-legend">
                  <span class="legend-dot legend-pending"></span><span class="legend-label">未提交</span>
                  <span class="legend-dot legend-submitted"></span><span class="legend-label">已提交</span>
                </div>
                <div class="toolbar-right">
                  <button class="icon-ghost-btn" @click="loadTerminalIssues" :disabled="loadingIssues">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
                    刷新
                  </button>
                  <button v-if="seatPerson?.isExpert" class="primary-btn" @click="showIssueEditor = !showIssueEditor">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                    新增问题
                  </button>
                </div>
              </div>

              <!-- 新增问题输入框 -->
              <div v-if="seatPerson?.isExpert && showIssueEditor" class="issue-editor-card">
                <div class="issue-editor-title">记录问题</div>
                <el-input
                  v-model="issueDraft"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入会中发现的问题或意见"
                  maxlength="300"
                  show-word-limit
                />
                <div class="issue-editor-actions">
                  <el-button size="small" @click="showIssueEditor = false">取消</el-button>
                  <el-button type="primary" size="small" :loading="savingIssue" @click="submitIssueRecord">保存问题</el-button>
                </div>
              </div>

              <!-- 问题列表 -->
              <div v-if="terminalIssues.length > 0">
                <div
                  v-for="issue in terminalIssues"
                  :key="issue.id"
                  class="issue-item"
                  :class="issue.submitted ? 'issue-submitted' : 'issue-pending'"
                >
                  <div class="issue-item-header">
                    <span class="issue-submit-badge" :class="issue.submitted ? 'badge-submitted' : 'badge-pending'">
                      {{ issue.submitted ? '已提交' : '未提交' }}
                    </span>
                    <span class="issue-reporter">{{ issue.reporter_name }}</span>
                    <span v-if="!issue.submitted" class="issue-actions">
                      <button class="issue-action-btn btn-submit-issue" :disabled="submittingIssueId === issue.id" @click="handleSubmitIssue(issue)">
                        <svg v-if="submittingIssueId !== issue.id" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" class="spin"><path d="M12 2a10 10 0 1 0 10 10"/></svg>
                        提交
                      </button>
                      <button class="issue-action-btn btn-delete-issue" :disabled="deletingIssueId === issue.id" @click="handleDeleteIssue(issue)">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>
                        删除
                      </button>
                    </span>
                  </div>
                  <div class="issue-content">{{ issue.content }}</div>
                  <div v-if="issue.response" class="issue-response">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="width:12px;height:12px;flex-shrink:0"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                    管理端回复：{{ issue.response }}
                  </div>
                </div>
              </div>
              <div v-else class="empty-state">
                <div class="empty-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                </div>
                <div class="empty-title">暂无问题记录</div>
                <div class="empty-desc">{{ seatPerson?.isExpert ? '点击右上角"新增问题"开始记录' : '专家可在此记录会议问题' }}</div>
              </div>
            </template>
            <el-empty v-else description="请先完成签到，再查看或录入问题记录" :image-size="52" />
          </div>
        </div>

        <!-- 智能问答 -->
        <div v-show="activeTab === 'qa'" class="tab-section">
          <div class="qa-section">
            <template v-if="canAccessMeetingContent">
              <!-- 头部 -->
              <div class="qa-header">
                <div class="qa-header-left">
                  <div class="qa-header-icon-wrap">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="width:18px;height:18px"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                  </div>
                  <div>
                    <div class="qa-title-row">
                      <span class="qa-title">智能问答</span>
                      <span class="qa-ai-badge">AI助手</span>
                    </div>
                    <div class="qa-subtitle">向AI提问会议基础信息、流程和材料内容</div>
                  </div>
                </div>
                <div class="qa-context-chips">
                  <div class="qa-context-chip">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="width:12px;height:12px"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                    会议材料
                  </div>
                  <div class="qa-context-chip">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="width:12px;height:12px"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                    参会信息
                  </div>
                  <div class="qa-context-chip">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="width:12px;height:12px"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                    会议流程
                  </div>
                </div>
              </div>
              <!-- 消息区 / 空状态 -->
              <div class="qa-messages-area">
                <!-- 有消息时 -->
                <div v-if="qaMessages.length > 0" class="qa-messages">
                  <div v-for="(item, index) in qaMessages" :key="index" class="qa-message" :class="item.role">
                    <div class="qa-role">{{ item.role === 'user' ? '我' : 'AI' }}</div>
                    <div class="qa-content">{{ item.content }}</div>
                  </div>
                  <div v-if="qaLoading" class="qa-message assistant qa-loading-bubble">
                    <div class="qa-role">AI</div>
                    <div class="qa-content">
                      <span class="qa-typing-dot"></span>
                      <span class="qa-typing-dot"></span>
                      <span class="qa-typing-dot"></span>
                    </div>
                  </div>
                </div>
                <!-- 无消息时空状态 -->
                <div v-else class="qa-empty-state">
                  <div class="qa-empty-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" style="width:44px;height:44px"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                  </div>
                  <div class="qa-empty-title">向AI助手提问</div>
                  <div class="qa-empty-desc">可提问关于本次会议的任何问题</div>
                  <div class="qa-quick-section">
                    <div class="qa-quick-label">常见问题</div>
                    <div class="qa-quick-pills">
                      <button class="qa-quick-pill" @click="qaQuestion = '本次会议的主要议程是什么？'; submitQaQuestion()">本次会议的主要议程是什么？</button>
                      <button class="qa-quick-pill" @click="qaQuestion = '参会专家有哪些人？'; submitQaQuestion()">参会专家有哪些人？</button>
                      <button class="qa-quick-pill" @click="qaQuestion = '会议材料有哪几份？'; submitQaQuestion()">会议材料有哪几份？</button>
                      <button class="qa-quick-pill" @click="qaQuestion = '评审费如何领取？'; submitQaQuestion()">评审费如何领取？</button>
                    </div>
                  </div>
                </div>
              </div>
              <!-- 输入区 -->
              <div class="qa-input-area">
                <div class="qa-input-box-wrap">
                  <textarea
                    v-model="qaQuestion"
                    class="qa-input-box"
                    placeholder="输入问题，按 Enter 发送，Shift+Enter 换行..."
                    rows="3"
                    @keydown.enter.exact.prevent="submitQaQuestion"
                  ></textarea>
                  <button class="qa-send-btn" :disabled="qaLoading || !qaQuestion.trim()" @click="submitQaQuestion">
                    <svg v-if="!qaLoading" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="width:18px;height:18px"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                    <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="width:18px;height:18px" class="qa-spin"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
                  </button>
                </div>
              </div>
            </template>
            <div v-else class="qa-section-locked">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" style="width:40px;height:40px;opacity:0.3"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
              <div class="qa-locked-title">请先完成签到</div>
              <div class="qa-locked-desc">完成签到后方可使用智能问答功能</div>
            </div>
          </div>
        </div>

        <!-- 实时摘要 -->
        <div v-show="activeTab === 'summary'" class="tab-section">
          <div class="summary-layout">
            <!-- 左主内容 -->
            <div class="summary-main">
              <div class="summary-header">
                <div class="summary-header-left">
                  <div class="live-indicator">
                    <div class="live-dot"></div>实时更新中
                  </div>
                </div>
                <button class="icon-ghost-btn" @click="refreshSummary" :disabled="loadingSummary">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
                  刷新
                </button>
              </div>
              <div class="summary-content-card">
                <div v-if="realtimeSummary" class="summary-section-block">
                  <div class="summary-block-title">会议主题</div>
                  <div class="summary-content-text">{{ realtimeSummary }}</div>
                </div>
                <div v-if="summaryKeypoints.length > 0" class="summary-section-block">
                  <div class="summary-block-title">核心议题</div>
                  <div v-for="(kp, idx) in summaryKeypoints" :key="idx" class="summary-kp-item">
                    <strong class="kp-title">{{ kp.title }}</strong>
                    <p class="kp-content">{{ kp.content }}</p>
                  </div>
                </div>
                <div v-if="summaryGeneratedAt" class="summary-gen-time">生成于 {{ summaryGeneratedAt }}</div>
                <div v-if="!realtimeSummary" class="empty-state">
                  <div class="empty-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                  </div>
                  <div class="empty-title">会议摘要将实时生成</div>
                  <div class="empty-desc">会议进行中，摘要将实时更新</div>
                </div>
              </div>
            </div>
            <!-- 右侧边栏 -->
            <div class="summary-sidebar">
              <div class="sidebar-card">
                <div class="sidebar-card-title">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
                  更新时间线
                </div>
                <div class="timeline">
                  <div v-if="summaryGeneratedAt" class="timeline-item">
                    <div class="timeline-dot"></div>
                    <div class="timeline-content">
                      <div class="timeline-time">{{ summaryGeneratedAt }}</div>
                      <div class="timeline-text">摘要已生成</div>
                    </div>
                  </div>
                  <div class="timeline-item">
                    <div class="timeline-dot timeline-dot-current"></div>
                    <div class="timeline-content">
                      <div class="timeline-time">实时</div>
                      <div class="timeline-text">持续监听中</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 会议纪要 -->
        <div v-show="activeTab === 'esign'" class="tab-section">
          <div class="esign-section">
            <!-- 纪要未就绪时提示 -->
            <template v-if="!minutesPublished">
              <div class="minutes-status-card">
                <div class="status-card-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                </div>
                <div class="status-card-text">管理员尚未发布会议纪要，请等待管理员发布后再进行审签。</div>
                <button class="icon-ghost-btn" @click="loadMinutesContent" :disabled="loadingMinutes">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
                  刷新状态
                </button>
              </div>
              <div class="waiting-layout">
                <div class="waiting-steps">
                  <div class="step-item">
                    <div class="step-circle step-done">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                    </div>
                    <div class="step-label">会议进行</div>
                  </div>
                  <div class="step-connector step-connector-done"></div>
                  <div class="step-item">
                    <div class="step-circle step-done">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                    </div>
                    <div class="step-label">语音转录</div>
                  </div>
                  <div class="step-connector step-connector-current"></div>
                  <div class="step-item">
                    <div class="step-circle step-current">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><circle cx="12" cy="12" r="3"/></svg>
                    </div>
                    <div class="step-label">生成纪要</div>
                  </div>
                  <div class="step-connector"></div>
                  <div class="step-item">
                    <div class="step-circle step-pending">
                      <span>4</span>
                    </div>
                    <div class="step-label">管理员审核</div>
                  </div>
                  <div class="step-connector"></div>
                  <div class="step-item">
                    <div class="step-circle step-pending">
                      <span>5</span>
                    </div>
                    <div class="step-label">专家组长审签</div>
                  </div>
                </div>
                <div class="waiting-title">等待管理员发布会议纪要</div>
                <div class="waiting-desc">纪要生成后，管理员审核通过后将发布，届时专家组长可进行手写审签</div>
              </div>
            </template>

            <!-- 纪要已发布：左右布局 -->
            <template v-else>
              <div class="esign-layout">
                <!-- 左侧：纸质感文档卡片 -->
                <div class="esign-left">
                  <!-- 文档工具栏 -->
                  <div class="doc-toolbar">
                    <div class="doc-toolbar-left">
                      <div class="doc-title-text">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="9" y1="13" x2="15" y2="13"/><line x1="9" y1="17" x2="15" y2="17"/></svg>
                        {{ meeting?.title || '会议纪要' }}
                      </div>
                      <span v-if="minutesStatus === 'signed'" class="doc-pill published">
                        <svg width="7" height="7" viewBox="0 0 10 10" fill="#00d278"><circle cx="5" cy="5" r="5"/></svg>
                        已归档
                      </span>
                      <span v-else class="doc-pill pending">
                        <svg width="7" height="7" viewBox="0 0 10 10" fill="#ffa500"><circle cx="5" cy="5" r="5"/></svg>
                        审签中
                      </span>
                    </div>
                    <div class="doc-toolbar-right">
                      <button class="toolbar-btn ghost" @click="loadMinutesContent" :disabled="loadingMinutes">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-3.51"/></svg>
                        刷新
                      </button>
                    </div>
                  </div>

                  <!-- 文档滚动区 -->
                  <div class="doc-scroll">
                    <div class="minutes-paper-card">
                      <!-- 顶部4px渐变色条 -->
                      <div class="paper-header-band"></div>

                      <!-- 文档正文 -->
                      <div class="paper-body">
                        <!-- 标题区 -->
                        <div class="paper-title-area">
                          <div class="paper-title-text-center">会 议 纪 要</div>
                          <div class="paper-subtitle-text">本纪要由系统根据会议记录自动生成，经专家组长审签后正式生效</div>
                          <div class="paper-meta-tags">
                            <div class="paper-meta-tag" v-if="meeting?.start_time">
                              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                              <strong>{{ meeting.start_time.slice(0,10) }}</strong>
                            </div>
                            <div class="paper-meta-tag" v-if="meeting?.location">
                              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
                              <strong>{{ meeting.location }}</strong>
                            </div>
                            <div class="paper-meta-tag" v-if="meeting?.start_time">
                              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                              <strong>{{ meeting.start_time.slice(11,16) }}<template v-if="meeting?.end_time"> — {{ meeting.end_time.slice(11,16) }}</template></strong>
                            </div>
                          </div>
                        </div>

                        <div v-if="minutesContent" class="paper-content" v-html="minutesContent" />
                        <div v-else class="paper-placeholder">
                          <span>暂无内容，管理员尚未生成纪要正文</span>
                        </div>

                        <!-- 底部签名区 -->
                        <div class="paper-footer">
                          <div class="paper-sign-col">
                            <div class="paper-sign-label">专家组长签字</div>
                            <div class="paper-sign-line" :class="{ signed: signRecords.some(r => r.sign_step === 'review') }">
                              {{ signRecords.find(r => r.sign_step === 'review')?.signer_name || '' }}
                            </div>
                          </div>
                          <div class="paper-sign-col">
                            <div class="paper-sign-label">记录人签字</div>
                            <div class="paper-sign-line">{{ meeting?.host_name || '' }}</div>
                          </div>
                          <div class="paper-sign-col">
                            <div class="paper-sign-label">日期</div>
                            <div class="paper-sign-line" :class="{ signed: !!meeting?.start_time }">
                              {{ meeting?.start_time ? meeting.start_time.slice(0,10).replace(/-/g, '.') : '' }}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 右侧：三块结构化面板 -->
                <div class="esign-right">
                  <!-- 块1：签审状态 -->
                  <div class="side-block">
                    <div class="side-block-title">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                      签审状态
                    </div>
                    <div class="sign-state-card" :class="minutesStatus === 'signed' ? 'card-success' : selfAlreadySigned ? 'card-blue' : seatPerson?.isLeader ? 'card-orange' : 'card-waiting'">
                      <div class="state-icon-circle" :class="minutesStatus === 'signed' ? 'icon-success' : selfAlreadySigned ? 'icon-blue' : seatPerson?.isLeader ? 'icon-orange' : 'icon-waiting'">
                        <svg v-if="minutesStatus === 'signed'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                        <svg v-else-if="selfAlreadySigned" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polyline points="16 10 11 15 8 12"/></svg>
                        <svg v-else-if="seatPerson?.isLeader" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
                        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                      </div>
                      <div class="state-info">
                        <div class="state-title">
                          <template v-if="minutesStatus === 'signed'">审签完成</template>
                          <template v-else-if="selfAlreadySigned">您已完成审签</template>
                          <template v-else-if="seatPerson?.isLeader">待您审签</template>
                          <template v-else>等待组长审签</template>
                        </div>
                        <div class="state-desc">
                          <template v-if="minutesStatus === 'signed'">所有审签人均已签署<br>纪要内容已正式归档</template>
                          <template v-else-if="selfAlreadySigned">您的签名已记录，等待后续流程</template>
                          <template v-else-if="seatPerson?.isLeader">请点击下方按钮进行手写签名</template>
                          <template v-else>由专家组长 {{ requiredSigners[0]?.signer_name || '—' }} 完成审签</template>
                        </div>
                      </div>
                      <el-button
                        v-if="seatPerson?.isLeader && !selfAlreadySigned && minutesStatus !== 'signed'"
                        type="primary"
                        size="small"
                        @click="leaderSignOverlay = true"
                        class="sign-action-btn"
                      >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="width:13px;height:13px;margin-right:4px"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
                        手写审签
                      </el-button>
                    </div>
                  </div>

                  <!-- 块2：签审流程 -->
                  <div class="side-block">
                    <div class="side-block-title">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
                      签审流程
                    </div>
                    <div class="flow-steps">
                      <!-- Step: 管理员发布 -->
                      <div class="flow-step">
                        <div class="flow-step-track">
                          <div class="flow-dot dot-done">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                          </div>
                          <div class="flow-line line-done"></div>
                        </div>
                        <div class="flow-content">
                          <div class="flow-label label-done">管理员发布纪要</div>
                          <div class="flow-sub">纪要内容已生成并推送</div>
                        </div>
                      </div>
                      <!-- Steps: 每位配置的审签人 -->
                      <template v-for="(signer, idx) in requiredSigners" :key="signer.signer_name">
                        <div class="flow-step">
                          <div class="flow-step-track">
                            <div class="flow-dot" :class="signRecords.some(r => r.signer_name === signer.signer_name && r.sign_step === 'review') ? 'dot-done' : (idx === 0 ? 'dot-current' : 'dot-pending')">
                              <svg v-if="signRecords.some(r => r.signer_name === signer.signer_name && r.sign_step === 'review')" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                              <span v-else>{{ idx + 1 }}</span>
                            </div>
                            <div class="flow-line" :class="signRecords.some(r => r.signer_name === signer.signer_name && r.sign_step === 'review') ? 'line-done' : 'line-pending'"></div>
                          </div>
                          <div class="flow-content">
                            <div class="flow-label" :class="signRecords.some(r => r.signer_name === signer.signer_name && r.sign_step === 'review') ? 'label-done' : ''">
                              {{ signer.signer_name }}
                              <span class="flow-unit">{{ signer.signer_unit }}</span>
                            </div>
                            <div class="flow-sub">{{ signRecords.find(r => r.signer_name === signer.signer_name && r.sign_step === 'review')?.signed_at || (signRecords.some(r => r.signer_name === signer.signer_name && r.sign_step === 'review') ? '已审签' : '待审签') }}</div>
                          </div>
                        </div>
                      </template>
                      <!-- 若无配置审签人，显示通用组长步骤 -->
                      <template v-if="requiredSigners.length === 0">
                        <div class="flow-step">
                          <div class="flow-step-track">
                            <div class="flow-dot" :class="selfAlreadySigned ? 'dot-done' : 'dot-current'">
                              <svg v-if="selfAlreadySigned" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
                            </div>
                            <div class="flow-line" :class="selfAlreadySigned ? 'line-done' : 'line-pending'"></div>
                          </div>
                          <div class="flow-content">
                            <div class="flow-label" :class="selfAlreadySigned ? 'label-done' : ''">专家组长审签</div>
                            <div class="flow-sub">{{ selfAlreadySigned ? '已完成电子签名' : '等待专家组长签名' }}</div>
                          </div>
                        </div>
                      </template>
                      <!-- Step: 纪要归档（最后一步，无line） -->
                      <div class="flow-step">
                        <div class="flow-step-track">
                          <div class="flow-dot" :class="minutesStatus === 'signed' ? 'dot-done' : 'dot-pending'">
                            <svg v-if="minutesStatus === 'signed'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/></svg>
                          </div>
                        </div>
                        <div class="flow-content">
                          <div class="flow-label" :class="minutesStatus === 'signed' ? 'label-done' : ''">纪要归档</div>
                          <div class="flow-sub">{{ minutesStatus === 'signed' ? '已完成归档' : '全部签名后自动归档' }}</div>
                        </div>
                      </div>
                    </div>

                    <!-- 待签提示 -->
                    <div v-if="minutesStatus !== 'signed' && !selfAlreadySigned && !seatPerson?.isLeader" class="pending-tip" style="margin-top:14px">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="width:14px;height:14px;flex-shrink:0;margin-top:1px"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                      <div class="pending-tip-text">还有 <strong>{{ (requiredSigners.length || 1) - signRecords.filter(r => r.sign_step === 'review').length }} 位专家</strong> 尚未完成签名，归档将在全员签名后自动触发。</div>
                    </div>
                  </div>

                  <!-- 块3：签署记录 -->
                  <div class="side-block" v-if="signRecords.length > 0">
                    <div class="side-block-title">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
                      签署记录
                    </div>
                    <div class="signer-list">
                      <div v-for="(rec, idx) in signRecords" :key="rec.id" class="signer-row">
                        <div class="signer-avatar" :class="['avatar-color-' + (idx % 3)]">{{ (rec.signer_name || '?').slice(0,1) }}</div>
                        <div class="signer-info">
                          <div class="signer-name-text">{{ rec.signer_name }}</div>
                          <div class="signer-role-text">{{ rec.sign_step === 'review' ? '审签' : '拟稿' }}</div>
                          <span class="signer-time-text">{{ rec.signed_at }}</span>
                        </div>
                        <span class="signer-status-badge" :class="rec.sign_step === 'review' ? 'badge-signed' : 'badge-draft'">
                          <span class="status-dot-sm" :class="rec.sign_step === 'review' ? 'dot-green' : 'dot-blue'"></span>
                          {{ rec.sign_step === 'review' ? '已审签' : '已拟稿' }}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div v-else class="side-block side-block-empty">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" style="width:24px;height:24px;opacity:0.2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                    <span style="font-size:12px;color:rgba(255,255,255,0.25);margin-top:6px">暂无签署记录</span>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </div>

      </div><!-- /content-area -->
    </div><!-- /terminal-body -->

    <!-- 驳回原因弹窗 -->
    <el-dialog
      v-model="showRejectDialog"
      title="驳回会议纪要"
      width="420px"
      :close-on-click-modal="false"
    >
      <p style="margin:0 0 12px;color:#606266">请填写驳回原因（选填），方便管理员修改。</p>
      <el-input
        v-model="rejectReason"
        type="textarea"
        :rows="3"
        placeholder="请输入驳回原因（选填）"
        maxlength="200"
        show-word-limit
      />
      <template #footer>
        <el-button @click="showRejectDialog = false">取消</el-button>
        <el-button type="danger" :loading="rejectingMinutes" @click="confirmReject">确定驳回</el-button>
      </template>
    </el-dialog>

    <!-- 签到确认弹窗（含手写签到板） -->
    <el-dialog
      v-model="checkinDialogVisible"
      :title="`为 ${checkinTarget?.real_name} 签到`"
      width="560px"
      :close-on-click-modal="false"
    >
      <p style="text-align:center;font-size:16px;margin:16px 0">
        请 <strong>{{ checkinTarget?.real_name }}</strong> 手写签名完成签到
      </p>
      <div class="checkin-dialog-sign-area">
        <div class="checkin-canvas-controls">
          <el-slider v-model="checkinPenWidth" :min="1" :max="8" :step="1" style="width: 100px" />
          <el-button size="small" @click="undoCheckinSign">撤销</el-button>
          <el-button size="small" @click="clearCheckinSign">清除</el-button>
          <el-button size="small" type="primary" plain @click="openCheckinExpand">展开</el-button>
        </div>
        <canvas
          ref="checkinCanvasRef"
          width="500"
          height="160"
          class="checkin-sign-canvas"
          @pointerdown="startCheckinSign"
          @pointermove="moveCheckinSign"
          @pointerup="endCheckinSign"
          @pointerleave="endCheckinSign"
        />
      </div>
      <template #footer>
        <el-button @click="checkinDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="checkingIn" @click="confirmCheckin">确认签到</el-button>
      </template>
    </el-dialog>

    <!-- 签名板展开弹窗（签到）-->
    <el-dialog
      v-model="checkinExpandVisible"
      :title="checkinTarget ? `签到：${checkinTarget.real_name}` : '手写签名（放大）'"
      width="860px"
      :append-to-body="true"
      destroy-on-close
      @closed="checkinTarget = null"
    >
      <p v-if="checkinTarget" style="text-align:center;font-size:15px;margin:0 0 12px;color:#d8f0ff">
        请 <strong>{{ checkinTarget.real_name }}</strong> 在下方手写签名完成签到
      </p>
      <div class="expand-canvas-wrap">
        <div class="expand-canvas-controls">
          <el-slider v-model="checkinPenWidth" :min="1" :max="8" :step="1" style="width: 120px" />
          <el-button size="small" @click="undoCheckinExpand">撤销</el-button>
          <el-button size="small" @click="clearCheckinExpand">清除</el-button>
        </div>
        <canvas
          ref="checkinExpandCanvasRef"
          width="800"
          height="320"
          class="expand-sign-canvas"
          @pointerdown="startCheckinExpandSign"
          @pointermove="moveCheckinExpandSign"
          @pointerup="endCheckinExpandSign"
          @pointerleave="endCheckinExpandSign"
        />
      </div>
      <template #footer>
        <el-button @click="checkinExpandVisible = false; checkinTarget = null">取消</el-button>
        <el-button v-if="checkinTarget" type="primary" :loading="checkingIn" @click="confirmCheckinFromExpand">确认签到</el-button>
        <el-button v-else type="primary" @click="confirmCheckinExpand">确认使用此签名</el-button>
      </template>
    </el-dialog>

    <!-- 签名板展开弹窗（审签）-->
    <el-dialog v-model="signExpandVisible" title="手写签名（放大）" width="860px" :append-to-body="true" destroy-on-close>
      <div class="expand-canvas-wrap">
        <div class="expand-canvas-controls">
          <el-slider v-model="signPenWidth" :min="1" :max="8" :step="1" style="width: 120px" />
          <el-button size="small" @click="undoSignExpand">撤销</el-button>
          <el-button size="small" @click="clearSignExpand">清除</el-button>
        </div>
        <canvas
          ref="signExpandCanvasRef"
          width="800"
          height="320"
          class="expand-sign-canvas"
          @pointerdown="startSignExpandSign"
          @pointermove="moveSignExpandSign"
          @pointerup="endSignExpandSign"
          @pointerleave="endSignExpandSign"
        />
      </div>
      <template #footer>
        <el-button @click="signExpandVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmSignExpand">确认使用此签名</el-button>
      </template>
    </el-dialog>

    <!-- 评审费签名弹窗 -->
    <el-dialog
      v-model="feeSignVisible"
      width="860px"
      :append-to-body="true"
      destroy-on-close
      custom-class="fee-sign-dialog"
      :show-close="false"
      @closed="feeTarget = null"
    >
      <!-- 自定义弹窗头部 -->
      <template #header>
        <div class="fee-dialog-header">
          <div class="fee-dialog-header-left">
            <div class="fee-dialog-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="width:18px;height:18px"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            </div>
            <span>评审费签名：</span>
            <span v-if="feeTarget" class="fee-dialog-person">{{ feeTarget.real_name }}</span>
          </div>
          <button class="fee-dialog-close-btn" @click="feeSignVisible = false; feeTarget = null">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="width:18px;height:18px"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
      </template>
      <!-- 信息提示条 -->
      <div class="fee-dialog-notice" v-if="feeTarget">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="width:15px;height:15px;flex-shrink:0"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        <span>请 <strong style="color:#4096ff">{{ feeTarget.real_name }}</strong> 填写信息并完成手写签名以确认收取评审费，所有信息将被加密保存。</span>
      </div>
      <!-- 表单区域 -->
      <div class="fee-dialog-form-grid">
        <div class="fee-dialog-field">
          <label class="fee-dialog-label"><span class="fee-required">*</span> 身份证号</label>
          <input v-model="feeSignIdCard" class="fee-text-input" placeholder="请输入身份证号" />
        </div>
        <div class="fee-dialog-field">
          <label class="fee-dialog-label"><span class="fee-required">*</span> 银行卡号</label>
          <input v-model="feeSignBankCard" class="fee-text-input" placeholder="请输入银行卡号" />
        </div>
      </div>
      <!-- 签名区 -->
      <div class="fee-dialog-sign-area">
        <div class="fee-dialog-sign-label-row">
          <label class="fee-dialog-label"><span class="fee-required">*</span> 手写签名</label>
          <div class="fee-dialog-sign-actions">
            <button class="fee-canvas-action-btn" @click="undoFeeSign">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="width:13px;height:13px"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-3.04"/></svg>
              撤销
            </button>
            <button class="fee-canvas-action-btn" @click="clearFeeSign">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="width:13px;height:13px"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>
              清除重写
            </button>
          </div>
        </div>
        <div class="fee-sign-canvas-wrap">
          <canvas
            ref="feeSignCanvasRef"
            width="800"
            height="240"
            class="expand-sign-canvas fee-canvas-styled"
            @pointerdown="startFeeSign"
            @pointermove="moveFeeSign"
            @pointerup="endFeeSign"
            @pointerleave="endFeeSign"
          />
          <div class="fee-canvas-placeholder" v-show="!feeHasStrokes">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" style="width:32px;height:32px;opacity:0.3"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            <div class="fee-canvas-hint-title">请在此处手写签名</div>
            <div class="fee-canvas-hint-sub">使用鼠标或触摸笔进行签名</div>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="fee-dialog-footer">
          <div class="fee-dialog-footer-left">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="width:14px;height:14px;flex-shrink:0;opacity:0.6"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            <span>信息加密传输，安全保存</span>
          </div>
          <div class="fee-dialog-footer-right">
            <el-button @click="feeSignVisible = false; feeTarget = null">取消</el-button>
            <el-button type="primary" :loading="submittingFeeSign" @click="confirmFeeSign">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" style="width:14px;height:14px"><polyline points="20 6 9 17 4 12"/></svg>
              确认签名
            </el-button>
          </div>
        </div>
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

    <!-- ===== 专家组长大屏签字板（纪要发布时弹出） ===== -->
    <Teleport to="body">
      <div v-if="leaderSignOverlay" class="leader-sign-overlay">
        <div class="lso-content">
          <div class="lso-notice-bar">
            <el-icon style="font-size:22px;color:#e6a23c"><InfoFilled /></el-icon>
            <span>管理员已发布会议纪要，请您作为专家组长完成审签</span>
          </div>
          <div class="lso-title">{{ meeting.title }}</div>
          <div class="lso-signer">
            审签人：<strong>{{ seatPerson?.userName }}</strong>
            <el-tag type="danger" size="small" effect="dark" style="margin-left:8px">专家组长</el-tag>
          </div>
          <div class="lso-canvas-label">
            <span>请在下方手写签名</span>
            <el-button size="small" text style="color:#8ab4d0" @click="clearLeaderSign">清除</el-button>
          </div>
          <div class="lso-canvas-wrap">
            <canvas
              ref="leaderCanvasRef"
              width="760"
              height="220"
              class="lso-canvas"
              @pointerdown="startLeaderSign"
              @pointermove="moveLeaderSign"
              @pointerup="endLeaderSign"
              @pointerleave="endLeaderSign"
            />
          </div>
          <div class="lso-opinion-row">
            <el-input
              v-model="leaderSignOpinion"
              placeholder="评审意见（选填）"
              style="width:100%;max-width:760px"
            />
          </div>
          <div class="lso-actions">
            <el-button type="success" size="large" :loading="submittingSign" @click="submitLeaderSign">
              <el-icon><Check /></el-icon>&nbsp;同意并签名
            </el-button>
            <el-button type="danger" plain size="large" @click="leaderSignOverlay = false; activeTab = 'esign'">
              <el-icon><CloseBold /></el-icon>&nbsp;驳回 / 查看纪要详情
            </el-button>
          </div>
          <div class="lso-skip" @click="leaderSignOverlay = false; activeTab = 'esign'">前往会议纪要标签查看详情 →</div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getMeetingPublic,
  getPublicParticipants,
  terminalCheckin,
  feeSign,
  getPublicAttachments,
  getSeatPerson,
  publicSignMinutes,
  getMinutesInfo,
  rejectMinutes,
  getTerminalIssues,
  getCurrentMeeting,
  createMeetingIssue,
  deleteMeetingIssue,
  submitMeetingIssue,
  publicMeetingQA,
} from '@/api/meeting'
import { ElMessage } from 'element-plus'
import { Check, Loading, CircleClose, InfoFilled, CircleCheckFilled, Edit, CloseBold } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
let meetingId = route.params.id
const seatId = ref(route.query.seat ? Number.parseInt(route.query.seat) : null)
const terminalEntered = ref(false)

const loading = ref(true)
const notFound = ref(false)
const seatPerson = ref(null)
const seatLoading = ref(false)
const meeting = ref({})
const participants = ref([])
const attachments = ref([])
const activeTab = ref('checkin')
const issueDraft = ref('')
const showIssueEditor = ref(false)
const savingIssue = ref(false)
const qaQuestion = ref('')
const qaLoading = ref(false)
const qaMessages = ref([])
const requiredSigners = ref([])
const signerUnitInput = ref('')

// 文件预览
const previewVisible = ref(false)
const previewUrl = ref('')
const previewTitle = ref('')
const previewType = ref('')

function canPreview(att) {
  const name = (att.filename || '').toLowerCase()
  const type = (att.file_type || '').toLowerCase()
  return type.startsWith('image/') || type === 'application/pdf'
    || name.endsWith('.pdf') || /\.(jpg|jpeg|png|gif|webp|bmp|svg)$/.test(name)
}

function previewFile(att) {
  const name = (att.filename || '').toLowerCase()
  const type = (att.file_type || '').toLowerCase()
  previewUrl.value = `/api/meeting/attachment/${att.id}/download`
  previewTitle.value = att.filename
  if (type === 'application/pdf' || name.endsWith('.pdf')) {
    previewType.value = 'pdf'
  } else if (type.startsWith('image/') || /\.(jpg|jpeg|png|gif|webp|bmp|svg)$/.test(name)) {
    previewType.value = 'image'
  } else {
    previewType.value = 'other'
  }
  previewVisible.value = true
}
let pollTimer = null

const checkinDialogVisible = ref(false)
const checkinTarget = ref(null)
const checkingIn = ref(false)
const checkinHasDrawn = ref(false)

// 材料搜索过滤
const materialSearch = ref('')
const materialTypeFilter = ref('all')
const materialViewMode = ref('list')

const checkedCount = computed(() => participants.value.filter(p => p.checked_in).length)

// 参会人员分组：专家 / 其他人员
const expertParticipants = computed(() => participants.value.filter(p => p.is_expert || p.is_leader))
const otherParticipants = computed(() => participants.value.filter(p => !p.is_expert && !p.is_leader))
// 当前座位绑定用户的参会记录（用于评审费自填）
const selfParticipant = computed(() => {
  if (!seatPerson.value?.userId) return null
  return participants.value.find(p => p.id === seatPerson.value.userId) || null
})

const filteredAttachments = computed(() => {
  let list = attachments.value
  if (materialSearch.value.trim()) {
    const q = materialSearch.value.trim().toLowerCase()
    list = list.filter(att => (att.filename || '').toLowerCase().includes(q))
  }
  if (materialTypeFilter.value !== 'all') {
    list = list.filter(att => getFileTypeCategory(att) === materialTypeFilter.value)
  }
  return list
})

const totalAttachmentSize = computed(() => formatSize(
  attachments.value.reduce((sum, att) => sum + (att.file_size || 0), 0)
))

const lastUpdatedAt = computed(() => {
  const dates = attachments.value
    .map(att => att.uploaded_at || att.created_at)
    .filter(Boolean)
    .map(d => new Date(d).getTime())
    .filter(t => !isNaN(t))
  if (!dates.length) return ''
  return formatUploadTime(new Date(Math.max(...dates)).toISOString())
})

// 问题记录
const terminalIssues = ref([])
const loadingIssues = ref(false)
const deletingIssueId = ref(null)
const submittingIssueId = ref(null)

function terminalIssueStatusLabel(status) {
  const map = { open: '待处理', explained: '已解释', adopted: '已采纳', adopted_resolved: '采纳·已解决', adopted_unresolved: '采纳·未解决' }
  return map[status] || status
}
function terminalIssueStatusType(status) {
  const map = { open: 'danger', explained: 'warning', adopted: 'success', adopted_resolved: 'success', adopted_unresolved: 'info' }
  return map[status] || 'info'
}

async function loadTerminalIssues() {
  loadingIssues.value = true
  try {
    const reporterName = seatPerson.value?.userName
    terminalIssues.value = await getTerminalIssues(meetingId, reporterName)
  } catch { terminalIssues.value = [] }
  finally { loadingIssues.value = false }
}

async function handleDeleteIssue(issue) {
  if (issue.submitted) {
    ElMessage.warning('已提交的问题不可删除')
    return
  }
  deletingIssueId.value = issue.id
  try {
    await deleteMeetingIssue(meetingId, issue.id)
    terminalIssues.value = terminalIssues.value.filter(i => i.id !== issue.id)
    ElMessage.success('问题已删除')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '删除失败')
  } finally {
    deletingIssueId.value = null
  }
}

async function handleSubmitIssue(issue) {
  if (issue.submitted) return
  submittingIssueId.value = issue.id
  try {
    await submitMeetingIssue(meetingId, issue.id)
    const idx = terminalIssues.value.findIndex(i => i.id === issue.id)
    if (idx !== -1) terminalIssues.value[idx] = { ...terminalIssues.value[idx], submitted: true }
    ElMessage.success('问题已提交到管理端')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '提交失败')
  } finally {
    submittingIssueId.value = null
  }
}

async function loadTerminalAttachments() {
  try {
    attachments.value = await getPublicAttachments(meetingId, seatPerson.value?.userId)
  } catch (error) {
    attachments.value = []
  }
}

async function submitIssueRecord() {
  if (!canRecordIssue.value) {
    ElMessage.warning('请先签到，并以专家身份进入问题记录')
    return
  }
  if (!issueDraft.value.trim()) {
    ElMessage.warning('请输入问题内容')
    return
  }
  savingIssue.value = true
  try {
    await createMeetingIssue(meetingId, {
      content: issueDraft.value.trim(),
      reporter_name: seatPerson.value?.userName || '专家',
    })
    issueDraft.value = ''
    showIssueEditor.value = false
    await loadTerminalIssues()
    ElMessage.success('问题已记录，可点击"提交"上报管理端')
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '问题记录失败')
  } finally {
    savingIssue.value = false
  }
}

async function submitQaQuestion() {
  if (!canAccessMeetingContent.value) {
    ElMessage.warning('请先完成签到，再使用智能问答')
    return
  }
  if (!qaQuestion.value.trim()) return
  const question = qaQuestion.value.trim()
  qaMessages.value.push({ role: 'user', content: question })
  qaQuestion.value = ''
  qaLoading.value = true
  try {
    const res = await publicMeetingQA(meetingId, question)
    const answer = res?.data?.answer || res?.answer || '暂未获取到回答'
    qaMessages.value.push({ role: 'assistant', content: answer })
  } catch (error) {
    qaMessages.value.push({ role: 'assistant', content: error?.response?.data?.detail || '智能问答暂时不可用' })
  } finally {
    qaLoading.value = false
  }
}

// 座位号映射 uid -> seatLabel（大屏显示用）
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

// 准备阶段：供参会者选择的座位列表（仅有人员分配的座位）
const seatList = computed(() => {
  if (!meeting.value?.seat_layout) return []
  try {
    const layout = typeof meeting.value.seat_layout === 'string'
      ? JSON.parse(meeting.value.seat_layout)
      : meeting.value.seat_layout
    return (layout.seats || []).filter(s => s.userId)
  } catch { return [] }
})

// 准备阶段选座
async function selectSeat(id) {
  seatId.value = id
  router.replace({ query: { seat: id } })
  seatLoading.value = true
  try {
    seatPerson.value = await getSeatPerson(meetingId, id)
    await loadTerminalAttachments()
    await loadMinutesContent()
  } catch {
    seatPerson.value = null
  } finally {
    seatLoading.value = false
  }
}

// 实时摘要
const realtimeSummary = ref('')
const summaryKeypoints = ref([])
const summaryGeneratedAt = ref('')
const loadingSummary = ref(false)
let summaryPollTimer = null
let issuesPollTimer = null

function loadSummaryFromStorage() {
  try {
    const stored = localStorage.getItem(`meeting_ref_${meetingId}`)
    if (stored) {
      const data = JSON.parse(stored)
      if (data.summary) {
        realtimeSummary.value = data.summary
        summaryKeypoints.value = data.keypoints || []
        summaryGeneratedAt.value = data.generatedAt
          ? new Date(data.generatedAt).toLocaleString('zh-CN', { hour12: false })
          : ''
        return true
      }
    }
  } catch {}
  return false
}

async function refreshSummary() {
  loadingSummary.value = true
  try {
    // 先尝试从后端获取
    const mtg = await getMeetingPublic(meetingId)
    meeting.value = mtg
    if (mtg.summary) {
      realtimeSummary.value = mtg.summary
    }
    // 再从 localStorage 获取（MeetingLive 生成的实时摘要）
    loadSummaryFromStorage()
  } catch {}
  finally { loadingSummary.value = false }
}

function startSummaryPoll() {
  if (summaryPollTimer) clearInterval(summaryPollTimer)
  summaryPollTimer = setInterval(() => {
    // 轮询 localStorage 以获取 MeetingLive 页面生成的实时摘要
    loadSummaryFromStorage()
  }, 5000)
}

// 本人签到状态（有座位时）
const selfChecked = computed(() => {
  if (!seatPerson.value?.userId) return false
  return participants.value.find(p => p.id === seatPerson.value.userId)?.checked_in || false
})

const canAccessMeetingContent = computed(() => {
  if (!seatPerson.value?.userId) return false
  return selfChecked.value
})

const canRecordIssue = computed(() => !!seatPerson.value?.isExpert && canAccessMeetingContent.value)
const currentRequiredSigner = computed(() => {
  const signerName = seatPerson.value?.userName
  if (!signerName) return null
  return requiredSigners.value.find(item => item.signer_name === signerName) || null
})
const canReviewMinutes = computed(() => canAccessMeetingContent.value && !!currentRequiredSigner.value)

function getParticipantByUserId(userId) {
  if (!userId) return null
  return participants.value.find(p => p.id === userId) || null
}

function signTypeLabel(type) {
  const map = {
    leader_review: '组长审签',
    review_sign: '审签',
    draft_sign: '拟稿签署',
  }
  return map[type] || '审签'
}

// 签到手写板
const checkinCanvasRef = ref(null)
const checkinPenWidth = ref(2)
let checkinCtx = null
let checkinDrawing = false
let checkinPaths = []
let checkinCurrentPath = []

function initCheckinCanvas() {
  const canvas = checkinCanvasRef.value
  if (!canvas) return
  checkinCtx = canvas.getContext('2d')
  checkinCtx.strokeStyle = '#ffffff'
  checkinCtx.lineWidth = checkinPenWidth.value
  checkinCtx.lineCap = 'round'
  checkinCtx.lineJoin = 'round'
}

function getCheckinCanvasCoords(e) {
  const canvas = checkinCanvasRef.value
  if (!canvas) return { x: e.offsetX, y: e.offsetY }
  const rect = canvas.getBoundingClientRect()
  return {
    x: (e.clientX - rect.left) * (canvas.width / rect.width),
    y: (e.clientY - rect.top) * (canvas.height / rect.height),
  }
}

function startCheckinSign(e) {
  if (!checkinCtx) initCheckinCanvas()
  checkinDrawing = true
  checkinHasDrawn.value = true
  const { x, y } = getCheckinCanvasCoords(e)
  checkinCurrentPath = [{ x, y }]
  checkinCtx.beginPath()
  checkinCtx.strokeStyle = '#ffffff'
  checkinCtx.lineWidth = checkinPenWidth.value
  checkinCtx.moveTo(x, y)
}

function moveCheckinSign(e) {
  if (!checkinDrawing) return
  const { x, y } = getCheckinCanvasCoords(e)
  checkinCurrentPath.push({ x, y })
  checkinCtx.lineTo(x, y)
  checkinCtx.stroke()
}

function endCheckinSign() {
  if (!checkinDrawing) return
  checkinDrawing = false
  checkinPaths.push([...checkinCurrentPath])
  checkinCurrentPath = []
}

function clearCheckinSign() {
  checkinPaths = []
  checkinHasDrawn.value = false
  if (!checkinCtx || !checkinCanvasRef.value) return
  checkinCtx.clearRect(0, 0, checkinCanvasRef.value.width, checkinCanvasRef.value.height)
}

function undoCheckinSign() {
  if (!checkinPaths.length || !checkinCtx) return
  checkinPaths.pop()
  if (checkinPaths.length === 0) checkinHasDrawn.value = false
  if (!checkinCanvasRef.value) return
  checkinCtx.clearRect(0, 0, checkinCanvasRef.value.width, checkinCanvasRef.value.height)
  checkinPaths.forEach(path => {
    if (path.length < 2) return
    checkinCtx.beginPath()
    checkinCtx.strokeStyle = '#ffffff'
    checkinCtx.lineWidth = checkinPenWidth.value
    checkinCtx.moveTo(path[0].x, path[0].y)
    path.slice(1).forEach(p => checkinCtx.lineTo(p.x, p.y))
    checkinCtx.stroke()
  })
}

function openCheckinSign(p) {
  if (p.checked_in) return
  checkinTarget.value = p
  // 直接打开展开版签名板
  checkinExpandPaths = []
  checkinExpandVisible.value = true
  nextTick(() => {
    const expandCanvas = checkinExpandCanvasRef.value
    if (!expandCanvas) return
    checkinExpandCtx = expandCanvas.getContext('2d')
    checkinExpandCtx.strokeStyle = '#ffffff'
    checkinExpandCtx.lineWidth = checkinPenWidth.value
    checkinExpandCtx.lineCap = 'round'
    checkinExpandCtx.lineJoin = 'round'
    checkinExpandCtx.clearRect(0, 0, expandCanvas.width, expandCanvas.height)
  })
}

async function handleSelfCheckinWithSign() {
  if (selfChecked.value) return
  if (!seatPerson.value?.userId) return
  if (checkinPaths.length === 0) {
    ElMessage.warning('请先完成手写签名')
    return
  }
  const target = participants.value.find(p => p.id === seatPerson.value.userId)
  if (!target) return
  checkingIn.value = true
  try {
    await terminalCheckin(meetingId, target.id)
    const idx = participants.value.findIndex(p => p.id === target.id)
    if (idx >= 0) participants.value[idx].checked_in = true
    await loadTerminalAttachments()
    ElMessage.success(`${target.real_name} 签到成功！`)
    clearCheckinSign()
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '签到失败')
  } finally {
    checkingIn.value = false
  }
}

async function handleSelfCheckin() {
  if (selfChecked.value) return
  if (!seatPerson.value?.userId) return
  const target = participants.value.find(p => p.id === seatPerson.value.userId)
  if (!target) return
  checkingIn.value = true
  try {
    await terminalCheckin(meetingId, target.id)
    const idx = participants.value.findIndex(p => p.id === target.id)
    if (idx >= 0) participants.value[idx].checked_in = true
    await loadTerminalAttachments()
    ElMessage.success(`${target.real_name} 签到成功！`)
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '签到失败')
  } finally {
    checkingIn.value = false
  }
}

// 电子审签
const signCanvasRef = ref(null)
const signPenWidth = ref(2)
const signPenColor = ref('#ffffff')
const submittingSign = ref(false)
const signRecords = ref([])
const minutesContent = ref('')
const reviewConclusion = ref('')
const loadingMinutes = ref(false)
const selfAlreadySigned = ref(false)
const minutesPublished = ref(false)
const minutesStatus = ref('none')
const rejectingMinutes = ref(false)
const showRejectDialog = ref(false)
const rejectReason = ref('')
const signOpinion = ref('')
let minutesPollTimer = null
let signCtx = null
let signDrawing = false
let signPaths = []
let signCurrentPath = []

// 专家组长大屏签字板
const leaderSignOverlay = ref(false)
const leaderCanvasRef = ref(null)
const leaderSignOpinion = ref('')
let leaderSignCtx = null
let leaderSignDrawing = false
let leaderSignPaths = []

function initLeaderCanvas() {
  const canvas = leaderCanvasRef.value
  if (!canvas) return
  leaderSignCtx = canvas.getContext('2d')
  leaderSignCtx.strokeStyle = '#00d4ff'
  leaderSignCtx.lineWidth = 3
  leaderSignCtx.lineCap = 'round'
  leaderSignCtx.lineJoin = 'round'
}

function startLeaderSign(e) {
  if (!leaderSignCtx) initLeaderCanvas()
  if (!leaderSignCtx) return
  leaderSignDrawing = true
  leaderCanvasRef.value.setPointerCapture(e.pointerId)
  const r = leaderCanvasRef.value.getBoundingClientRect()
  const { width, height } = leaderCanvasRef.value
  const sx = (e.clientX - r.left) * (width / r.width)
  const sy = (e.clientY - r.top) * (height / r.height)
  leaderSignCtx.beginPath()
  leaderSignCtx.moveTo(sx, sy)
  leaderSignPaths.push([{ x: sx, y: sy }])
}

function moveLeaderSign(e) {
  if (!leaderSignDrawing || !leaderSignCtx) return
  const r = leaderCanvasRef.value.getBoundingClientRect()
  const { width, height } = leaderCanvasRef.value
  const sx = (e.clientX - r.left) * (width / r.width)
  const sy = (e.clientY - r.top) * (height / r.height)
  leaderSignCtx.lineTo(sx, sy)
  leaderSignCtx.stroke()
  if (leaderSignPaths.length) leaderSignPaths[leaderSignPaths.length - 1].push({ x: sx, y: sy })
}

function endLeaderSign() { leaderSignDrawing = false }

function clearLeaderSign() {
  if (!leaderSignCtx || !leaderCanvasRef.value) return
  leaderSignCtx.clearRect(0, 0, leaderCanvasRef.value.width, leaderCanvasRef.value.height)
  leaderSignPaths = []
}

async function submitLeaderSign() {
  if (!leaderSignPaths.length) { ElMessage.warning('请先在上方手写签名'); return }
  const signerName = seatPerson.value?.userName
  if (!signerName) { ElMessage.warning('无法获取签署人信息'); return }
  const imageData = leaderCanvasRef.value?.toDataURL('image/png') || ''
  submittingSign.value = true
  try {
    await publicSignMinutes(meetingId, {
      signature_image: imageData,
      signer_name: signerName,
      signer_unit: signerUnitInput.value || currentRequiredSigner.value?.signer_unit || seatPerson.value?.department || '',
      opinion: leaderSignOpinion.value || '',
    })
    ElMessage.success('审签成功！')
    selfAlreadySigned.value = true
    leaderSignOverlay.value = false
    await loadMinutesContent()
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '签署失败')
  } finally {
    submittingSign.value = false
  }
}

// 加载纪要内容和签署记录
async function loadMinutesContent() {
  loadingMinutes.value = true
  try {
    const res = await getMinutesInfo(meetingId)
    const data = res?.data || res
    minutesContent.value = data?.content || ''
    reviewConclusion.value = data?.review_conclusion || ''
    const status = data?.status || 'none'
    minutesStatus.value = status
    minutesPublished.value = (status === 'published' || status === 'reviewing' || status === 'signed')
    const sigs = data?.signatures || []
    signRecords.value = sigs
    requiredSigners.value = data?.required_signers || []
    // 检查本人是否已签
    const myName = seatPerson.value?.userName
    if (myName) {
      selfAlreadySigned.value = sigs.some(s => s.signer_name === myName && s.sign_step === 'review')
    }
    const matchedSigner = myName
      ? requiredSigners.value.find(item => item.signer_name === myName)
      : null
    signerUnitInput.value = matchedSigner?.signer_unit || seatPerson.value?.department || signerUnitInput.value || ''
  } catch (e) {
    console.error('加载纪要失败:', e)
  } finally {
    loadingMinutes.value = false
  }
}

function initSignCanvas() {
  const canvas = signCanvasRef.value
  if (!canvas) return
  signCtx = canvas.getContext('2d')
  signCtx.strokeStyle = signPenColor.value
  signCtx.lineWidth = signPenWidth.value
  signCtx.lineCap = 'round'
  signCtx.lineJoin = 'round'
}

function getCanvasCoords(e) {
  const canvas = signCanvasRef.value
  if (!canvas) return { x: e.offsetX, y: e.offsetY }
  const rect = canvas.getBoundingClientRect()
  return {
    x: (e.clientX - rect.left) * (canvas.width / rect.width),
    y: (e.clientY - rect.top) * (canvas.height / rect.height),
  }
}

function startSign(e) {
  if (!signCtx) initSignCanvas()
  signDrawing = true
  const { x, y } = getCanvasCoords(e)
  signCurrentPath = [{ x, y }]
  signCtx.beginPath()
  signCtx.strokeStyle = signPenColor.value
  signCtx.lineWidth = signPenWidth.value
  signCtx.moveTo(x, y)
}

function moveSign(e) {
  if (!signDrawing) return
  const { x, y } = getCanvasCoords(e)
  signCurrentPath.push({ x, y })
  signCtx.lineTo(x, y)
  signCtx.stroke()
}

function endSign() {
  if (!signDrawing) return
  signDrawing = false
  signPaths.push([...signCurrentPath])
  signCurrentPath = []
}

function clearSign() {
  if (!signCtx) return
  signCtx.clearRect(0, 0, signCanvasRef.value.width, signCanvasRef.value.height)
  signPaths = []
}

function undoSign() {
  if (!signPaths.length || !signCtx) return
  signPaths.pop()
  signCtx.clearRect(0, 0, signCanvasRef.value.width, signCanvasRef.value.height)
  signPaths.forEach(path => {
    if (path.length < 2) return
    signCtx.beginPath()
    signCtx.moveTo(path[0].x, path[0].y)
    path.slice(1).forEach(p => signCtx.lineTo(p.x, p.y))
    signCtx.stroke()
  })
}

async function submitSign() {
  if (!signPaths.length) { ElMessage.warning('请先完成手写签名'); return }
  const signerName = seatPerson.value?.userName
  if (!signerName) { ElMessage.warning('请先绑定座位以获取签署人信息'); return }
  const imageData = signCanvasRef.value?.toDataURL('image/png') || ''
  submittingSign.value = true
  try {
    await publicSignMinutes(meetingId, {
      signature_image: imageData,
      signer_name: signerName,
      signer_unit: signerUnitInput.value || currentRequiredSigner.value?.signer_unit || seatPerson.value?.department || '',
      opinion: signOpinion.value || '',
    })
    ElMessage.success('会签成功！')
    clearSign()
    signOpinion.value = ''
    selfAlreadySigned.value = true
    await loadMinutesContent()
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '签署失败')
  } finally {
    submittingSign.value = false
  }
}

// 签到签名板展开功能
const checkinExpandVisible = ref(false)
const checkinExpandCanvasRef = ref(null)
let checkinExpandCtx = null
let checkinExpandDrawing = false
let checkinExpandPaths = []
let checkinExpandCurrentPath = []

function openCheckinExpand() {
  checkinExpandPaths = []
  checkinExpandVisible.value = true
  nextTick(() => {
    const expandCanvas = checkinExpandCanvasRef.value
    if (!expandCanvas) return
    checkinExpandCtx = expandCanvas.getContext('2d')
    checkinExpandCtx.strokeStyle = '#ffffff'
    checkinExpandCtx.lineWidth = checkinPenWidth.value
    checkinExpandCtx.lineCap = 'round'
    checkinExpandCtx.lineJoin = 'round'
    const smallCanvas = checkinCanvasRef.value
    if (smallCanvas) {
      checkinExpandCtx.drawImage(smallCanvas, 0, 0, expandCanvas.width, expandCanvas.height)
    }
  })
}

function getCheckinExpandCoords(e) {
  const canvas = checkinExpandCanvasRef.value
  if (!canvas) return { x: e.offsetX, y: e.offsetY }
  const rect = canvas.getBoundingClientRect()
  return {
    x: (e.clientX - rect.left) * (canvas.width / rect.width),
    y: (e.clientY - rect.top) * (canvas.height / rect.height),
  }
}

function startCheckinExpandSign(e) {
  if (!checkinExpandCtx) return
  checkinExpandDrawing = true
  const { x, y } = getCheckinExpandCoords(e)
  checkinExpandCurrentPath = [{ x, y }]
  checkinExpandCtx.beginPath()
  checkinExpandCtx.strokeStyle = '#ffffff'
  checkinExpandCtx.lineWidth = checkinPenWidth.value
  checkinExpandCtx.moveTo(x, y)
}

function moveCheckinExpandSign(e) {
  if (!checkinExpandDrawing) return
  const { x, y } = getCheckinExpandCoords(e)
  checkinExpandCurrentPath.push({ x, y })
  checkinExpandCtx.lineTo(x, y)
  checkinExpandCtx.stroke()
}

function endCheckinExpandSign() {
  if (!checkinExpandDrawing) return
  checkinExpandDrawing = false
  checkinExpandPaths.push([...checkinExpandCurrentPath])
  checkinExpandCurrentPath = []
}

function clearCheckinExpand() {
  if (!checkinExpandCtx) return
  checkinExpandCtx.clearRect(0, 0, checkinExpandCanvasRef.value.width, checkinExpandCanvasRef.value.height)
  checkinExpandPaths = []
}

function undoCheckinExpand() {
  if (!checkinExpandPaths.length || !checkinExpandCtx) return
  checkinExpandPaths.pop()
  const canvas = checkinExpandCanvasRef.value
  checkinExpandCtx.clearRect(0, 0, canvas.width, canvas.height)
  checkinExpandPaths.forEach(path => {
    if (path.length < 2) return
    checkinExpandCtx.beginPath()
    checkinExpandCtx.strokeStyle = '#ffffff'
    checkinExpandCtx.lineWidth = checkinPenWidth.value
    checkinExpandCtx.moveTo(path[0].x, path[0].y)
    path.slice(1).forEach(p => checkinExpandCtx.lineTo(p.x, p.y))
    checkinExpandCtx.stroke()
  })
}

function confirmCheckinExpand() {
  const expandCanvas = checkinExpandCanvasRef.value
  const smallCanvas = checkinCanvasRef.value
  if (expandCanvas && smallCanvas) {
    const ctx = smallCanvas.getContext('2d')
    ctx.clearRect(0, 0, smallCanvas.width, smallCanvas.height)
    ctx.drawImage(expandCanvas, 0, 0, smallCanvas.width, smallCanvas.height)
    checkinPaths = [[{ x: 0, y: 0 }]]
    checkinCtx = ctx
  }
  checkinExpandVisible.value = false
}

async function confirmCheckinFromExpand() {
  if (!checkinTarget.value) return
  if (checkinExpandPaths.length === 0) {
    ElMessage.warning('请先完成手写签名')
    return
  }
  const expandCanvas = checkinExpandCanvasRef.value
  const signatureImage = expandCanvas ? expandCanvas.toDataURL('image/png') : ''
  checkingIn.value = true
  try {
    await terminalCheckin(meetingId, checkinTarget.value.id)
    const idx = participants.value.findIndex(p => p.id === checkinTarget.value.id)
    if (idx >= 0) {
      participants.value[idx].checked_in = true
      if (signatureImage) participants.value[idx].signature_image = signatureImage
    }
    ElMessage.success(`${checkinTarget.value.real_name} 签到成功！`)
    checkinExpandVisible.value = false
    checkinTarget.value = null
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '签到失败')
  } finally {
    checkingIn.value = false
  }
}

// 评审费签名
const feeSignVisible = ref(false)
const feeTarget = ref(null)
const submittingFeeSign = ref(false)
const feeSignCanvasRef = ref(null)
const feeSignPenWidth = ref(2)
const feeSignIdCard = ref('')
const feeSignBankCard = ref('')
const feeHasStrokes = ref(false)
let feeSignCtx = null
let feeSignDrawing = false
let feeSignPaths = []
let feeSignCurrentPath = []

function openFeeSign(p) {
  feeTarget.value = p
  feeSignIdCard.value = p.fee_id_card || ''
  feeSignBankCard.value = p.fee_bank_card || ''
  feeSignPaths = []
  feeHasStrokes.value = false
  feeSignVisible.value = true
  nextTick(() => {
    const canvas = feeSignCanvasRef.value
    if (!canvas) return
    feeSignCtx = canvas.getContext('2d')
    feeSignCtx.strokeStyle = '#ffffff'
    feeSignCtx.lineWidth = feeSignPenWidth.value
    feeSignCtx.lineCap = 'round'
    feeSignCtx.lineJoin = 'round'
    feeSignCtx.clearRect(0, 0, canvas.width, canvas.height)
  })
}

function getFeeSignCoords(e) {
  const canvas = feeSignCanvasRef.value
  if (!canvas) return { x: e.offsetX, y: e.offsetY }
  const rect = canvas.getBoundingClientRect()
  return {
    x: (e.clientX - rect.left) * (canvas.width / rect.width),
    y: (e.clientY - rect.top) * (canvas.height / rect.height),
  }
}

function startFeeSign(e) {
  if (!feeSignCtx) return
  feeSignDrawing = true
  const { x, y } = getFeeSignCoords(e)
  feeSignCurrentPath = [{ x, y }]
  feeSignCtx.beginPath()
  feeSignCtx.strokeStyle = '#ffffff'
  feeSignCtx.lineWidth = feeSignPenWidth.value
  feeSignCtx.moveTo(x, y)
}

function moveFeeSign(e) {
  if (!feeSignDrawing) return
  const { x, y } = getFeeSignCoords(e)
  feeSignCurrentPath.push({ x, y })
  feeSignCtx.lineTo(x, y)
  feeSignCtx.stroke()
}

function endFeeSign() {
  if (!feeSignDrawing) return
  feeSignDrawing = false
  if (feeSignCurrentPath.length > 1) {
    feeHasStrokes.value = true
  }
  feeSignPaths.push([...feeSignCurrentPath])
  feeSignCurrentPath = []
}

function clearFeeSign() {
  if (!feeSignCtx) return
  feeSignCtx.clearRect(0, 0, feeSignCanvasRef.value.width, feeSignCanvasRef.value.height)
  feeSignPaths = []
  feeHasStrokes.value = false
}

function undoFeeSign() {
  if (!feeSignPaths.length || !feeSignCtx) return
  feeSignPaths.pop()
  const canvas = feeSignCanvasRef.value
  feeSignCtx.clearRect(0, 0, canvas.width, canvas.height)
  feeSignPaths.forEach(path => {
    if (path.length < 2) return
    feeSignCtx.beginPath()
    feeSignCtx.strokeStyle = '#ffffff'
    feeSignCtx.lineWidth = feeSignPenWidth.value
    feeSignCtx.moveTo(path[0].x, path[0].y)
    path.slice(1).forEach(p => feeSignCtx.lineTo(p.x, p.y))
    feeSignCtx.stroke()
  })
}

async function confirmFeeSign() {
  if (!feeTarget.value) return
  if (feeSignPaths.length === 0) {
    ElMessage.warning('请先完成手写签名')
    return
  }
  const canvas = feeSignCanvasRef.value
  const signatureImage = canvas ? canvas.toDataURL('image/png') : ''
  submittingFeeSign.value = true
  try {
    await feeSign(meetingId, feeTarget.value.id, signatureImage, feeSignIdCard.value, feeSignBankCard.value)
    const idx = participants.value.findIndex(p => p.id === feeTarget.value.id)
    if (idx >= 0) {
      participants.value[idx].fee_signature_image = signatureImage
      participants.value[idx].fee_id_card = feeSignIdCard.value
      participants.value[idx].fee_bank_card = feeSignBankCard.value
    }
    ElMessage.success(`${feeTarget.value.real_name} 评审费签名成功！`)
    feeSignVisible.value = false
    feeTarget.value = null
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '签名失败')
  } finally {
    submittingFeeSign.value = false
  }
}

// 审签签名板展开功能
const signExpandVisible = ref(false)
const signExpandCanvasRef = ref(null)
let signExpandCtx = null
let signExpandDrawing = false
let signExpandPaths = []
let signExpandCurrentPath = []

function openSignExpand() {
  signExpandPaths = []
  signExpandVisible.value = true
  nextTick(() => {
    const expandCanvas = signExpandCanvasRef.value
    if (!expandCanvas) return
    signExpandCtx = expandCanvas.getContext('2d')
    signExpandCtx.strokeStyle = signPenColor.value
    signExpandCtx.lineWidth = signPenWidth.value
    signExpandCtx.lineCap = 'round'
    signExpandCtx.lineJoin = 'round'
    const smallCanvas = signCanvasRef.value
    if (smallCanvas) {
      signExpandCtx.drawImage(smallCanvas, 0, 0, expandCanvas.width, expandCanvas.height)
    }
  })
}

function getSignExpandCoords(e) {
  const canvas = signExpandCanvasRef.value
  if (!canvas) return { x: e.offsetX, y: e.offsetY }
  const rect = canvas.getBoundingClientRect()
  return {
    x: (e.clientX - rect.left) * (canvas.width / rect.width),
    y: (e.clientY - rect.top) * (canvas.height / rect.height),
  }
}

function startSignExpandSign(e) {
  if (!signExpandCtx) return
  signExpandDrawing = true
  const { x, y } = getSignExpandCoords(e)
  signExpandCurrentPath = [{ x, y }]
  signExpandCtx.beginPath()
  signExpandCtx.strokeStyle = signPenColor.value
  signExpandCtx.lineWidth = signPenWidth.value
  signExpandCtx.moveTo(x, y)
}

function moveSignExpandSign(e) {
  if (!signExpandDrawing) return
  const { x, y } = getSignExpandCoords(e)
  signExpandCurrentPath.push({ x, y })
  signExpandCtx.lineTo(x, y)
  signExpandCtx.stroke()
}

function endSignExpandSign() {
  if (!signExpandDrawing) return
  signExpandDrawing = false
  signExpandPaths.push([...signExpandCurrentPath])
  signExpandCurrentPath = []
}

function clearSignExpand() {
  if (!signExpandCtx) return
  signExpandCtx.clearRect(0, 0, signExpandCanvasRef.value.width, signExpandCanvasRef.value.height)
  signExpandPaths = []
}

function undoSignExpand() {
  if (!signExpandPaths.length || !signExpandCtx) return
  signExpandPaths.pop()
  const canvas = signExpandCanvasRef.value
  signExpandCtx.clearRect(0, 0, canvas.width, canvas.height)
  signExpandPaths.forEach(path => {
    if (path.length < 2) return
    signExpandCtx.beginPath()
    signExpandCtx.strokeStyle = signPenColor.value
    signExpandCtx.lineWidth = signPenWidth.value
    signExpandCtx.moveTo(path[0].x, path[0].y)
    path.slice(1).forEach(p => signExpandCtx.lineTo(p.x, p.y))
    signExpandCtx.stroke()
  })
}

function confirmSignExpand() {
  const expandCanvas = signExpandCanvasRef.value
  const smallCanvas = signCanvasRef.value
  if (expandCanvas && smallCanvas) {
    const ctx = smallCanvas.getContext('2d')
    ctx.clearRect(0, 0, smallCanvas.width, smallCanvas.height)
    ctx.drawImage(expandCanvas, 0, 0, smallCanvas.width, smallCanvas.height)
    signPaths = [[{ x: 0, y: 0 }]]
    signCtx = ctx
  }
  signExpandVisible.value = false
}

async function confirmReject() {
  rejectingMinutes.value = true
  try {
    await rejectMinutes(meetingId, { reason: rejectReason.value || '' })
    minutesPublished.value = false
    showRejectDialog.value = false
    rejectReason.value = ''
    ElMessage.success('已驳回，管理员可修改后重新发布')
    startMinutesPoll()
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '驳回失败')
  } finally {
    rejectingMinutes.value = false
  }
}

// 切换到审签标签时初始化画布
watch(activeTab, (tab) => {
  if (
    tab !== 'checkin'
    && ['materials', 'people', 'issues', 'qa', 'summary', 'esign'].includes(tab)
    && !canAccessMeetingContent.value
  ) {
    ElMessage.warning('请先完成签到，再查看会议内容')
    activeTab.value = 'checkin'
    return
  }
  if (tab === 'esign' && minutesPublished.value && canReviewMinutes.value && !selfAlreadySigned.value) {
    nextTick(() => setTimeout(() => initSignCanvas(), 50))
  }
  if (tab === 'checkin' && seatId.value && !selfChecked.value) {
    nextTick(() => setTimeout(() => initCheckinCanvas(), 50))
  }
})

function startMinutesPoll() {
  if (minutesPollTimer) clearInterval(minutesPollTimer)
  if (minutesPublished.value) return // 已发布则无需轮询
  minutesPollTimer = setInterval(async () => {
    try {
      const res = await getMinutesInfo(meetingId)
      const data = res?.data || res
      const status = data?.status || ''
      if (status === 'published' || status === 'signed' || status === 'reviewing') {
        minutesPublished.value = true
        minutesContent.value = data?.content || ''
        const sigs = data?.signatures || []
        signRecords.value = sigs
        const myName = seatPerson.value?.userName
        if (myName) {
          selfAlreadySigned.value = sigs.some(s => s.signer_name === myName && s.sign_step === 'review')
        }
        clearInterval(minutesPollTimer)
        minutesPollTimer = null
        // 初始化签名画布 - 使用 nextTick 确保 DOM 已渲染
        nextTick(() => setTimeout(() => initSignCanvas(), 100))
        // 专家组长：弹出大屏签字板
        if (seatPerson.value?.isLeader && !selfAlreadySigned.value) {
          leaderSignOverlay.value = true
          nextTick(() => setTimeout(() => initLeaderCanvas(), 100))
        }
      }
    } catch {}
  }, 8000)
}

function statusLabel(s) {
  const map = { pending: '待开始', preparing: '准备中', in_progress: '进行中', finished: '已结束', archived: '会议结束', signing: '审签中' }
  return map[s] || s || '—'
}

function statusType(s) {
  const map = { pending: 'info', preparing: 'warning', in_progress: 'success', finished: 'warning', archived: 'success', signing: 'warning' }
  return map[s] || 'info'
}

function formatTime(t) {
  if (!t) return '--'
  return dayjs(t).format('MM月DD日 HH:mm')
}

function formatSize(bytes) {
  if (!bytes) return ''
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function getFileTypeCategory(att) {
  const ext = (att.filename || '').split('.').pop().toLowerCase()
  const type = (att.file_type || '').toLowerCase()
  if (type.includes('pdf') || ext === 'pdf') return 'pdf'
  if (['doc', 'docx'].includes(ext) || type.includes('word')) return 'word'
  if (['ppt', 'pptx'].includes(ext) || type.includes('presentation')) return 'ppt'
  if (['xls', 'xlsx'].includes(ext) || type.includes('spreadsheet')) return 'excel'
  return 'other'
}

function getFileTypeInfo(att) {
  const cat = getFileTypeCategory(att)
  if (cat === 'pdf') return { label: 'PDF', color: '#e54d42', bg: 'rgba(229,77,66,0.12)' }
  if (cat === 'word') return { label: 'DOC', color: '#2b82d9', bg: 'rgba(43,130,217,0.12)' }
  if (cat === 'ppt') return { label: 'PPT', color: '#e6703c', bg: 'rgba(230,112,60,0.12)' }
  if (cat === 'excel') return { label: 'XLS', color: '#2aab72', bg: 'rgba(42,171,114,0.12)' }
  return { label: 'FILE', color: '#7f99be', bg: 'rgba(127,153,190,0.12)' }
}

function formatUploadTime(t) {
  if (!t) return ''
  try {
    const d = new Date(t)
    const now = new Date()
    const diffDays = Math.floor((now - d) / 86400000)
    if (diffDays === 0) return '今天 ' + d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    if (diffDays === 1) return '昨天'
    return d.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
  } catch { return '' }
}

function handleCheckin(p) {
  if (p.checked_in) return
  openCheckinSign(p)
}

async function confirmCheckin() {
  if (!checkinTarget.value) return
  if (checkinPaths.length === 0) {
    ElMessage.warning('请先完成手写签名')
    return
  }
  checkingIn.value = true
  try {
    await terminalCheckin(meetingId, checkinTarget.value.id)
    const idx = participants.value.findIndex(p => p.id === checkinTarget.value.id)
    if (idx >= 0) participants.value[idx].checked_in = true
    ElMessage.success(`${checkinTarget.value.real_name} 签到成功！`)
    checkinDialogVisible.value = false
    clearCheckinSign()
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '签到失败')
  } finally {
    checkingIn.value = false
  }
}

function downloadFile(att) {
  const url = `/api/meeting/attachment/${att.id}/download`
  const a = document.createElement('a')
  a.href = url
  a.download = att.filename || 'file'
  a.click()
}

async function pollStatus() {
  try {
    const mtg = await getMeetingPublic(meetingId)
    const prevStatus = meeting.value.status
    meeting.value = mtg
    if ((prevStatus === 'pending' || prevStatus === 'preparing') && mtg.status === 'in_progress') {
      // 会议已开始，刷新参会列表
      const pList = await getPublicParticipants(meetingId)
      participants.value = pList
    } else if (prevStatus === 'pending' && mtg.status === 'preparing') {
      // 进入准备状态，无需刷新内容
    }
  } catch {}
}

let participantsPollTimer = null
async function pollParticipants() {
  try {
    const pList = await getPublicParticipants(meetingId)
    participants.value = pList
  } catch {}
}

onMounted(async () => {
  // 如果 id 是 'auto'，自动获取当前会议
  if (meetingId === 'auto') {
    try {
      const mtg = await getCurrentMeeting()
      meetingId = String(mtg.id)
      if (!seatId.value) seatId.value = 1
      // 更新地址栏但不重新挂载组件
      router.replace(`/terminal/${meetingId}?seat=${seatId.value}`)
    } catch {
      notFound.value = true
      loading.value = false
      return
    }
  }
  try {
    const [mtg, pList] = await Promise.all([
      getMeetingPublic(meetingId),
      getPublicParticipants(meetingId),
    ])
    meeting.value = mtg
    participants.value = pList
    await loadTerminalAttachments()

    // 加载座位信息
    if (seatId.value) {
      seatLoading.value = true
      try {
        const sp = await getSeatPerson(meetingId, seatId.value)
        seatPerson.value = sp
        await loadTerminalAttachments()
        await loadMinutesContent()
      } catch {
        seatPerson.value = null
      } finally {
        seatLoading.value = false
      }
    }

    if (mtg.status === 'pending' || mtg.status === 'preparing') {
      pollTimer = setInterval(pollStatus, 10000)
    }

    // 每 8 秒轮询参会人员签到状态（支持管理端回退后终端同步）
    participantsPollTimer = setInterval(pollParticipants, 8000)

    // 加载纪要内容（始终加载，审签依赖纪要发布状态）
    await loadMinutesContent()
    // 加载问题记录
    loadTerminalIssues()
    // 加载实时摘要
    loadSummaryFromStorage()
    if (mtg.summary) realtimeSummary.value = mtg.summary
    startSummaryPoll()
    // 每 10 秒轮询问题列表
    issuesPollTimer = setInterval(loadTerminalIssues, 10000)
    // 如果已发布，立即初始化签名画布
    if (minutesPublished.value) {
      nextTick(() => setTimeout(() => initSignCanvas(), 100))
    }
    // 启动纪要发布状态轮询（等待管理端发布后自动刷新）
    startMinutesPoll()
  } catch (e) {
    if (e?.response?.status === 404) {
      notFound.value = true
    } else {
      ElMessage.error('加载会议信息失败')
    }
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
  if (participantsPollTimer) clearInterval(participantsPollTimer)
  if (minutesPollTimer) clearInterval(minutesPollTimer)
  if (summaryPollTimer) clearInterval(summaryPollTimer)
  if (issuesPollTimer) clearInterval(issuesPollTimer)
})
</script>

<style lang="scss" scoped>
.terminal-page {
  height: 100vh;
  background: #03142d;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.bigscreen {
  flex: 1;
  position: relative;
  overflow: hidden;
  height: 0;
  background: #03142d url('/images/background.jpg') center center / contain no-repeat;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ===== 准备阶段提示横幅 ===== */
.preparing-notice-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(230,162,60,0.12);
  border-bottom: 1px solid rgba(230,162,60,0.3);
  color: #e6a23c;
  font-size: 14px;
  flex-shrink: 0;
}

/* ===== 准备中大屏 ===== */
.preparing-screen {
  flex: 1;
  overflow-y: auto;
  background: #03142d url('/images/background.jpg') center center / contain no-repeat;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.preparing-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  text-align: center;
  max-width: 700px;
  width: 100%;
}

.preparing-hint {
  color: rgba(180, 220, 255, 0.8);
  font-size: 16px;
  margin-bottom: 8px;
}

.seat-select-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  justify-content: center;
  margin: 8px 0;
}

.seat-select-card {
  width: 100px;
  min-height: 80px;
  border: 2px solid rgba(32,64,130,0.7);
  border-radius: 12px;
  background: #14284b;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  backdrop-filter: blur(8px);
  padding: 8px 6px;
  &:hover {
    border-color: #00d4ff;
    background: rgba(0, 212, 255, 0.15);
    transform: scale(1.06);
    box-shadow: 0 0 20px rgba(0, 212, 255, 0.4);
  }
}

.seat-select-num {
  font-size: 22px;
  font-weight: 700;
  color: #a8d8ff;
  font-family: 'Arial', sans-serif;
}

.seat-select-name {
  font-size: 14px;
  color: #e0f0ff;
  margin-top: 2px;
}

.seat-select-sub {
  font-size: 14px;
  color: #6a9abf;
  margin-top: 2px;
  text-align: center;
  line-height: 1.3;
}

.bigscreen-content {
  position: relative;
  z-index: 2;
  padding: 32px 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  max-height: 100%;
  overflow: hidden;
}

/* ===== 顶部全局栏 ===== */
.global-bar {
  height: 64px;
  background: #14284b;
  color: #fff;
  display: flex;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid rgba(57, 144, 241, 0.3);
  position: relative;
  z-index: 10;
  flex-shrink: 0;
}
.global-bar::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, #3990f1 40%, #2bffbc 60%, transparent);
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: rgba(255,255,255,0.7);
  cursor: pointer;
  padding: 6px 10px;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 6px;
  transition: all 0.2s;
  svg { width: 14px; height: 14px; }
  &:hover { color: #fff; border-color: rgba(255,255,255,0.3); background: rgba(255,255,255,0.08); }
}

.divider-v {
  width: 1px;
  height: 20px;
  background: rgba(255,255,255,0.12);
  margin: 0 14px;
  flex-shrink: 0;
}

.terminal-icon {
  color: rgba(255,255,255,0.6);
  flex-shrink: 0;
  margin-right: 6px;
}

.meeting-type-label {
  font-size: 15px;
  font-weight: 600;
  color: rgba(255,255,255,0.9);
  white-space: nowrap;
  letter-spacing: 1px;
}

.global-bar-title-group {
  display: flex;
  flex-direction: column;
  justify-content: center;
  flex: 1;
  min-width: 0;
}

.meeting-name {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.meeting-meta-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 4px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: rgba(255,255,255,0.55);
  svg { width: 13px; height: 13px; flex-shrink: 0; }
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-left: 16px;
  flex-shrink: 0;
  padding: 4px 12px;
  background: rgba(0,200,100,0.12);
  border: 1px solid rgba(0,200,100,0.25);
  border-radius: 100px;
  font-size: 13px;
  color: #00d278;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #00d278;
  animation: status-pulse 1.8s infinite;
}

@keyframes status-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(0,210,120,0.6); }
  50% { box-shadow: 0 0 0 5px rgba(0,210,120,0); }
}

.global-bar-right {
  margin-left: 12px;
  display: flex;
  align-items: center;
}

.icon-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  cursor: pointer;
  color: rgba(255,255,255,0.6);
  transition: all 0.2s;
  svg { width: 16px; height: 16px; }
  &:hover { background: rgba(255,255,255,0.1); color: #fff; }
}

/* ===== 加载/错误 ===== */
.state-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: #909399;
  font-size: 15px;
}

.loading-icon {
  font-size: 48px;
  color: #409eff;
  animation: spin 1s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ===== 大屏（待开始）===== */

.bs-title {
  font-size: 42px;
  font-weight: 800;
  color: #e8f4ff;
  text-align: center;
  letter-spacing: 4px;
  text-shadow: 0 0 30px rgba(0,212,255,0.5), 0 2px 8px rgba(0,0,0,0.6);
  margin-bottom: 14px;
}

.bs-subtitle {
  font-size: 18px;
  color: rgba(200,225,255,0.7);
  text-align: center;
  margin-bottom: 36px;
  letter-spacing: 1px;
}

.bs-divider {
  width: 100%;
  max-width: 900px;
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 36px;

  &::before, &::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, transparent, rgba(0,212,255,0.4));
  }
  &::after {
    background: linear-gradient(to left, transparent, rgba(0,212,255,0.4));
  }

  span {
    font-size: 16px;
    color: rgba(0,212,255,0.8);
    letter-spacing: 4px;
    white-space: nowrap;
    padding: 0 8px;
  }
}

.bs-participant-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  width: 100%;
  max-width: 1100px;
  justify-items: center;
}

/* ===== 2:1 名牌卡片 ===== */
.bs-nameplate {
  position: relative;
  width: 100%;
  aspect-ratio: 2 / 1;
  border-radius: 18px;
  border: 1.5px solid rgba(100, 200, 255, 0.35);
  background: linear-gradient(170deg, rgba(8, 20, 50, 0.85) 0%, rgba(4, 12, 30, 0.92) 100%);
  backdrop-filter: blur(12px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  animation: nameplateIn 0.6s ease both;
  transition: all 0.3s ease;
  box-shadow:
    0 0 1px rgba(100, 200, 255, 0.5),
    0 0 15px rgba(60, 180, 255, 0.08),
    0 8px 32px rgba(0, 0, 0, 0.6);
  overflow: hidden;
}

.bs-nameplate:hover {
  border-color: rgba(100, 210, 255, 0.65);
  transform: translateY(-5px) scale(1.02);
  box-shadow:
    0 0 2px rgba(100, 200, 255, 0.7),
    0 0 25px rgba(60, 180, 255, 0.18),
    0 0 50px rgba(60, 180, 255, 0.06),
    0 12px 40px rgba(0, 0, 0, 0.7);
}

/* 卡片内顶部辉光 */
.nameplate-glow {
  position: absolute;
  top: -40%;
  left: 50%;
  transform: translateX(-50%);
  width: 120%;
  height: 80%;
  background: radial-gradient(ellipse, rgba(80, 200, 255, 0.08) 0%, transparent 60%);
  pointer-events: none;
}

.nameplate-text {
  font-size: 38px;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: 12px;
  text-align: center;
  text-shadow:
    0 0 12px rgba(100, 200, 255, 0.7),
    0 0 30px rgba(80, 180, 255, 0.4),
    0 0 60px rgba(60, 160, 255, 0.15);
  position: relative;
  z-index: 1;
}

.nameplate-seat {
  font-size: 14px;
  font-weight: 600;
  color: #00d4ff;
  letter-spacing: 2px;
  position: relative;
  z-index: 1;
  opacity: 0.85;
  margin-bottom: 4px;
}

.nameplate-dept {
  font-size: 14px;
  color: rgba(150, 200, 240, 0.6);
  letter-spacing: 3px;
  position: relative;
  z-index: 1;
}

@keyframes nameplateIn {
  from { opacity: 0; transform: translateY(30px) scale(0.95); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

.bs-empty {
  color: rgba(180,210,255,0.5);
  font-size: 16px;
  margin: 40px 0;
}

/* ===== 座位大屏显示 ===== */
.seat-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  margin: 20px 0 20px;
  animation: fadeInUp 0.6s ease both;
}

.seat-display-badge {
  display: inline-block;
  background: rgba(0,212,255,0.12);
  border: 2px solid rgba(0,212,255,0.5);
  border-radius: 32px;
  padding: 8px 36px;
  font-size: 20px;
  color: #00d4ff;
  letter-spacing: 6px;
  margin-bottom: 20px;
  text-shadow: 0 0 12px rgba(0,212,255,0.4);
}

.seat-display-name {
  font-size: clamp(60px, 12vw, 140px);
  font-weight: 900;
  color: #ffffff;
  letter-spacing: 16px;
  text-align: center;
  line-height: 1.1;
  text-shadow:
    0 0 14px rgba(100,200,255,0.8),
    0 0 40px rgba(80,180,255,0.45),
    0 0 80px rgba(60,160,255,0.2),
    0 4px 12px rgba(0,0,0,0.8);
  padding: 30px 60px;
  max-width: 80vw;
  aspect-ratio: 2 / 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1.5px solid rgba(100,200,255,0.35);
  border-radius: 20px;
  background: linear-gradient(170deg, rgba(8,20,50,0.85) 0%, rgba(4,12,30,0.92) 100%);
  backdrop-filter: blur(12px);
  position: relative;
  box-shadow:
    0 0 2px rgba(100,200,255,0.5),
    0 0 20px rgba(60,180,255,0.12),
    0 8px 40px rgba(0,0,0,0.6);

  &::before {
    content: '';
    position: absolute;
    top: -30%;
    left: 50%;
    transform: translateX(-50%);
    width: 120%;
    height: 70%;
    background: radial-gradient(ellipse, rgba(80,200,255,0.08) 0%, transparent 60%);
    pointer-events: none;
  }
}

.seat-display-dept {
  font-size: 36px;
  color: rgba(0,212,255,0.8);
  letter-spacing: 8px;
  margin-top: 32px;
  text-shadow: 0 0 16px rgba(0,212,255,0.3);
}

.seat-display-loading {
  font-size: 28px;
  color: rgba(180,210,255,0.6);
  letter-spacing: 2px;
}

.seat-display-empty {
  font-size: 40px;
  color: rgba(180,210,255,0.5);
  letter-spacing: 6px;
  margin-top: 20px;
}

.bs-waiting {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 48px;
}

.waiting-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #00d4ff;
  animation: pulse 1.4s ease-in-out infinite;

  &.delay1 { animation-delay: 0.2s; }
  &.delay2 { animation-delay: 0.4s; }
}

@keyframes pulse {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40%           { transform: scale(1); opacity: 1; }
}

.waiting-text {
  font-size: 16px;
  color: rgba(180,210,255,0.6);
  letter-spacing: 3px;
}

/* ===== 会议进行/结束：标签页 ===== */
.terminal-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 自定义导航栏 */
.nav-bar {
  height: 52px;
  background: #0e1d38;
  display: flex;
  align-items: center;
  padding: 0 16px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  flex-shrink: 0;
  gap: 8px;
}

.seg-control {
  display: flex;
  align-items: center;
  background: rgba(255,255,255,0.05);
  border-radius: 10px;
  padding: 4px;
  gap: 2px;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 5px;
  height: 36px;
  padding: 0 14px;
  border-radius: 8px;
  font-size: 13px;
  color: rgba(255,255,255,0.55);
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  user-select: none;
  svg { width: 14px; height: 14px; flex-shrink: 0; }
  &:hover { background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.85); }
  &.active {
    background: #1677ff;
    color: #fff;
    box-shadow: 0 2px 8px rgba(22,119,255,0.35);
  }
}

.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  background: rgba(22,119,255,0.8);
  border-radius: 8px;
  font-size: 11px;
  color: #fff;
  font-weight: 600;
  .tab-item.active & { background: rgba(255,255,255,0.3); }
}

.nav-bar-right {
  margin-left: auto;
}

.nav-action-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  height: 32px;
  padding: 0 12px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
  svg { width: 13px; height: 13px; }
  &.btn-ghost {
    background: transparent;
    border-color: rgba(255,255,255,0.18);
    color: rgba(255,255,255,0.65);
    &:hover { border-color: rgba(255,255,255,0.35); color: #fff; background: rgba(255,255,255,0.06); }
  }
}

/* 内容区域 */
.content-area {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.tab-section {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 通用按钮样式 */
.icon-ghost-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 30px;
  padding: 0 10px;
  background: transparent;
  border: 1px solid rgba(255,255,255,0.18);
  border-radius: 6px;
  color: rgba(255,255,255,0.65);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  svg { width: 13px; height: 13px; }
  &:hover { border-color: rgba(255,255,255,0.35); color: #fff; }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
}

.primary-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 30px;
  padding: 0 12px;
  background: #1677ff;
  border: none;
  border-radius: 6px;
  color: #fff;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  svg { width: 13px; height: 13px; }
  &:hover { background: #3989ff; }
}

/* 通用空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  gap: 12px;
  color: rgba(255,255,255,0.4);
}

.empty-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255,255,255,0.05);
  border-radius: 50%;
  svg { width: 28px; height: 28px; stroke: rgba(255,255,255,0.3); }
}

.empty-title {
  font-size: 15px;
  font-weight: 600;
  color: rgba(255,255,255,0.55);
}

.empty-desc {
  font-size: 13px;
  color: rgba(255,255,255,0.35);
}

/* 签到 */
.checkin-stats {
  display: flex;
  gap: 40px;
  margin-bottom: 24px;
  padding: 16px 24px;
  background: #14284b;
  border-radius: 8px;
  border: 1px solid #204082;
  box-shadow: 0 1px 4px rgba(0,0,0,0.3);

  :deep(.el-statistic__head) { color: #5e8aad !important; }
  :deep(.el-statistic__content) { color: #ffffff !important; }
}

.participant-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 16px;
}

.participant-card {
  background: #14284b;
  border-radius: 10px;
  padding: 18px 12px;
  text-align: center;
  cursor: pointer;
  border: 1px solid #204082;
  box-shadow: 0 1px 4px rgba(0,0,0,0.3);
  transition: all 0.2s;
  position: relative;

  &:hover { border-color: #409eff; box-shadow: 0 4px 12px rgba(64,158,255,0.2); }
  &.is-checked { border-color: #67c23a; background: rgba(103,194,58,0.08); cursor: default; }
  &.is-checked:hover { border-color: #67c23a; }
}

.participant-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff, #1a7ad4);
  color: #fff;
  font-size: 20px;
  font-weight: 700;
  line-height: 50px;
  margin: 0 auto 10px;
}

.participant-name {
  font-size: 15px;
  font-weight: 600;
  color: rgba(255,255,255,0.85);
  margin-bottom: 4px;
}

.participant-dept {
  font-size: 14px;
  color: rgba(255,255,255,0.45);
  margin-bottom: 6px;
}

.checkin-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 14px;
  color: #67c23a;
  font-weight: 600;
}

.unchecked-badge {
  font-size: 14px;
  color: #409eff;
}

/* 签到手写板 */
.checkin-sign-area,
.checkin-dialog-sign-area {
  margin-top: 16px;
  padding: 16px;
  border: 1px solid rgba(32,64,130,0.5);
  border-radius: 6px;
  background: #1a3966;

  .checkin-sign-title {
    margin: 0 0 8px;
    color: #ffffff;
    font-size: 15px;
  }
}

.checkin-canvas-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.checkin-sign-canvas {
  border: 2px dashed rgba(0,212,255,0.25);
  border-radius: 4px;
  cursor: crosshair;
  display: block;
  touch-action: none;
  background: #0b1a2e;
  width: 100%;
  max-width: 500px;
  &:hover { border-color: #00d4ff; }
}

.expand-canvas-wrap {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.expand-canvas-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}
.expand-sign-canvas {
  border: 2px dashed rgba(0,212,255,0.25);
  border-radius: 4px;
  cursor: crosshair;
  display: block;
  touch-action: none;
  background: #0b1a2e;
  width: 100%;
  &:hover { border-color: #00d4ff; }
}

.fee-text-input {
  width: 100%;
  background: rgba(0,16,40,0.6);
  border: 1px solid rgba(0,212,255,0.25);
  border-radius: 4px;
  color: #e0efff;
  font-size: 14px;
  padding: 8px 10px;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s;
  &:focus { border-color: #00d4ff; background: rgba(0,16,40,0.8); }
  &::placeholder { color: rgba(106,143,175,0.5); }
}

/* 材料 */
.attachment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff;
  border-radius: 8px;
  padding: 14px 18px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.att-icon { font-size: 24px; color: #409eff; }
.att-info { flex: 1; }
.att-name { font-size: 15px; color: #303133; }
.att-size { font-size: 14px; color: #909399; margin-top: 2px; }

/* 本人签到 */
.self-checkin-header {
  text-align: center;
  margin-bottom: 20px;
}
.self-checkin-hint {
  font-size: 16px;
  color: #e0ecff;
  letter-spacing: 1px;
}
.self-checkin-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}
.self-card {
  width: 200px;
  cursor: pointer;
  &:hover { border-color: #409eff; }
}
.self-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff, #1a7ad4);
  color: #fff;
  font-size: 28px;
  font-weight: 700;
  line-height: 64px;
  margin: 0 auto 12px;
}

/* 电子审签 */
.esign-section {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  flex: 1;
}
.esign-notice {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(250,173,20,0.1);
  border: 1px solid rgba(250,173,20,0.3);
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 14px;
  color: #faad14;
  margin-bottom: 20px;
  max-width: 640px;
  margin-left: auto;
  margin-right: auto;
}
.esign-layout {
  display: flex;
  gap: 0;
  align-items: flex-start;
  height: calc(100vh - 200px);
  overflow: hidden;
}
.esign-left {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  height: 100%;
  border-right: 1px solid rgba(255,255,255,0.06);
}
.esign-right {
  width: 290px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  height: 100%;
  scrollbar-width: thin;
  scrollbar-color: rgba(255,255,255,0.06) transparent;
  &::-webkit-scrollbar { width: 4px; }
  &::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.06); border-radius: 2px; }
}

/* === 文档工具栏 === */
.doc-toolbar {
  height: 48px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: rgba(255,255,255,0.015);
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.doc-toolbar-left { display: flex; align-items: center; gap: 10px; }
.doc-title-text {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255,255,255,0.7);
  display: flex;
  align-items: center;
  gap: 8px;
  svg { width: 15px; height: 15px; color: #4096ff; }
}
.doc-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 500;
  padding: 3px 9px;
  border-radius: 10px;
}
.doc-pill.published { background: rgba(0,210,120,0.1); color: #00d278; border: 1px solid rgba(0,210,120,0.2); }
.doc-pill.pending   { background: rgba(255,165,0,0.1);  color: #ffa500; border: 1px solid rgba(255,165,0,0.2); }
.doc-toolbar-right { display: flex; align-items: center; gap: 8px; }
.toolbar-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  height: 30px;
  padding: 0 12px;
  border-radius: 7px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  font-family: inherit;
  svg { width: 12px; height: 12px; }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
}
.toolbar-btn.ghost {
  background: rgba(255,255,255,0.05);
  color: rgba(255,255,255,0.5);
  border: 1px solid rgba(255,255,255,0.1);
  &:hover:not(:disabled) { background: rgba(255,255,255,0.1); color: #fff; }
}

/* === 文档滚动区 === */
.doc-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 28px 24px;
  background: #03142d;
  scrollbar-width: thin;
  scrollbar-color: rgba(255,255,255,0.08) transparent;
  display: flex;
  justify-content: center;
  &::-webkit-scrollbar { width: 4px; }
  &::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 2px; }
}

/* === 纸张文档卡片 === */
.minutes-paper-card {
  width: 640px;
  max-width: calc(100% - 0px);
  background: #0c1d3a;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  overflow: hidden;
}

/* 4px 顶部动态色条 */
.paper-header-band {
  height: 4px;
  background: linear-gradient(90deg, #1677ff 0%, #00d278 50%, #1677ff 100%);
  background-size: 200% 100%;
  animation: bandShift 4s linear infinite;
}
@keyframes bandShift {
  0%   { background-position: 0 0; }
  100% { background-position: 200% 0; }
}

.paper-body {
  padding: 36px 44px 44px;
}

/* 文档标题区 */
.paper-title-area {
  text-align: center;
  margin-bottom: 28px;
  padding-bottom: 22px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
}
.paper-title-text-center {
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 4px;
  margin-bottom: 10px;
}
.paper-subtitle-text {
  font-size: 12px;
  color: rgba(255,255,255,0.35);
  margin-bottom: 14px;
}
.paper-meta-tags {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  flex-wrap: wrap;
}
.paper-meta-tag {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: rgba(255,255,255,0.4);
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.07);
  padding: 4px 12px;
  border-radius: 20px;
  svg { width: 12px; height: 12px; }
  strong { color: rgba(255,255,255,0.65); font-weight: 500; }
}

/* 纪要正文内容 */
.paper-content {
  font-size: 14px;
  color: rgba(255,255,255,0.72);
  line-height: 2.0;
  letter-spacing: 0.2px;
  :deep(h1) {
    font-size: 18px;
    text-align: center;
    font-weight: 700;
    color: #fff;
    letter-spacing: 2px;
    margin: 0 0 20px;
  }
  :deep(h2) {
    font-size: 15px;
    font-weight: 700;
    color: rgba(255,255,255,0.9);
    margin: 28px 0 14px;
    display: flex;
    align-items: center;
    gap: 8px;
    &::before {
      content: '';
      display: block;
      width: 3px;
      height: 16px;
      background: linear-gradient(180deg, #1677ff, #00d278);
      border-radius: 2px;
      flex-shrink: 0;
    }
  }
  :deep(h3) {
    font-size: 14px;
    font-weight: 600;
    color: rgba(255,255,255,0.8);
    margin: 16px 0 8px;
  }
  :deep(p) {
    margin-bottom: 12px;
    text-indent: 2em;
    color: rgba(255,255,255,0.68);
  }
  :deep(ol), :deep(ul) {
    padding-left: 1.5em;
    margin-bottom: 12px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  :deep(li) {
    color: rgba(255,255,255,0.65);
    line-height: 1.85;
  }
  :deep(li::marker) { color: #4096ff; }
  :deep(blockquote) {
    margin: 16px 0;
    padding: 14px 18px;
    background: rgba(22,119,255,0.06);
    border-left: 3px solid rgba(22,119,255,0.5);
    border-radius: 0 8px 8px 0;
    font-size: 13px;
    color: rgba(200,220,255,0.7);
    line-height: 1.75;
  }
  :deep(.conclusion) {
    margin-top: 20px;
    padding: 18px 22px;
    background: rgba(0,210,120,0.06);
    border: 1px solid rgba(0,210,120,0.18);
    border-radius: 10px;
    font-size: 13px;
    color: rgba(180,240,210,0.8);
    line-height: 1.85;
  }
  :deep(strong) { color: rgba(255,255,255,0.9); font-weight: 600; }
}
.paper-placeholder {
  text-align: center;
  padding: 40px 0;
  color: rgba(255,255,255,0.2);
  font-style: italic;
  font-size: 14px;
}

/* 底部签名区 */
.paper-footer {
  display: flex;
  justify-content: flex-end;
  gap: 36px;
  margin-top: 36px;
  padding-top: 22px;
  border-top: 1px solid rgba(255,255,255,0.07);
}
.paper-sign-col {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 110px;
}
.paper-sign-label {
  font-size: 12px;
  color: rgba(255,255,255,0.35);
}
.paper-sign-line {
  height: 32px;
  border-bottom: 1px solid rgba(255,255,255,0.12);
  display: flex;
  align-items: flex-end;
  padding-bottom: 4px;
  font-size: 13px;
  color: rgba(255,255,255,0.5);
  &.signed { color: #00d278; border-color: rgba(0,210,120,0.3); }
}

/* === 右侧面板块 === */
.side-block {
  padding: 18px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  &:last-child { border-bottom: none; }
}
.side-block-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 18px;
}
.side-block-title {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255,255,255,0.28);
  letter-spacing: 1.2px;
  text-transform: uppercase;
  margin-bottom: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  svg { width: 11px; height: 11px; }
}

/* 签审状态卡片 */
.sign-state-card {
  border-radius: 12px;
  padding: 18px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  text-align: center;
}
.card-success { background: rgba(0,210,120,0.07); border: 1px solid rgba(0,210,120,0.2); }
.card-blue    { background: rgba(22,119,255,0.07); border: 1px solid rgba(22,119,255,0.25); }
.card-orange  { background: rgba(255,165,0,0.07);  border: 1px solid rgba(255,165,0,0.2); }
.card-waiting { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); }

.state-icon-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  svg { width: 22px; height: 22px; }
}
.icon-success { background: rgba(0,210,120,0.15); border: 2px solid rgba(0,210,120,0.35); box-shadow: 0 0 20px rgba(0,210,120,0.18); color: #00d278; stroke: #00d278; }
.icon-blue    { background: rgba(22,119,255,0.18); border: 2px solid rgba(22,119,255,0.4);  color: #4096ff; stroke: #4096ff; }
.icon-orange  { background: rgba(255,165,0,0.12);  border: 2px solid rgba(255,165,0,0.3);   color: #ffa500; stroke: #ffa500; }
.icon-waiting { background: rgba(255,255,255,0.05); border: 2px solid rgba(255,255,255,0.1); color: rgba(255,255,255,0.4); stroke: rgba(255,255,255,0.4); }

.state-info { display: flex; flex-direction: column; align-items: center; gap: 6px; }
.state-title { font-size: 15px; font-weight: 700; }
.card-success .state-title { color: #00d278; }
.card-blue    .state-title { color: #4096ff; }
.card-orange  .state-title { color: #ffa500; }
.card-waiting .state-title { color: rgba(255,255,255,0.65); }
.state-desc { font-size: 12px; color: rgba(255,255,255,0.38); line-height: 1.6; }
.sign-action-btn { margin-top: 4px; }

/* 流程步骤 */
.flow-steps { display: flex; flex-direction: column; }
.flow-step { display: flex; gap: 10px; }
.flow-step-track {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
  padding-top: 2px;
}
.flow-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  svg { width: 11px; height: 11px; }
}
.dot-done    { background: rgba(0,210,120,0.2);  border: 2px solid rgba(0,210,120,0.45); color: #00d278; stroke: #00d278; }
.dot-current { background: rgba(22,119,255,0.2); border: 2px solid #1677ff; color: #4096ff; stroke: #4096ff; box-shadow: 0 0 0 3px rgba(22,119,255,0.12); }
.dot-pending { background: rgba(255,255,255,0.04); border: 2px solid rgba(255,255,255,0.1); color: rgba(255,255,255,0.2); stroke: rgba(255,255,255,0.2); }
.flow-line {
  width: 1px;
  flex: 1;
  min-height: 18px;
  margin: 3px 0;
}
.line-done    { background: rgba(0,210,120,0.25); }
.line-pending { background: rgba(255,255,255,0.06); }
.flow-content { padding: 2px 0 18px; flex: 1; }
.flow-step:last-child .flow-content { padding-bottom: 0; }
.flow-label {
  font-size: 13px;
  font-weight: 500;
  color: rgba(255,255,255,0.7);
  margin-bottom: 2px;
}
.flow-label.label-done { color: #00d278; }
.flow-sub { font-size: 11px; color: rgba(255,255,255,0.32); line-height: 1.5; }
.flow-unit { font-size: 11px; color: rgba(255,255,255,0.32); font-weight: 400; margin-left: 4px; }

/* 待签提示 */
.pending-tip {
  padding: 12px 14px;
  border-radius: 9px;
  background: rgba(255,122,0,0.07);
  border: 1px solid rgba(255,122,0,0.18);
  display: flex;
  gap: 9px;
  align-items: flex-start;
}
.pending-tip-text {
  font-size: 12px;
  color: rgba(255,200,120,0.7);
  line-height: 1.65;
  strong { color: #ff9c40; }
}

/* 签署人列表 */
.signer-list { display: flex; flex-direction: column; gap: 7px; }
.signer-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 9px;
  background: rgba(255,255,255,0.025);
  border: 1px solid rgba(255,255,255,0.055);
  transition: all 0.2s;
  &:hover { background: rgba(22,119,255,0.05); border-color: rgba(22,119,255,0.14); }
}
.signer-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}
.avatar-color-0 { background: rgba(0,210,120,0.15);  color: #00d278; border: 1px solid rgba(0,210,120,0.25); }
.avatar-color-1 { background: rgba(22,119,255,0.18); color: #4096ff; border: 1px solid rgba(22,119,255,0.3); }
.avatar-color-2 { background: rgba(148,0,255,0.15);  color: #b37feb; border: 1px solid rgba(148,0,255,0.28); }
.signer-info { flex: 1; min-width: 0; }
.signer-name-text { font-size: 12px; font-weight: 500; color: rgba(255,255,255,0.75); }
.signer-role-text { font-size: 10px; color: rgba(255,255,255,0.32); margin-top: 1px; }
.signer-time-text { font-size: 10px; color: rgba(255,255,255,0.22); display: block; margin-top: 2px; }
.signer-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 9px;
  flex-shrink: 0;
}
.badge-signed { background: rgba(0,210,120,0.1);  color: #00d278; border: 1px solid rgba(0,210,120,0.2); }
.badge-draft  { background: rgba(22,119,255,0.1); color: #4096ff; border: 1px solid rgba(22,119,255,0.25); }
.status-dot-sm { width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; }
.dot-green { background: #00d278; }
.dot-blue  { background: #4096ff; }

/* 文件预览 */
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

/* 实时摘要（旧版保留-新版见文末）*/
.summary-section {
  max-width: 800px;
  margin: 0 auto;
  padding: 16px 0;
}
.summary-title {
  font-size: 16px;
  font-weight: 600;
  color: #e0ecf5;
}
.summary-content {
  background: rgba(0,212,255,0.05);
  border: 1px solid rgba(0,212,255,0.2);
  border-radius: 8px;
  padding: 20px;
  font-size: 14px;
  line-height: 1.8;
  color: #c5dbe8;
  white-space: pre-wrap;
}

.summary-keypoints {
  margin-top: 16px;
  .summary-kp-title {
    font-size: 14px; font-weight: 600; color: #00d4ff; margin-bottom: 10px;
  }
  .summary-kp-item {
    padding: 10px 12px; margin-bottom: 8px;
    background: rgba(0,212,255,0.04);
    border-left: 2px solid rgba(0,212,255,0.3);
    border-radius: 4px;
    strong { color: #e0eef8; font-size: 14px; }
    p { color: #5e8aad; font-size: 14px; margin: 4px 0 0; line-height: 1.5; }
  }
}

/* 参会人员（旧版，新版见文末）*/
.people-stats {
  display: flex;
  gap: 32px;
  justify-content: center;
  margin-bottom: 8px;
  :deep(.el-statistic) {
    text-align: center;
    .el-statistic__head { color: #8899aa; font-size: 14px; }
    .el-statistic__content { color: #e0ecff; font-size: 24px; font-weight: 700; }
  }
}
.people-group-title {
  font-size: 15px;
  font-weight: 600;
  color: #00d4ff;
  margin-bottom: 10px;
  letter-spacing: 1px;
}

/* 问题记录（旧版，新版见文末）*/
.terminal-issue-item {
  background: #14284b;
  border: 1px solid #204082;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 10px;
  &.resolved { opacity: 0.55; }
  .issue-content {
    font-size: 14px;
    color: #d0e0f0;
    margin-bottom: 6px;
    line-height: 1.5;
  }
  .issue-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 14px;
    color: #6a8090;
  }
}

/* ===== 评审费管理（新） ===== */
.fee-manage-section {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.fee-notice-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 56px 24px;
  color: #8ab4d0;
  font-size: 15px;
  text-align: center;

  p { margin: 0; line-height: 1.6; }
}

.fee-manage-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
}

.fee-manage-header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.fee-manage-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: rgba(255,255,255,0.85);
}

.fee-manage-subtitle {
  font-size: 13px;
  color: rgba(255,255,255,0.4);
}

.fee-manage-stats {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

.fee-stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  padding: 8px 16px;
  min-width: 64px;
}

.fee-stat-item.fee-stat-signed {
  background: rgba(52,211,153,0.08);
  border-color: rgba(52,211,153,0.3);
}

.fee-stat-item.fee-stat-pending {
  background: rgba(251,146,60,0.08);
  border-color: rgba(251,146,60,0.3);
}

.fee-stat-num {
  font-size: 20px;
  font-weight: 700;
  color: rgba(255,255,255,0.9);
  line-height: 1;
}

.fee-stat-item.fee-stat-signed .fee-stat-num { color: #34d399; }
.fee-stat-item.fee-stat-pending .fee-stat-num { color: #fb923c; }

.fee-stat-label {
  font-size: 11px;
  color: rgba(255,255,255,0.4);
  margin-top: 3px;
}

.fee-progress-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.fee-progress-label {
  font-size: 12px;
  color: rgba(255,255,255,0.4);
  flex-shrink: 0;
}

.fee-progress-frac {
  font-size: 12px;
  color: rgba(255,255,255,0.5);
  flex-shrink: 0;
}

.fee-group-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: rgba(255,255,255,0.45);
  font-weight: 500;
}

.fee-expert-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.fee-expert-item {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #14284b;
  border: 1px solid #204082;
  border-radius: 12px;
  padding: 14px 16px;
  transition: border-color 0.2s;

  &:hover {
    border-color: rgba(64,150,255,0.5);
  }
}

.fee-expert-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  flex-shrink: 0;
}

.fee-expert-info {
  flex: 1;
  min-width: 0;
}

.fee-expert-name {
  font-size: 15px;
  font-weight: 600;
  color: rgba(255,255,255,0.9);
  display: flex;
  align-items: center;
}

.fee-expert-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 12px;
  color: rgba(255,255,255,0.35);
  margin-top: 4px;

  span {
    display: flex;
    align-items: center;
    gap: 3px;
  }
}

.fee-expert-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  flex-shrink: 0;
}

.fee-expert-status {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 100px;

  &.status-signed {
    background: rgba(52,211,153,0.12);
    color: #34d399;
    border: 1px solid rgba(52,211,153,0.3);
  }

  &.status-pending {
    background: rgba(251,146,60,0.1);
    color: #fb923c;
    border: 1px solid rgba(251,146,60,0.25);
  }
}

.fee-status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  display: inline-block;
}

.fee-sign-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 14px;
  background: linear-gradient(135deg, rgba(22,119,255,0.25), rgba(22,119,255,0.12));
  border: 1px solid rgba(22,119,255,0.5);
  border-radius: 8px;
  color: #4096ff;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: linear-gradient(135deg, rgba(22,119,255,0.4), rgba(22,119,255,0.2));
    border-color: rgba(22,119,255,0.8);
    color: #69b1ff;
  }
}

/* ===== 评审费签名弹窗（新） ===== */
.fee-sign-dialog {
  .el-dialog__header { padding: 0 !important; }
  .el-dialog__body { padding: 0 20px 0 !important; }
  .el-dialog__footer { padding: 0 !important; }
}

.fee-dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px 14px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}

.fee-dialog-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: rgba(255,255,255,0.85);
}

.fee-dialog-icon {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: rgba(64,150,255,0.15);
  border: 1px solid rgba(64,150,255,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4096ff;
}

.fee-dialog-person {
  color: #4096ff;
}

.fee-dialog-close-btn {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.1);
  background: transparent;
  color: rgba(255,255,255,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: rgba(255,255,255,0.08);
    color: rgba(255,255,255,0.8);
  }
}

.fee-dialog-notice {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: rgba(64,150,255,0.08);
  border: 1px solid rgba(64,150,255,0.2);
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 13px;
  color: rgba(255,255,255,0.55);
  margin: 16px 0;
  line-height: 1.5;
  color: rgba(180,210,255,0.7);
}

.fee-dialog-form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.fee-dialog-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.fee-dialog-label {
  font-size: 13px;
  color: rgba(255,255,255,0.55);
  font-weight: 500;
}

.fee-required {
  color: #f56c6c;
  margin-right: 2px;
}

.fee-dialog-sign-area {
  margin-bottom: 16px;
}

.fee-dialog-sign-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.fee-dialog-sign-actions {
  display: flex;
  gap: 8px;
}

.fee-canvas-action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 5px 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 6px;
  color: rgba(255,255,255,0.5);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: rgba(255,255,255,0.1);
    color: rgba(255,255,255,0.8);
  }
}

.fee-sign-canvas-wrap {
  position: relative;
  border-radius: 10px;
  overflow: hidden;
  background: #0e1d38;
  border: 1px solid #204082;
}

.fee-canvas-styled {
  display: block;
  width: 100%;
  height: 240px;
  cursor: crosshair;
}

.fee-canvas-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  pointer-events: none;
  color: rgba(255,255,255,0.3);
}

.fee-canvas-hint-title {
  font-size: 14px;
  color: rgba(255,255,255,0.3);
}

.fee-canvas-hint-sub {
  font-size: 12px;
  color: rgba(255,255,255,0.18);
}

.fee-dialog-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 24px 18px;
  border-top: 1px solid rgba(255,255,255,0.08);
}

.fee-dialog-footer-left {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: rgba(255,255,255,0.3);
}

.fee-dialog-footer-right {
  display: flex;
  gap: 10px;
}

/* ===== 智能问答（新） ===== */
.qa-section {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px 24px;
  gap: 14px;
}

.qa-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.qa-header-left {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.qa-header-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(64,150,255,0.15);
  border: 1px solid rgba(64,150,255,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4096ff;
  flex-shrink: 0;
  margin-top: 2px;
}

.qa-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 3px;
}

.qa-title {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255,255,255,0.85);
}

.qa-ai-badge {
  font-size: 11px;
  padding: 2px 8px;
  background: rgba(64,150,255,0.15);
  border: 1px solid rgba(64,150,255,0.3);
  border-radius: 100px;
  color: #4096ff;
}

.qa-subtitle {
  font-size: 12px;
  color: rgba(255,255,255,0.35);
}

.qa-context-chips {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.qa-context-chip {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  padding: 4px 10px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 100px;
  color: rgba(255,255,255,0.4);
}

.qa-messages-area {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.qa-messages {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.qa-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 200px;
  gap: 8px;
  padding: 24px 0;
}

.qa-empty-icon {
  color: rgba(255,255,255,0.2);
  margin-bottom: 8px;
}

.qa-empty-title {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255,255,255,0.55);
}

.qa-empty-desc {
  font-size: 13px;
  color: rgba(255,255,255,0.3);
  margin-bottom: 8px;
}

.qa-quick-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  width: 100%;
  max-width: 560px;
}

.qa-quick-label {
  font-size: 12px;
  color: rgba(255,255,255,0.3);
}

.qa-quick-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.qa-quick-pill {
  padding: 8px 16px;
  background: #14284b;
  border: 1px solid #204082;
  border-radius: 100px;
  color: rgba(255,255,255,0.6);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: rgba(64,150,255,0.5);
    color: #4096ff;
    background: rgba(64,150,255,0.08);
  }
}

.qa-loading-bubble .qa-content {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 12px 16px !important;
}

.qa-typing-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #4096ff;
  animation: qa-dot-pulse 1.2s ease-in-out infinite;

  &:nth-child(2) { animation-delay: 0.2s; }
  &:nth-child(3) { animation-delay: 0.4s; }
}

@keyframes qa-dot-pulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1); }
}

.qa-input-area {
  flex-shrink: 0;
  border-top: 1px solid rgba(255,255,255,0.06);
  padding-top: 12px;
}

.qa-input-box-wrap {
  position: relative;
  display: flex;
  gap: 0;
}

.qa-input-box {
  flex: 1;
  background: #14284b;
  border: 1px solid #204082;
  border-right: none;
  border-radius: 10px 0 0 10px;
  padding: 12px 16px;
  color: rgba(255,255,255,0.85);
  font-size: 14px;
  resize: none;
  outline: none;
  line-height: 1.5;
  font-family: inherit;

  &::placeholder { color: rgba(255,255,255,0.25); }

  &:focus {
    border-color: rgba(64,150,255,0.5);
  }
}

.qa-send-btn {
  width: 50px;
  background: #1677ff;
  border: 1px solid #1677ff;
  border-radius: 0 10px 10px 0;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;

  &:hover:not(:disabled) {
    background: #4096ff;
    border-color: #4096ff;
  }

  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
}

.qa-spin {
  animation: qa-spin 1s linear infinite;
}

@keyframes qa-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.qa-section-locked {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 200px;
  gap: 10px;
  padding: 40px 24px;
}

.qa-locked-title {
  font-size: 15px;
  font-weight: 600;
  color: rgba(255,255,255,0.4);
}

.qa-locked-desc {
  font-size: 13px;
  color: rgba(255,255,255,0.25);
}

/* ===== 专家组长大屏签字板 overlay ===== */
.leader-sign-overlay {
  position: fixed; inset: 0; z-index: 9999;
  background: rgba(2, 10, 25, 0.97);
  backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  overflow-y: auto;
}
.lso-content {
  width: 100%; max-width: 860px; padding: 40px 32px;
  display: flex; flex-direction: column; align-items: center; gap: 20px;
}
.lso-notice-bar {
  display: flex; align-items: center; gap: 10px;
  background: rgba(230,162,60,0.15); border: 1px solid rgba(230,162,60,0.4);
  border-radius: 8px; padding: 12px 20px;
  color: #e6a23c; font-size: 15px; width: 100%; max-width: 760px;
}
.lso-title {
  font-size: 24px; font-weight: 700; color: #00d4ff; letter-spacing: 2px; text-align: center;
}
.lso-signer {
  font-size: 15px; color: #c8dff5; display: flex; align-items: center; gap: 6px;
}
.lso-canvas-label {
  display: flex; align-items: center; justify-content: space-between;
  width: 100%; max-width: 760px; font-size: 14px; color: #8ab4d0;
}
.lso-canvas-wrap {
  width: 100%; max-width: 760px;
  border: 1.5px dashed rgba(0,212,255,0.4); border-radius: 8px;
  background: rgba(0,15,40,0.8); overflow: hidden;
}
.lso-canvas {
  display: block; width: 100%; height: auto; cursor: crosshair; touch-action: none;
}
.lso-opinion-row {
  width: 100%; max-width: 760px;
}
.lso-actions {
  display: flex; gap: 16px; flex-wrap: wrap; justify-content: center;
}
.lso-skip {
  font-size: 14px; color: #5e8aad; cursor: pointer; text-decoration: underline;
}
.lso-skip:hover { color: #00d4ff; }

/* ===== 签到Tab - 新版左右布局 ===== */
.self-signed-done-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 48px 24px;
  text-align: center;
}
.ssd-check-icon {
  font-size: 72px;
  color: #00d278;
  filter: drop-shadow(0 0 16px rgba(103,194,58,0.4));
}
.ssd-text {
  font-size: 22px;
  font-weight: 700;
  color: #00d278;
  letter-spacing: 2px;
}
.ssd-name {
  font-size: 20px;
  color: #e0ecff;
  font-weight: 600;
  letter-spacing: 3px;
}
.ssd-dept {
  font-size: 14px;
  color: #5e8aad;
}
.self-checkin-split-layout {
  display: flex;
  gap: 24px;
  align-items: stretch;
  min-height: 360px;
}
.identity-confirm-panel {
  width: 220px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 20px 16px;
  background: #14284b;
  border: 1px solid #204082;
  border-radius: 10px;
}
.icp-title {
  font-size: 15px;
  font-weight: 600;
  color: #c8dff5;
  letter-spacing: 2px;
  align-self: flex-start;
}
.icp-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 16px;
  width: 100%;
  background: #1a3966;
  border: 1px solid rgba(32,64,130,0.5);
  border-radius: 8px;
  text-align: center;
}
.icp-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff, #1a7ad4);
  color: #fff;
  font-size: 28px;
  font-weight: 700;
  line-height: 64px;
  margin-bottom: 4px;
}
.icp-name {
  font-size: 18px;
  font-weight: 600;
  color: #e0ecff;
  letter-spacing: 2px;
}
.icp-dept {
  font-size: 13px;
  color: #5e8aad;
}
.icp-confirm-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 6px;
  padding: 4px 12px;
  background: rgba(103,194,58,0.12);
  border: 1px solid rgba(103,194,58,0.3);
  border-radius: 20px;
  font-size: 13px;
  color: #67c23a;
  font-weight: 600;
}
.icp-reidentify-btn {
  width: 100%;
  color: #5e8aad !important;
  border-color: rgba(0,212,255,0.2) !important;
  background: transparent !important;
  font-size: 13px !important;
}
.icp-reidentify-btn:hover {
  color: #00d4ff !important;
  border-color: rgba(0,212,255,0.5) !important;
}
.sign-input-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0;
  background: #14284b;
  border: 1px solid #204082;
  border-radius: 10px;
  overflow: hidden;
}
.sip-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(32,64,130,0.5);
  background: #1a3966;
}
.sip-title {
  font-size: 15px;
  font-weight: 600;
  color: #c8dff5;
  letter-spacing: 2px;
}
.sip-tools {
  display: flex;
  gap: 4px;
  :deep(.el-button) { color: #7fa8c8 !important; }
  :deep(.el-button:hover) { color: #00d4ff !important; }
}
.sip-canvas-wrap {
  flex: 1;
  position: relative;
  min-height: 260px;
}
.sip-canvas {
  display: block;
  width: 100%;
  height: 100%;
  cursor: crosshair;
  touch-action: none;
  background: #07121e;
}
.sip-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  pointer-events: none;
  color: rgba(100,160,210,0.35);
  font-size: 15px;
  letter-spacing: 1px;
}
.sip-ph-icon {
  font-size: 48px;
  color: rgba(100,160,210,0.2);
}
.sip-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-top: 1px solid rgba(32,64,130,0.5);
  background: #1a3966;
}
.sip-tip {
  font-size: 13px;
  color: #4a6e8a;
}
.sip-confirm-btn {
  padding: 10px 24px !important;
  font-size: 15px !important;
  font-weight: 600 !important;
}

/* ===== 会议材料 - 新版 ===== */
.materials-section {
  display: flex;
  flex-direction: column;
  padding: 20px 24px;
  flex: 1;
}

.mat-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  justify-content: space-between;
  flex-wrap: wrap;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  padding: 0 12px;
  height: 34px;
  width: 220px;
  transition: border-color 0.2s;
  svg { width: 14px; height: 14px; stroke: rgba(255,255,255,0.4); flex-shrink: 0; }
  input {
    background: transparent;
    border: none;
    outline: none;
    color: rgba(255,255,255,0.85);
    font-size: 13px;
    width: 100%;
    &::placeholder { color: rgba(255,255,255,0.3); }
  }
  &:focus-within { border-color: rgba(22,119,255,0.5); }
}

.filter-group {
  display: flex;
  gap: 4px;
  align-items: center;
}

.filter-btn {
  display: inline-flex;
  align-items: center;
  height: 28px;
  padding: 0 10px;
  border-radius: 100px;
  border: 1px solid rgba(255,255,255,0.12);
  background: transparent;
  color: rgba(255,255,255,0.5);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  &:hover { border-color: rgba(255,255,255,0.25); color: rgba(255,255,255,0.75); }
  &.active { background: rgba(22,119,255,0.2); border-color: rgba(22,119,255,0.5); color: #4096ff; }
}

.view-toggle {
  display: flex;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 6px;
  overflow: hidden;
}

.view-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 28px;
  cursor: pointer;
  color: rgba(255,255,255,0.4);
  transition: all 0.2s;
  svg { width: 14px; height: 14px; }
  &:hover { color: rgba(255,255,255,0.75); background: rgba(255,255,255,0.06); }
  &.active { color: #fff; background: rgba(22,119,255,0.4); }
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #14284b;
  border: 1px solid #204082;
  border-radius: 12px;
  padding: 12px 16px;
  transition: all 0.2s;
  &:hover {
    background: rgba(22,119,255,0.12);
    border-color: rgba(22,119,255,0.45);
    transform: translateX(2px);
  }
}

.file-icon {
  width: 42px;
  height: 42px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.5px;
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255,255,255,0.85);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 4px;
  flex-wrap: wrap;
}

.file-meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: rgba(255,255,255,0.4);
  svg { width: 12px; height: 12px; }
}

.file-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.file-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 28px;
  padding: 0 10px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  svg { width: 13px; height: 13px; }
  &.file-btn-preview {
    background: rgba(22,119,255,0.15);
    border: 1px solid rgba(22,119,255,0.3);
    color: #4096ff;
    &:hover { background: rgba(22,119,255,0.25); }
  }
  &.file-btn-download {
    background: transparent;
    border: 1px solid rgba(255,255,255,0.18);
    color: rgba(255,255,255,0.65);
    &:hover { border-color: rgba(255,255,255,0.35); color: #fff; }
  }
}

.mat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
}

.mat-grid-item {
  background: #14284b;
  border: 1px solid #204082;
  border-radius: 12px;
  padding: 18px 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-align: center;
  transition: all 0.2s;
  &:hover { background: rgba(22,119,255,0.12); border-color: rgba(22,119,255,0.45); }
}

.mat-grid-type-icon {
  width: 56px;
  height: 56px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
}

.materials-stats {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 14px;
  padding: 10px 16px;
  background: #14284b;
  border: 1px solid #204082;
  border-radius: 8px;
  font-size: 13px;
  color: rgba(255,255,255,0.4);
  .divider-v { height: 14px; margin: 0 6px; }
  strong { color: rgba(255,255,255,0.7); }
}

/* ===== 参会人员 - 新版 ===== */
.people-section {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
}

.people-stat-cards {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.psc-card {
  flex: 1;
  min-width: 100px;
  padding: 16px 12px 14px;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  text-align: center;
  border: 1px solid transparent;
}

.psc-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
  svg { width: 18px; height: 18px; }
}

.psc-num {
  font-size: 26px;
  font-weight: 800;
  line-height: 1;
}
.psc-label {
  font-size: 12px;
  font-weight: 500;
}
.psc-total {
  background: rgba(59,130,246,0.1);
  border-color: rgba(59,130,246,0.2);
  .psc-icon { background: rgba(59,130,246,0.15); svg { stroke: #3b82f6; } }
  .psc-num { color: #3b82f6; }
  .psc-label { color: rgba(59,130,246,0.7); }
}
.psc-expert {
  background: rgba(179,127,235,0.1);
  border-color: rgba(179,127,235,0.2);
  .psc-icon { background: rgba(179,127,235,0.15); svg { stroke: #b37feb; } }
  .psc-num { color: #b37feb; }
  .psc-label { color: rgba(179,127,235,0.7); }
}
.psc-other {
  background: rgba(54,207,201,0.1);
  border-color: rgba(54,207,201,0.2);
  .psc-icon { background: rgba(54,207,201,0.15); svg { stroke: #36cfc9; } }
  .psc-num { color: #36cfc9; }
  .psc-label { color: rgba(54,207,201,0.7); }
}
.psc-checked-in {
  background: rgba(82,196,26,0.1);
  border-color: rgba(82,196,26,0.2);
  .psc-icon { background: rgba(82,196,26,0.15); svg { stroke: #52c41a; } }
  .psc-num { color: #52c41a; }
  .psc-label { color: rgba(82,196,26,0.7); }
}
.psc-unchecked {
  background: rgba(250,173,20,0.1);
  border-color: rgba(250,173,20,0.2);
  .psc-icon { background: rgba(250,173,20,0.15); svg { stroke: #faad14; } }
  .psc-num { color: #faad14; }
  .psc-label { color: rgba(250,173,20,0.7); }
}

/* 自定义进度条 */
.people-progress-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.progress-bar-label {
  font-size: 14px;
  color: rgba(255,255,255,0.55);
  white-space: nowrap;
}

.progress-bar-track {
  flex: 1;
  height: 6px;
  background: rgba(255,255,255,0.08);
  border-radius: 100px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #1677ff, #00d278);
  border-radius: 100px;
  transition: width 0.5s ease;
}

.progress-bar-frac {
  font-size: 13px;
  color: rgba(255,255,255,0.55);
  white-space: nowrap;
  min-width: 50px;
  text-align: right;
}
.people-group-block {
  margin-bottom: 4px;
}
.people-group-header-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #e0ecff;
  margin-bottom: 10px;
  letter-spacing: 1px;
}
.pgb-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.pgb-expert-dot { background: #b37feb; }
.pgb-other-dot { background: #36cfc9; }
.people-table {
  :deep(.el-table) {
    background: transparent;
    --el-table-bg-color: rgba(255,255,255,0.02);
    --el-table-tr-bg-color: transparent;
    --el-table-row-hover-bg-color: rgba(22,119,255,0.07);
    --el-table-border-color: rgba(255,255,255,0.07);
    --el-table-header-bg-color: rgba(255,255,255,0.05);
    --el-table-text-color: rgba(255,255,255,0.75);
    --el-table-header-text-color: rgba(255,255,255,0.45);
  }
  :deep(.el-table__row .el-tag--warning) {
    background-color: rgba(250,173,20,0.12);
    border-color: rgba(250,173,20,0.4);
    color: #faad14;
  }
  :deep(.el-table__row .el-tag--success) {
    background-color: rgba(82,196,26,0.12);
    border-color: rgba(82,196,26,0.4);
    color: #52c41a;
  }
}

/* ===== 问题记录 - 新版 ===== */
.issues-section {
  display: flex;
  flex-direction: column;
  padding: 20px 24px;
}

.issues-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  gap: 12px;
  flex-wrap: wrap;
}

.issue-editor-card {
  background: #14284b;
  border: 1px solid #204082;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 16px;
}

.issue-editor-title {
  font-size: 15px;
  font-weight: 600;
  color: rgba(255,255,255,0.8);
  margin-bottom: 10px;
}

.issue-editor-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 10px;
}

/* 图例 */
.issue-legend {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: rgba(255,255,255,0.45);
}
.legend-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.legend-pending { background: #faad14; }
.legend-submitted { background: #52c41a; }
.legend-label { font-size: 12px; }

/* 问题卡片 */
.issue-item {
  border-radius: 10px;
  padding: 14px 16px;
  margin-bottom: 10px;
  transition: all 0.2s;
}
.issue-pending {
  background: rgba(250,173,20,0.06);
  border: 1.5px solid rgba(250,173,20,0.35);
  &:hover { border-color: rgba(250,173,20,0.6); }
}
.issue-submitted {
  background: rgba(82,196,26,0.05);
  border: 1.5px solid rgba(82,196,26,0.3);
  &:hover { border-color: rgba(82,196,26,0.55); }
}

.issue-item-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.issue-submit-badge {
  font-size: 11px;
  padding: 1px 8px;
  border-radius: 100px;
  font-weight: 500;
  flex-shrink: 0;
}
.badge-pending {
  color: #faad14;
  background: rgba(250,173,20,0.12);
  border: 1px solid rgba(250,173,20,0.35);
}
.badge-submitted {
  color: #52c41a;
  background: rgba(82,196,26,0.1);
  border: 1px solid rgba(82,196,26,0.3);
}

.issue-reporter {
  font-size: 12px;
  color: rgba(255,255,255,0.4);
  flex: 1;
}

.issue-actions {
  display: flex;
  gap: 6px;
  margin-left: auto;
}

.issue-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 12px;
  border: 1px solid;
  cursor: pointer;
  transition: all 0.18s;
  background: transparent;
  svg { width: 12px; height: 12px; }
  &:disabled { opacity: 0.45; cursor: not-allowed; }
}
.btn-submit-issue {
  color: #1677ff;
  border-color: rgba(22,119,255,0.4);
  &:hover:not(:disabled) { background: rgba(22,119,255,0.12); border-color: #1677ff; }
}
.btn-delete-issue {
  color: #ff4d4f;
  border-color: rgba(255,77,79,0.35);
  &:hover:not(:disabled) { background: rgba(255,77,79,0.1); border-color: #ff4d4f; }
}

.issue-content {
  font-size: 14px;
  color: rgba(255,255,255,0.85);
  line-height: 1.6;
  margin-bottom: 6px;
}

.issue-response {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 12px;
  color: rgba(255,255,255,0.5);
  padding: 6px 10px;
  background: rgba(22,119,255,0.06);
  border-left: 2px solid rgba(22,119,255,0.4);
  border-radius: 0 4px 4px 0;
  margin-top: 6px;
  line-height: 1.5;
}

.spin {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ===== 实时摘要 - 新版 ===== */
.summary-layout {
  display: flex;
  gap: 20px;
  padding: 20px 24px;
  flex: 1;
  min-height: 0;
}

.summary-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.summary-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.summary-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.live-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #00d278;
}

.live-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #00d278;
  animation: status-pulse 1.8s infinite;
}

.summary-content-card {
  background: #14284b;
  border: 1px solid #204082;
  border-radius: 12px;
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}

.summary-section-block {
  padding-bottom: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  &:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
}

.summary-block-title {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255,255,255,0.35);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 10px;
}

.summary-content-text {
  font-size: 14px;
  color: rgba(255,255,255,0.8);
  line-height: 1.8;
  white-space: pre-wrap;
}

.summary-gen-time {
  font-size: 12px;
  color: rgba(255,255,255,0.3);
  margin-top: 12px;
  text-align: right;
}

.kp-title {
  font-size: 14px;
  color: rgba(255,255,255,0.75);
  font-weight: 600;
}

.kp-content {
  font-size: 13px;
  color: rgba(255,255,255,0.55);
  margin: 4px 0 0;
  line-height: 1.6;
}

.summary-sidebar {
  width: 240px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.sidebar-card {
  background: #14284b;
  border: 1px solid #204082;
  border-radius: 12px;
  padding: 16px;
}

.sidebar-card-title {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 13px;
  font-weight: 600;
  color: rgba(255,255,255,0.45);
  margin-bottom: 14px;
  svg { width: 14px; height: 14px; }
}

.timeline {
  display: flex;
  flex-direction: column;
}

.timeline-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding-bottom: 14px;
  &:last-child { padding-bottom: 0; }
}

.timeline-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255,255,255,0.2);
  margin-top: 4px;
  flex-shrink: 0;
  &.timeline-dot-current {
    background: #1677ff;
    box-shadow: 0 0 0 3px rgba(22,119,255,0.2);
  }
}

.timeline-content { flex: 1; }

.timeline-time {
  font-size: 11px;
  color: rgba(255,255,255,0.3);
  margin-bottom: 2px;
}

.timeline-text {
  font-size: 13px;
  color: rgba(255,255,255,0.6);
}

/* ===== 会议纪要 - 等待状态 ===== */
.minutes-status-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: rgba(250,173,20,0.08);
  border: 1px solid rgba(250,173,20,0.2);
  border-radius: 10px;
  margin-bottom: 28px;
}

.status-card-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  svg { width: 20px; height: 20px; stroke: #faad14; }
}

.status-card-text {
  flex: 1;
  font-size: 14px;
  color: rgba(250,173,20,0.9);
  line-height: 1.5;
}

.waiting-layout {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 32px 0;
}

.waiting-steps {
  display: flex;
  align-items: center;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.step-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  svg { width: 16px; height: 16px; }
  &.step-done {
    background: #52c41a;
    color: #fff;
    svg { stroke: #fff; }
  }
  &.step-current {
    background: transparent;
    border: 2px solid #1677ff;
    color: #1677ff;
    animation: step-glow 2s infinite;
    svg { stroke: #1677ff; }
  }
  &.step-pending {
    background: rgba(255,255,255,0.06);
    border: 2px solid rgba(255,255,255,0.12);
    color: rgba(255,255,255,0.3);
  }
}

@keyframes step-glow {
  0%, 100% { box-shadow: 0 0 8px rgba(22,119,255,0.3); }
  50% { box-shadow: 0 0 16px rgba(22,119,255,0.6); }
}

.step-label {
  font-size: 12px;
  color: rgba(255,255,255,0.4);
  white-space: nowrap;
}

.step-connector {
  width: 56px;
  height: 2px;
  background: rgba(255,255,255,0.1);
  margin-bottom: 20px;
  flex-shrink: 0;
  &.step-connector-done { background: #52c41a; }
  &.step-connector-current { background: linear-gradient(90deg, #52c41a, #1677ff); }
}

.waiting-title {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255,255,255,0.7);
}

.waiting-desc {
  font-size: 13px;
  color: rgba(255,255,255,0.35);
  text-align: center;
  max-width: 400px;
  line-height: 1.6;
}
</style>
