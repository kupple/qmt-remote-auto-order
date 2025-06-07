import { get, post, put } from '@/utils/api'

// 发送验证码
export function sendVerificationCode(email,purpose) {
  return post('/api/v1/verification/send', { email,purpose })
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

export function resetPassword(data){
  return post('/api/v1/users/reset-password', data)
}

export function getStrategyKeyByStrategyCode(strategy_code){
  return get(`/api/v1/strategy-keys?strategy_code=${strategy_code}`)
}

export function createStrategyKey(data){
  return post(`/api/v1/strategy-keys`, data)
}
    
export function bindStrategyKey(data){
  return post(`/api/v1/strategy-keys/bind`, data)
}

export function unbindStrategyKey(data){
  return post(`/api/v1/strategy-keys/unbind`, data)
}

export function getBindPeopleList(data){
  return get(`/api/v1/strategy-keys/users`,data)
}

export function updateBindPeople(data){
  return put(`/api/v1/strategy-mappings`,data)
}

export function updateStrategyKey(data){
    return put(`/api/v1/strategy-keys`,data)
}