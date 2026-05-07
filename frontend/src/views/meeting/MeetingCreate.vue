<template>
  <div class="page-container">
    <!-- 顶部标题栏 -->
    <div class="page-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" text @click="router.push('/meeting/list')" />
        <h2 class="page-title">{{ isEdit ? '编辑会议' : '新建会议' }}</h2>
      </div>
      <div class="header-right">
        <el-button @click="router.push('/meeting/list')">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          <el-icon><Check /></el-icon>{{ isEdit ? '保存修改' : '创建会议' }}
        </el-button>
      </div>
    </div>

    <!-- 步骤条导航 -->
    <div class="steps-nav">
      <div
        v-for="(step, i) in steps"
        :key="step.name"
        class="step-item"
        :class="{ active: activeTab === step.name, done: isStepDone(step.name) }"
        @click="activeTab = step.name"
      >
        <div class="step-dot">
          <el-icon v-if="isStepDone(step.name)"><Check /></el-icon>
          <span v-else>{{ i + 1 }}</span>
        </div>
        <span class="step-label">{{ step.label }}</span>
      </div>
    </div>

    <div class="main-body">
      <div class="main-content">

        <!-- ==================== Tab 1: 基本信息 & 参会人员 ==================== -->
        <div v-show="activeTab === 'info'" class="tab-panel">
          <div class="panel-inner">
            <!-- 基本信息区 -->
            <h3 class="panel-title">
              <el-icon><Edit /></el-icon>填写会议基本信息
            </h3>
            <el-form ref="basicFormRef" :model="form" :rules="basicRules" label-position="top" class="nice-form">
              <el-form-item label="会议名称" prop="title">
                <el-input v-model="form.title" placeholder="请输入会议名称" size="large" maxlength="50" show-word-limit />
              </el-form-item>

              <div class="form-row-2">
                <el-form-item label="会议类型" prop="meeting_type">
                  <el-select v-model="form.meeting_type" placeholder="请选择" size="large" style="width: 100%">
                    <el-option label="例会" value="regular" />
                    <el-option label="专题会议" value="special" />
                    <el-option label="决策会议" value="decision" />
                    <el-option label="评审会议" value="review" />
                    <el-option label="其他" value="other" />
                  </el-select>
                </el-form-item>
              </div>

              <!-- 时间选择区域 -->
              <div class="time-block">
                <div class="time-block-title">会议时间 <span class="required-star">*</span></div>
                <div class="time-row">
                  <div class="time-group">
                    <span class="time-label">日期</span>
                    <el-date-picker
                      v-model="form.startDate"
                      type="date"
                      placeholder="选择日期"
                      size="large"
                      format="YYYY年MM月DD日"
                      value-format="YYYY-MM-DD"
                      :shortcuts="dateShortcuts"
                      style="width: 200px"
                    />
                  </div>
                  <div class="time-group">
                    <span class="time-label">开始</span>
                    <el-time-picker v-model="form.startTime" placeholder="开始时间" size="large" format="HH:mm" style="width: 140px" />
                  </div>
                  <el-icon class="time-arrow"><Right /></el-icon>
                  <div class="time-group">
                    <span class="time-label">结束</span>
                    <el-time-picker v-model="form.endTime" placeholder="结束时间" size="large" format="HH:mm" style="width: 140px" />
                  </div>
                </div>
                <div class="duration-shortcuts">
                  <span class="shortcut-label">快捷时长：</span>
                  <el-button v-for="d in durationOptions" :key="d.value" size="small" :type="activeDuration === d.value ? 'primary' : ''" plain @click="setDuration(d.value)">
                    {{ d.label }}
                  </el-button>
                </div>
                <div v-if="durationText" class="duration-info">
                  <el-icon><Timer /></el-icon> 会议时长：{{ durationText }}
                </div>
              </div>

              <el-form-item label="会议描述">
                <el-input v-model="form.description" type="textarea" :rows="2" placeholder="请简要描述会议内容和目的" maxlength="500" show-word-limit />
              </el-form-item>
              <div class="form-row-2">
                <el-form-item label="准备欢迎词">
                  <el-input
                    v-model="form.welcome_message"
                    type="textarea"
                    :rows="2"
                    placeholder="请输入会议准备阶段展示的欢迎词，可为空"
                    maxlength="300"
                    show-word-limit
                  />
                </el-form-item>
                <el-form-item label="欢迎屏风格">
                  <el-select v-model="form.welcome_theme" style="width:100%">
                    <el-option
                      v-for="theme in welcomeThemeOptions"
                      :key="theme.value"
                      :label="theme.label"
                      :value="theme.value"
                    />
                  </el-select>
                </el-form-item>
              </div>
              <div class="review-fee-toggle-row" :class="{ active: form.has_review_fee }" @click="form.has_review_fee = !form.has_review_fee">
                <div class="review-fee-toggle-left">
                  <div class="review-fee-toggle-icon">
                    <el-icon><Tickets /></el-icon>
                  </div>
                  <div class="review-fee-toggle-text">
                    <span class="review-fee-toggle-title">开启评审费功能</span>
                  </div>
                </div>
                <el-switch v-model="form.has_review_fee" @click.stop active-color="#2bffbc" inactive-color="rgba(30,92,162,0.5)" />
              </div>
            </el-form>

            <div class="panel-actions">
              <span></span>
              <el-button type="primary" @click="goNext('persons')">
                下一步：选择人员 <el-icon><Right /></el-icon>
              </el-button>
            </div>
          </div>
        </div>

        <!-- ==================== Tab 2: 选择参会人员 ==================== -->
        <div v-show="activeTab === 'persons'" class="tab-panel">
          <div class="panel-inner">
            <!-- 合并头部：标题 + 搜索 + 操作 -->
            <div class="persons-header">
              <div class="persons-header-title">
                <el-icon><User /></el-icon>
                <span>选择参会人员</span>
              </div>
              <el-input v-model="personSearch" placeholder="搜索姓名/单位/职位" prefix-icon="Search" clearable class="persons-search" />
              <div class="persons-header-actions">
                <el-button link type="primary" @click="selectAll">全选</el-button>
                <el-button link type="danger" v-if="form.participant_ids.length > 0" @click="clearAll">清空</el-button>
                <el-button type="primary" plain size="small" @click="showAddPersonDialog">
                  <el-icon><Plus /></el-icon>新建人员
                </el-button>
              </div>
            </div>

            <div class="person-body">
              <!-- 左侧：可选人员 -->
              <div class="person-panel">
                <div class="person-panel-header">
                  <span>可选人员</span>
                  <span class="header-count">{{ allUsers.length }} 人</span>
                </div>
                <el-scrollbar height="360px">
                  <div v-if="loadingUsers" class="center-loading">
                    <el-icon class="is-loading"><Loading /></el-icon>
                    <span>加载中..</span>
                  </div>
                  <template v-else>
                    <!-- 专家 -->
                    <div v-if="Object.keys(groupedExperts).length > 0" class="user-type-section">
                      <div class="user-type-header registered-header">
                        <span class="type-dot registered-dot"></span>
                        <span>专家</span>
                        <span class="type-count">{{ expertUsers.length }} 人</span>
                      </div>
                      <div v-for="(members, dept) in groupedExperts" :key="'r-'+dept" class="dept-group">
                        <div class="dept-header" @click="toggleDept('r-'+dept)">
                          <el-checkbox
                            :model-value="isDeptAllSelected('r-'+dept, members)"
                            :indeterminate="isDeptPartialSelected('r-'+dept, members)"
                            @click.stop
                            @change="(val) => toggleDeptSelect(val, members)"
                            style="margin-right:6px"
                          />
                          <el-icon><OfficeBuilding /></el-icon>
                          <span>{{ dept }}</span>
                          <span class="dept-count">{{ filteredMembers(members).length }}</span>
                          <el-icon class="dept-arrow" :class="{ expanded: !collapsedDepts['r-'+dept] }"><ArrowRight /></el-icon>
                        </div>
                        <div v-show="!collapsedDepts['r-'+dept]" class="dept-members">
                          <div
                            v-for="user in filteredMembers(members)"
                            :key="user.id"
                            class="person-row"
                            :class="{ selected: form.participant_ids.includes(user.id), 'is-busy': isExternalBusy(user) }"
                            @click="togglePerson(user)"
                          >
                            <el-checkbox :model-value="form.participant_ids.includes(user.id)" :disabled="isExternalBusy(user)" @click.stop @change="togglePerson(user)" />
                            <el-avatar :size="30" class="person-avatar">{{ user.real_name?.charAt(0) }}</el-avatar>
                            <div class="person-info">
                              <span class="person-name">{{ user.real_name }}</span>
                              <span class="person-extra" v-if="user.professional_title">{{ user.professional_title }}</span>
                              <span class="person-extra" v-else-if="user.position">{{ user.position }}</span>
                            </div>
                            <el-tooltip
                              v-if="isExternalBusy(user)"
                              :content="`${getExternalBusyInfo(user)?.timeRange} 有外部任务：${getExternalBusyInfo(user)?.task}`"
                              placement="top"
                            >
                              <el-tag type="danger" size="small" class="busy-tag">
                                <el-icon><Warning /></el-icon> 忙碌
                              </el-tag>
                            </el-tooltip>
                            <el-tooltip v-if="user.is_participant_only" content="删除此人员" placement="top">
                              <el-icon class="delete-participant-btn" @click.stop="handleDeleteParticipant(user)"><Delete /></el-icon>
                            </el-tooltip>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- 其他人员 -->
                    <div v-if="Object.keys(groupedOthers).length > 0" class="user-type-section">
                      <div class="user-type-header participant-header">
                        <span class="type-dot participant-dot"></span>
                        <span>其他人员</span>
                        <span class="type-count">{{ otherUsers.length }} 人</span>
                      </div>
                      <div v-for="(members, dept) in groupedOthers" :key="'p-'+dept" class="dept-group">
                        <div class="dept-header" @click="toggleDept('p-'+dept)">
                          <el-checkbox
                            :model-value="isDeptAllSelected('p-'+dept, members)"
                            :indeterminate="isDeptPartialSelected('p-'+dept, members)"
                            @click.stop
                            @change="(val) => toggleDeptSelect(val, members)"
                            style="margin-right:6px"
                          />
                          <el-icon><User /></el-icon>
                          <span>{{ dept }}</span>
                          <span class="dept-count">{{ filteredMembers(members).length }}</span>
                          <el-icon class="dept-arrow" :class="{ expanded: !collapsedDepts['p-'+dept] }"><ArrowRight /></el-icon>
                        </div>
                        <div v-show="!collapsedDepts['p-'+dept]" class="dept-members participant-only-members">
                          <div
                            v-for="user in filteredMembers(members)"
                            :key="user.id"
                            class="person-row"
                            :class="{ selected: form.participant_ids.includes(user.id), 'is-busy': isExternalBusy(user) }"
                            @click="togglePerson(user)"
                          >
                            <el-checkbox :model-value="form.participant_ids.includes(user.id)" :disabled="isExternalBusy(user)" @click.stop @change="togglePerson(user)" />
                            <el-avatar :size="30" class="person-avatar participant-only-avatar">{{ user.real_name?.charAt(0) }}</el-avatar>
                            <div class="person-info">
                              <span class="person-name">{{ user.real_name }}</span>
                              <span class="person-extra" v-if="user.professional_title">{{ user.professional_title }}</span>
                              <span class="person-extra" v-else-if="user.position">{{ user.position }}</span>
                            </div>
                            <el-tooltip
                              v-if="isExternalBusy(user)"
                              :content="`${getExternalBusyInfo(user)?.timeRange} 有外部任务：${getExternalBusyInfo(user)?.task}`"
                              placement="top"
                            >
                              <el-tag type="danger" size="small" class="busy-tag">
                                <el-icon><Warning /></el-icon> 忙碌
                              </el-tag>
                            </el-tooltip>
                            <el-tooltip content="删除此人员" placement="top">
                              <el-icon class="delete-participant-btn" @click.stop="handleDeleteParticipant(user)"><Delete /></el-icon>
                            </el-tooltip>
                          </div>
                        </div>
                      </div>
                    </div>

                    <el-empty v-if="allUsers.length === 0" description="暂无可用人员" :image-size="60" />
                  </template>
                </el-scrollbar>
              </div>

              <!-- 右侧：已选人员 -->
              <div class="person-panel selected-panel">
                <div class="person-panel-header">
                  <span>已选人员</span>
                  <span class="header-count">{{ form.participant_ids.length }} 人</span>
                </div>
                <el-scrollbar height="360px">
                  <!-- 专家区 -->
                  <div v-if="selectedExperts.length > 0" class="selected-group-header">
                    <span class="type-dot registered-dot"></span>
                    <span>专家（{{ selectedExperts.length }}人）</span>
                  </div>
                  <TransitionGroup name="list" tag="div" class="selected-list">
                    <div v-for="person in selectedExperts" :key="'e-'+person.id" class="selected-row">
                      <el-avatar :size="30" class="person-avatar selected-avatar">{{ person.real_name?.charAt(0) }}</el-avatar>
                      <div class="person-info">
                        <span class="person-name">{{ person.real_name }}</span>
                        <span class="person-extra">{{ person.department || '' }}</span>
                        <span class="person-extra" v-if="person.professional_title">{{ person.professional_title }}</span>
                      </div>
                      <el-tag
                        v-if="form.leader_id === person.id"
                        type="warning" size="small" effect="dark"
                        style="margin-right:4px;cursor:pointer"
                        @click="form.leader_id = null"
                      >组长</el-tag>
                      <el-button
                        v-else
                        link type="warning" size="small"
                        @click="form.leader_id = person.id"
                        style="margin-right:4px"
                      >设为组长</el-button>
                      <el-icon class="remove-btn" @click="togglePerson(person)"><Close /></el-icon>
                    </div>
                  </TransitionGroup>
                  <!-- 其他人员区 -->
                  <div v-if="selectedOthers.length > 0" class="selected-group-header" style="margin-top:8px">
                    <span class="type-dot participant-dot"></span>
                    <span>其他人员（{{ selectedOthers.length }}人）</span>
                  </div>
                  <TransitionGroup name="list" tag="div" class="selected-list">
                    <div v-for="person in selectedOthers" :key="'o-'+person.id" class="selected-row">
                      <el-avatar :size="30" class="person-avatar selected-avatar">{{ person.real_name?.charAt(0) }}</el-avatar>
                      <div class="person-info">
                        <span class="person-name">{{ person.real_name }}</span>
                        <span class="person-extra">{{ person.department || '' }}</span>
                        <span class="person-extra" v-if="person.professional_title">{{ person.professional_title }}</span>
                      </div>
                      <el-icon class="remove-btn" @click="togglePerson(person)"><Close /></el-icon>
                    </div>
                  </TransitionGroup>
                  <el-empty v-if="selectedPersons.length === 0" description="请从左侧点击选择参会人员" :image-size="60" />
                </el-scrollbar>
              </div>
            </div>

            <!-- 冲突检测区 -->
            <div v-if="conflicts.length > 0" class="conflict-alert">
              <el-alert title="⚠️ 参会时间冲突提示" type="warning" :closable="false" show-icon>
                <div v-for="c in conflicts" :key="c.user_id" class="conflict-item">
                  <strong>{{ c.user_name }}</strong> 与「{{ c.conflict_meeting }}」时间冲突
                  <span class="conflict-time">({{ c.conflict_time }})</span>
                </div>
              </el-alert>
            </div>

            <!-- 底部导航 -->
            <div class="persons-footer">
              <span class="persons-selected-hint">已选 {{ form.participant_ids.length }} 人 · 可继续添加</span>
              <div class="persons-footer-btns">
                <el-button @click="activeTab = 'info'">
                  <el-icon><ArrowLeft /></el-icon> 上一步
                </el-button>
                <el-button type="primary" @click="goNext('seats')">
                  下一步：座位排布 <el-icon><Right /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- ==================== Tab 3: 座位排布 ==================== -->
        <div v-show="activeTab === 'seats'" class="tab-panel">
          <div class="panel-inner">
            <h3 class="panel-title">
              <el-icon color="#E6A23C"><Grid /></el-icon>座位排布
              <span class="optional-badge">选填</span>
            </h3>
            <p class="section-desc">选择会议室后，将左侧人员拖到右侧座位上。会议端进入后将显示特定座位上所安排人员的姓名。</p>

            <div v-if="!currentRoomLayout" class="seat-empty-hint">
              <el-icon style="font-size:40px;color:#c0c4cc"><Warning /></el-icon>
              <p>该会议室暂无预设座位布局</p>
            </div>

            <div v-else class="seat-editor">
              <!-- 左侧：参会人员列表 -->
              <div class="seat-sidebar">
                <div class="seat-sidebar-title">
                  <el-icon style="color:#2bffbc;font-size:13px"><User /></el-icon>
                  <span>参会人员</span>
                  <span class="seat-assign-count">{{ seatAssignments.filter(s => s.userId).length }} / {{ form.participant_ids.length }} 已分配</span>
                </div>
                <div class="seat-sidebar-hint">← 拖拽或点击人员，再选择座位</div>
                <el-scrollbar height="420px">
                  <div
                    v-for="p in selectedPersons"
                    :key="p.id"
                    class="drag-person"
                    :class="{ 'is-assigned': seatAssignments.some(s => s.userId === p.id) }"
                    draggable="true"
                    @dragstart="onSeatDragStart($event, p)"
                  >
                    <span class="drag-avatar">{{ p.real_name?.charAt(0) }}</span>
                    <div class="drag-info">
                      <span class="drag-name">{{ p.real_name }}</span>
                      <span class="drag-sub">{{ [p.department || p.affiliation, p.professional_title].filter(Boolean).join('·') }}</span>
                    </div>
                    <span v-if="seatAssignments.some(s => s.userId === p.id)" class="drag-seat-badge">{{ seatAssignments.find(s => s.userId === p.id)?.label }}</span>
                    <el-icon v-else class="drag-handle"><Rank /></el-icon>
                  </div>
                  <div v-if="selectedPersons.length === 0" class="drag-empty">暂无参会人员</div>
                </el-scrollbar>
              </div>

              <!-- 右侧：俯视图 -->
              <div class="seat-map-wrap" ref="seatMapWrapRef">
                <div class="seat-map-header">
                  <span class="seat-map-room-name">
                    <el-icon style="color:#f24b55"><Location /></el-icon>
                    {{ form.location }}
                  </span>
                  <div class="seat-map-header-right">
                    <span class="seat-legend"><span class="seat-legend-dot seat-vacant-dot"></span>空闲</span>
                    <span class="seat-legend"><span class="seat-legend-dot seat-assigned-dot"></span>已分配</span>
                    <span class="seat-legend seat-drag-legend">拖入中</span>
                    <button class="seat-clear-btn" @click="clearAllSeats">⚠ 清空座位</button>
                  </div>
                </div>
                <div class="seat-map-scaler" :style="seatMapScalerStyle">
                  <div
                    class="seat-map"
                    :style="{ width: currentRoomLayout.roomWidth + 'px', height: currentRoomLayout.roomHeight + 'px' }"
                  >
                  <!-- 大屏幕标识 -->
                  <div
                    v-if="currentRoomLayout.screen"
                    class="map-screen"
                    :style="{ left: currentRoomLayout.screen.x + 'px', top: currentRoomLayout.screen.y + 'px', width: currentRoomLayout.screen.w + 'px', height: currentRoomLayout.screen.h + 'px' }"
                  >大屏幕</div>
                  <!-- 会议区 -->
                  <div
                    v-for="(t, ti) in currentRoomLayout.tables"
                    :key="'t'+ti"
                    class="map-table"
                    :style="{ left: t.x + 'px', top: t.y + 'px', width: t.w + 'px', height: t.h + 'px', borderRadius: (t.rx||0) + 'px' }"
                  >
                    {{ t.label }}
                  </div>
                  <!-- 座位 -->
                  <div
                    v-for="seat in seatAssignments"
                    :key="seat.id"
                    class="map-seat"
                    :class="{ occupied: !!seat.userId }"
                    :style="{ left: (seat.x - 32) + 'px', top: (seat.y - 32) + 'px' }"
                    @dragover.prevent
                    @drop="onSeatDrop($event, seat)"
                    @click="removeSeatPerson(seat)"
                  >
                    <div class="seat-num">{{ seat.label }}</div>
                    <div v-if="seat.userId" class="seat-person-name">{{ seat.userName }}</div>
                    <div v-else class="seat-vacant">空位</div>
                  </div>
                </div>
                </div>
              </div>
            </div>

            <div class="panel-actions">
              <el-button @click="activeTab = 'persons'">
                <el-icon><ArrowLeft /></el-icon> 上一步
              </el-button>
              <el-button type="primary" @click="goNext('materials')">
                下一步：会议材料 <el-icon><Right /></el-icon>
              </el-button>
            </div>
          </div>
        </div>

        <!-- ==================== Tab 4: 会议材料 & 签到表 ==================== -->
        <div v-show="activeTab === 'materials'" class="tab-panel">
          <div class="panel-inner">
            <h3 class="panel-title">
              <el-icon color="#E6A23C"><Document /></el-icon>会议材料与签到表
              <span class="optional-badge">选填</span>
            </h3>

            <!-- 文件上传 -->
            <div class="material-section">
              <h4 class="section-subtitle">📁 上传会议材料</h4>
              <!-- 会议类型材料提示 -->
              <div v-if="materialHints.length > 0" class="material-type-hint">
                <el-icon style="color:#e6a23c;margin-right:6px;flex-shrink:0"><InfoFilled /></el-icon>
                <span>建议上传（{{ meetingTypeLabel }}）：</span>
                <span v-for="(hint, i) in materialHints" :key="i" class="hint-tag">{{ hint }}</span>
              </div>
              <el-upload
                drag
                multiple
                action="#"
                :auto-upload="false"
                v-model:file-list="fileList"
                class="file-upload"
              >
                <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
                <template #tip>
                  <div class="el-upload__tip">支持 PDF、Word、PPT、图片等格式，单文件不超过 50MB</div>
                </template>
              </el-upload>
              <div v-if="fileList.length > 0" class="perm-block">
                <!-- 标题行 -->
                <div class="perm-header">
                  <div class="perm-header-left">
                    <el-icon class="perm-header-icon"><InfoFilled /></el-icon>
                    <span class="perm-header-title">文档查看权限</span>
                    <span class="perm-header-desc">留空 = 所有参会人员可看；指定人员后仅限所选人员查看</span>
                  </div>
                </div>

                <!-- 批量设置行 -->
                <div v-if="fileList.length > 1" class="perm-batch-row">
                  <span class="perm-batch-label">批量应用：</span>
                  <el-select
                    v-model="batchPermUserIds"
                    multiple
                    collapse-tags
                    :max-collapse-tags="3"
                    filterable
                    clearable
                    placeholder="选择人员后点击「应用到所有文件」"
                    class="perm-batch-select"
                  >
                    <el-option-group label="专家">
                      <el-option
                        v-for="person in selectedExperts"
                        :key="`batch-e-${person.id}`"
                        :label="`${person.real_name}${person.department ? ' · ' + person.department : ''}`"
                        :value="person.id"
                      />
                    </el-option-group>
                    <el-option-group label="其他人员">
                      <el-option
                        v-for="person in selectedOthers"
                        :key="`batch-o-${person.id}`"
                        :label="`${person.real_name}${person.department ? ' · ' + person.department : ''}`"
                        :value="person.id"
                      />
                    </el-option-group>
                  </el-select>
                  <button class="perm-apply-btn" @click="applyBatchPermissions">应用到所有文件</button>
                  <button class="perm-clear-all-btn" @click="clearAllPermissions">全部清空</button>
                </div>

                <!-- 每个文件的权限行 -->
                <div class="perm-file-list">
                  <div v-for="file in fileList" :key="file.uid || file.name" class="perm-file-row">
                    <div class="perm-file-info">
                      <el-icon class="perm-file-icon"><Document /></el-icon>
                      <span class="perm-file-name">{{ file.name }}</span>
                      <span v-if="!file.allowedUserIds || file.allowedUserIds.length === 0" class="perm-file-badge perm-badge-all">全员可见</span>
                      <span v-else class="perm-file-badge perm-badge-limited">{{ file.allowedUserIds.length }} 人</span>
                    </div>
                    <div class="perm-file-selector">
                      <el-select
                        v-model="file.allowedUserIds"
                        multiple
                        collapse-tags
                        :max-collapse-tags="4"
                        collapse-tags-tooltip
                        filterable
                        clearable
                        placeholder="全员可见（点击限制查看人员）"
                        class="perm-select"
                      >
                        <el-option-group label="专家">
                          <el-option
                            v-for="person in selectedExperts"
                            :key="`${file.uid || file.name}-e-${person.id}`"
                            :label="`${person.real_name}${person.department ? ' · ' + person.department : ''}`"
                            :value="person.id"
                          />
                        </el-option-group>
                        <el-option-group label="其他人员">
                          <el-option
                            v-for="person in selectedOthers"
                            :key="`${file.uid || file.name}-o-${person.id}`"
                            :label="`${person.real_name}${person.department ? ' · ' + person.department : ''}`"
                            :value="person.id"
                          />
                        </el-option-group>
                      </el-select>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 分割线 -->
            <div class="section-divider">
              <span class="divider-dot"></span>
              <span class="divider-line"></span>
              <span class="divider-dot"></span>
            </div>

            <!-- 签到表区 -->
            <div class="material-section">
              <h4 class="section-subtitle">📋 生成签到表</h4>
              <p class="section-desc">根据已选参会人员自动生成三类签到表（专家签到、其他人员签到、评审费签收），支持编辑和导出 PDF 打印</p>
              <div class="checkin-actions">
                <el-button plain style="margin-right:8px" @click="templateDialogVisible = true">
                  <el-icon><Document /></el-icon>选择模板
                  <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <el-button type="success" plain :loading="generating.checkin" @click="handleGenerateCheckin">
                  <el-icon><Tickets /></el-icon>生成签到表
                </el-button>
                <template v-if="checkinExpertRows.length > 0 || checkinOtherRows.length > 0">
                  <el-button :type="checkinEditMode ? 'warning' : 'info'" plain @click="checkinEditMode = !checkinEditMode">
                    <el-icon><Edit /></el-icon>{{ checkinEditMode ? '完成编辑' : '编辑' }}
                  </el-button>
                  <el-button type="primary" plain @click="handleExportCheckinPdf">
                    <el-icon><Printer /></el-icon>导出 PDF
                  </el-button>
                </template>
              </div>

              <!-- 专家签到表 -->
              <div v-if="checkinExpertRows.length > 0" class="checkin-table-wrap">
                <div class="checkin-table-title">一、专家签到表</div>
                <table class="checkin-edit-table">
                  <thead>
                    <tr>
                      <th style="width:60px">序号</th>
                      <th style="width:140px">姓名</th>
                      <th style="width:160px">单位</th>
                      <th style="width:120px">职称</th>
                      <th>签到时间</th>
                      <th>签名</th>
                      <th v-if="checkinEditMode" style="width:96px">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, idx) in checkinExpertRows" :key="row._id">
                      <td class="cell-center">{{ idx + 1 }}</td>
                      <td>
                        <input v-if="checkinEditMode" v-model="row.name" class="cell-input" placeholder="姓名" />
                        <span v-else class="cell-text">{{ row.name || '　' }}</span>
                      </td>
                      <td>
                        <input v-if="checkinEditMode" v-model="row.dept" class="cell-input" placeholder="单位" />
                        <span v-else class="cell-text">{{ row.dept || '　' }}</span>
                      </td>
                      <td>
                        <input v-if="checkinEditMode" v-model="row.title" class="cell-input" placeholder="职称" />
                        <span v-else class="cell-text">{{ row.title || '　' }}</span>
                      </td>
                      <td>
                        <input v-if="checkinEditMode" v-model="row.time" class="cell-input" placeholder="签到时间" />
                        <span v-else class="cell-text">{{ row.time || '　' }}</span>
                      </td>
                      <td>
                        <input v-if="checkinEditMode" v-model="row.sign" class="cell-input" placeholder="" />
                        <span v-else class="cell-text">{{ row.sign || '　' }}</span>
                      </td>
                      <td v-if="checkinEditMode" class="cell-ops">
                        <el-button size="small" :disabled="idx === 0" @click="moveExpertRowUp(idx)">上</el-button>
                        <el-button size="small" :disabled="idx === checkinExpertRows.length - 1" @click="moveExpertRowDown(idx)">下</el-button>
                        <el-button size="small" type="danger" plain @click="removeExpertRow(idx)">删</el-button>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <div v-if="checkinEditMode" class="checkin-add-row">
                  <el-button size="small" type="primary" plain @click="addExpertRow">+ 新增行</el-button>
                </div>
              </div>

              <!-- 其他人员签到表 -->
              <div v-if="checkinOtherRows.length > 0" class="checkin-table-wrap" style="margin-top:16px">
                <div class="checkin-table-title">二、其他人员签到表</div>
                <table class="checkin-edit-table">
                  <thead>
                    <tr>
                      <th style="width:60px">序号</th>
                      <th style="width:140px">姓名</th>
                      <th style="width:160px">单位</th>
                      <th>签到时间</th>
                      <th>签名</th>
                      <th v-if="checkinEditMode" style="width:96px">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, idx) in checkinOtherRows" :key="row._id">
                      <td class="cell-center">{{ idx + 1 }}</td>
                      <td>
                        <input v-if="checkinEditMode" v-model="row.name" class="cell-input" placeholder="姓名" />
                        <span v-else class="cell-text">{{ row.name || '　' }}</span>
                      </td>
                      <td>
                        <input v-if="checkinEditMode" v-model="row.dept" class="cell-input" placeholder="单位" />
                        <span v-else class="cell-text">{{ row.dept || '　' }}</span>
                      </td>
                      <td>
                        <input v-if="checkinEditMode" v-model="row.time" class="cell-input" placeholder="签到时间" />
                        <span v-else class="cell-text">{{ row.time || '　' }}</span>
                      </td>
                      <td>
                        <input v-if="checkinEditMode" v-model="row.sign" class="cell-input" placeholder="" />
                        <span v-else class="cell-text">{{ row.sign || '　' }}</span>
                      </td>
                      <td v-if="checkinEditMode" class="cell-ops">
                        <el-button size="small" :disabled="idx === 0" @click="moveOtherRowUp(idx)">上</el-button>
                        <el-button size="small" :disabled="idx === checkinOtherRows.length - 1" @click="moveOtherRowDown(idx)">下</el-button>
                        <el-button size="small" type="danger" plain @click="removeOtherRow(idx)">删</el-button>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <div v-if="checkinEditMode" class="checkin-add-row">
                  <el-button size="small" type="primary" plain @click="addOtherRow">+ 新增行</el-button>
                </div>
              </div>

              <!-- 评审费签收表 -->
              <div v-if="checkinExpertRows.length > 0" class="checkin-table-wrap" style="margin-top:16px">
                <div class="checkin-table-title">三、评审费签收表</div>
                <table class="checkin-edit-table">
                  <thead>
                    <tr>
                      <th style="width:50px">序号</th>
                      <th style="width:120px">姓名</th>
                      <th style="width:150px">身份证号</th>
                      <th style="width:150px">银行卡号</th>
                      <th style="width:120px">单位</th>
                      <th style="width:100px">职称</th>
                      <th style="width:80px">金额</th>
                      <th>签名</th>
                      <th v-if="checkinEditMode" style="width:96px">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, idx) in checkinExpertRows" :key="'fee-'+row._id">
                      <td class="cell-center">{{ idx + 1 }}</td>
                      <td>
                        <input v-if="checkinEditMode" v-model="row.name" class="cell-input" placeholder="姓名" />
                        <span v-else class="cell-text">{{ row.name || '　' }}</span>
                      </td>
                      <td>
                        <input v-if="checkinEditMode" v-model="row.idCard" class="cell-input" placeholder="身份证号" />
                        <span v-else class="cell-text">{{ row.idCard || '　' }}</span>
                      </td>
                      <td>
                        <input v-if="checkinEditMode" v-model="row.bankCard" class="cell-input" placeholder="银行卡号" />
                        <span v-else class="cell-text">{{ row.bankCard || '　' }}</span>
                      </td>
                      <td>
                        <input v-if="checkinEditMode" v-model="row.dept" class="cell-input" placeholder="单位" />
                        <span v-else class="cell-text">{{ row.dept || '　' }}</span>
                      </td>
                      <td>
                        <input v-if="checkinEditMode" v-model="row.title" class="cell-input" placeholder="职称" />
                        <span v-else class="cell-text">{{ row.title || '　' }}</span>
                      </td>
                      <td>
                        <input v-if="checkinEditMode" v-model="row.fee" class="cell-input" placeholder="金额" />
                        <span v-else class="cell-text">{{ row.fee || '　' }}</span>
                      </td>
                      <td>
                        <input v-if="checkinEditMode" v-model="row.sign" class="cell-input" placeholder="" />
                        <span v-else class="cell-text">{{ row.sign || '　' }}</span>
                      </td>
                      <td v-if="checkinEditMode" class="cell-ops">
                        <el-button size="small" :disabled="idx === 0" @click="moveExpertRowUp(idx)">上</el-button>
                        <el-button size="small" :disabled="idx === checkinExpertRows.length - 1" @click="moveExpertRowDown(idx)">下</el-button>
                        <el-button size="small" type="danger" plain @click="removeExpertRow(idx)">删</el-button>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <div v-if="checkinEditMode" class="checkin-add-row">
                  <el-button size="small" type="primary" plain @click="addExpertRow">+ 新增行</el-button>
                </div>
              </div>
            </div>

            <div class="panel-actions">
              <el-button @click="activeTab = 'seats'">
                <el-icon><ArrowLeft /></el-icon> 上一步
              </el-button>
              <el-button type="primary" @click="goNext('agenda')">
                下一步：生成议程 <el-icon><Right /></el-icon>
              </el-button>
            </div>
          </div>
        </div>

        <!-- ==================== Tab 3: AI 智能议程（对话编辑器）==================== -->
        <div v-show="activeTab === 'agenda'" class="tab-panel">
          <div class="agenda-chat-layout">
            <!-- 左侧：AI 对话面板 -->
            <div class="chat-panel">
              <div class="chat-header">
                <div class="chat-header-left">
                  <span class="chat-header-icon">🤖</span>
                  <span class="chat-header-title">AI 对话</span>
                </div>
                <el-tag size="small" type="info" effect="plain" round>对话改写议程</el-tag>
              </div>

              <div class="chat-messages" ref="chatMessagesRef">
                <!-- 欢迎消息 -->
                <div class="chat-welcome">
                  <div class="welcome-avatar">🤖</div>
                  <div class="welcome-bubble">
                    <p>你好！我是智能会议助手。</p>
                    <p>描述需求即可生成议程，也可以随时对话修改已有内容。</p>
                  </div>
                </div>

                <!-- 快捷操作（仅首次显示） -->
                <div v-if="chatMessages.length === 0" class="chat-quick-actions">
                  <button class="quick-btn" @click="quickSend('请根据会议信息生成一份专业的会议议程')">
                    <span class="quick-icon">🤖</span>自动生成议程
                  </button>
                  <button class="quick-btn" @click="quickSend('请生成包含开场致辞、工作汇报、讨论环节、总结的详细议程')">
                    <span class="quick-icon">📋</span>详细议程
                  </button>
                  <button class="quick-btn" @click="quickSend('请生成一个简洁的议程，只包含核心环节')">
                    <span class="quick-icon">📝</span>简洁议程
                  </button>
                </div>

                <!-- 对话消息列表 -->
                <template v-for="(msg, i) in chatMessages" :key="i">
                  <div class="chat-msg" :class="msg.role">
                    <div class="msg-avatar">
                      <template v-if="msg.role === 'user'">👤</template>
                      <template v-else>🤖</template>
                    </div>
                    <div class="msg-bubble">
                      <div class="msg-content" v-text="msg.content"></div>
                      <span v-if="msg.role === 'assistant' && generating.agenda && i === chatMessages.length - 1 && msg.content" class="typing-dot">•</span>
                      <div v-if="msg.role === 'assistant' && generating.agenda && i === chatMessages.length - 1 && !msg.content" class="msg-loading">
                        <el-icon class="is-loading"><Loading /></el-icon> 思考中...
                      </div>
                    </div>
                  </div>
                </template>
              </div>

              <!-- 输入区域 -->
              <div class="chat-input-area">
                <div class="input-wrapper">
                  <el-input
                    v-model="chatInput"
                    type="textarea"
                    :rows="2"
                    :placeholder="chatMessages.length === 0 ? '描述您的议程需求..' : '继续对话修改议程...'"
                    resize="none"
                    :disabled="generating.agenda"
                    @keydown.enter.ctrl.prevent="sendChatMessage"
                  />
                </div>
                <div class="input-footer">
                  <span class="input-hint">Ctrl + Enter 发送</span>
                  <div class="input-btns">
                    <el-button v-if="generating.agenda" @click="stopGeneration" type="danger" size="small" round plain>
                      <el-icon><VideoPause /></el-icon>停止
                    </el-button>
                    <el-button type="primary" size="small" :loading="generating.agenda" :disabled="generating.agenda" @click="sendChatMessage" round>
                      <el-icon><Position /></el-icon>发送
                    </el-button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 右侧：议程编辑器面板 -->
            <div class="editor-panel">
              <div class="editor-header">
                <div class="editor-header-left">
                  <span class="editor-header-icon">📝</span>
                  <span class="editor-header-title">会议议程</span>
                  <el-tag v-if="generating.agenda" type="danger" size="small" effect="dark" round style="margin-left:8px">
                    <el-icon class="is-loading" style="margin-right:2px"><Loading /></el-icon>生成中
                  </el-tag>
                  <el-tag v-else-if="agendaContent" type="success" size="small" effect="plain" round style="margin-left:8px">✅ 已生成</el-tag>
                </div>
                <div class="editor-header-right">
                  <el-dropdown @command="applyAgendaTemplate" trigger="click">
                    <el-button size="small" plain>
                      <el-icon><Document /></el-icon>选择模板
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="regular">例会议程</el-dropdown-item>
                        <el-dropdown-item command="review">评审会议议程</el-dropdown-item>
                        <el-dropdown-item command="special">专题研讨议程</el-dropdown-item>
                        <el-dropdown-item command="decision">决策会议议程</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                  <template v-if="agendaContent && !generating.agenda">
                    <el-button-group size="small">
                      <el-button :type="agendaViewMode === 'preview' ? 'primary' : ''" @click="agendaViewMode = 'preview'">
                        <el-icon><Document /></el-icon>预览
                      </el-button>
                      <el-button :type="agendaViewMode === 'source' ? 'primary' : ''" @click="agendaViewMode = 'source'">
                        <el-icon><Edit /></el-icon>编辑
                      </el-button>
                    </el-button-group>
                    <el-button text type="primary" size="small" @click="handleExportWord">
                      <el-icon><Download /></el-icon>导出Word
                    </el-button>
                    <el-button text type="danger" size="small" @click="clearAgenda">
                      <el-icon><Delete /></el-icon>清空
                    </el-button>
                  </template>
                </div>
              </div>

              <div class="editor-body" ref="agendaPreviewRef">
                <!-- 空状态 -->
                <div v-if="!agendaContent && !generating.agenda" class="editor-empty">
                  <div class="empty-icon">📝</div>
                  <p class="empty-main">议程内容将在此展示</p>
                  <p class="empty-sub">在左侧对话框中发送需求，AI 将自动生成议程</p>
                </div>
                <!-- 预览模式 / 生成中 -->
                <div v-else-if="agendaViewMode === 'preview' || generating.agenda" class="editor-preview">
                  <div class="rendered-html" v-html="renderedAgendaHtml"></div>
                  <span v-if="generating.agenda && agendaContent" class="typing-cursor">|</span>
                  <div v-if="!agendaContent && generating.agenda" class="gen-placeholder">
                    <el-icon class="is-loading"><Loading /></el-icon>
                    <span>AI 正在生成议程...</span>
                  </div>
                </div>
                <!-- 源文本编辑模式 -->
                <textarea v-else class="raw-editor" v-model="agendaContent" placeholder="直接编辑议程文本..." spellcheck="false"></textarea>
              </div>
            </div>
          </div>

          <div class="panel-actions" style="margin-top:16px;padding-top:16px;border-top:1px solid rgba(0,212,255,0.2);">
            <el-button @click="activeTab = 'materials'">
              <el-icon><ArrowLeft /></el-icon> 上一步
            </el-button>
            <el-button type="primary" :loading="submitting" @click="handleSubmit">
              <el-icon><Check /></el-icon>{{ isEdit ? '保存修改' : '创建会议' }}
            </el-button>
          </div>
        </div>

      </div>

      <!-- 右侧摘要卡片 -->
      <div class="sidebar">
        <el-affix :offset="80">
          <div class="summary-card">
            <div class="summary-header">会议概览</div>
            <div class="summary-body">
              <div class="s-row"><span class="s-label">名称</span><span class="s-value">{{ form.title || '　' }}</span></div>
              <div class="s-row"><span class="s-label">类型</span><el-tag size="small" :type="typeTagType">{{ meetingTypeLabel }}</el-tag></div>
              <div class="s-row"><span class="s-label">日期</span><span class="s-value">{{ form.startDate || '　' }}</span></div>
              <div class="s-row"><span class="s-label">时间</span><span class="s-value">{{ timeRangeLabel }}</span></div>
              <div class="s-row"><span class="s-label">时长</span><span class="s-value">{{ durationText || '　' }}</span></div>
              <div class="s-row"><span class="s-label">地点</span><span class="s-value">{{ form.location || '　' }}</span></div>
              <div class="s-row"><span class="s-label">参会人数</span><span class="s-value s-highlight">{{ form.participant_ids.length }} 人</span></div>
              <div class="s-row"><span class="s-label">附件</span><span class="s-value">{{ fileList.length }} 个</span></div>
              <div class="s-row"><span class="s-label">议程</span><span class="s-value" :class="{ 's-highlight': agendaContent }">{{ agendaContent ? '✅ 已生成' : '未生成' }}</span></div>
            </div>
            <el-button type="primary" :loading="submitting" @click="handleSubmit" style="width: 100%; margin-top: 16px; border-radius: 8px;">
              <el-icon><Check /></el-icon>{{ isEdit ? '保存修改' : '创建会议' }}
            </el-button>
          </div>
        </el-affix>
      </div>
    </div>

    <!-- 新建人员对话框 -->
    <el-dialog v-model="addPersonVisible" title="新建参会人员" width="460px" :close-on-click-modal="false">
      <el-form ref="personFormRef" :model="personForm" :rules="personRules" label-width="80px">
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="personForm.real_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="单位" prop="department">
          <el-input v-model="personForm.department" placeholder="如：XX公司、XX处室" />
        </el-form-item>
        <el-form-item label="职位">
          <el-input v-model="personForm.position" placeholder="选填" />
        </el-form-item>
        <el-form-item label="职称">
          <el-input v-model="personForm.professional_title" placeholder="如：高级工程师、教授" />
        </el-form-item>
        <el-form-item label="身份证号">
          <el-input v-model="personForm.id_card_number" placeholder="用于评审费签收" />
        </el-form-item>
        <el-form-item label="是否专家">
          <el-switch v-model="personForm.is_expert" active-text="专家" inactive-text="其他人员" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="personForm.phone" placeholder="选填" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="personForm.email" placeholder="选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addPersonVisible = false">取消</el-button>
        <el-button type="primary" :loading="addingPerson" @click="handleAddPerson">确定创建</el-button>
      </template>
    </el-dialog>

    <!-- 签到表模板选择对话框 -->
    <el-dialog v-model="templateDialogVisible" title="选择签到表模板" width="620px" :close-on-click-modal="false">
      <p style="color:#909399;font-size:14px;margin-bottom:16px">点击模板可预览字段，勾选后点击确认生成</p>
      <div class="template-option-list">
        <div
          v-for="tpl in checkinTemplateOptions"
          :key="tpl.key"
          class="template-option-item"
          :class="{ 'is-selected': selectedTemplateKeys.includes(tpl.key), 'is-previewing': previewTemplateKey === tpl.key }"
          @click="previewTemplateKey = tpl.key"
        >
          <el-checkbox
            :model-value="selectedTemplateKeys.includes(tpl.key)"
            @click.stop
            @change="toggleTemplateKey(tpl.key)"
            style="margin-right:10px"
          />
          <div class="tpl-info">
            <div class="tpl-name">{{ tpl.name }}</div>
            <div class="tpl-cols">字段：{{ tpl.cols.join('、') }}</div>
          </div>
        </div>
      </div>
      <!-- 模板预览区 -->
      <div v-if="previewTemplateKey" class="tpl-preview-wrap">
        <div class="tpl-preview-title">预览：{{ checkinTemplateOptions.find(t => t.key === previewTemplateKey)?.name }}</div>
        <table class="tpl-preview-table">
          <thead>
            <tr>
              <th v-for="col in checkinTemplateOptions.find(t => t.key === previewTemplateKey)?.cols" :key="col">{{ col }}</th>
            </tr>
          </thead>
          <tbody>
            <tr class="tpl-preview-row">
              <td v-for="col in checkinTemplateOptions.find(t => t.key === previewTemplateKey)?.cols" :key="col">
                <span v-if="col === '序号'">1</span>
                <span v-else-if="col === '姓名'">张三</span>
                <span v-else-if="col === '单位'">示例单位</span>
                <span v-else-if="col === '职称'">高级工程师</span>
                <span v-else-if="col === '身份证号'">3504**********0000</span>
                <span v-else-if="col === '签到时间'">09:00</span>
                <span v-else-if="col === '金额'">500</span>
                <span v-else class="tpl-sign-placeholder">（签名区）</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <template #footer>
        <el-button @click="templateDialogVisible = false">取消</el-button>
        <el-button type="primary" :disabled="selectedTemplateKeys.length === 0" @click="applySelectedTemplates">
          确认生成
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onActivated, onBeforeUnmount, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'

