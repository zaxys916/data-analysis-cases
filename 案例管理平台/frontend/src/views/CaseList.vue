<template>
  <div>
    <!-- 筛选栏 -->
    <el-card shadow="never" class="filter-card">
      <div class="filters">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索名称 / 描述 / 数据集"
          clearable
          style="width: 260px"
          :prefix-icon="Search"
          @change="load"
        />
        <el-select v-model="filters.category" placeholder="分类" clearable style="width: 140px" @change="load">
          <el-option v-for="c in categoryOptions" :key="c" :label="c" :value="c" />
        </el-select>
        <el-select v-model="filters.status" placeholder="状态" clearable style="width: 120px" @change="load">
          <el-option label="规划中" value="规划中" />
          <el-option label="进行中" value="进行中" />
          <el-option label="已完成" value="已完成" />
        </el-select>
        <el-select v-model="filters.tag" placeholder="标签" clearable filterable style="width: 160px" @change="load">
          <el-option v-for="t in tagOptions" :key="t" :label="t" :value="t" />
        </el-select>
        <div class="spacer" />
        <el-button :icon="Refresh" :loading="scanning" @click="doScan(false)">扫描文件夹</el-button>
        <el-button type="primary" :icon="Plus" @click="formRef.open()">新建案例</el-button>
      </div>
    </el-card>

    <!-- 案例卡片列表 -->
    <div v-loading="loading" class="case-grid">
      <el-empty v-if="!loading && cases.length === 0" description="暂无案例，点击右上角「新建案例」开始" class="empty" />
      <el-card v-for="c in cases" :key="c.id" shadow="hover" class="case-card" @click="goDetail(c.id)">
        <div class="card-head">
          <span class="card-title">{{ c.title }}</span>
          <el-tag :type="statusType(c.status)" size="small">{{ c.status }}</el-tag>
        </div>
        <div class="card-meta">
          <el-tag size="small" effect="plain" type="info">{{ c.category }}</el-tag>
          <span v-if="c.dataset" class="meta-text" :title="c.dataset">{{ c.dataset }}</span>
        </div>
        <p class="card-summary">{{ c.summary || '暂无描述' }}</p>
        <div class="card-tags">
          <el-tag v-for="t in c.tags" :key="t" size="small" type="warning" effect="light">{{ t }}</el-tag>
        </div>
        <div class="card-foot" @click.stop>
          <span class="time">{{ c.updated_at.slice(0, 10) }}</span>
          <div>
            <el-button text type="primary" size="small" @click="formRef.open(c)">编辑</el-button>
            <el-popconfirm title="删除后不可恢复，确认删除？" width="220" @confirm="remove(c.id)">
              <template #reference>
                <el-button text type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </div>
        </div>
      </el-card>
    </div>

    <CaseForm ref="formRef" :categories="categoryOptions" :tag-options="tagOptions" @saved="load" />
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElNotification } from 'element-plus'
import { Plus, Refresh, Search } from '@element-plus/icons-vue'
import api from '../api'
import CaseForm from '../components/CaseForm.vue'

const router = useRouter()
const loading = ref(false)
const scanning = ref(false)
const cases = ref([])
const formRef = ref(null)
const categoryOptions = ref([])
const tagOptions = ref([])

const filters = reactive({ keyword: '', category: '', status: '', tag: '' })

async function load() {
  loading.value = true
  try {
    const params = Object.fromEntries(Object.entries(filters).filter(([, v]) => v))
    cases.value = await api.get('/cases', { params }).then((r) => r.data)
    // 从全部案例中汇总分类 / 标签选项
    const all = await api.get('/cases').then((r) => r.data)
    categoryOptions.value = [...new Set(all.map((c) => c.category))]
    tagOptions.value = [...new Set(all.flatMap((c) => c.tags))]
  } finally {
    loading.value = false
  }
}

async function remove(id) {
  await api.delete(`/cases/${id}`)
  ElMessage.success('已删除')
  load()
}

function statusType(status) {
  return { 规划中: 'info', 进行中: 'warning', 已完成: 'success' }[status] || 'info'
}

function goDetail(id) {
  router.push(`/cases/${id}`)
}

async function doScan(notify = true) {
  scanning.value = true
  try {
    const { added, missing } = await api.post('/scan').then((r) => r.data)
    if (added.length) {
      ElNotification.success({
        title: '扫描完成',
        message: `自动导入 ${added.length} 个新案例：${added.join('、')}`,
        duration: 5000,
      })
    } else if (notify) {
      ElMessage.info('未发现新案例文件夹')
    }
    if (missing.length) {
      ElNotification.warning({
        title: '存在失效案例',
        message: `${missing.length} 个案例的文件夹已不存在：${missing.map((m) => m.title).join('、')}`,
        duration: 0,
      })
    }
    load()
  } finally {
    scanning.value = false
  }
}

onMounted(() => doScan(false))
</script>

<style scoped>
.filter-card { margin-bottom: 16px; }
.filters { display: flex; gap: 12px; align-items: center; }
.spacer { flex: 1; }

.case-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
  min-height: 200px;
}
.empty { grid-column: 1 / -1; }
.case-card { cursor: pointer; transition: transform 0.15s; }
.case-card:hover { transform: translateY(-2px); }

.card-head { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.card-meta { display: flex; align-items: center; gap: 8px; margin: 8px 0 4px; }
.meta-text {
  font-size: 12px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.card-summary {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  margin: 4px 0 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 42px;
}
.card-tags { display: flex; flex-wrap: wrap; gap: 6px; min-height: 20px; }
.card-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid #f0f2f5;
}
.time { font-size: 12px; color: #c0c4cc; }
</style>
