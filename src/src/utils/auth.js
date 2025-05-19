// Token 相关操作
const TOKEN_KEY = 'qmt_token'
const USER_INFO_KEY = 'qmt_user_info'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
}

// 用户信息相关操作
export function getUserInfo() {
  const userInfo = localStorage.getItem(USER_INFO_KEY)
  return userInfo ? JSON.parse(userInfo) : null
}

export function setUserInfo(userInfo) {
  localStorage.setItem(USER_INFO_KEY, JSON.stringify(userInfo))
}

export function removeUserInfo() {
  localStorage.removeItem(USER_INFO_KEY)
}

// 清除所有认证信息
export function clearAuth() {
  removeToken()
  removeUserInfo()
} 