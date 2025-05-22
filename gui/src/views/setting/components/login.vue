<template>
  <div class="login-container">
    <div class="login-box">
      <el-form ref="loginFormRef" :model="loginForm" :rules="rules" label-position="top">
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="loginForm.email" placeholder="请输入邮箱" :prefix-icon="Message" />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" :prefix-icon="Lock" show-password />
        </el-form-item>

        <el-form-item>
          <div class="button-group">
            <el-button type="primary" :loading="loading" class="login-btn" @click="handleLogin">登录</el-button>
            <el-button type="default" class="register-btn" @click="handleRegister">注册</el-button>
          </div>
        </el-form-item>
        <span class="forget-code" @click="handleForgetCodeAction">忘记密码?</span>
        <el-divider content-position="center">or</el-divider>
        <el-button class="own-remote-service-btn" type="primary" @click="handleOwnRemoteService"> 使用自定义远程服务 </el-button>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Message, Lock, Connection } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { login } from '@/api/user'
import { setToken, setUserInfo } from '@/api/auth'
import { saveConfig, connectWs } from '@/api/comm_tube'
const router = useRouter()
const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  email: 'rtys788@icloud.com',
  password: 'a123456'
})

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

const handleForgetCodeAction = () => {
  router.push('/setting/code-login')
}

const handleOwnRemoteService = async () => {
  await saveConfig({
    run_model_type: 0
  })
  router.push({ name: 'SettingLocal' })
}

const handleLogin =  async() => {
  if (!loginFormRef.value) return

  try {
    loginFormRef.value.validate()
    loading.value = true

    await saveConfig({
      run_model_type: 2
    })

    const res =  await login(loginForm)
    // 保存 token
    await setToken(res.data.token)
    await setUserInfo(res.data.user)
    // 连接websocket
    await connectWs(res.data.user.server_url)
    ElMessage.success('登录成功')
    // 跳转到用户明细页面
    router.push({ name: 'SettingUserDetail' })
  } catch (error) {
    console.log(error)
    // console.log('登录失败:', error)
    // ElMessage.error(error.message || '登录失败，请检查输入信息')
  } finally {
    loading.value = false
  }
}

const handleRegister = () => {
  router.push('/setting/register')
}
</script>

<style scoped lang="less">
.login-container {
  display: flex;
  align-items: center;
  height: 100vh;
  flex-direction: column;
  background-color: #f5f5f5;
}

.button-group {
  display: flex;
  gap: 12px;
  flex-direction: column;
  justify-content: stretch;
  flex-wrap: wrap;
  width: 100%;
}
.own-remote-service-btn {
  background-color: #206bff;
  color: #fff;
  border: none;
  width: 100%;
  height: 40px;
}
.login-btn {
  flex: 1;
  width: 100%;
}

.register-btn {
  flex: 1;
  width: 100%;
  margin-left: 0px;
}
.forget-code {
  color: #206bff;
  cursor: pointer;
  /* position: absolute; */
  right: 0px;
  font-size: 14px;
}

.login-box {
  width: 36vw;
  background: #fff;
  border-radius: 10px;
  padding: 20px;
  position: relative;
  justify-content: flex-end;
  margin-top: 10%;
}
</style>