defineOptions({ name: 'MeetingCreate' })
import {
  createMeeting,
  updateMeeting,
  getMeetingById,
  checkConflicts,
  aiQA,
  getUserList,
  uploadAttachment,
  checkRoomConflict,
  updateAttachmentPermissions,
} from '@/api/meeting'
import { createParticipant, deleteParticipant } from '@/api/auth'
import { getRoomListPublic } from '@/api/room'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, ArrowRight, ArrowDown, Check, Right, Timer, Plus, Close, Location, Loading, OfficeBuilding, Download, UploadFilled, Tickets, Document, Edit, User, MagicStick, VideoPause, Delete, Printer, Grid, Position, Warning, Rank, InfoFilled } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { asBlob } from 'html-docx-js-typescript'
import { saveAs } from 'file-saver'
import draggable from 'vuedraggable'

const router = useRouter()
const route = useRoute()
const isEdit = computed(() => !!route.params.id)

// ======= 状态 =======
const submitting = ref(false)
const basicFormRef = ref(null)
const personSearch = ref('')
const conflicts = ref([])

// ===== 外部系统冲突检测（前端模拟） =====
// 模拟外部系统数据：陈东明 每天 18:00-20:00 有政务外联例会
const MOCK_EXTERNAL_BUSY = {
  chen_dongming: {
    schedule: [
      { startHour: 18, startMin: 0, endHour: 20, endMin: 0, task: '政务外联例会（外部系统）' }
    ]
  }
}

