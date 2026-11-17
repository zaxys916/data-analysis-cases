<template>
  <div>
    <!-- 指标卡 -->
    <el-row :gutter="16">
      <el-col :span="6" v-for="m in metricCards" :key="m.label">
        <el-card shadow="never" class="metric-card">
          <div class="metric-row">
            <el-icon :size="34" :color="m.color"><component :is="m.icon" /></el-icon>
            <div>
              <div class="metric-value">{{ m.value }}</div>
              <div class="metric-label">{{ m.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表 -->
    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header><b>状态分布</b></template>
          <div ref="statusChart" class="chart" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header><b>分类分布</b></template>
          <div ref="categoryChart" class="chart" />
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="24">
        <el-card shadow="never">
          <template #header><b>高频标签 TOP10</b></template>
          <div ref="tagChart" class="chart tall" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { DataAnalysis, Files, Notebook, TrendCharts } from '@element-plus/icons-vue'
import api from '../api'

const stats = ref(null)
const statusChart = ref(null)
const categoryChart = ref(null)
const tagChart = ref(null)

const metricCards = computed(() => {
  const s = stats.value
  return [
    { label: '案例总数', value: s?.total ?? 0, icon: Files, color: '#409eff' },
    { label: '已完成', value: s?.done ?? 0, icon: DataAnalysis, color: '#67c23a' },
    { label: '完成率', value: (s?.completion_rate ?? 0) + '%', icon: TrendCharts, color: '#e6a23c' },
    { label: '分类数', value: Object.keys(s?.by_category ?? {}).length, icon: Notebook, color: '#f56c6c' },
  ]
})

const STATUS_COLORS = { 规划中: '#909399', 进行中: '#e6a23c', 已完成: '#67c23a' }

function renderCharts(s) {
  if (!s) return
  // 状态分布 - 环形图
  echarts.init(statusChart.value).setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} 个 ({d}%)' },
    legend: { bottom: 0 },
    series: [
      {
        type: 'pie',
        radius: ['45%', '68%'],
        center: ['50%', '45%'],
        itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
        data: Object.entries(s.by_status).map(([name, value]) => ({
          name,
          value,
          itemStyle: { color: STATUS_COLORS[name] || '#409eff' },
        })),
      },
    ],
  })

  // 分类分布 - 柱状图
  const cats = Object.entries(s.by_category)
  echarts.init(categoryChart.value).setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 16, top: 24, bottom: 56 },
    xAxis: { type: 'category', data: cats.map(([k]) => k), axisLabel: { rotate: 20 } },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        type: 'bar',
        barMaxWidth: 40,
        itemStyle: { color: '#409eff', borderRadius: [4, 4, 0, 0] },
        data: cats.map(([, v]) => v),
      },
    ],
  })

  // 高频标签 - 条形图
  const tags = Object.entries(s.top_tags).reverse()
  echarts.init(tagChart.value).setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 110, right: 30, top: 16, bottom: 24 },
    xAxis: { type: 'value', minInterval: 1 },
    yAxis: { type: 'category', data: tags.map(([k]) => k) },
    series: [
      {
        type: 'bar',
        barMaxWidth: 22,
        itemStyle: { color: '#e6a23c', borderRadius: [0, 4, 4, 0] },
        data: tags.map(([, v]) => v),
      },
    ],
  })
}

onMounted(async () => {
  stats.value = await api.get('/stats').then((r) => r.data)
  renderCharts(stats.value)
})
watch(stats, renderCharts)
</script>

<style scoped>
.metric-card :deep(.el-card__body) { padding: 20px; }
.metric-row { display: flex; align-items: center; gap: 14px; }
.metric-value { font-size: 26px; font-weight: 700; color: #303133; }
.metric-label { font-size: 13px; color: #909399; margin-top: 2px; }
.chart { height: 300px; }
.chart.tall { height: 340px; }
</style>
