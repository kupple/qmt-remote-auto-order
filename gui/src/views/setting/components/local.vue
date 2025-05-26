<template>
  <div class="setting-container">
    <div v-if="isWSConnectedState === 1" class="tips-view">远程服务连接正常</div>
    <div class="setting-form">
      <el-form :disabled="isWSConnectedState === 1" label-width="auto" :model="params" :rules="rules" ref="formRef">
        <el-form-item class="el-form-item__content" required label="远程服务器地址" prop="server_url">
          <el-input v-model="params.server_url" placeholder="请输入远程服务器地址" />
          <el-tooltip effect="dark" content="仅支持ws/wss协议格式如: ws://192.112.151.12:8080/ws" placement="top">
            <el-icon style="margin-left: 10px; color: #999; font-size: 18px"><QuestionFilled /></el-icon>
          </el-tooltip>
        </el-form-item>
        <el-form-item label="QMT路径" prop="qmtPath" required>
          <span class="path" v-if="hasBeenSelect == 1">{{ params.qmtPath }}</span>
          <el-button v-if="hasBeenSelect == 0" type="primary" @click="chooseDirectoryAction">打开目录</el-button>
          <el-button v-if="hasBeenSelect == 1" type="primary" @click="connectionAction" style="margin-left: 10px">获取资金账号</el-button>
          <el-button style="margin-left: 0px" v-if="hasBeenSelect == 1" type="danger" @click="chooseDirectoryAction">重置</el-button>
          <el-tooltip effect="dark" content="示例: D:\长城策略交易系统\userdata_mini" placement="top">
            <el-icon style="margin-left: 10px; color: #999; font-size: 18px"><QuestionFilled /></el-icon>
          </el-tooltip>
        </el-form-item>
        <el-form-item label="客户编号" prop="clientId" required>
          <el-select v-if="passStatus !== 2" :disabled="passStatus === 0" v-model="params.clientId" placeholder="请选择客户编号ID" required>
            <el-option v-for="item in accountArr" :key="item" :label="item" :value="item" />
          </el-select>
          <el-input v-else v-model="params.clientId" placeholder="请输入客户编号ID" required />
          <el-tooltip effect="dark" content="示例: 121600018888" placement="top">
            <el-icon style="margin-left: 10px; color: #999; font-size: 18px"><QuestionFilled /></el-icon>
          </el-tooltip>
        </el-form-item>
        <el-form-item label="加密盐/用于加密通信" prop="salt" required>
          <el-input v-model="params.salt" placeholder="请输入加密盐" required />
          <el-tooltip effect="dark" content="请与远程服务器一致" placement="top">
            <el-icon style="margin-left: 10px; color: #999; font-size: 18px"><QuestionFilled /></el-icon>
          </el-tooltip>
        </el-form-item>

        <el-form-item label="qmt客户端是否打开" required>
          <div v-if="isQMTProcessExit == true" class="footer-cell">
            <el-tag type="success">mini迅投客户端已打开</el-tag>
          </div>
          <div v-else class="footer-cell">
            <el-tag type="danger">mini迅投客户端暂未打开</el-tag>
          </div>
        </el-form-item>
      </el-form>

      <!-- <el-divider /> -->
      <el-button v-if="isWSConnectedState === 0" class="save-btn" @click="saveAction" type="primary">确定 / 连接</el-button>
      <el-button v-else-if="isWSConnectedState === 2" class="save-btn" type="primary" disabled>正在连接</el-button>
      <el-button v-else class="save-btn" @click="disconnectAction" type="danger">断开连接</el-button>
      <el-button v-if="isWSConnectedState === 0" class="save-btn" @click="backAction">返回上一页</el-button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRemoteStore } from '@/store/remote.js'
import { useRoute, useRouter } from 'vue-router'
const router = useRouter()
import { getSettingConfig, saveConfig, connectWs, disconnect, getRemoteState, chooseDirectory,connectQMT } from '@/api/comm_tube'
import { QuestionFilled } from '@element-plus/icons-vue'
import { useCommonStore } from '@/store/common.js'
import { CircleCheckFilled, CircleCloseFilled } from '@element-plus/icons-vue'
import { testQMTConnect } from '@/api/comm_tube'