/**
 * 获取某用户与当前会议时间段冲突的外部任务信息
 * @param {Object} user - 用户对象（含 username 字段）
 * @returns {{ task: string, timeRange: string } | null}
 */
function getExternalBusyInfo(user) {
  if (!user?.username) return null
  const schedule = MOCK_EXTERNAL_BUSY[user.username]
  if (!schedule) return null
  if (!form.startTime || !form.endTime) return null
  const startDt = new Date(form.startTime)
  const endDt = new Date(form.endTime)
  if (isNaN(startDt) || isNaN(endDt)) return null
  const meetingStart = startDt.getHours() * 60 + startDt.getMinutes()
  const meetingEnd = endDt.getHours() * 60 + endDt.getMinutes()
  for (const slot of schedule.schedule) {
    const slotStart = slot.startHour * 60 + slot.startMin
    const slotEnd = slot.endHour * 60 + slot.endMin
    if (slotStart < meetingEnd && slotEnd > meetingStart) {
      const pad = n => String(n).padStart(2, '0')
      return {
        task: slot.task,
        timeRange: `${pad(slot.startHour)}:${pad(slot.startMin)}-${pad(slot.endHour)}:${pad(slot.endMin)}`
      }
    }
  }
  return null
}

/** 判断某用户是否与当前会议时间存在外部任务冲突 */
function isExternalBusy(user) {
  return !!getExternalBusyInfo(user)
}
const fileList = ref([])
const batchPermUserIds = ref([])

