<template>
  <div v-loading="loading">
    <el-page-header class="page-header" @back="router.back()">
      <template #content>
        <span class="detail-title">{{ c.title }}</span>
      </template>
      <template #extra>
        <el-button type="primary" :icon="Edit" @click="formRef.open(c)">编辑案例</el-button>
      </template>
    </el-page-header>

    <el-row :gutter="16">
      <!-- 左：案例信息 -->
      <el-col :span="9">
        <el-card shadow="never" class="block">
          <template #header><b>案例信息</b></template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="分类">
              <el-tag size="small" type="info">{{ c.category }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag size="small" :type="statusType(c.status)">{{ c.status }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="数据集">{{ c.dataset || '-' }}</el-descriptions-item>
            <el-descriptions-item label="技术栈">
              <el-tag
                v-for="t in techList"
                :key="t"
                size="small"
                effect="plain"
                style="margin-right: 6px"
              >{{ t }}</el-tag>
              <span v-if="!techList.length">-</span>
            </el-descriptions-item>
            <el-descriptions-item label="标签">
              <el-tag v-for="t in c.tags" :key="t" size="small" type="warning" style="margin-right: 6px">{{ t }}</el-tag>
              <span v-if="!c.tags.length">-</span>
            </el-descriptions-item>
            <el-descriptions-item label="本地路径">
              <span class="path">{{ c.path || '-' }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ c.created_at?.slice(0, 19).replace('T', ' ') }}</el-descriptions-item>
          </el-descriptions>
          <el-divider />
          <h4 class="section-title">案例描述</h4>
          <p class="summary">{{ c.summary || '暂无描述' }}</p>
        </el-card>
      </el-col>

      <!-- 右：分析笔记 -->
      <el-col :span="15">
        <el-card shadow="never" class="block">
          <template #header>
            <div class="note-head">
              <b>分析笔记 / 复盘</b>
              <el-button size="small" type="primary" :icon="Plus" @click="noteForm = { title: '', content: '' }; noteVisible = true">
                写笔记
              </el-button>
            </div>
          </template>
          <el-empty v-if="!notes.length" description="还没有笔记，点击「写笔记」记录分析过程与结论" />
          <div v-for="n in notes" :key="n.id" class="note-item">
            <div class="note-item-head">
              <span class="note-title">{{ n.title }}</span>
              <el-popconfirm title="确认删除该笔记？" width="180" @confirm="removeNote(n.id)">
                <template #reference>
                  <el-button text type="danger" size="small" :icon="Delete">删除</el-button>
                </template>
              </el-popconfirm>
            </div>
            <p class="note-content">{{ n.content }}</p>
            <span class="note-time">{{ n.created_at.replace('T', ' ').slice(0, 19) }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 编辑案例 -->
    <CaseForm ref="formRef" :categories="categoryOptions" :tag-options="tagOptions" @saved="load" />

    <!-- 写笔记 -->
    <el-dialog v-model="noteVisible" title="写笔记" width="560px" destroy-on-close>
      <el-form label-width="70px">
        <el-form-item label="标题">
          <el-input v-model="noteForm.title" placeholder="如：核心结论复盘、踩坑记录" maxlength="200" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="noteForm.content" type="textarea" :rows="8" placeholder="分析步骤、关键结论、心得体会…" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="noteVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingNote" @click="saveNote">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Delete, Edit, Plus } from '@element-plus/icons-vue'
import api from '../api'
import CaseForm from '../components/CaseForm.vue'

const route = useRoute()
const router = useRouter()
const caseId = route.params.id

const loading = ref(false)
const c = ref({ tags: [] })
const notes = ref([])
const formRef = ref(null)
const categoryOptions = ref([])
const tagOptions = ref([])

const noteVisible = ref(false)
const savingNote = ref(false)
const noteForm = reactive({ title: '', content: '' })

const techList = computed(() =>
  (c.value.tech_stack || '').split(',').map((s) => s.trim()).filter(Boolean),
)

function statusType(status) {
  return { 规划中: 'info', 进行中: 'warning', 已完成: 'success' }[status] || 'info'
}

async function load() {
  loading.value = true
  try {
    const [caseRes, noteRes, allRes] = await Promise.all([
      api.get(`/cases/${caseId}`),
      api.get(`/cases/${caseId}/notes`),
      api.get('/cases'),
    ])
    c.value = caseRes.data
    notes.value = noteRes.data
    categoryOptions.value = [...new Set(allRes.data.map((x) => x.category))]
    tagOptions.value = [...new Set(allRes.data.flatMap((x) => x.tags))]
  } catch {
    ElMessage.error('案例不存在或已删除')
    router.replace('/cases')
  } finally {
    loading.value = false
  }
}

async function saveNote() {
  if (!noteForm.title.trim()) {
    ElMessage.warning('请输入笔记标题')
    return
  }
  savingNote.value = true
  try {
    await api.post(`/cases/${caseId}/notes`, noteForm)
    ElMessage.success('笔记已保存')
    noteVisible.value = false
    notes.value = await api.get(`/cases/${caseId}/notes`).then((r) => r.data)
  } finally {
    savingNote.value = false
  }
}

async function removeNote(id) {
  await api.delete(`/notes/${id}`)
  ElMessage.success('笔记已删除')
  notes.value = await api.get(`/cases/${caseId}/notes`).then((r) => r.data)
}

onMounted(load)
</script>

<style scoped>
.page-header { margin-bottom: 16px; }
.detail-title { font-size: 16px; font-weight: 600; }
.block { min-height: 300px; }
.section-title { margin-bottom: 8px; color: #303133; }
.summary { font-size: 13px; color: #606266; line-height: 1.8; white-space: pre-wrap; }
.path { font-size: 12px; color: #909399; word-break: break-all; }

.note-head { display: flex; justify-content: space-between; align-items: center; }
.note-item { padding: 12px 0; border-bottom: 1px solid #f0f2f5; }
.note-item:last-of-type { border-bottom: none; }
.note-item-head { display: flex; justify-content: space-between; align-items: center; }
.note-title { font-size: 14px; font-weight: 600; color: #303133; }
.note-content {
  font-size: 13px;
  color: #606266;
  line-height: 1.8;
  white-space: pre-wrap;
  margin: 8px 0;
}
.note-time { font-size: 12px; color: #c0c4cc; }
</style>
