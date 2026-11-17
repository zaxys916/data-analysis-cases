<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑案例' : '新建案例'"
    width="640px"
    destroy-on-close
    @closed="reset"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="案例名称" prop="title">
        <el-input v-model="form.title" placeholder="如：Olist 巴西电商数据分析实战" maxlength="200" />
      </el-form-item>
      <el-form-item label="分类" prop="category">
        <el-select v-model="form.category" filterable allow-create default-first-option style="width: 100%">
          <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-radio-group v-model="form.status">
          <el-radio-button value="规划中">规划中</el-radio-button>
          <el-radio-button value="进行中">进行中</el-radio-button>
          <el-radio-button value="已完成">已完成</el-radio-button>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="数据集">
        <el-input v-model="form.dataset" placeholder="如：Kaggle Olist Brazilian E-commerce Dataset" />
      </el-form-item>
      <el-form-item label="技术栈">
        <el-input v-model="form.tech_stack" placeholder="逗号分隔，如：Python, pandas, scikit-learn" />
      </el-form-item>
      <el-form-item label="标签">
        <el-select
          v-model="form.tags"
          multiple
          filterable
          allow-create
          default-first-option
          placeholder="输入后回车创建标签"
          style="width: 100%"
        >
          <el-option v-for="t in tagOptions" :key="t" :label="t" :value="t" />
        </el-select>
      </el-form-item>
      <el-form-item label="案例描述">
        <el-input v-model="form.summary" type="textarea" :rows="4" placeholder="项目背景、分析目标、主要产出等" />
      </el-form-item>
      <el-form-item label="本地路径">
        <el-input v-model="form.path" placeholder="项目文件夹路径，如 D:\study\数据分析\olist实战" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="save">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const props = defineProps({
  categories: { type: Array, default: () => ['电商', '金融', '用户行为', '预测建模', '其他'] },
  tagOptions: { type: Array, default: () => [] },
})
const emit = defineEmits(['saved'])

const visible = ref(false)
const saving = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const formRef = ref(null)

const emptyForm = () => ({
  title: '', category: '电商', status: '规划中',
  dataset: '', tech_stack: '', tags: [], summary: '', path: '',
})
const form = reactive(emptyForm())

const rules = {
  title: [{ required: true, message: '请输入案例名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
}

function open(caseData = null) {
  visible.value = true
  if (caseData) {
    isEdit.value = true
    editId.value = caseData.id
    Object.assign(form, caseData)
  }
}

function reset() {
  isEdit.value = false
  editId.value = null
  Object.assign(form, emptyForm())
  formRef.value?.clearValidate()
}

async function save() {
  await formRef.value?.validate().catch(() => Promise.reject())
  saving.value = true
  try {
    if (isEdit.value) {
      await api.put(`/cases/${editId.value}`, form)
      ElMessage.success('案例已更新')
    } else {
      await api.post('/cases', form)
      ElMessage.success('案例已创建')
    }
    visible.value = false
    emit('saved')
  } finally {
    saving.value = false
  }
}

defineExpose({ open })
</script>