function applyBatchPermissions() {
  fileList.value.forEach(f => {
    f.allowedUserIds = [...batchPermUserIds.value]
  })
}

function clearAllPermissions() {
  fileList.value.forEach(f => {
    f.allowedUserIds = []
  })
  batchPermUserIds.value = []
}
const generatedContent = ref('')
const checkinExpertRows = ref([])
const checkinOtherRows = ref([])
let _checkinIdCounter = 0
const checkinEditMode = ref(false)
const generating = reactive({ agenda: false, checkin: false })

// 签到表行管理
function addExpertRow() {
  checkinExpertRows.value.push({ _id: ++_checkinIdCounter, name: '', dept: '', title: '', idCard: '', bankCard: '', fee: '', time: '', sign: '' })
}
function removeExpertRow(idx) { checkinExpertRows.value.splice(idx, 1) }
function moveExpertRowUp(idx) {
  if (idx === 0) return
  const arr = checkinExpertRows.value
  ;[arr[idx - 1], arr[idx]] = [arr[idx], arr[idx - 1]]
}
function moveExpertRowDown(idx) {
  const arr = checkinExpertRows.value
  if (idx === arr.length - 1) return
  ;[arr[idx], arr[idx + 1]] = [arr[idx + 1], arr[idx]]
}
function addOtherRow() {
  checkinOtherRows.value.push({ _id: ++_checkinIdCounter, name: '', dept: '', time: '', sign: '' })
}
function removeOtherRow(idx) { checkinOtherRows.value.splice(idx, 1) }
function moveOtherRowUp(idx) {
  if (idx === 0) return
  const arr = checkinOtherRows.value
  ;[arr[idx - 1], arr[idx]] = [arr[idx], arr[idx - 1]]
}
function moveOtherRowDown(idx) {
  const arr = checkinOtherRows.value
  if (idx === arr.length - 1) return
  ;[arr[idx], arr[idx + 1]] = [arr[idx + 1], arr[idx]]
}

// ======= 会议室列表（从后端动态加载） =======
const availableRooms = ref([])
const roomLayoutMap = ref({})  // name -> { roomWidth, roomHeight, screen, tables, seats }
const roomConflicts = ref([])

async function fetchRooms() {
  try {
    const list = await getRoomListPublic()
    availableRooms.value = Array.isArray(list) ? list : (list?.data || [])
    // 构建 name -> layout 映射
    const map = {}
    for (const room of availableRooms.value) {
      let screen = null, tables = [], seats = []
      try { screen = room.screen_data ? JSON.parse(room.screen_data) : null } catch {}
      try { tables = room.tables_data ? JSON.parse(room.tables_data) : [] } catch {}
      try { seats = room.seats_data ? JSON.parse(room.seats_data) : [] } catch {}
      map[room.name] = { roomWidth: room.room_width, roomHeight: room.room_height, screen, tables, seats }
    }
    roomLayoutMap.value = map
    // 自动选择唯一会议室
    if (availableRooms.value.length > 0) {
      form.location = availableRooms.value[0].name
    }
  } catch (e) {
    console.error('获取会议室列表失败', e)
  }
}

async function checkRoomConflictAsync() {
  try {
    const startDt = combineDatetime(form.startDate, form.startTime)
    const endDt = combineDatetime(form.endDate || form.startDate, form.endTime)
    if (!startDt || !endDt) return
    const res = await checkRoomConflict({
      start_time: startDt,
      end_time: endDt,
      exclude_meeting_id: route.params.id || undefined,
    })
    roomConflicts.value = res || []
  } catch {}
}

const seatAssignments = ref([])
let dragPerson = null
const seatMapWrapRef = ref(null)
const seatMapScale = ref(1)

const currentRoomLayout = computed(() => {
  // 优先从 form.location 匹配，找不到则回退到第一个可用布局
  if (roomLayoutMap.value[form.location]) return roomLayoutMap.value[form.location]
  const firstKey = Object.keys(roomLayoutMap.value)[0]
  return firstKey ? roomLayoutMap.value[firstKey] : null
})

const seatMapScalerStyle = computed(() => {
  const s = seatMapScale.value
  const layout = currentRoomLayout.value
  if (!layout) return {}
  return {
    transform: `scale(${s})`,
    transformOrigin: 'top left',
    width: (layout.roomWidth * s) + 'px',
    height: (layout.roomHeight * s) + 'px',
  }
})

const unassignedParticipants = computed(() => {
  const assignedIds = new Set(seatAssignments.value.filter(s => s.userId).map(s => s.userId))
  return allUsers.value.filter(u => form.participant_ids.includes(u.id) && !assignedIds.has(u.id))
})

function initSeatLayout() {
  const layout = currentRoomLayout.value
  if (!layout) { seatAssignments.value = []; return }
  // Only preserve existing assignments when editing an existing meeting
  const prevMap = {}
  if (isEdit.value) {
    seatAssignments.value.forEach(s => { if (s.userId) prevMap[s.id] = { userId: s.userId, userName: s.userName } })
  }
  seatAssignments.value = layout.seats.map(s => ({
    id: s.id, label: s.label, x: s.x, y: s.y,
    userId: prevMap[s.id]?.userId || null,
    userName: prevMap[s.id]?.userName || '',
  }))
  // Auto-scale after DOM update
  nextTick(() => { updateSeatMapScale() })
}

function updateSeatMapScale() {
  const layout = currentRoomLayout.value
  const wrap = seatMapWrapRef.value
  if (!layout || !wrap) { seatMapScale.value = 1; return }
  const availW = wrap.clientWidth - 24  // minus some padding
  if (availW > 0 && layout.roomWidth > availW) {
    seatMapScale.value = Math.max(0.4, availW / layout.roomWidth)
  } else {
    seatMapScale.value = 1
  }
}

function onSeatDragStart(e, person) {
  dragPerson = person
  e.dataTransfer.effectAllowed = 'move'
}

function onSeatDrop(e, seat) {
  e.preventDefault()
  if (!dragPerson) return
  // Remove from any previous seat
  seatAssignments.value.forEach(s => { if (s.userId === dragPerson.id) { s.userId = null; s.userName = '' } })
  seat.userId = dragPerson.id
  seat.userName = dragPerson.real_name
  dragPerson = null
}

function removeSeatPerson(seat) {
  if (!seat.userId) return
  seat.userId = null
  seat.userName = ''
}

function clearAllSeats() {
  seatAssignments.value.forEach(s => { s.userId = null; s.userName = '' })
}

function buildSeatLayoutJson() {
  const layout = currentRoomLayout.value
  if (!layout || seatAssignments.value.length === 0) return null
  if (!seatAssignments.value.some(s => s.userId)) return null
  return JSON.stringify({
    room: form.location,
    roomWidth: layout.roomWidth,
    roomHeight: layout.roomHeight,
    tables: layout.tables,
    seats: seatAssignments.value.map(s => ({
      id: s.id, label: s.label, x: s.x, y: s.y,
      userId: s.userId, userName: s.userName,
    })),
  })
}

const loadingUsers = ref(false)
const allUsers = ref([])
const activeDuration = ref(null)
const agendaContent = ref('')
const agendaViewMode = ref('preview')
const agendaPreviewRef = ref(null)
const chatMessages = ref([])
const chatInput = ref('')
const chatMessagesRef = ref(null)
const collapsedDepts = reactive({})
let abortController = null

const renderedAgendaHtml = computed(() => {
  if (!agendaContent.value) return ''
  return agendaTextToHtml(agendaContent.value)
})

// Tab / Step
const activeTab = ref('info')
const steps = [
  { name: 'info', label: '基本信息' },
  { name: 'persons', label: '选择人员' },
  { name: 'seats', label: '座位排布' },
  { name: 'materials', label: '材料与签到表' },
  { name: 'agenda', label: '智能议程' },
]

function isStepDone(name) {
  if (name === 'info') return !!(form.title && form.meeting_type && form.startDate && form.startTime && form.endTime)
  if (name === 'persons') return form.participant_ids.length > 0
  if (name === 'seats') return seatAssignments.value.some(s => s.userId)
  if (name === 'materials') return !!(fileList.value.length > 0 || generatedContent.value)
  if (name === 'agenda') return !!agendaContent.value
  return false
}

async function goNext(tabName) {
  if (tabName === 'persons' || tabName === 'seats' || tabName === 'materials') {
    const formValid = await basicFormRef.value?.validate().catch(() => false)
    if (!formValid) {
      ElMessage.warning('请完善基本信息（会议名称、类型、地点）')
      return
    }
    if (!form.startDate || !form.startTime || !form.endTime) {
      ElMessage.warning('请完整选择会议时间（日期、开始时间、结束时间）')
      return
    }
    if (tabName === 'seats') {
      initSeatLayout()
    }
  }
  if (tabName === 'agenda') {
    const formValid = await basicFormRef.value?.validate().catch(() => false)
    if (!formValid || !form.startDate || !form.startTime || !form.endTime) {
      activeTab.value = 'info'
      ElMessage.warning('请先完善第一步的基本信息')
      return
    }
  }
  activeTab.value = tabName
}

const form = reactive({
  title: '',
  meeting_type: 'regular',
  startDate: '',
  startTime: null,
  endDate: '',
  endTime: null,
  location: '',
  description: '',
  welcome_message: '',
  welcome_theme: 'aurora',
  participant_ids: [],
  leader_id: null,
  has_review_fee: false,
})

const basicRules = {
  title: [{ required: true, message: '请输入会议名称', trigger: 'blur' }],
  meeting_type: [{ required: true, message: '请选择会议类型', trigger: 'change' }],
}

// ======= 时间 =======
const dateShortcuts = [
  { text: '今天', value: new Date() },
  { text: '明天', value: () => { const d = new Date(); d.setDate(d.getDate() + 1); return d } },
  { text: '后天', value: () => { const d = new Date(); d.setDate(d.getDate() + 2); return d } },
  { text: '下周一', value: () => { const d = new Date(); d.setDate(d.getDate() + ((8 - d.getDay()) % 7 || 7)); return d } },
]

const durationOptions = [
  { label: '30分钟', value: 30 },
  { label: '1小时', value: 60 },
  { label: '1.5小时', value: 90 },
  { label: '2小时', value: 120 },
  { label: '3小时', value: 180 },
  { label: '半天', value: 240 },
]

function setDuration(minutes) {
  activeDuration.value = minutes
  if (!form.startTime) {
    const now = new Date()
    now.setHours(now.getHours() + 1, 0, 0, 0)
    form.startTime = now
  }
  if (!form.startDate) {
    form.startDate = dayjs().format('YYYY-MM-DD')
  }
  const start = new Date(form.startTime)
  const end = new Date(start.getTime() + minutes * 60 * 1000)
  form.endTime = end
  form.endDate = form.startDate
  if (end.getDate() !== start.getDate()) {
    form.endDate = dayjs(form.startDate).add(1, 'day').format('YYYY-MM-DD')
  }
}

const durationText = computed(() => {
  if (!form.startTime || !form.endTime) return ''
  const start = new Date(form.startTime)
  const end = new Date(form.endTime)
  const diff = (end - start) / 1000 / 60
  if (diff <= 0) return ''
  if (diff < 60) return `${diff}分钟`
  const h = Math.floor(diff / 60)
  const m = diff % 60
  return m > 0 ? `${h}小时${m}分钟` : `${h}小时`
})

const timeRangeLabel = computed(() => {
  if (!form.startTime || !form.endTime) return '未选择'
  const s = dayjs(form.startTime).format('HH:mm')
  const e = dayjs(form.endTime).format('HH:mm')
  return `${s} - ${e}`
})

// ======= 类型 =======
const typeMap = { regular: '例会', special: '专题会议', decision: '决策会议', review: '评审会议', other: '其他' }
const typeTagMap = { regular: 'info', special: 'warning', decision: 'danger', review: 'success', other: '' }
const meetingTypeLabel = computed(() => typeMap[form.meeting_type] || '未选择')
const typeTagType = computed(() => typeTagMap[form.meeting_type] || 'info')

const materialHints = computed(() => {
  const hintsMap = {
    regular: ['会议议程', '上次会议纪要', '工作报告材料'],
    special: ['专题研究方案', '相关调研数据', '背景资料文件'],
    decision: ['议案说明材料', '決策依据文件', '评估报告', '财务数据'],
    review: ['被评审项目方案', '设计图纸', '技术说明书', '相关计算书', '局面文件'],
  }
  return form.meeting_type ? (hintsMap[form.meeting_type] || []) : []
})

const welcomeThemeOptions = [
  { label: '流光蓝', value: 'aurora' },
  { label: '晨曦橙', value: 'sunrise' },
  { label: '峰会灰蓝', value: 'summit' },
  { label: '海岸青', value: 'harbor' },
]

// ======= 人员管理 =======
function groupByDept(users) {
  const map = {}
  users.forEach(u => {
    const dept = u.department || '未分配部门'
    if (!map[dept]) map[dept] = []
    map[dept].push(u)
  })
  return map
}

const registeredUsers = computed(() => allUsers.value.filter(u => !u.is_participant_only))
const participantOnlyUsers = computed(() => allUsers.value.filter(u => u.is_participant_only))
const expertUsers = computed(() => allUsers.value.filter(u => u.is_expert))
const otherUsers = computed(() => allUsers.value.filter(u => !u.is_expert))
const groupedRegistered = computed(() => groupByDept(registeredUsers.value))
const groupedParticipantOnly = computed(() => groupByDept(participantOnlyUsers.value))
const groupedExperts = computed(() => groupByDept(expertUsers.value))
const groupedOthers = computed(() => groupByDept(otherUsers.value))

function filteredMembers(members) {
  if (!personSearch.value) return members
  const kw = personSearch.value.toLowerCase()
  return members.filter(m =>
    m.real_name?.toLowerCase().includes(kw) ||
    m.department?.toLowerCase().includes(kw) ||
    m.position?.toLowerCase().includes(kw)
  )
}

function isDeptAllSelected(dept, members) {
  const available = filteredMembers(members).filter(u => !isExternalBusy(u))
  return available.length > 0 && available.every(u => form.participant_ids.includes(u.id))
}

function isDeptPartialSelected(dept, members) {
  const available = filteredMembers(members).filter(u => !isExternalBusy(u))
  const n = available.filter(u => form.participant_ids.includes(u.id)).length
  return n > 0 && n < available.length
}

function toggleDeptSelect(val, members) {
  const available = filteredMembers(members).filter(u => !isExternalBusy(u))
  if (val) {
    available.forEach(u => { if (!form.participant_ids.includes(u.id)) form.participant_ids.push(u.id) })
  } else {
    const ids = new Set(available.map(u => u.id))
    form.participant_ids = form.participant_ids.filter(id => !ids.has(id))
  }
}

const selectedPersons = computed(() => {
  return allUsers.value.filter(u => form.participant_ids.includes(u.id))
})

const selectedExperts = computed(() => {
  return selectedPersons.value.filter(u => u.is_expert)
})

const selectedOthers = computed(() => {
  return selectedPersons.value.filter(u => !u.is_expert)
})

