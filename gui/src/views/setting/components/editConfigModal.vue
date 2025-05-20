<template>
  <el-dialog v-model="dialogVisible" title="基本设置" width="50vw" center>
    <el-form label-width="auto" :model="params" :rules="rules" ref="formRef">
      <el-form-item label="QMT路径" prop="qmtPath" required>
        <el-input v-model="params.qmtPath" placeholder="请输入QMT安装路径" required />
        <el-tooltip effect="dark" content="示例: D:\长城策略交易系统\userdata_mini" placement="top">
          <el-icon style="margin-left: 10px; color: #999; font-size: 18px"><QuestionFilled /></el-icon>
        </el-tooltip>
      </el-form-item>
      <el-form-item label="客户编号" prop="clientId" required>
        <el-input v-model="params.clientId" placeholder="请输入客户编号ID" required />
        <el-tooltip effect="dark" content="示例: 121600018888" placement="top">
          <el-icon style="margin-left: 10px; color: #999; font-size: 18px"><QuestionFilled /></el-icon>
        </el-tooltip>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" class="save-btn" @click="saveConfigAction">保存</el-button>
      </el-form-item>
    </el-form>
  </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'
import { getSettingConfig, saveConfig } from '@/api/comm_tube'
const formRef = ref(null)
const dialogVisible = ref(false)
const emit = defineEmits(['callBack'])
const rules = {
  qmtPath: [{ required: true, message: '请输入QMT路径', trigger: 'blur' }],
  clientId: [{ required: true, message: '请输入客户编号ID', trigger: 'blur' }]
}

const params = reactive({
  qmtPath: '',
  clientId: ''
})

const getSetting = async () => {
  const res = await getSettingConfig()
  params.qmtPath = res.mini_qmt_path
  params.clientId = res.client_id
}

const showModal = () => {
  dialogVisible.value = true
  getSetting()
}

const saveConfigAction = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    await saveConfig({
      mini_qmt_path: params.qmtPath,
      client_id: params.clientId,
      run_model_type: 1
    })
    ElMessage({
      message: '保存成功',
      type: 'success'
    })
    dialogVisible.value = false
    emit('callBack')
  } catch (error) {
    ElMessage({
      message: '请填写完整的表单信息',
      type: 'error'
    })
  }
}

defineExpose({
  showModal
})
</script>

<style scoped lang="less">
.list-container-modal {
  padding: 20px;
  background: #fff;
}
.el-form-item__content {
  display: flex !important;
  align-items: center !important;
  flex-wrap: nowrap !important;
}
.el-input {
  flex: 1;
}
.save-btn {
  width: 100%;
}
</style>
