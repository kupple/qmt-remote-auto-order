<template>
  <div class="register-container">
    <div class="register-box">
      <el-form ref="registerFormRef" :model="registerForm" :rules="rules" label-position="top">
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱" :prefix-icon="Message" />
        </el-form-item>

        <el-form-item label="验证码" prop="verificationCode">
          <div class="verification-code-container">
            <el-input v-model="registerForm.verificationCode" placeholder="请输入验证码" :prefix-icon="Key" maxlength="6" />
            <el-button type="primary" :disabled="!canSendCode || countdown > 0" @click="handleSendCode" class="send-code-btn">
              {{ countdown > 0 ? `${countdown}秒后重试` : '发送验证码' }}
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" :prefix-icon="Lock" show-password />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请再次输入密码" :prefix-icon="Lock" show-password />
        </el-form-item>

        <el-form-item>
          <div class="button-group">
            <el-button type="primary" :loading="loading" class="register-btn" @click="handleRegister">注册</el-button>
            <el-button type="default" class="login-btn" @click="goToLogin">返回登录</el-button>
          </div>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onUnmounted } from 'vue'
import { Message, Lock, Key } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { sendVerificationCode, register } from '@/api/user'

const router = useRouter()
const registerFormRef = ref(null)
const loading = ref(false)
const countdown = ref(0)
const timer = ref(null)

const registerForm = reactive({
  email: '',
  verificationCode: '',
  password: '',
  confirmPassword: ''
})

const canSendCode = computed(() => {
  return registerForm.email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(registerForm.email)
})

const startCountdown = () => {
  countdown.value = 60
  timer.value = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer.value)
    }
  }, 1000)
}

const handleSendCode = async () => {
  if (!canSendCode.value) {
    ElMessage.warning('请输入正确的邮箱地址')
    return
  }

  try {
    await sendVerificationCode(registerForm.email)
    ElMessage.success('验证码已发送')
    startCountdown()
  } catch (error) {
    console.error('发送验证码失败:', error)
    ElMessage.error(error.response?.data?.message || error.message || '发送验证码失败，请重试')
  }
}

const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else {
    const hasLetter = /[a-zA-Z]/.test(value)
    const hasNumber = /[0-9]/.test(value)

    if (!hasLetter) {
      callback(new Error('密码必须包含至少一个字母'))
    } else if (!hasNumber) {
      callback(new Error('密码必须包含至少一个数字'))
    } else if (value.length < 6) {
      callback(new Error('密码长度不能少于6位'))
    } else {
      if (registerForm.confirmPassword !== '') {
        registerFormRef.value?.validateField('confirmPassword')
      }
      callback()
    }
  }
}

const validatePass2 = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const validateVerificationCode = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入验证码'))
  } else if (!/^\d{6}$/.test(value)) {
    callback(new Error('验证码必须是6位数字'))
  } else {
    callback()
  }
}

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  verificationCode: [{ required: true, validator: validateVerificationCode, trigger: 'blur' }],
  password: [
    { required: true, validator: validatePass, trigger: 'blur' },
    { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  confirmPassword: [{ required: true, validator: validatePass2, trigger: 'blur' }]
}

const handleRegister = async () => {
  if (!registerFormRef.value) return

  try {
    await registerFormRef.value.validate()
    loading.value = true

    const { email, verificationCode, password } = registerForm
    await register({
      email,
      verification_code: verificationCode,
      password
    })

    ElMessage.success('注册成功')
    router.push('/setting/login')
  } catch (error) {
    console.error('注册失败:', error)
    ElMessage.error(error.response?.data?.message || error.message || '注册失败，请重试')
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/setting/login')
}

// 组件卸载时清除定时器
onUnmounted(() => {
  if (timer.value) {
    clearInterval(timer.value)
  }
})
</script>

<style scoped lang="less">
.register-container {
  display: flex;
  align-items: center;
  height: 100vh;
  flex-direction: column;
  background-color: #f5f5f5;
}

.verification-code-container {
  display: flex;
  gap: 12px;
}

.verification-code-container .el-input {
  flex: 1;
}

.send-code-btn {
  width: 120px;
  flex-shrink: 0;
}
.register-title {
  font-weight: bold;
  font-size: 30px;
  margin-left: -24%;
  background-color: #f5f5f5;
  margin-bottom: 20px;
  margin-top: 10%;
}
.register-box {
  background: #fff;
  padding: 20px;
  border-radius: 20px;
  width: 36vw;
  margin-top: 10%;
}
</style>