function togglePerson(user) {
  const idx = form.participant_ids.indexOf(user.id)
  if (idx >= 0) {
    form.participant_ids.splice(idx, 1)
  } else {
    const extConflict = getExternalBusyInfo(user)
    if (extConflict) {
      ElMessage({
        type: 'error',
        message: `${user.real_name} 在 ${extConflict.timeRange} 有「${extConflict.task}」，与本次会议时间冲突，无法添加。`,
        duration: 4000,
        showClose: true
      })
      return
    }
    form.participant_ids.push(user.id)
  }
  if (form.participant_ids.length > 0 && form.startDate && form.startTime && form.endTime) {
    checkConflictsAsync()
  }
}

function toggleDept(dept) {
  collapsedDepts[dept] = !collapsedDepts[dept]
}

function selectAll() {
  const ids = allUsers.value.filter(u => !isExternalBusy(u)).map(u => u.id)
  form.participant_ids = [...ids]
}

// 当会议时间变化时，重新检查已选人员的外部冲突
watch([() => form.startTime, () => form.endTime], () => {
  if (!form.startTime || !form.endTime) return
  const busyUsers = allUsers.value.filter(u =>
    form.participant_ids.includes(u.id) && isExternalBusy(u)
  )
  if (busyUsers.length > 0) {
    busyUsers.forEach(u => {
      const info = getExternalBusyInfo(u)
      ElMessage({
        type: 'warning',
        message: `已选人员 ${u.real_name} 在 ${info.timeRange} 有「${info.task}」，与变更后的会议时间冲突，已自动移除。`,
        duration: 4000,
        showClose: true,
      })
    })
    const busyIds = new Set(busyUsers.map(u => u.id))
    form.participant_ids = form.participant_ids.filter(id => !busyIds.has(id))
  }
  if (form.participant_ids.length > 0 && form.startDate) {
    checkConflictsAsync()
  }
  if (form.startDate) {
    checkRoomConflictAsync()
  }
})

function clearAll() {
  form.participant_ids = []
}

async function fetchUsers() {
  loadingUsers.value = true
  try {
    const res = await getUserList()
    allUsers.value = Array.isArray(res) ? res : (res?.data || [])
  } catch (e) {
    console.error('获取人员列表失败:', e)
    ElMessage.error('获取人员列表失败')
  } finally {
    loadingUsers.value = false
  }
}

async function checkConflictsAsync() {
  try {
    const startDt = combineDatetime(form.startDate, form.startTime)
    const endDt = combineDatetime(form.endDate || form.startDate, form.endTime)
    if (!startDt || !endDt) return
    const res = await checkConflicts({
      participant_ids: form.participant_ids,
      start_time: startDt,
      end_time: endDt,
    })
    conflicts.value = res || []
  } catch (e) {
    console.error(e)
  }
}

// ======= 删除参会人员 =======
async function handleDeleteParticipant(user) {
  try {
    await ElMessageBox.confirm(
      `确认删除「${user.real_name}」？该操作无法撤销。`,
      '删除人员',
      { type: 'warning', confirmButtonText: '确认删除', cancelButtonText: '取消' }
    )
  } catch {
    return // 用户取消
  }
  try {
    await deleteParticipant(user.id)
    // 从本地列表移除
    allUsers.value = allUsers.value.filter(u => u.id !== user.id)
    // 如果已选也移除
    const idx = form.participant_ids.indexOf(user.id)
    if (idx >= 0) form.participant_ids.splice(idx, 1)
    ElMessage.success(`已删除「${user.real_name}」`)
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '删除失败')
  }
}

// ======= 新建人员 =======
const addPersonVisible = ref(false)
const addingPerson = ref(false)
const personFormRef = ref(null)
const personForm = reactive({
  real_name: '',
  department: '',
  position: '',
  professional_title: '',
  id_card_number: '',
  is_expert: false,
  phone: '',
  email: '',
})
const personRules = {
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
}

function generateUsername(name) {
  const ts = Date.now().toString(36)
  const prefix = name ? name.replace(/[^a-zA-Z\u4e00-\u9fa5]/g, '').slice(0, 4) : 'user'
  return `${prefix}_${ts}`
}

function showAddPersonDialog() {
  Object.assign(personForm, { real_name: '', department: '', position: '', professional_title: '', id_card_number: '', is_expert: false, phone: '', email: '' })
  addPersonVisible.value = true
}

async function handleAddPerson() {
  const valid = await personFormRef.value?.validate().catch(() => false)
  if (!valid) return
  addingPerson.value = true
  try {
    const created = await createParticipant({
      real_name: personForm.real_name,
      department: personForm.department,
      position: personForm.position,
      professional_title: personForm.professional_title,
      id_card_number: personForm.id_card_number,
      is_expert: personForm.is_expert,
      phone: personForm.phone,
      email: personForm.email,
    })
    ElMessage.success(`人员"${personForm.real_name}"创建成功`)
    addPersonVisible.value = false
    await fetchUsers()
    // 自动勾选刚创建的人员
    if (created?.id && !form.participant_ids.includes(created.id)) {
      form.participant_ids.push(created.id)
    }
  } catch (e) {
    console.error('创建人员失败:', e)
    ElMessage.error(e?.response?.data?.detail || '创建失败')
  } finally {
    addingPerson.value = false
  }
}

// ======= 文件 =======
function handleFileChange() {
  // v-model:file-list 已自动同步
}

// ======= AI 对话生成议程 =======
function buildAgendaSystemPrompt(previousAgenda) {
  let base = `你是一位资深的会议管理专家和行政秘书，擅长撰写规范的会议议程。
请严格按照以下纯文本格式输出议程，绝对不要使用任何特殊符号（不要用┌┐└┘│├┤─等框线符号，不要用Markdown语法、##、*等）。
格式要求：
1. 标题行：XX会议议程（单独一行）
2. 基本信息：每条一行，如：会议时间：XXX、会议地点：XXX、主持人：XXX、参会人员：XXX
3. 议程条目：用中文序号（一、二、三...），格式：序号、时间段、内容（负责人：XXX）
4. 备注：最后一行
注意：
- 只输出议程内容本身，不要输出解释性文字或开头寒暄语
- 时间安排要合理，开场5分钟、每个议程5-30分钟、最后留10分钟总结
- 语言正式、简洁、专业
- 各部分之间用空行分隔`

  if (previousAgenda) {
    base += `\n\n【当前已有议程如下，请根据用户要求进行修改，输出完整修改后的议程】：\n${previousAgenda}`
  }
  return base
}

async function sendChatMessage(msgOrEvent) {
  const input = (typeof msgOrEvent === 'string') ? msgOrEvent : chatInput.value?.trim()
  if (!input) return
  if (!form.title) {
    ElMessage.warning('请先填写会议名称')
    return
  }

  // 添加用户消息
  chatMessages.value.push({ role: 'user', content: input })
  chatInput.value = ''

  // 添加 AI 消息占位
  chatMessages.value.push({ role: 'assistant', content: '' })
  const assistantIdx = chatMessages.value.length - 1

  generating.agenda = true
  agendaViewMode.value = 'preview'

  // 保存当前议程用于上下文
  const previousAgenda = agendaContent.value
  agendaContent.value = ''

  const systemPrompt = buildAgendaSystemPrompt(previousAgenda)
  const participantNames = selectedPersons.value.map(p => p.real_name).join('、') || '待定'
  const timeInfo = (form.startDate && form.startTime && form.endTime)
    ? `${form.startDate} ${timeRangeLabel.value}`
    : '待定'

  let prompt = `会议信息：
会议名称：${form.title}
会议类型：${meetingTypeLabel.value}
会议时间：${timeInfo}
会议时长：${durationText.value || '待定'}
会议地点：${form.location || '待定'}
会议描述：${form.description || '（无）'}
参会人员：${participantNames}（共${form.participant_ids.length}人）

用户要求：${input}`

  abortController = new AbortController()

  try {
    const token = localStorage.getItem('token')
    const resp = await fetch('/api/ai/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        question: prompt,
        system_prompt: systemPrompt,
      }),
      signal: abortController.signal,
    })

    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)

    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const data = line.slice(6)
        if (data === '[DONE]') break
        if (data.startsWith('[ERROR]')) {
          ElMessage.error('AI生成失败: ' + data.slice(8))
          break
        }
        const decoded = data.replace(/\\n/g, '\n')
        // 同时更新对话气泡和右侧议程内容
        chatMessages.value[assistantIdx].content += decoded
        agendaContent.value += decoded
        await nextTick()
        // 自动滚动对话栏
        if (chatMessagesRef.value) {
          chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
        }
        // 自动滚动预览区
        if (agendaPreviewRef.value) {
          agendaPreviewRef.value.scrollTop = agendaPreviewRef.value.scrollHeight
        }
      }
    }

    if (agendaContent.value) {
      ElMessage.success('议程生成完成')
    }
  } catch (e) {
    if (e.name === 'AbortError') {
      ElMessage.info('已停止生成')
    } else {
      console.error('生成失败:', e)
      ElMessage.error('生成失败，请检查网络连接')
      chatMessages.value[assistantIdx].content = '⚠️ 生成失败，请重试'
    }
  } finally {
    generating.agenda = false
    abortController = null
  }
}

function quickSend(text) {
  sendChatMessage(text)
}

function clearAgenda() {
  agendaContent.value = ''
  chatMessages.value = []
  chatInput.value = ''
}

function applyAgendaTemplate(cmd) {
  const templates = {
    regular: '# 例行会议议程\n\n一、传达上级精神（10分钟）\n二、工作汇报（30分钟）\n三、讨论研究（15分钟）\n四、布置部署工作（10分钟）\n五、散会',
    review: '# 评审会议议程\n\n一、会议开始，宣读会议纪律（5分钟）\n二、项目情况介绍（15分钟）\n三、专家提问与讨论（30分钟）\n四、形成评审意见（20分钟）\n五、宣读评审结论（5分钟）\n六、散会',
    special: '# 专题研讨议程\n\n一、主题发言（10分钟）\n二、专家点评（20分钟）\n三、自由讨论（30分钟）\n四、总结发言（10分钟）\n五、散会',
    decision: '# 决策会议议程\n\n一、宣读议题（5分钟）\n二、情况说明（15分钟）\n三、讨论与决策（30分钟）\n四、表决通过（10分钟）\n五、宣布决定（5分钟）\n六、散会',
  }
  agendaContent.value = templates[cmd] || ''
  agendaViewMode.value = 'source'
  ElMessage.success('已应用议程模板，可在右侧直接编辑修改')
}

function stopGeneration() {
  if (abortController) {
    abortController.abort()
  }
}

// ======= 议程导出Word =======
function agendaTextToHtml(text) {
  // 先清理可能残余的特殊框线字符
  const cleaned = text.replace(/[┌┐└┘├┤─┬┴┼│]+/g, '')
  const lines = cleaned.split('\n')
  let html = ''
  const agendaItemRegex = /^[一二三四五六七八九十]+[、．.]?\s*/

  for (let i = 0; i < lines.length; i++) {
    const trimmed = lines[i].trim()

    if (!trimmed) {
      html += '<div style="height:8px;"></div>'
      continue
    }

    // 标题行：前几行中包含"议程"的、或者第一行
    const isTitle = (i === 0 || (i <= 2 && trimmed.includes('议程'))) && !trimmed.includes('】') && !trimmed.includes(':')
    if (isTitle) {
      html += `<p style="text-align:center;font-size:18px;font-weight:bold;margin:12px 0 8px;line-height:2;color:#1d2129;">${trimmed}</p>`
      continue
    }

    // 基本信息行（包含"："的）
    const isInfoLine = /^(会议时间|会议地点|主\s*持\s*人|参会人员|记\s*录\s*人|会议类型|会议主题)[：:]/.test(trimmed)
    if (isInfoLine) {
      const [label, ...rest] = trimmed.split(/[：:]/)
      const value = rest.join('：')
      html += `<p style="font-size:14px;line-height:2.2;margin:1px 0;color:#303133;"><span style="color:#606266;min-width:70px;display:inline-block;">${label}：</span>${value}</p>`
      continue
    }

    // 议程条目行（以中文序号开头）
    if (agendaItemRegex.test(trimmed)) {
      html += `<p style="font-size:14px;line-height:2.2;margin:2px 0;padding:4px 0 4px 4px;color:#303133;border-bottom:1px dashed #ebeef5;">${trimmed}</p>`
      continue
    }

    // 备注行
    if (trimmed.startsWith('备注') || trimmed.startsWith('注：')) {
      html += `<p style="font-size:14px;line-height:2;margin:12px 0 2px;color:#909399;font-style:italic;">${trimmed}</p>`
      continue
    }

    // 普通行
    html += `<p style="font-size:14px;line-height:2;margin:2px 0;color:#303133;">${trimmed}</p>`
  }

  return html
}

async function handleExportWord() {
  if (!agendaContent.value) {
    ElMessage.warning('没有可导出的议程内容')
    return
  }
  try {
    const bodyHtml = agendaTextToHtml(agendaContent.value)
    const htmlContent = `<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>会议议程</title></head>
<body style="font-family:SimSun,宋体,serif;padding:40px 60px;">
${bodyHtml}
</body></html>`

    const blob = await asBlob(htmlContent)
    saveAs(blob, `${form.title || '会议'}-议程.docx`)
    ElMessage.success('导出成功')
  } catch (e) {
    console.error('导出Word失败:', e)
    ElMessage.error('导出失败，请重试')
  }
}

// ======= 签到表 =======
const templateDialogVisible = ref(false)
const selectedTemplateKeys = ref([])
const previewTemplateKey = ref('')
const checkinTemplateOptions = [
  { key: 'expert', name: '专家签到表', cols: ['序号', '姓名', '单位', '职称', '签到时间', '签名'] },
  { key: 'others', name: '其他人员签到表', cols: ['序号', '姓名', '单位', '签到时间', '签名'] },
  { key: 'fee', name: '评审费发放表', cols: ['序号', '姓名', '身份证号', '单位', '职称', '金额', '签名'] },
]
function toggleTemplateKey(key) {
  const idx = selectedTemplateKeys.value.indexOf(key)
  if (idx === -1) selectedTemplateKeys.value.push(key)
  else selectedTemplateKeys.value.splice(idx, 1)
}
function applySelectedTemplates() {
  if (form.participant_ids.length === 0) { ElMessage.warning('请先选择参会人员'); return }
  const keys = selectedTemplateKeys.value
  // expert or fee: fill expertRows
  if (keys.includes('expert') || keys.includes('fee')) {
    checkinExpertRows.value = selectedExperts.value.map(p => ({
      _id: ++_checkinIdCounter,
      name: p.real_name || '',
      dept: p.department || '',
      title: p.professional_title || '',
      idCard: p.id_card_number || '',
      bankCard: '',
      fee: '',
      time: '',
      sign: '',
    }))
  } else {
    checkinExpertRows.value = []
  }
  if (keys.includes('others')) {
    checkinOtherRows.value = selectedOthers.value.map(p => ({
      _id: ++_checkinIdCounter,
      name: p.real_name || '',
      dept: p.department || '',
      time: '',
      sign: '',
    }))
  } else {
    checkinOtherRows.value = []
  }
  templateDialogVisible.value = false
  ElMessage.success('签到表已生成')
}

function applyCheckinTemplate(cmd) {
  if (form.participant_ids.length === 0) {
    ElMessage.warning('请先选择参会人员')
    return
  }
  if (cmd === 'expert') {
    checkinExpertRows.value = selectedExperts.value.map(p => ({
      _id: ++_checkinIdCounter,
      name: p.real_name || '',
      dept: p.department || '',
      title: p.professional_title || '',
      idCard: p.id_card_number || '',
      bankCard: '',
      fee: '',
      time: '',
      sign: '',
    }))
    checkinOtherRows.value = []
    ElMessage.success('已生成专家签到表')
  } else if (cmd === 'others') {
    checkinExpertRows.value = []
    checkinOtherRows.value = selectedOthers.value.map(p => ({
      _id: ++_checkinIdCounter,
      name: p.real_name || '',
      dept: p.department || '',
      time: '',
      sign: '',
    }))
    ElMessage.success('已生成其他人员签到表')
  } else if (cmd === 'fee') {
    checkinExpertRows.value = selectedExperts.value.map(p => ({
      _id: ++_checkinIdCounter,
      name: p.real_name || '',
      dept: p.department || '',
      title: p.professional_title || '',
      idCard: p.id_card_number || '',
      bankCard: '',
      fee: '',
      time: '',
      sign: '',
    }))
    checkinOtherRows.value = []
    ElMessage.success('已生成评审费发放表')
  } else if (cmd === 'all') {
    handleGenerateCheckin()
  }
}