const isQMTProcessExit = computed(() => useCommonStore().isQMTProcessExit)

const formRef = ref(null)

const remoteStoreDic = computed(() => {
  return useRemoteStore()
})

const isWSConnectedState = computed(() => useRemoteStore().connectState)

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

const getRemoteStateAction = async () => {
  const res = await getRemoteState()
  useRemoteStore().setRemoteStore({
    state: res.state == true ? 1 : 0,
    unique_id: res.unique_id
  })
}

const rules = {
  qmtPath: [{ required: true, message: '请输入QMT路径', trigger: 'blur' }],
  clientId: [{ required: true, message: '请输入客户编号ID', trigger: 'blur' }],
  server_url: [{ required: true, message: '请输入远程服务器地址', trigger: 'blur' }],
  salt: [{ required: true, message: '请输入加密盐', trigger: 'blur' }]
}

const accountArr = ref([])
const hasBeenSelect = ref(false)
const passStatus = ref(0)

const params = reactive({
  qmtPath: '',
  clientId: '',
  server_url: '',
  salt: ''
})

const saveAction = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    if (isQMTProcessExit.value == false) {
      ElMessage({
        message: '请手动打开miniqmt',
        type: 'error'
      })
      return
    }
    await saveConfig({
      mini_qmt_path: params.qmtPath,
      client_id: params.clientId,
      server_url: params.server_url,
      salt: params.salt,
      run_model_type: 1
    })
    ElMessage({
      message: '连接成功',
      type: 'success'
    })
    useRemoteStore().changeConnectState(2)
    await connectQMT({ mini_qmt_path: params.qmtPath, client_id: params.clientId })
    await connectWs(params.server_url,1)
  } catch (error) {
    console.log(error)
    ElMessage({
      message: '请填写完整的表单信息',
      type: 'error'
    })
  }
}

// 获取配置文件
const getSetting = async () => {
  const res = await getSettingConfig()
  params.qmtPath = res.mini_qmt_path
  params.clientId = res.client_id
  params.salt = res.salt
  params.server_url = res.server_url
  if (res.mini_qmt_path) {
    hasBeenSelect.value = true
  } else {
    hasBeenSelect.value = false
  }
}

const backAction = async () => {
  await saveConfig({
    run_model_type: 0
  })
  router.push('/setting/login')
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

const disconnectAction = () => {
  ElMessageBox.confirm('确定要断开连接吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(() => {
      saveConfig({
        run_model_type: 0
      })
      disconnect().then((res) => {
        console.log(res)
        ElMessage.success('断开连接成功')
      })
    })
    .catch(() => {
      // 用户点击取消，不做任何操作
    })
}

onMounted(async () => {
  await getSetting()
  await getRemoteStateAction()
})
</script>

<style scoped lang="less">
.setting-container {
  display: flex;
  align-items: center;
  height: 100vh;
  flex-direction: column;
  background-color: #f5f5f5;
  position: relative;
  // justify-content: center;
}
.setting-form {
  display: flex;
  flex-direction: column;
  width: 60vw;
  background: #fff;
  border-radius: 10px;
  padding: 20px;
  position: relative;
  justify-content: center;
  // align-items: center;
  margin-top: 10%;
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
  width: 80%;
  margin-top: 10px;
  align-self: center;
  margin-left: 0px;
}
.tips-view {
  width: 100%;
  height: 30px;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  background: rgb(114, 205, 131);
  font-size: 12px;
  color: #fff;
  font-weight: bold;
  line-height: 30px;
  padding-left: 10px;
}
.path {
  white-space: nowrap; /* 禁止换行 */
  overflow: hidden; /* 隐藏溢出内容 */
  text-overflow: ellipsis; /* 超出部分显示省略号 */
  display: inline-block; /* 使宽度约束生效（必要时） */
}
</style>
