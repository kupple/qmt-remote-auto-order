// Token 相关操作
const TOKEN_KEY = 'qmt_token'
const USER_INFO_KEY = 'qmt_user_info'

export async function getToken() {
  const token = await window.pywebview.api.storage_get(TOKEN_KEY)
  return token
}

export async function setToken(token) {
  await window.pywebview.api.storage_set(TOKEN_KEY, token)
}

export async function removeToken() {
  await window.pywebview.api.storage_set(TOKEN_KEY, '')
}

// 用户信息相关操作
 export async function getUserInfo() {
  const userInfo = await window.pywebview.api.storage_get(USER_INFO_KEY)
  return userInfo ? JSON.parse(userInfo) : null
}

export async function setUserInfo(userInfo) {
  await window.pywebview.api.storage_set(USER_INFO_KEY, JSON.stringify(userInfo))
}

export async function removeUserInfo() {
  await window.pywebview.api.storage_set(USER_INFO_KEY, '')
}


// 清除所有认证信息
export function clearAuth() {
  removeToken()
  removeUserInfo()
} 