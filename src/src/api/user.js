import { get, post } from '@/utils/api'

// 发送验证码
export function sendVerificationCode(email) {
  return post('/api/v1/verification/send', { email })
}

// 用户注册
export function register(data) {
  return post('/api/v1/users', data)
} 

// 用户登录
export function login(data) {
  return post('/api/v1/users/login', data)
}

// 获取用户信息
export function fetchUserInfo() {
  return get(`/api/v1/users`)
}

// 更新用户信息
export function updateUserInfo(data) {
  return put(`/api/v1/users`, data)
}