async function handleGenerateCheckin() {
  if (form.participant_ids.length === 0) {
    ElMessage.warning('请先选择参会人员')
    return
  }
  generating.checkin = true
  try {
    checkinExpertRows.value = selectedExperts.value.map(p => ({
      _id: ++_checkinIdCounter,
      name: p.real_name || '',
      dept: p.department || '',
      title: p.professional_title || '',
      idCard: p.id_card_number || '',
      bankCard: '',
      fee: '',
      time: '',
      sign: '',
    }))
    checkinOtherRows.value = selectedOthers.value.map(p => ({
      _id: ++_checkinIdCounter,
      name: p.real_name || '',
      dept: p.department || '',
      time: '',
      sign: '',
    }))
    ElMessage.success('签到表生成成功')
  } catch (e) {
    ElMessage.error('签到表生成失败')
  } finally {
    generating.checkin = false
  }
}

// (checkin editing removed - tables are now read-only display)

function buildCheckinHtml() {
  let html = `<h3 style="text-align:center;margin-bottom:16px">${form.title || '会议'} - 签到表</h3>
    <p>会议时间：${form.startDate || '待定'} ${timeRangeLabel.value}</p>
    <p>会议地点：${form.location || '待定'}</p>`

  // 专家签到表
  if (checkinExpertRows.value.length > 0) {
    const expertRows = checkinExpertRows.value.map((r, i) =>
      `<tr><td>${i + 1}</td><td>${r.name}</td><td>${r.dept}</td><td>${r.title}</td><td>${r.time}</td><td></td></tr>`
    ).join('')
    html += `<h4 style="margin-top:20px">一、专家签到表（${checkinExpertRows.value.length}人）</h4>
      <table border="1" cellpadding="8" cellspacing="0" style="width:100%;border-collapse:collapse;font-size:14px">
        <thead><tr style="background:#f0f5ff"><th>序号</th><th>姓名</th><th>单位</th><th>职称</th><th>签到时间</th><th>签名</th></tr></thead>
        <tbody>${expertRows}</tbody>
      </table>`
  }

  // 其他人员签到表
  if (checkinOtherRows.value.length > 0) {
    const otherRows = checkinOtherRows.value.map((r, i) =>
      `<tr><td>${i + 1}</td><td>${r.name}</td><td>${r.dept}</td><td>${r.time}</td><td></td></tr>`
    ).join('')
    html += `<h4 style="margin-top:20px">二、其他人员签到表（${checkinOtherRows.value.length}人）</h4>
      <table border="1" cellpadding="8" cellspacing="0" style="width:100%;border-collapse:collapse;font-size:14px">
        <thead><tr style="background:#f0f5ff"><th>序号</th><th>姓名</th><th>单位</th><th>签到时间</th><th>签名</th></tr></thead>
        <tbody>${otherRows}</tbody>
      </table>`
  }

  // 评审费签收表
  if (checkinExpertRows.value.length > 0) {
    const feeRows = checkinExpertRows.value.map((r, i) =>
      `<tr><td>${i + 1}</td><td>${r.name}</td><td>${r.idCard}</td><td>${r.bankCard || ''}</td><td>${r.dept}</td><td>${r.title}</td><td>${r.fee || ''}</td><td></td></tr>`
    ).join('')
    html += `<h4 style="margin-top:20px">三、评审费签收表</h4>
      <table border="1" cellpadding="8" cellspacing="0" style="width:100%;border-collapse:collapse;font-size:14px">
        <thead><tr style="background:#f0f5ff"><th>序号</th><th>姓名</th><th>身份证号</th><th>银行卡号</th><th>单位</th><th>职称</th><th>金额</th><th>签名</th></tr></thead>
        <tbody>${feeRows}</tbody>
      </table>`
  }

  return html
}

function handleExportCheckinPdf() {
  if (checkinExpertRows.value.length === 0 && checkinOtherRows.value.length === 0) {
    ElMessage.warning('请先生成签到表')
    return
  }
  try {
    const content = buildCheckinHtml()
    const printHtml = `<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>${form.title || '会议'} - 签到表</title>
<style>
  @page { size: A4; margin: 20mm 15mm; }
  body { font-family: SimSun, 宋体, serif; padding: 0; margin: 0; color: #000; }
  h3 { text-align: center; font-size: 20px; margin-bottom: 16px; }
  p { font-size: 14px; margin: 4px 0; }
  table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 14px; }
  th, td { border: 1px solid #333; padding: 8px 12px; text-align: center; }
  th { background-color: #f0f5ff; font-weight: bold; }
  td { height: 36px; }
</style>
</head><body>${content}</body></html>`

    const printWindow = window.open('', '_blank')
    if (!printWindow) {
      ElMessage.error('弹窗被浏览器拦截，请允许弹窗后重试')
      return
    }
    printWindow.document.write(printHtml)
    printWindow.document.close()
    printWindow.onload = () => {
      setTimeout(() => {
        printWindow.print()
        printWindow.onafterprint = () => printWindow.close()
      }, 300)
    }
    ElMessage.success('请在打印对话框中选择"另存为PDF"')
  } catch (e) {
    console.error('导出PDF失败:', e)
    ElMessage.error('导出失败，请重试')
  }
}

// ======= 工具 =======
function combineDatetime(dateStr, timeObj) {
  if (!dateStr || !timeObj) return null
  const t = new Date(timeObj)
  return `${dateStr}T${String(t.getHours()).padStart(2, '0')}:${String(t.getMinutes()).padStart(2, '0')}:00`
}

// ======= 提交 =======
async function handleSubmit() {
  const valid = await basicFormRef.value?.validate().catch(() => false)
  if (!valid) {
    activeTab.value = 'info'
    ElMessage.warning('请完善基本信息')
    return
  }
  if (!form.startDate || !form.startTime || !form.endTime) {
    activeTab.value = 'info'
    ElMessage.warning('请选择会议时间')
    return
  }

  submitting.value = true
  try {
    const startDt = combineDatetime(form.startDate, form.startTime)
    const endDt = combineDatetime(form.endDate || form.startDate, form.endTime)

    const data = {
      title: form.title,
      meeting_type: form.meeting_type,
      start_time: startDt,
      end_time: endDt,
      location: form.location,
      description: form.description,
      welcome_message: form.welcome_message,
      welcome_theme: form.welcome_theme,
      participant_ids: form.participant_ids,
      expert_ids: selectedExperts.value.map(u => u.id),
      leader_id: form.leader_id,
      seat_layout: buildSeatLayoutJson(),
      has_review_fee: form.has_review_fee,
    }

    let meetingId
    if (isEdit.value) {
      meetingId = route.params.id
      await updateMeeting(meetingId, data)
    } else {
      const res = await createMeeting(data)
      meetingId = res.id
    }

    // 上传会议材料
    if (fileList.value.length > 0) {
      for (const f of fileList.value) {
        const rawFile = f.raw || f
        try {
          const uploadRes = await uploadAttachment(meetingId, rawFile)
          const attachmentId = uploadRes?.data?.id || uploadRes?.data?.data?.id
          if (attachmentId && Array.isArray(f.allowedUserIds) && f.allowedUserIds.length > 0) {
            await updateAttachmentPermissions(meetingId, attachmentId, f.allowedUserIds)
          }
        } catch (e) {
          console.error('上传附件失败:', f.name, e)
        }
      }
    }

    ElMessage.success(isEdit.value ? '修改成功' : '创建成功')
    router.push('/meeting/list')
  } catch (e) {
    console.error(e)
    ElMessage.error('操作失败，请重试')
  } finally {
    submitting.value = false
  }
}

// ======= 初始化 =======
function resetForm() {
  form.title = ''
  form.meeting_type = 'regular'
  form.startDate = dayjs().format('YYYY-MM-DD')
  form.startTime = null
  form.endDate = dayjs().format('YYYY-MM-DD')
  form.endTime = null
  form.location = ''
  form.description = ''
  form.welcome_message = ''
  form.welcome_theme = 'aurora'
  form.participant_ids = []
  form.leader_id = null
  form.has_review_fee = false
  activeTab.value = 'info'
  activeDuration.value = null
  agendaContent.value = ''
  agendaViewMode.value = 'preview'
  chatMessages.value = []
  chatInput.value = ''
  generatedContent.value = ''
  checkinExpertRows.value = []
  checkinOtherRows.value = []
  fileList.value = []
  seatAssignments.value = []
  conflicts.value = []
  personSearch.value = ''
  submitting.value = false
  basicFormRef.value?.resetFields()
}

async function loadMeetingData() {
  try {
    const meeting = await getMeetingById(route.params.id)
    form.title = meeting.title
    form.meeting_type = meeting.meeting_type || 'regular'
    form.location = meeting.location || ''
    form.description = meeting.description || ''
    form.welcome_message = meeting.welcome_message || ''
    form.welcome_theme = meeting.welcome_theme || 'aurora'
    form.startDate = dayjs(meeting.start_time).format('YYYY-MM-DD')
    form.startTime = new Date(meeting.start_time)
    form.endDate = dayjs(meeting.end_time).format('YYYY-MM-DD')
    form.endTime = new Date(meeting.end_time)
    form.participant_ids = (meeting.participants || []).map(p => p.id)
    form.has_review_fee = meeting.has_review_fee || false
  } catch (e) {
    console.error(e)
    ElMessage.error('加载会议信息失败')
  }
}

onMounted(async () => {
  fetchUsers()
  await fetchRooms()
  form.startDate = dayjs().format('YYYY-MM-DD')
  form.endDate = dayjs().format('YYYY-MM-DD')
  if (isEdit.value) {
    await loadMeetingData()
  }
})

// 座位地图自适应缩放
let seatResizeOb = null
watch(activeTab, (val) => {
  if (val === 'seats') {
    nextTick(() => {
      if (!isEdit.value) {
        initSeatLayout()
      } else {
        updateSeatMapScale()
      }
      if (!seatResizeOb && seatMapWrapRef.value) {
        seatResizeOb = new ResizeObserver(() => updateSeatMapScale())
        seatResizeOb.observe(seatMapWrapRef.value)
      }
    })
  }
})
onBeforeUnmount(() => {
  if (seatResizeOb) { seatResizeOb.disconnect(); seatResizeOb = null }
})

// keep-alive 缓存激活时，非编辑模式重置表单
onActivated(async () => {
  if (isEdit.value) {
    await loadMeetingData()
  } else {
    resetForm()
    await fetchRooms()
  }
  fetchUsers()
})
</script>

