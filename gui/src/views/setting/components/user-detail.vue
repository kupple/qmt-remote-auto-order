<template>
  <div class="user-detail-container">
    <el-card class="user-info-card">
      <el-button class="user-info-card-logout" link type="danger" @click="handleLogout">退出登录</el-button>
      <div class="user-info-card-content">
        <img src="@/assets/images/avatar.png" alt="头像" class="user-info-card-avatar" />
        <span class="user-info-card-email">{{ userInfo?.email }}</span>
        <span v-if="userInfo?.level === 0" class="user-info-card-email-level">{{ '普通用户' }}</span>
        <span v-if="userInfo?.level === 1" class="user-info-card-email-level">{{ 'VIP豪华用户' }}</span>
        <span class="user-info-card-created-at">{{ formatDate(userInfo?.created_at) }}</span>
      </div>
    </el-card>
    <el-card class="edit-div">
      <template #header>
        <div class="card-header">
          <span>基本设置</span>
          <span class="edit-span" @click="editConfigAction">编辑</span>
        </div>
      </template>
      <p>QMT路径:{{ params.qmtPath }}</p>
      <p>客户编号:{{ params.clientId }}</p>
    </el-card>
    <editConfigModal ref="editConfigModalRef" @callBack="getSetting" />
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUserInfo, clearAuth } from '@/api/auth'
import { useRouter } from 'vue-router'
import { SwitchButton } from '@element-plus/icons-vue'
import editConfigModal from './editConfigModal.vue'
const router = useRouter()
const userInfo = ref(null)
const editConfigModalRef = ref(null)
import { getSettingConfig,saveConfig,disconnect } from '@/api/comm_tube'
const params = reactive({
  qmtPath: '',
  clientId: ''
})

const editConfigAction = () => {
  
  editConfigModalRef.value.showModal()
}

onMounted(async () => {
  const setting = await getSetting()
  const tmpuserInfo = await getUserInfo()
  userInfo.value = tmpuserInfo
})

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 获取配置文件
const getSetting = async () => {
  const res = await getSettingConfig()
  console.log(res)
  params.qmtPath = res.mini_qmt_path
  params.clientId = res.client_id
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
