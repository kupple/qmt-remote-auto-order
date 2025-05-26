<template>
  <el-dialog v-model="dialogVisible" title="基本设置" width="60vw" center>
    <el-form label-width="auto" :model="params" :rules="rules" ref="formRef">
      <el-form-item class="el-form-item__content" label="QMT路径" prop="qmtPath" required>
        <span class="path" v-if="hasBeenSelect == 1">{{ params.qmtPath }}</span>
        <el-button v-if="hasBeenSelect == 0" type="primary" @click="chooseDirectoryAction">打开目录</el-button>
        <el-button v-if="hasBeenSelect == 1" type="primary" @click="connectionAction" style="margin-left: 10px">获取资金账号</el-button>
        <el-button style="margin-left:0px" v-if="hasBeenSelect == 1" type="danger" @click="chooseDirectoryAction">重置</el-button>
        <el-tooltip effect="dark" content="示例: D:\长城策略交易系统\userdata_mini" placement="top">
          <el-icon style="margin-left: 10px; color: #999; font-size: 18px"><QuestionFilled /></el-icon>
        </el-tooltip>
      </el-form-item>
      <el-form-item label="客户编号" prop="clientId" required>
        <el-select v-if="passStatus !== 2" :disabled="passStatus === 0" v-model="params.clientId" placeholder="请选择客户编号ID" required>
          <el-option v-for="item in accountArr" :key="item" :label="item" :value="item" />
        </el-select>
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
import { getSettingConfig, saveConfig, testQMTConnect, connectQMT, chooseDirectory } from '@/api/comm_tube'
const formRef = ref(null)
const dialogVisible = ref(false)
const emit = defineEmits(['callBack'])
const passStatus = ref(0)
const accountArr = ref([])
const hasBeenSelect = ref(false)

const connectionAction = () => {
  testQMTConnect(params.qmtPath).then((res) => {
    if (res.is_connect) {
      if (res.account_arr.length == 0) {
        ElMessage({
          message: '获取的资金数量为0 请重新登录MiniQMT客户端',
          type: 'error'
        })
        passStatus.value = 2
        return
      }
      accountArr.value = res.account_arr
      ElMessage({
        message: '连接成功请选择资金编号',
        type: 'success'
      })
      passStatus.value = 1
    } else {
      ElMessage({
        message: '请检查QMT路径是否正确',
        type: 'error'
      })
      passStatus.value = 0
    }
  })
}

const chooseDirectoryAction = async () => {
  const res = await chooseDirectory()
  if (res[0] == true) {
    ElMessage.success('该目录通过验证')
    params.qmtPath = res[1]
    hasBeenSelect.value = 1
  } else {
    ElMessage.error('请选择正确的目录地址')
    hasBeenSelect.value = 0
  }
}

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
  if(res.mini_qmt_path){
    hasBeenSelect.value = true
  }else{
    hasBeenSelect.value = false
  }
}

const showModal = () => {
  dialogVisible.value = true
  getSetting()
}

const saveConfigAction = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    const testDic = await testQMTConnect(params.qmtPath, params.clientId)
    if (!testDic.is_connect) {
      ElMessage({
        message: testDic.msg,
        type: 'error'
      })
      return
    }
    await connectQMT({ mini_qmt_path: params.qmtPath, client_id: params.clientId })
    await saveConfig({
      mini_qmt_path: params.qmtPath,
      client_id: params.clientId
    })
    ElMessage({
      message: '保存成功',
      type: 'success'
    })
    dialogVisible.value = false
    emit('callBack')
  } catch (error) {
    console.log(error)
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
.el-select {
  flex: 1;
}
.save-btn {
  width: 100%;
}
.path {
  white-space: nowrap; /* 禁止换行 */
  overflow: hidden; /* 隐藏溢出内容 */
  text-overflow: ellipsis; /* 超出部分显示省略号 */
  display: inline-block; /* 使宽度约束生效（必要时） */
}
</style>
