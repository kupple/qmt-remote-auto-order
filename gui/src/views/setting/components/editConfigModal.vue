<template>
  <el-dialog v-model="dialogVisible" title="基本设置" width="60vw" center>
    <el-form label-width="auto" :model="params" :rules="rules" ref="formRef">
      <el-form-item label="下单方式" prop="client_type">
        <el-radio-group v-model="params.client_type">
          <!-- <el-radio-button label="同花顺下单模式" :value="1" /> -->
          <el-radio-button label="QMT下单模式" :value="2" />
        </el-radio-group>
      </el-form-item>
      <el-form-item class="el-form-item__content" label="同花顺目录" prop="ths_path" required v-if="params.client_type == 1">
        <span class="path">{{ params.ths_path }}</span>
        <el-button type="primary" style="margin-left: 10px" @click="chooseDirectoryAction">选择目录</el-button>
        <el-button style="margin-left: 0px" type="danger" @click="chooseDirectoryAction">重置</el-button>
        <el-tooltip effect="dark" content="示例: D:\同花顺" placement="top">
          <el-icon style="margin-left: 10px; color: #999; font-size: 18px"><QuestionFilled /></el-icon>
        </el-tooltip>
      </el-form-item>
      <el-form-item label="交易账号" prop="ths_client_id" v-if="params.client_type == 1">
        <el-input v-model="params.ths_client_id" placeholder="请输入同花顺账号" required />
        <el-tooltip effect="dark" content="示例: 121600018888" placement="top">
          <el-icon style="margin-left: 10px; color: #999; font-size: 18px"><QuestionFilled /></el-icon>
        </el-tooltip>
      </el-form-item>
      <el-form-item label="交易密码" prop="ths_pwd" v-if="params.client_type == 1">
        <el-input v-model="params.ths_pwd" placeholder="请输入同花顺密码" required />
        <el-tooltip effect="dark" content="示例: 121600018888" placement="top">
          <el-icon style="margin-left: 10px; color: #999; font-size: 18px"><QuestionFilled /></el-icon>
        </el-tooltip>
      </el-form-item>
      <div v-if="params.client_type == 1" style="margin-left: 10px; color: red; margin-bottom: 10px">⚠️⚠️注意：资金账号密码仅作为自动登录用！不会上传至服务器,不信任可不输入⚠️⚠️</div>
      <el-form-item class="el-form-item__content" label="QMT路径" prop="mini_qmt_path" required v-if="params.client_type == 2">
        <span class="path" v-if="hasQmtBeenSelect == 1">{{ params.mini_qmt_path }}</span>
        <el-button v-if="hasQmtBeenSelect == 0" type="primary" @click="chooseDirectoryAction">打开目录</el-button>
        <el-button v-if="hasQmtBeenSelect == 1" type="primary" @click="connectionAction" style="margin-left: 10px">获取资金账号</el-button>
        <el-button style="margin-left: 0px" v-if="hasQmtBeenSelect == 1" type="danger" @click="chooseDirectoryAction">重置</el-button>
        <el-tooltip effect="dark" content="示例: D:\长城策略交易系统" placement="top">
          <el-icon style="margin-left: 10px; color: #999; font-size: 18px"><QuestionFilled /></el-icon>
        </el-tooltip>
      </el-form-item>
      <el-form-item label="客户编号" prop="client_id" required v-if="params.client_type == 2">
        <el-select v-if="passStatus !== 2" :disabled="passStatus === 0" v-model="params.client_id" placeholder="请选择客户编号ID" required>
          <el-option v-for="item in accountArr" :key="item" :label="item" :value="item" />
        </el-select>
        <el-tooltip effect="dark" content="示例: 121600018888" placement="top">
          <el-icon style="margin-left: 10px; color: #999; font-size: 18px"><QuestionFilled /></el-icon>
        </el-tooltip>
      </el-form-item>
    </el-form>
    <div class="btn-container">
      <el-button type="danger" v-if="params.client_type == 1" class="test-btn" @click="testThsConfigAction">测试</el-button>
      <el-button type="primary" class="save-btn" @click="saveConfigAction">保存</el-button>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'
import { getSettingConfig, saveConfig, testConnect, connectQMT, chooseDirectory } from '@/api/comm_tube'
const formRef = ref(null)
const dialogVisible = ref(false)
const emit = defineEmits(['callBack'])
const passStatus = ref(0)
const accountArr = ref([])
const hasQmtBeenSelect = ref(false)

