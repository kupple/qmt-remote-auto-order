<template>
  <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑账号' : '添加账号'" width="60vw" center>
    <el-form label-width="auto" :model="params" :rules="rules" ref="formRef">
      <el-form-item label="下单方式" prop="client_type">
        <el-radio-group v-model="params.client_type" :disabled="isEdit">
          <el-radio-button label="同花顺下单模式" :value="1" />
          <el-radio-button label="QMT下单模式" :value="2" />
        </el-radio-group>
      </el-form-item>
      <el-form-item class="el-form-item__content" label="同花顺目录" prop="ths_path" required v-if="params.client_type == 1">
        <span class="path">{{ params.ths_path }}</span>
        <el-button type="primary" style="margin-left: 10px" @click="chooseDirectoryAction">选择目录</el-button>
        <el-button style="margin-left: 0px" type="danger" @click="chooseDirectoryAction">重置</el-button>
      </el-form-item>
      <el-form-item label="交易账号" prop="ths_client_id" v-if="params.client_type == 1">
        <el-input v-model="params.ths_client_id" placeholder="请输入同花顺账号" required />
      </el-form-item>
      <el-form-item label="交易密码" prop="ths_pwd" v-if="params.client_type == 1">
        <el-input v-model="params.ths_pwd" placeholder="请输入同花顺密码" required />
      </el-form-item>
      <el-form-item class="el-form-item__content" label="QMT路径" prop="mini_qmt_path" required v-if="params.client_type == 2">
        <span class="path" v-if="hasQmtBeenSelect == 1">{{ params.mini_qmt_path }}</span>
        <el-button v-if="hasQmtBeenSelect == 0" type="primary" @click="chooseDirectoryAction">打开目录</el-button>
        <el-button v-if="hasQmtBeenSelect == 1" type="primary" @click="connectionAction" style="margin-left: 10px">获取资金账号</el-button>
        <el-button style="margin-left: 0px" v-if="hasQmtBeenSelect == 1" type="danger" @click="chooseDirectoryAction">重置</el-button>
      </el-form-item>
      <el-form-item label="客户编号" prop="client_id" required v-if="params.client_type == 2">
        <el-select v-if="passStatus !== 2" :disabled="passStatus === 0 && !isEdit" v-model="params.client_id" placeholder="请选择客户编号ID" required>
          <el-option v-for="item in accountArr" :key="item" :label="item" :value="item" />
        </el-select>
      </el-form-item>
      <el-form-item label="备注" prop="remark">
        <el-input v-model="params.remark" placeholder="请输入备注" />
      </el-form-item>
    </el-form>
    <div class="btn-container">
      <el-button type="primary" class="save-btn" @click="saveConfigAction">保存</el-button>
    </div>
  </el-dialog>
</template>

<script setup>
import { chooseDirectory, connectQMT, testConnect, addAccount, updateAccount }from '@/api/comm_tube'
import { ElMessage }from 'element-plus'
import { reactive, ref }from 'vue'

const formRef = ref(null)
const dialogVisible = ref(false)
const emit = defineEmits(['callBack'])
const passStatus = ref(0)
const accountArr = ref([])
const hasQmtBeenSelect = ref(false)
const isEdit = ref(false)
const editId = ref(undefined)

const connectionAction = () => {
  // 按反斜杠拆分路径（注意转义）
  const pathParts = params.mini_qmt_path

  // 重新拼接成完整路径
  const str2 = pathParts.join("\\");

  testConnect(str2, params.client_type).then((res) => {
    if (res.is_connect) {
      accountArr.value = res.account_arr || []
      passStatus.value = 1
      ElMessage.success('连接成功请选择资金编号')
    }else {
      passStatus.value = 0
      ElMessage.error('请检查QMT路径是否正确')
    }
  })
}

const chooseDirectoryAction = async () => {
  const res = await chooseDirectory(params.client_type)
  if (res[0] == true) {
    if (params.client_type == 2) {
      params.mini_qmt_path = res[1]
      hasQmtBeenSelect.value = 1
    }else {
      params.ths_path = res[1]
    }
  }else {
    hasQmtBeenSelect.value = 0
  }
}

const rules = {
  mini_qmt_path: [{ required: true, message: '请输入QMT路径', trigger: 'blur' }],
  client_id: [{ required: true, message: '请输入客户编号ID', trigger: 'blur' }],
  ths_path: [{ required: true, message: '请选择同花顺路径', trigger: 'blur' }]
}

const params = reactive({
  mini_qmt_path: '',
  client_id: '',
  client_type: 2,
  ths_path: '',
  ths_client_id: '',
  ths_pwd: '',
  remark: ''
})

const resetForm = () => {
  params.mini_qmt_path = ''
  params.client_id = ''
  params.client_type = 2
  params.ths_path = ''
  params.ths_client_id = ''
  params.ths_pwd = ''
  params.remark = ''
  passStatus.value = 0
  accountArr.value = []
  hasQmtBeenSelect.value = false
}

const showModal = (row) => {
  dialogVisible.value = true
  if (row) {
    isEdit.value = true
    editId.value = row.id
    params.mini_qmt_path = row.mini_qmt_path || ''
    params.client_id = row.client_id || ''
    params.client_type = row.client_type || 2
    params.ths_path = row.ths_path || ''
    params.ths_client_id = row.ths_client_id || ''
    params.ths_pwd = row.ths_pwd || ''
    params.remark = row.remark || ''
    hasQmtBeenSelect.value = !!row.mini_qmt_path
    passStatus.value = 1
  }else {
    isEdit.value = false
    editId.value = undefined
    resetForm()
  }
}

const saveConfigAction = async () => {
  if (!formRef.value) return
  try {
    if (params.client_type == 2) {
      await connectQMT({ mini_qmt_path: params.mini_qmt_path, client_id: params.client_id })
    }

    const payload = {
      mini_qmt_path: params.mini_qmt_path,
      client_id: params.client_id,
      client_type: params.client_type,
      ths_path: params.ths_path,
      ths_client_id: params.ths_client_id,
      ths_pwd: params.ths_pwd,
      remark: params.remark,
      status: 1
    }

    if (isEdit.value && editId.value) {
      await updateAccount(editId.value, payload)
    }else {
      await addAccount({ ...payload, is_connected: 0, is_main: 0 })
    }

    ElMessage.success('保存成功')
    dialogVisible.value = false
    emit('callBack')
  }catch (error) {
    ElMessage.error(error.message || '保存失败')
  }
}

defineExpose({
  showModal
})
</script>

<style scoped lang="less">
.el-form-item__content {
  display: flex !important;
  align-items: center !important;
  flex-wrap: nowrap !important;
}
.el-input,
.el-select {
  flex: 1;
}
.path {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: inline-block;
}
.btn-container {
  width: 100%;
  display: flex;
  justify-content: center;
  .save-btn {
    width: 80%;
  }
}
</style>

