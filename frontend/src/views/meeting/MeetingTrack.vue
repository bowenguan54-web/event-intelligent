<template>
  <div class="page-container track-page">
    <!-- 上部：统计卡片 -->
    <div class="stats-row">
      <el-card v-for="stat in statCards" :key="stat.label" class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-info">
            <span class="stat-value" :style="{ color: stat.color }">{{ stat.value }}</span>
            <span class="stat-label">{{ stat.label }}</span>
          </div>
          <el-progress type="circle" :percentage="stat.percentage" :width="60" :color="stat.color" :stroke-width="5" />
        </div>
      </el-card>
    </div>

    <!-- 中部：图表区 -->
    <div class="charts-row">
      <el-card class="chart-card" shadow="never">
        <template #header>甘特图 - 事项时间线</template>
        <div ref="ganttChartRef" class="chart-container" />
      </el-card>

      <el-card class="chart-card" shadow="never">
        <template #header>趋势对比 - 计划 vs 实际</template>
        <div ref="trendChartRef" class="chart-container" />
      </el-card>
    </div>

    <!-- 下部：明细列片 -->
    <el-card shadow="never">
      <template #header>
        <div class="detail-header">
          <span>事项明细</span>
          <el-button type="primary" size="small" @click="handleGenerateReport" :loading="generatingReport">
            <el-icon><Document /></el-icon>生成闭环报表
          </el-button>
        </div>
      </template>

      <el-table :data="todoDetails" stripe row-key="id">
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="expand-logs">
              <h4>执行日志</h4>
              <el-timeline>
                <el-timeline-item
                  v-for="log in row.logs"
                  :key="log.id"
                  :timestamp="log.time"
                  placement="top"
                >
                  {{ log.content }}
                </el-timeline-item>
              </el-timeline>
              <el-empty v-if="!row.logs?.length" description="暂无日志" :image-size="40" />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="事项" min-width="200" />
        <el-table-column prop="assignee" label="责任人" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="due_date" label="截止日期" width="120" />
        <el-table-column prop="progress" label="进度" width="150">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :color="row.progress >= 100 ? '#00e676' : '#409eff'" :stroke-width="6" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 报表预览弹窗 -->
    <el-dialog v-model="showReport" title="闭环报表预览" width="700px">
      <div v-if="reportData" class="report-preview">
        <h2>{{ reportData.meeting_title }} - 闭环报表</h2>
        <p>生成时间：{{ reportData.generated_at }}</p>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="待办总数">{{ reportData.summary?.total_items }}</el-descriptions-item>
          <el-descriptions-item label="已完成">{{ reportData.summary?.completed }}</el-descriptions-item>
          <el-descriptions-item label="已逾期">{{ reportData.summary?.overdue }}</el-descriptions-item>
          <el-descriptions-item label="完成率">{{ reportData.summary?.completion_rate }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="showReport = false">关闭</el-button>
        <el-button type="primary">导出 PDF</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { getTrackStats, getGanttData, generateReport } from '@/api/track'
import * as echarts from 'echarts'

const route = useRoute()
const meetingId = route.params.id

const ganttChartRef = ref(null)
const trendChartRef = ref(null)

// 统计数据
const stats = ref({ total: 10, completed: 6, in_progress: 2, overdue: 2, completion_rate: 60 })

const statCards = computed(() => [
  { label: '待办总数', value: stats.value.total, percentage: 100, color: '#409eff' },
  { label: '已完成', value: stats.value.completed, percentage: stats.value.completion_rate, color: '#00e676' },
  { label: '进行中', value: stats.value.in_progress, percentage: (stats.value.in_progress / stats.value.total) * 100, color: '#ffab40' },
  { label: '已逾期', value: stats.value.overdue, percentage: (stats.value.overdue / stats.value.total) * 100, color: '#ff5252' },
])

// 明细数据
const todoDetails = ref([
  { id: 1, title: '完成模块联调测试', assignee: '张三', status: 'in_progress', due_date: '2026-03-20', progress: 60, logs: [{ id: 1, time: '2026-03-14', content: '开始联调前端模块' }] },
  { id: 2, title: '协调第三方接口对接', assignee: '李四', status: 'completed', due_date: '2026-03-18', progress: 100, logs: [{ id: 1, time: '2026-03-15', content: '已完成对接' }] },
  { id: 3, title: '编写测试用例', assignee: '王五', status: 'overdue', due_date: '2026-03-12', progress: 30, logs: [] },
  { id: 4, title: '更新部署文档', assignee: '赵六', status: 'pending', due_date: '2026-03-22', progress: 0, logs: [] },
])

// 报表
const generatingReport = ref(false)
const showReport = ref(false)
const reportData = ref(null)

function statusType(s) {
  return { pending: 'info', in_progress: 'primary', completed: 'success', overdue: 'danger' }[s] || 'info'
}

function statusLabel(s) {
  return { pending: '待处理', in_progress: '进行中', completed: '已完成', overdue: '已逾期' }[s] || s
}

async function handleGenerateReport() {
  generatingReport.value = true
  try {
    const res = await generateReport(meetingId)
    reportData.value = res?.data || {
      meeting_title: '项目周例会',
      generated_at: new Date().toLocaleString(),
      summary: { total_items: 10, completed: 6, overdue: 2, completion_rate: '60%' },
    }
    showReport.value = true
  } catch (e) {
    reportData.value = {
      meeting_title: '项目周例会',
      generated_at: new Date().toLocaleString(),
      summary: { total_items: 10, completed: 6, overdue: 2, completion_rate: '60%' },
    }
    showReport.value = true
  } finally {
    generatingReport.value = false
  }
}

let ganttChart = null
let trendChart = null

onMounted(() => {
  nextTick(() => {
    initGanttChart()
    initTrendChart()
  })
})

onUnmounted(() => {
  if (ganttChart) {
    ganttChart.dispose()
    ganttChart = null
  }
  if (trendChart) {
    trendChart.dispose()
    trendChart = null
  }
  window.removeEventListener('resize', handleResize)
})

function handleResize() {
  ganttChart?.resize()
  trendChart?.resize()
}

function initGanttChart() {
  if (!ganttChartRef.value) return
  ganttChart = echarts.init(ganttChartRef.value)

  const categories = ['联调测试', '接口对接', '测试用例', '部署文档']
  const data = [
    { name: '联调测试', value: [0, Date.parse('2026-03-14'), Date.parse('2026-03-20'), 60] },
    { name: '接口对接', value: [1, Date.parse('2026-03-13'), Date.parse('2026-03-18'), 100] },
    { name: '测试用例', value: [2, Date.parse('2026-03-10'), Date.parse('2026-03-12'), 30] },
    { name: '部署文档', value: [3, Date.parse('2026-03-18'), Date.parse('2026-03-22'), 0] },
  ]

  ganttChart.setOption({
    tooltip: { formatter: (p) => `${p.name}: ${p.value[3]}%` },
    grid: { left: 100, right: 40, top: 20, bottom: 30 },
    xAxis: { type: 'time', axisLabel: { formatter: '{MM}-{dd}' } },
    yAxis: { type: 'category', data: categories, inverse: true },
    series: [{
      type: 'custom',
      renderItem: (params, api) => {
        const categoryIndex = api.value(0)
        const start = api.coord([api.value(1), categoryIndex])
        const end = api.coord([api.value(2), categoryIndex])
        const height = api.size([0, 1])[1] * 0.6
        return {
          type: 'rect',
          shape: { x: start[0], y: start[1] - height / 2, width: end[0] - start[0], height },
          style: { fill: api.value(3) >= 100 ? '#00e676' : '#409eff', ...api.style() },
        }
      },
      encode: { x: [1, 2], y: 0 },
      data,
    }],
  })

  window.addEventListener('resize', handleResize)
}

function initTrendChart() {
  if (!trendChartRef.value) return
  trendChart = echarts.init(trendChartRef.value)

  const dates = ['03-10', '03-11', '03-12', '03-13', '03-14', '03-15', '03-16', '03-17', '03-18', '03-19', '03-20']

  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['计划完成', '实际完成'] },
    grid: { left: 40, right: 20, top: 40, bottom: 30 },
    xAxis: { type: 'category', data: dates },
    yAxis: { type: 'value', name: '累计完成数' },
    series: [
      { name: '计划完成', type: 'line', data: [1, 2, 3, 4, 5, 6, 6, 7, 8, 9, 10], smooth: true, lineStyle: { type: 'dashed' }, areaStyle: { opacity: 0.1 } },
      { name: '实际完成', type: 'line', data: [0, 1, 1, 2, 3, 4, 4, 5, 6, 6, 6], smooth: true, areaStyle: { opacity: 0.1 } },
    ],
  })
}
</script>

<style lang="scss" scoped>
.track-page {}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;

  .stat-card {
    .stat-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .stat-info {
      display: flex;
      flex-direction: column;
      .stat-value { font-size: 32px; font-weight: 700; color: #ffffff; }
      .stat-label { font-size: 14px; color: #5e8aad; margin-top: 4px; }
    }
  }
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
  .chart-card .chart-container { height: 280px; }
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.expand-logs {
  padding: 12px 20px;
  h4 { margin: 0 0 8px; font-size: 14px; color: #ffffff; }
}

.report-preview {
  h2 { margin: 0 0 12px; font-size: 20px; color: #ffffff; }
  p { color: #5e8aad; margin-bottom: 16px; }
}
</style>