<style lang="scss" scoped>
/* ===== 军事风格主题 - 页面头部 ===== */
.page-container {
  padding: 10px 16px 16px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 7px 0 9px;
  border-bottom: 2px solid rgba(0,212,255,0.2);
  margin-bottom: 10px;

  .header-left {
    display: flex;
    align-items: center;
    gap: 8px;

    :deep(.el-button) {
      color: #7f99be;
      &:hover { color: #3990f1; }
    }
  }

  .page-title {
    margin: 0;
    font-size: 20px;
    font-weight: 700;
    color: #dee5f2;
    letter-spacing: 2px;
  }

  .header-right {
    display: flex;
    gap: 8px;

    :deep(.el-button--default) {
      background: rgba(71,160,235,0.2);
      border-color: #1e5ca2;
      color: #7f99be;
      border-radius: 12px;
      &:hover { border-color: #3990f1; color: #dee5f2; }
    }
    :deep(.el-button--primary) {
      background: #1e5ca2;
      border-color: #3990f1;
      color: #dee5f2;
      border-radius: 12px;
      &:hover { background: #2a6dbf; border-color: #3990f1; }
    }
  }
}

/* ===== 步骤条 ===== */
.steps-nav {
  display: flex;
  align-items: center;
  gap: 0;
  margin-bottom: 8px;
  background: #0e1d38;
  border: 1px solid rgba(30,92,162,0.45);
  border-radius: 6px;
  padding: 3px 4px;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  flex: 1;
  justify-content: center;

  &:hover { background: #132f4c; }

  &.active {
    background: rgba(71,160,235,0.2);
    border: 1px solid #1e5ca2;
    border-radius: 8px;
    .step-dot { background: #1e5ca2; color: #e0efff; border-color: transparent; }
    .step-label { color: #dee5f2; font-weight: 600; letter-spacing: 1px; }
  }

  &.done:not(.active) {
    .step-dot { background: #2bffbc; color: #0a1628; border-color: transparent; }
  }

  .step-dot {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 600;
    background: rgba(57,144,241,0.15);
    color: #7f99be;
    border: 1px solid rgba(57,144,241,0.25);
    flex-shrink: 0;
  }

  .step-label {
    font-size: 13px;
    color: #7f99be;
    white-space: nowrap;
  }
}

/* ===== 主体布局 ===== */
.main-body {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

.main-content {
  flex: 1;
  min-width: 0;
}

.sidebar {
  width: 240px;
  flex-shrink: 0;
}

/* ===== Tab 面板 ===== */
.tab-panel {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.panel-inner {
  background: #0e1d38;
  border: 1px solid rgba(30,92,162,0.45);
  border-radius: 6px;
  padding: 10px 14px;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 8px;
  font-size: 14px;
  font-weight: 600;
  color: #dee5f2;
  padding-bottom: 7px;
  border-bottom: 1px solid rgba(30,92,162,0.45);
  letter-spacing: 1px;

  :deep(.el-icon) {
    color: #a4ffe6;
    filter: drop-shadow(0 0 8px rgba(0,234,255,0.64));
  }

  .optional-badge {
    font-size: 14px;
    color: #3a5f80;
    font-weight: 400;
    background: #0d2137;
    padding: 2px 8px;
    border-radius: 2px;
    margin-left: auto;
    letter-spacing: 1px;
  }
}

.panel-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid #163153;

  :deep(.el-button--default) {
    background: #0e1d38;
    border: 1px solid #3990f1;
    color: #dee5f2;
    border-radius: 2px;
    &:hover { background: rgba(57,144,241,0.2); border-color: #5aaaf7; }
  }
  :deep(.el-button--primary) {
    background: rgba(57,144,241,0.25);
    border: 1px solid #3990f1;
    color: #dee5f2;
    border-radius: 2px;
    &:hover { background: rgba(57,144,241,0.5); }
  }
}

/* ===== 分割线 ===== */
.section-divider {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 10px 0 6px;

  .divider-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: rgba(0,212,255,0.2);
    flex-shrink: 0;
  }

  .divider-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, rgba(0,212,255,0.2), #0b1a2e, rgba(0,212,255,0.2));
  }
}

/* ===== 表单优化 ===== */
.nice-form {
  :deep(.el-form-item) { margin-bottom: 8px; }

  :deep(.el-form-item__label) {
    font-weight: 500;
    color: #ffffff;
    letter-spacing: 1px;
  }

  :deep(.el-input__wrapper) {
    background: rgba(14,29,56,0.35);
    border: 1px solid #0c3d80;
    box-shadow: none;
    border-radius: 12px;
    &:hover, &.is-focus { border-color: #3990f1; }
  }
  :deep(.el-input__inner) {
    color: #dee5f2;
    &::placeholder { color: #797d87; }
  }
  :deep(.el-textarea__inner) {
    background: rgba(14,29,56,0.35);
    border: 1px solid #0c3d80;
    box-shadow: none;
    border-radius: 12px;
    color: #dee5f2;
    &:hover, &:focus { border-color: #3990f1; }
    &::placeholder { color: #797d87; }
  }
  :deep(.el-select) {
    .el-input__wrapper {
      background: #0d2137;
      border: 1px solid rgba(0,212,255,0.2);
      box-shadow: none;
    }
  }
}

.form-row-2 {
  display: flex;
  gap: 8px;
  > * { flex: 1; }
}

.time-block {
  margin-bottom: 8px;
  padding: 8px 12px;
  background: #14284b;
  border-radius: 4px;
  border: 1px solid #204082;

  .time-block-title {
    font-size: 14px;
    font-weight: 500;
    color: #ffffff;
    margin-bottom: 8px;
    letter-spacing: 1px;
    .required-star { color: #f56c6c; }
  }

  :deep(.el-date-editor), :deep(.el-input) {
    .el-input__wrapper {
      background: rgba(14,29,56,0.5);
      border: 1px solid #0c3d80;
      box-shadow: none;
      border-radius: 12px;
      &:hover, &.is-focus { border-color: #3990f1; }
    }
    .el-input__inner {
      color: #dee5f2;
      &::placeholder { color: #797d87; }
    }
  }
}

.time-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;

  .time-group { display: flex; align-items: center; gap: 8px; }
  .time-label { font-size: 14px; color: #5e8aad; white-space: nowrap; min-width: 28px; }
  .time-arrow { color: #3a5f80; font-size: 16px; }
}

.duration-shortcuts {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  flex-wrap: wrap;

  .shortcut-label { font-size: 14px; color: #3a5f80; white-space: nowrap; }

  :deep(.el-button) {
    background: #0b1a2e;
    border-color: rgba(0,212,255,0.2);
    color: #5e8aad;
    border-radius: 3px;
    &:hover { border-color: #00d4ff; color: #ffffff; }
  }
  :deep(.el-button--primary) {
    background: #00d4ff;
    border-color: #00d4ff;
    color: #ffffff;
  }
}

.duration-info {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  font-size: 14px;
  color: #00d4ff;
  font-family: 'Consolas', monospace;
}

/* ===== 参会人员选择 ===== */

/* 新版合并头部 */
.persons-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;

  .persons-header-title {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 16px;
    font-weight: 600;
    color: #00d4ff;
    white-space: nowrap;
    letter-spacing: 1px;
  }

  .persons-search {
    flex: 1;
    min-width: 160px;
    max-width: 320px;

    :deep(.el-input__wrapper) {
      background: #0d2137;
      border: 1px solid rgba(0,212,255,0.2);
      box-shadow: none;
      border-radius: 12px;
      &:hover, &.is-focus { border-color: #00d4ff; }
    }
    :deep(.el-input__inner) {
      color: #ffffff;
      &::placeholder { color: #3a5f80; }
    }
  }

  .persons-header-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-left: auto;
  }
}

/* 底部导航栏 */
.persons-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid rgba(0,212,255,0.15);

  .persons-selected-hint {
    font-size: 13px;
    color: #5e8aad;
  }

  .persons-footer-btns {
    display: flex;
    gap: 10px;
  }
}

/* 旧版 toolbar（保留以防兼容） */
.person-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 8px;

  .toolbar-actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  :deep(.el-input__wrapper) {
    background: #0d2137;
    border: 1px solid rgba(0,212,255,0.2);
    box-shadow: none;
    border-radius: 12px;
    &:hover, &.is-focus { border-color: #00d4ff; }
  }
  :deep(.el-input__inner) {
    color: #ffffff;
    &::placeholder { color: #3a5f80; }
  }
}

.person-body {
  display: flex;
  gap: 16px;
}

.person-panel {
  flex: 1;
  border: 1px solid rgba(0,212,255,0.2);
  border-radius: 12px;
  overflow: hidden;
}

.person-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: #0d2137;
  border-bottom: 1px solid rgba(0,212,255,0.2);
  font-size: 14px;
  font-weight: 500;
  color: #00d4ff;
  letter-spacing: 1px;

  .header-count {
    font-size: 14px;
    color: #5e8aad;
    background: #0b1a2e;
    padding: 1px 8px;
    border-radius: 2px;
    font-family: 'Consolas', monospace;
  }
}

.center-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 60px;
  color: #3a5f80;
}

.dept-group {
  .dept-header {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px 6px 14px;
    font-size: 13px;
    font-weight: 600;
    color: #8fb8d8;
    background: rgba(20,40,75,0.95);
    border-left: 2px solid rgba(57,144,241,0.5);
    cursor: pointer;
    user-select: none;

    &:hover { background: rgba(57,144,241,0.1); }

    .dept-count {
      color: #456484;
      font-weight: 400;
      font-size: 12px;
      margin-left: 2px;
    }

    .dept-arrow {
      margin-left: auto;
      font-size: 13px;
      color: #456484;
      transition: transform 0.2s;
      &.expanded { transform: rotate(90deg); }
    }
  }
}

.dept-members {
  padding: 2px 0;
  background: #0b1a2e;
}

.person-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 12px 7px 32px;
  cursor: pointer;
  transition: all 0.15s;

  &:hover { background: #132f4c; }

  &.selected {
    background: #0f2942;
    .person-name { color: #00d4ff; font-weight: 500; }
  }

  &.is-busy {
    cursor: not-allowed;
    opacity: 0.55;
    &:hover { background: transparent; }
    .person-name { color: #5e8aad; }
  }
}

.busy-tag {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 14px;
}

.person-avatar {
  background: rgba(0,212,255,0.2);
  color: #00d4ff;
  font-size: 14px;
  flex-shrink: 0;
}

.selected-avatar {
  background: #132f4c;
  color: #00d4ff;
}

.person-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;

  .person-name { font-size: 14px; color: #ffffff; }
  .person-extra { font-size: 14px; color: #3a5f80; margin-top: 1px; }
}

.selected-panel {
  background: #0b1a2e;

  .selected-list {
    padding: 4px 0;
  }

  .selected-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 7px 16px;
    transition: background 0.15s;

    &:hover { background: #132f4c; }
  }

  .remove-btn {
    margin-left: auto;
    cursor: pointer;
    color: #3a5f80;
    font-size: 14px;
    transition: color 0.15s;
    &:hover { color: #f56c6c; }
  }

  .delete-participant-btn {
    margin-left: 4px;
    cursor: pointer;
    color: #3a5f80;
    font-size: 14px;
    flex-shrink: 0;
    transition: color 0.15s;
    &:hover { color: #f56c6c; }
  }
}

.conflict-alert {
  margin-top: 16px;
  .conflict-item { font-size: 14px; margin: 4px 0; color: #ffffff; }
  .conflict-time { color: #3a5f80; font-size: 14px; }
}

/* ===== 会议材料 Tab ===== */

/* 评审费 Toggle 行 */
.review-fee-toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgba(14,29,56,0.6);
  border: 1px solid #204082;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
  margin-bottom: 4px;

  &:hover { border-color: rgba(57,144,241,0.6); background: rgba(57,144,241,0.06); }
  &.active {
    border-color: rgba(43,255,188,0.55);
    background: rgba(43,255,188,0.06);
    .review-fee-toggle-icon { color: #2bffbc; filter: drop-shadow(0 0 6px rgba(43,255,188,0.6)); }
    .review-fee-toggle-title { color: #2bffbc; }
  }
}

.review-fee-toggle-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.review-fee-toggle-icon {
  font-size: 20px;
  color: #456484;
  transition: all 0.2s;
  display: flex;
  align-items: center;
}

.review-fee-toggle-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.review-fee-toggle-title {
  font-size: 14px;
  font-weight: 600;
  color: #dee5f2;
  transition: color 0.2s;
}

.review-fee-toggle-desc {
  font-size: 12px;
  color: #7f99be;
}

/* 文档查看权限 */
.perm-block {
  margin-top: 14px;
  background: #0e1d38;
  border: 1px solid #204082;
  border-radius: 4px;
  overflow: hidden;
}

.perm-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: rgba(20,40,75,0.8);
  border-bottom: 1px solid #163153;
}

.perm-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.perm-header-icon {
  color: #3990f1;
  font-size: 14px;
}

.perm-header-title {
  font-size: 14px;
  font-weight: 600;
  color: #dee5f2;
}

.perm-header-desc {
  font-size: 12px;
  color: #456484;
}

.perm-batch-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(57,144,241,0.04);
  border-bottom: 1px solid #163153;
  flex-wrap: wrap;
}

.perm-batch-label {
  font-size: 13px;
  color: #7f99be;
  white-space: nowrap;
  flex-shrink: 0;
}

.perm-batch-select {
  flex: 1;
  min-width: 220px;
  max-width: 500px;

  :deep(.el-input__wrapper) {
    background: rgba(14,29,56,0.5);
    border: 1px solid #0c3d80;
    box-shadow: none;
    border-radius: 2px;
    &:hover, &.is-focus { border-color: #3990f1; }
  }
  :deep(.el-input__inner) { color: #dee5f2; font-size: 13px; &::placeholder { color: #797d87; } }
  :deep(.el-tag) { background: rgba(57,144,241,0.2); border-color: rgba(57,144,241,0.4); color: #dee5f2; }
}

.perm-apply-btn {
  border: 1px solid #3990f1;
  background: rgba(57,144,241,0.2);
  color: #dee5f2;
  font-size: 13px;
  padding: 5px 12px;
  border-radius: 2px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s;
  &:hover { background: rgba(57,144,241,0.45); }
}

.perm-clear-all-btn {
  border: 1px solid rgba(242,75,85,0.5);
  background: rgba(242,75,85,0.08);
  color: #f24b55;
  font-size: 13px;
  padding: 5px 12px;
  border-radius: 2px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s;
  &:hover { background: rgba(242,75,85,0.2); }
}

.perm-file-list {
  padding: 4px 0;
}

.perm-file-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 14px;
  border-bottom: 1px solid rgba(22,49,83,0.7);
  &:last-child { border-bottom: none; }
  &:hover { background: rgba(57,144,241,0.04); }
}

.perm-file-info {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 180px;
  max-width: 220px;
}

.perm-file-icon {
  color: #7f99be;
  font-size: 14px;
  flex-shrink: 0;
}

.perm-file-name {
  font-size: 13px;
  color: #dee5f2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.perm-file-badge {
  flex-shrink: 0;
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 2px;
  white-space: nowrap;
}

.perm-badge-all {
  background: rgba(43,255,188,0.1);
  border: 1px solid rgba(43,255,188,0.3);
  color: #2bffbc;
}

.perm-badge-limited {
  background: rgba(57,144,241,0.15);
  border: 1px solid rgba(57,144,241,0.4);
  color: #5aaaf7;
}

.perm-file-selector {
  flex: 1;
  min-width: 0;
}

.perm-select {
  width: 100%;

  :deep(.el-input__wrapper) {
    background: rgba(14,29,56,0.4);
    border: 1px solid #0c3d80;
    box-shadow: none;
    border-radius: 2px;
    &:hover, &.is-focus { border-color: #3990f1; }
  }
  :deep(.el-input__inner) { color: #dee5f2; font-size: 13px; &::placeholder { color: #797d87; } }
  :deep(.el-tag) { background: rgba(57,144,241,0.2); border-color: rgba(57,144,241,0.4); color: #dee5f2; font-size: 12px; }
  :deep(.el-select__tags-text) { font-size: 12px; }
}

.material-type-hint {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  padding: 10px 14px;
  margin-bottom: 14px;
  background: rgba(230,162,60,0.08);
  border: 1px solid rgba(230,162,60,0.25);
  border-radius: 8px;
  font-size: 14px;
  color: #e6a23c;

  .hint-tag {
    display: inline-block;
    background: rgba(230,162,60,0.15);
    border: 1px solid rgba(230,162,60,0.3);
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 14px;
  }
}

.material-section {
  .section-subtitle {
    margin: 0 0 14px;
    font-size: 15px;
    font-weight: 500;
    color: #ffffff;
    letter-spacing: 1px;
  }

  .section-desc {
    font-size: 14px;
    color: #3a5f80;
    margin: -8px 0 14px;
  }
}

.file-upload {
  :deep(.el-upload-dragger) {
    border-radius: 12px;
    padding: 30px;
    background: #0d2137;
    border-color: rgba(0,212,255,0.2);
    &:hover { border-color: #00d4ff; }
  }
  :deep(.el-upload-dragger .el-icon) { color: #3a5f80; }
  :deep(.el-upload__text) { color: #5e8aad; }
  :deep(.el-upload__tip) { color: #3a5f80; }
}

.checkin-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.template-option-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.template-option-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  &:hover { border-color: #409eff; background: #f0f7ff; }
  &.is-selected { border-color: #409eff; background: #ecf5ff; }
  &.is-previewing { border-color: #67c23a; background: #f0f9eb; }
}
.tpl-name { font-size: 14px; font-weight: 600; color: #303133; }
.tpl-cols { font-size: 14px; color: #909399; margin-top: 3px; }

.tpl-preview-wrap {
  margin-top: 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: auto;
  background: #f9fafb;
}
.tpl-preview-title {
  padding: 8px 14px;
  font-size: 14px;
  font-weight: 600;
  color: #409eff;
  background: #f0f7ff;
  border-bottom: 1px solid #d9ecff;
}
.tpl-preview-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  th {
    background: #ecf5ff;
    color: #409eff;
    padding: 6px 10px;
    border: 1px solid #d9ecff;
    text-align: center;
    white-space: nowrap;
    font-weight: 600;
  }
  td {
    padding: 6px 10px;
    border: 1px solid #e4e7ed;
    text-align: center;
    color: #606266;
  }
}
.tpl-sign-placeholder {
  color: #c0c4cc;
  font-style: italic;
}

.checkin-table-wrap {
  background: rgba(14,36,64,0.6);
  border: 1px solid rgba(0,212,255,0.2);
  border-radius: 12px;
  overflow: auto;
  max-height: 500px;
}

.checkin-table-title {
  padding: 10px 16px;
  font-size: 15px;
  font-weight: 600;
  color: #00d4ff;
  border-bottom: 1px solid rgba(0,212,255,0.15);
}

.selected-group-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  font-size: 14px;
  font-weight: 600;
  color: #8fb8d8;
}

.checkin-edit-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;

  th {
    background: rgba(36,85,128,0.8);
    color: #00d4ff;
    padding: 10px 12px;
    text-align: center;
    border: 1px solid rgba(0,212,255,0.2);
    font-weight: 600;
    white-space: nowrap;
  }

  td {
    padding: 6px 8px;
    border: 1px solid rgba(0,212,255,0.15);
    text-align: center;
    color: #d8f0ff;
  }

  tbody tr:hover {
    background: rgba(0,212,255,0.06);
  }
}

.cell-input {
  width: 100%;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 4px;
  color: #e0efff;
  font-size: 14px;
  padding: 6px 8px;
  outline: none;
  transition: border-color 0.2s;

  &:hover { border-color: rgba(0,212,255,0.3); }
  &:focus { border-color: #00d4ff; background: rgba(0,16,40,0.4); }
  &::placeholder { color: rgba(106,143,175,0.5); }
}

.cell-text {
  display: block;
  padding: 6px 8px;
  color: #e0efff;
  font-size: 14px;
}

.cell-ops {
  white-space: nowrap;
  padding: 4px 6px !important;
  .el-button { margin: 1px; }
}

.checkin-add-row {
  padding: 6px 0;
  text-align: left;
}

.cell-center {
  text-align: center;
  color: #6a8faf;
}

/* ===== AI 议程：聊天编辑器双栏布局 ===== */
.agenda-chat-layout {
  display: flex;
  gap: 0;
  height: calc(100vh - 260px);
  min-height: 420px;
  border: 1px solid rgba(0,212,255,0.2);
  border-radius: 12px;
  overflow: hidden;
  background: #0b1a2e;
}

/* -- 左侧聊天面板 -- */
.chat-panel {
  width: 400px;
  min-width: 360px;
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(0,212,255,0.2);
  background: #070e1a;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: #14284b;
  border-bottom: 1px solid rgba(0,212,255,0.2);
  flex-shrink: 0;

  .chat-header-left {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .chat-header-icon {
    font-size: 20px;
  }

  .chat-header-title {
    font-size: 15px;
    font-weight: 600;
    color: #00d4ff;
    letter-spacing: 1px;
  }

  :deep(.el-tag) {
    background: #0d2137;
    border-color: rgba(0,212,255,0.2);
    color: #5e8aad;
  }
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;

  &::-webkit-scrollbar { width: 4px; }
  &::-webkit-scrollbar-track { background: transparent; }
  &::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.2); border-radius: 2px; }
}

.chat-welcome {
  display: flex;
  gap: 10px;
  align-items: flex-start;

  .welcome-avatar {
    width: 36px;
    height: 36px;
    border-radius: 12px;
    background: #132f4c;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
    border: 1px solid rgba(0,212,255,0.2);
  }

  .welcome-bubble {
    background: #0b1a2e;
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 2px 8px 8px 8px;
    padding: 12px 16px;
    max-width: 280px;

    p {
      margin: 0;
      font-size: 14px;
      color: #5e8aad;
      line-height: 1.7;

      &:first-child {
        font-weight: 500;
        color: #ffffff;
        margin-bottom: 4px;
      }
    }
  }
}

.chat-quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 4px 0 4px 46px;

  .quick-btn {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 7px 14px;
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 3px;
    background: #0b1a2e;
    font-size: 14px;
    color: #5e8aad;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;

    &:hover {
      border-color: #00d4ff;
      color: #00d4ff;
      background: #132f4c;
      transform: translateY(-1px);
      box-shadow: 0 2px 6px rgba(11,42,74,0.06);
    }

    .quick-icon {
      font-size: 14px;
    }
  }
}

/* -- 对话气泡 -- */
.chat-msg {
  display: flex;
  gap: 10px;
  align-items: flex-start;

  &.user {
    flex-direction: row-reverse;

    .msg-bubble {
      background: #00d4ff;
      color: #ffffff;
      border-radius: 8px 2px 8px 8px;
      border: none;

      .msg-content {
        color: #ffffff;
      }
    }

    .msg-avatar {
      background: rgba(0,212,255,0.2);
      color: #00d4ff;
    }
  }

  &.assistant {
    .msg-bubble {
      background: #0b1a2e;
      border: 1px solid rgba(0,212,255,0.2);
      border-radius: 2px 8px 8px 8px;
    }
  }
}

.msg-avatar {
  width: 34px;
  height: 34px;
  border-radius: 12px;
  background: #132f4c;
  border: 1px solid rgba(0,212,255,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

.msg-bubble {
  max-width: 280px;
  padding: 10px 14px;
  position: relative;

  .msg-content {
    font-size: 14px;
    color: #ffffff;
    line-height: 1.7;
    white-space: pre-wrap;
    word-break: break-word;
  }

  .typing-dot {
    display: inline-block;
    color: #00d4ff;
    font-size: 14px;
    animation: blink 0.8s infinite;
    margin-left: 2px;
    vertical-align: middle;
  }

  .msg-loading {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 14px;
    color: #3a5f80;
    padding: 2px 0;

    .el-icon {
      font-size: 16px;
      color: #00d4ff;
    }
  }
}

/* -- 输入区 -- */
.chat-input-area {
  padding: 12px 16px;
  background: #0b1a2e;
  border-top: 1px solid rgba(0,212,255,0.2);
  flex-shrink: 0;

  .input-wrapper {
    :deep(.el-textarea__inner) {
      background: #0d2137;
      border: 1px solid rgba(0,212,255,0.2);
      border-radius: 12px;
      font-size: 14px;
      line-height: 1.6;
      padding: 10px 14px;
      color: #ffffff;
      box-shadow: none;

      &:focus {
        background: #132f4c;
        border-color: #00d4ff;
      }
      &::placeholder { color: #3a5f80; }
    }
  }

  .input-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 8px;
  }

  .input-hint {
    font-size: 14px;
    color: #3a5f80;
  }

  .input-btns {
    display: flex;
    gap: 6px;

    :deep(.el-button--primary) {
      background: #00d4ff;
      border-color: #00d4ff;
      border-radius: 12px;
      &:hover { background: #00bde6; }
    }
    :deep(.el-button--danger) {
      background: transparent;
      border-color: #f56c6c;
      color: #f56c6c;
      border-radius: 12px;
      &:hover { background: rgba(245,108,108,0.1); }
    }
  }
}

/* -- 右侧编辑器面板 -- */
.editor-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #0b1a2e;
}

.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 18px;
  background: #14284b;
  border-bottom: 1px solid rgba(0,212,255,0.2);
  flex-shrink: 0;
  flex-wrap: wrap;
  gap: 8px;

  .editor-header-left {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .editor-header-icon {
    font-size: 18px;
  }

  .editor-header-title {
    font-size: 15px;
    font-weight: 600;
    color: #00d4ff;
    letter-spacing: 1px;
  }

  .editor-header-right {
    display: flex;
    align-items: center;
    gap: 8px;

    :deep(.el-button-group .el-button) {
      background: #0b1a2e;
      border-color: rgba(0,212,255,0.2);
      color: #5e8aad;
      &:hover { color: #ffffff; }
    }
    :deep(.el-button-group .el-button--primary) {
      background: #00d4ff;
      border-color: #00d4ff;
      color: #ffffff;
    }
  }
}

.editor-body {
  flex: 1;
  overflow-y: auto;
  position: relative;

  &::-webkit-scrollbar { width: 4px; }
  &::-webkit-scrollbar-track { background: transparent; }
  &::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.2); border-radius: 2px; }
}

.editor-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 40px;

  .empty-icon {
    font-size: 56px;
    margin-bottom: 16px;
    opacity: 0.4;
  }

  .empty-main {
    margin: 0 0 6px;
    font-size: 16px;
    font-weight: 500;
    color: #3a5f80;
    letter-spacing: 1px;
  }

  .empty-sub {
    margin: 0;
    font-size: 14px;
    color: #3a5f80;
  }
}

.editor-preview {
  padding: 24px 28px;
  min-height: 100%;

  .rendered-html {
    font-size: 14px;
    line-height: 2;
    color: #e0efff;

    :deep(p) {
      margin: 2px 0;
      color: #e0efff !important;
    }

    :deep(span) {
      color: #7ab7d8 !important;
    }

    :deep(table) {
      border-collapse: collapse;
      width: 100%;
      margin: 12px 0;

      th, td {
        border: 1px solid rgba(0,212,255,0.2);
        padding: 8px 12px;
        font-size: 14px;
        text-align: center;
      }

      th {
        background: #132f4c;
        font-weight: 600;
        color: #00d4ff;
      }

      td {
        color: #ffffff;
      }

      tr:hover td {
        background: #0d2137;
      }
    }
  }

  .typing-cursor {
    display: inline-block;
    color: #00d4ff;
    font-weight: bold;
    font-size: 18px;
    margin-left: 4px;
    animation: blink 0.8s infinite;
  }

  .gen-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 100px 40px;
    color: #3a5f80;
    font-size: 14px;

    .el-icon {
      font-size: 32px;
      color: #00d4ff;
    }
  }
}

.raw-editor {
  width: 100%;
  height: 100%;
  border: none;
  outline: none;
  padding: 24px 28px;
  font-size: 14px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  line-height: 1.8;
  color: #ffffff;
  resize: none;
  background: #0b1a2e;
  box-sizing: border-box;

  &::placeholder {
    color: #3a5f80;
  }
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* ===== 右侧摘要卡片 ===== */
.summary-card {
  background: #14284b;
  border: 1px solid rgba(0,212,255,0.2);
  border-radius: 12px;
  overflow: hidden;

  .summary-header {
    padding: 14px 16px;
    font-weight: 600;
    font-size: 14px;
    color: #00d4ff;
    background: #14284b;
    border-bottom: 1px solid rgba(0,212,255,0.2);
    letter-spacing: 2px;
  }

  .summary-body {
    padding: 12px 16px;
  }

  .s-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 7px 0;
    border-bottom: 1px dashed rgba(0,212,255,0.2);
    &:last-child { border-bottom: none; }
  }

  .s-label {
    font-size: 14px;
    color: #7f99be;
    flex-shrink: 0;
    letter-spacing: 1px;
  }

  .s-value {
    font-size: 14px;
    color: #dee5f2;
    text-align: right;
    max-width: 150px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;

    &.s-highlight { color: #3990f1; font-weight: 600; }
  }

  :deep(.el-tag) {
    border-radius: 2px;
  }

  :deep(.el-button--primary) {
    background: #00d4ff;
    border-color: #00d4ff;
    border-radius: 12px;
    &:hover { background: #00bde6; }
  }
}

/* ===== Transition ===== */
.list-enter-active,
.list-leave-active {
  transition: all 0.25s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* ===== 对话框军事风格 ===== */
:deep(.el-dialog) {
  background: #0b1a2e;
  border: 1px solid rgba(0,212,255,0.2);
  border-radius: 12px;

  .el-dialog__header {
    background: #0d2137;
    border-bottom: 1px solid rgba(0,212,255,0.2);
  }
  .el-dialog__title {
    color: #00d4ff;
    letter-spacing: 1px;
  }
  .el-dialog__body {
    color: #ffffff;
  }
  .el-form-item__label {
    color: #ffffff;
  }
  .el-input__wrapper {
    background: #0d2137;
    border: 1px solid rgba(0,212,255,0.2);
    box-shadow: none;
    border-radius: 12px;
    &:hover, &.is-focus { border-color: #00d4ff; }
  }
  .el-input__inner {
    color: #ffffff;
    &::placeholder { color: #3a5f80; }
  }
  .el-dialog__footer {
    border-top: 1px solid rgba(0,212,255,0.2);
  }
}

/* ===== 响应式 ===== */
@media (max-width: 960px) {
  .page-container { padding: 16px; }
  .main-body { flex-direction: column; }
  .sidebar { width: 100%; }
  .person-body { flex-direction: column; }
  .steps-nav { overflow-x: auto; }
  .time-row {
    flex-direction: column;
    align-items: flex-start;
    .time-arrow { display: none; }
  }
  .form-row-2 { flex-direction: column; }
  .agenda-chat-layout {
    flex-direction: column;
    height: auto;
  }
  .chat-panel {
    width: 100%;
    min-width: 0;
    border-right: none;
    border-bottom: 1px solid rgba(0,212,255,0.2);
    max-height: 400px;
  }
  .editor-panel {
    min-height: 400px;
  }
}

/* ========== 座位排布 ========== */
.seat-empty-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px 0;
  color: #8bb3d9;
}

.seat-editor {
  display: flex;
  gap: 20px;
  margin-top: 16px;
}

.seat-sidebar {
  width: 200px;
  flex-shrink: 0;
  background: #0e1d38;
  border: 1px solid #204082;
  border-radius: 4px;
  padding: 12px 10px;
}

.seat-sidebar-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #dee5f2;
  margin-bottom: 4px;

  .seat-assign-count {
    margin-left: auto;
    font-size: 12px;
    color: #2bffbc;
    font-weight: 400;
  }
}

.seat-sidebar-hint {
  font-size: 12px;
  color: #456484;
  margin-bottom: 10px;
}

.drag-person {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 8px;
  margin-bottom: 4px;
  background: #14284b;
  border: 1px solid #204082;
  border-radius: 4px;
  cursor: grab;
  transition: all 0.15s;

  &:hover { background: rgba(57,144,241,0.12); border-color: #3990f1; }
  &:active { cursor: grabbing; }
  &.is-assigned {
    border-color: rgba(43,255,188,0.4);
    background: rgba(43,255,188,0.06);
    cursor: default;
  }
}

.drag-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(57,144,241,0.2);
  border: 1px solid #3990f1;
  color: #dee5f2;
  font-size: 13px;
  font-weight: 700;
  line-height: 28px;
  text-align: center;
  flex-shrink: 0;
}

.drag-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.drag-name {
  font-size: 13px;
  color: #dee5f2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.drag-sub {
  font-size: 11px;
  color: #7f99be;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.drag-seat-badge {
  flex-shrink: 0;
  font-size: 11px;
  color: #2bffbc;
  border: 1px solid rgba(43,255,188,0.5);
  background: rgba(43,255,188,0.1);
  padding: 1px 5px;
  border-radius: 2px;
  white-space: nowrap;
}

.drag-handle {
  flex-shrink: 0;
  color: #456484;
  font-size: 14px;
}

.drag-empty {
  text-align: center;
  padding: 20px 0;
  color: #456484;
  font-size: 13px;
}

.seat-map-wrap {
  flex: 1;
  overflow: auto;
  min-width: 0;
}

.seat-map-scaler {
  transition: transform 0.2s ease;
}

.seat-map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 600;
  color: #dee5f2;
}

.seat-map-room-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #dee5f2;
}

.seat-map-header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.seat-legend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #7f99be;
}

.seat-legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  flex-shrink: 0;
}

.seat-vacant-dot {
  background: rgba(100,160,220,0.15);
  border: 1px dashed rgba(100,160,220,0.5);
}

.seat-assigned-dot {
  background: rgba(57,144,241,0.3);
  border: 1px solid rgba(57,144,241,0.7);
}

.seat-drag-legend {
  color: #7f99be;
  border: 1px solid rgba(43,255,188,0.4);
  padding: 1px 6px;
  border-radius: 2px;
  font-size: 12px;
  background: rgba(43,255,188,0.05);
}

.seat-clear-btn {
  border: 1px solid #f24b55;
  background: rgba(242,75,85,0.1);
  color: #f24b55;
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 2px;
  cursor: pointer;
  transition: all 0.15s;
  &:hover { background: rgba(242,75,85,0.25); }
}

.seat-map {
  position: relative;
  background: rgba(0,16,40,0.6);
  border: 1px solid rgba(0,212,255,0.2);
  border-radius: 12px;
  overflow: hidden;
}

.map-table {
  position: absolute;
  background: rgba(0,212,255,0.08);
  border: 2px solid rgba(0,212,255,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(0,212,255,0.5);
  font-size: 14px;
  pointer-events: none;
}

.map-screen {
  position: absolute;
  background: linear-gradient(90deg, #e74c3c, #c0392b);
  border: 1px solid #e74c3c;
  border-radius: 4px;
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  letter-spacing: 3px;
  box-shadow: 0 0 12px rgba(231,76,60,0.4);
  pointer-events: none;
  z-index: 2;
}

.map-seat {
  position: absolute;
  width: 64px;
  height: 64px;
  border-radius: 12px;
  background: rgba(255,255,255,0.06);
  border: 2px dashed rgba(100,160,220,0.35);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: rgba(0,212,255,0.6);
    background: rgba(0,212,255,0.1);
  }

  &.occupied {
    background: rgba(0,212,255,0.15);
    border: 2px solid rgba(0,212,255,0.5);
    cursor: pointer;
  }
}

.seat-num {
  font-size: 14px;
  color: #6a8faf;
  margin-bottom: 2px;
}

.seat-person-name {
  font-size: 14px;
  font-weight: 700;
  color: #00d4ff;
  max-width: 56px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.seat-vacant {
  font-size: 14px;
  color: rgba(100,160,220,0.4);
}

/* ===== 人员分类区域 ===== */
.user-type-section {
  margin-bottom: 4px;
}

.user-type-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
  border-bottom: 1px solid rgba(0,212,255,0.1);
}

.registered-header {
  background: linear-gradient(90deg, rgba(0,212,255,0.12) 0%, transparent 100%);
  color: #00d4ff;
}

.participant-header {
  background: linear-gradient(90deg, rgba(230,162,60,0.12) 0%, transparent 100%);
  color: #e6a23c;
}

.type-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.registered-dot {
  background: #00d4ff;
  box-shadow: 0 0 6px rgba(0,212,255,0.5);
}

.participant-dot {
  background: #e6a23c;
  box-shadow: 0 0 6px rgba(230,162,60,0.5);
}

.type-count {
  margin-left: auto;
  font-size: 14px;
  font-weight: 400;
  opacity: 0.7;
}

.participant-only-members {
  background: rgba(230,162,60,0.03);
}

.participant-only-avatar {
  background: rgba(230,162,60,0.2) !important;
  color: #e6a23c !important;
}

/* ===== 签到表编辑模式 ===== */
.cell-input.readonly {
  cursor: default;
  &:hover { border-color: transparent; }
  &:focus { border-color: transparent; background: transparent; }
}

.checkin-drag-handle {
  cursor: grab;
  color: #6a8faf;
  display: flex;
  align-items: center;
  padding: 2px;
  transition: color 0.2s;
}

.checkin-drag-handle:hover {
  color: #00d4ff;
}

.checkin-drag-handle:active {
  cursor: grabbing;
}

.drag-ghost-row {
  opacity: 0.4;
  background: rgba(0,212,255, 0.08) !important;
}

.drag-ghost-row td {
  background: rgba(0,212,255, 0.08) !important;
}
</style>
