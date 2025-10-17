<template>
  <div class="user-detail-container">
    <el-card class="user-info-card">
      <el-button class="user-info-card-logout" link type="danger" @click="handleLogout">退出登录</el-button>
      <div class="user-info-card-content">
        <img src="@/assets/images/avatar.png" alt="头像" class="user-info-card-avatar" />
        <span class="user-info-card-email">{{ userInfo?.email }}</span>
        <span v-if="userInfo?.level === 0" class="user-info-card-email-level">{{ '普通用户' }}</span>
        <span v-if="userInfo?.level === 1" class="user-info-card-email-level">{{ 'VIP豪华用户' }}</span>
        <span class="user-info-card-created-at">{{ dayjs(userInfo?.created_at).format('YYYY-MM-DD HH:mm:ss') }}</span>
      </div>
    </el-card>
    <el-card class="edit-div">
      <template #header>
        <div class="card-header">
          <span>基本设置</span>
          <span class="edit-span" @click="editConfigAction">编辑</span>
        </div>
      </template>
      <p>下单模式：<el-tag>{{ params.client_type == 1 ? ' 同花顺下单模式' : ' QMT下单模式' }}</el-tag></p>
      <p v-if="params.client_type == 2">QMT路径:{{ params.mini_qmt_path }}</p>
      <p v-if="params.client_type == 2">客户编号:{{ params.client_id }}</p>
      <p v-if="params.client_type == 1">同花顺路径:{{ params.ths_path }}</p>
      <p v-if="params.client_type == 1">证券账号:{{ params.ths_client_id }}</p>
    </el-card>
    <editConfigModal ref="editConfigModalRef" @callBack="getSetting" />
  </div>
</template>

<script setup>
import { clearAuth, getUserInfo } from '@/api/auth'
import { disconnect, getSettingConfig, saveConfig } from '@/api/comm_tube'
import dayjs from "dayjs"
import { ElMessage, ElMessageBox } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import editConfigModal from './editConfigModal.vue'
const router = useRouter()
const userInfo = ref(null)
const editConfigModalRef = ref(null)
const params = reactive({
  mini_qmt_path: '',
  client_id: '',
  client_type: 1,
  ths_path: '',
  ths_client_id: '',
  ths_pwd: ''
})

const editConfigAction = () => {
  
  editConfigModalRef.value.showModal()
}

onMounted(async () => {
  const setting = await getSetting()
  const tmpuserInfo = await getUserInfo()
  userInfo.value = tmpuserInfo

  if(setting.client_id == "" || setting.mini_qmt_path == ""){
    console.log("配置文件未初始化")
    editConfigModalRef.value.showModal()
  }
})

// 获取配置文件
const getSetting = async () => {
  const res = await getSettingConfig()
  params.mini_qmt_path = res.mini_qmt_path
  params.client_id = res.client_id
  params.ths_path = res.ths_path
  params.ths_client_id = res.ths_client_id
  params.ths_pwd = res.ths_pwd
  params.client_type = res.client_type
  return res
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(() => {
      saveConfig({
        run_model_type: 0
      })
      disconnect()
      clearAuth()
      ElMessage.success('退出登录成功')
      router.push('/setting/login')
    })
    .catch(() => {
      // 用户点击取消，不做任何操作
    })
}
</script>

<style scoped lang="less">
.user-detail-container {
  display: flex;
  flex-direction: column;
  // align-items: center;
  background-color: #f5f5f5;
  width: 100%;
  padding: 10px;
  box-sizing: border-box;
  height: 100%;

  .user-info-card {
    width: 100%;
    display: flex;
    flex-direction: column;
    height: 50%;
    position: relative;
  }
  .user-info-card-logout {
    position: absolute;
    right: 10px;
    text-align: center;
    font-size: 16px;
  }
  .user-info-card-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    margin-top: 30px;
    .user-info-card-avatar {
      overflow: hidden;
      height: 100px;
      width: 100px;
      border-radius: 50%;
    }
    .user-info-card-email {
      font-size: 20px;
      font-weight: bold;
      margin-top: 10px;
    }
    .user-info-card-email-level {
      font-size: 14px;
      color: #999;
      margin-top: 5px;
    }
    .user-info-card-created-at {
      font-size: 14px;
      color: #999;
      margin-top: 5px;
    }
  }
  .tools-container {
    display: flex;
    margin-top: 20px;
    background: #fff;

    .edit-div {
      width: 40vw;
    }
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  .edit-span {
    cursor: pointer;
    color: #409eff;
  }
}
</style>
