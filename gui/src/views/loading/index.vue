<template>
  <div class="loading-container">
    <div class="loading-content">
      <div class="logo">
        <img src="@/assets/images/logo.png" alt="Logo" />
      </div>
      <div class="loading-text">正在加载中...</div>
      <el-icon class="loading-icon" :size="40">
        <Loading style="color: #fff" />
      </el-icon>
    </div>
  </div>
</template>

<script setup>
import { getToken, getUserInfo } from '@/api/auth'
import { connectQMT, connectWs, getSettingConfig, getAccountList, programStart } from '@/api/comm_tube'
import { Loading } from '@element-plus/icons-vue'
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

onMounted(() => {
  setTimeout(async () => {
    const config = await getSettingConfig()
    const account_list = await getAccountList()
    for (const item of account_list) {
      await connectQMT(item.id)
    }
    
    if (config.run_model_type === 1) {
      if (config.salt && config.server_url && config.client_id && config.mini_qmt_path) {
        await connectWs(config.server_url, 1)
      }
    } else if (config.run_model_type === 2) {
      const userInfo = await getUserInfo()
      const token = await getToken()
      if (userInfo && token && config.server_url) {
        await connectWs(config.server_url, 2)
      }
    }
    router.push('/home/list')
    programStart()
  }, 1000)
})
</script>
c

<style scoped>
.loading-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: var(--el-bg-color);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  background: #f2f2f2;
}

.loading-content {
  text-align: center;
  padding: 2rem;
  border-radius: 8px;
  background: var(--el-bg-color-overlay);
  box-shadow: var(--el-box-shadow-light);
  background: #646464;
  width: 40%;
}

.logo {
  margin-bottom: 2rem;
}

.logo img {
  width: 120px;
  height: auto;
  animation: flip 3s ease-in-out infinite;
}

@keyframes flip {
  0% {
    transform: perspective(400px) rotateY(0);
  }
  50% {
    transform: perspective(400px) rotateY(180deg);
  }
  100% {
    transform: perspective(400px) rotateY(360deg);
  }
}

.loading-text {
  color: #fff;
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
  font-weight: 500;
}

.loading-icon {
  color: var(--el-color-primary);
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
