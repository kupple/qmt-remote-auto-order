<template>
  <div class="setting-container">
    <h1>设置</h1>
    <el-form :model="params" :rules="rules" ref="formRef" label-width="120px">
      <el-form-item label="QMT路径" prop="qmtPath" required>
        <div class="input-wrapper">
          <el-input v-model="params.qmtPath" placeholder="请输入QMT安装路径" required />
          <div class="tips" >示例: D:\长城策略交易系统\userdata_mini <span class="help">帮助</span></div>
        </div>
      </el-form-item>
      <el-form-item label="客户编号" prop="clientId" required>
        <div class="input-wrapper">
          <el-input v-model="params.clientId" placeholder="请输入客户编号ID" required />
          <div class="tips" >示例: 121600018888 <span class="help">帮助</span></div>
        </div>
      </el-form-item>
      <el-form-item>
        <el-button style="margin-top:80px;width:100px" @click="connectAction" type="primary">确定</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
// import {
//   ConnectPython,
//   CheckQMTIsInit,
// } from "../../wailsjs/go/api/Common";
// import { LoadSetting, SaveSettin } from "../../wailsjs/go/api/SQLExc";
import { onMounted, reactive, ref } from "vue";
import { ElMessage } from 'element-plus'

const formRef = ref(null);

const rules = {
  qmtPath: [
    { required: true, message: '请输入QMT路径', trigger: 'blur' },
  ],
  clientId: [
    { required: true, message: '请输入客户编号ID', trigger: 'blur' },
  ],
};

const params = reactive({
  qmtPath:"",
  clientId:"",
});

const connectAction = async() => {
  if (!formRef.value) return;
  
  try {
    await formRef.value.validate();
    await window.pywebview.api.saveConfig({
      mini_qmt_path: params.qmtPath,
      client_id: params.clientId,
    });
    ElMessage({
      message: '保存成功',
      type: 'success',
    });
  } catch (error) {
    console.log(error)
    ElMessage({
      message: '请填写完整的表单信息',
      type: 'error',
    });
  }
};

// 检测是否安装qmt
// const checkIsInitQMT = ()=>{
//   const check = CheckQMTIsInit()
//   console.log(check)
// }

// 获取配置文件
const getSetting = async()=>{
  window.pywebview.api.getSettingConfig().then((res) => {
    params.qmtPath = res.mini_qmt_path
    params.clientId = res.client_id
  });
}


onMounted(async () => {
  await getSetting()
});
</script>

<style scoped lang="less">
.setting-container {
  padding: 20px;
  background: #fff;
}

.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.input-wrapper :deep(.el-form-item__error) {
  position: static;
  margin-top: 4px;
}
.tips{
  text-align: left;
  display: flex;
  color: rgb(121, 121, 121);
  .help {
    text-decoration: underline;
    color: blue;
    cursor: pointer;
    margin-left: 5px;
  }
  
}
</style>