const connectionAction = () => {
  testConnect(params.mini_qmt_path).then((res) => {
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

const testThsConfigAction= () => {
  testConnect(params.ths_path, params.client_type).then((res) => {
    if (res.is_connect) {
      ElMessage({
        message: '连接成功',
        type: 'success'
      })
    } else {
      ElMessage({
        message: '请检查同花顺路径是否正确',
        type: 'error'
      })
    }
  })
}

const chooseDirectoryAction = async () => {
  const res = await chooseDirectory(params.client_type)
  if (res[0] == true) {
    ElMessage.success('该目录通过验证')
    if (params.client_type == 2) {
      params.mini_qmt_path = res[1]
      hasQmtBeenSelect.value = 1
    } else {
      params.ths_path = res[1]
    }
  } else {
    ElMessage.error('请选择正确的目录地址')
    hasQmtBeenSelect.value = 0
  }
}

const chooseThsDirectoryAction = () => {}

const rules = {
  mini_qmt_path: [{ required: true, message: '请输入QMT路径', trigger: 'blur' }],
  client_id: [{ required: true, message: '请输入客户编号ID', trigger: 'blur' }],
  ths_path: [{ required: true, message: '请选择同花顺路径', trigger: 'blur' }],
  ths_client_id: [{ required: false, message: '请输入同花顺账号', trigger: 'blur' }],
  ths_pwd: [{ required: false, message: '请输入同花顺密码', trigger: 'blur' }]
}

const params = reactive({
  mini_qmt_path: '',
  client_id: '',
  client_type: 2,
  ths_path: '',
  ths_client_id: '',
  ths_pwd: ''
})

const getSetting = async () => {
  const res = await getSettingConfig()
  params.mini_qmt_path = res.mini_qmt_path
  params.client_id = res.client_id
  params.client_type = res.client_type
  params.ths_path = res.ths_path
  params.ths_client_id = res.ths_client_id
  params.ths_pwd = res.ths_pwd
  if (res.mini_qmt_path) {
    hasQmtBeenSelect.value = true
  } else {
    hasQmtBeenSelect.value = false
  }
}

const showModal = () => {
  dialogVisible.value = true
  getSetting()
}

const saveConfigAction = async () => {
  if (!formRef.value) return
  try {
    // 表单验证
    if (params.client_type === 2) {
      if (!params.mini_qmt_path || params.mini_qmt_path == '' || !params.client_id || params.client_id == '') {
        ElMessage({
          message: '请输入QMT路径和客户编号',
          type: 'error'
        })
        return
      }
    } else {
      if (!params.ths_path || params.ths_path == '') {
        ElMessage({
          message: '请输入同花顺路径',
          type: 'error'
        })
        return
      }
    }
    // 连接测试
    if (params.client_type == 2) {
      const testDic = await testConnect(params.mini_qmt_path, params.client_type)
      if (!testDic.is_connect) {
        ElMessage({
          message: testDic.msg,
          type: 'error'
        })
        return
      }
    } else {
      const testDic = await testConnect(params.ths_path, params.client_type)
      // if (!testDic.is_connect) {
      //   ElMessage({
      //     message: testDic.msg,
      //     type: 'error'
      //   })
      //   return
      // }
    }
    // 连接提交内容
    if (params.client_type == 2) {
      await connectQMT({ mini_qmt_path: params.mini_qmt_path, client_id: params.client_id })
    }
    await saveConfig({
      mini_qmt_path: params.mini_qmt_path,
      client_id: params.client_id,
      client_type: params.client_type,
      ths_path: params.ths_path,
      ths_client_id: params.ths_client_id,
      ths_pwd: params.ths_pwd
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
      message: error.message,
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

.path {
  white-space: nowrap; /* 禁止换行 */
  overflow: hidden; /* 隐藏溢出内容 */
  text-overflow: ellipsis; /* 超出部分显示省略号 */
  display: inline-block; /* 使宽度约束生效（必要时） */
}

.btn-container {
  width: 100%;
  justify-content: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  .save-btn {
    width: 80%;
    margin-left:0px
  }
  .test-btn {
    width: 80%;
    margin-bottom: 10px;
  }
}
</style>
