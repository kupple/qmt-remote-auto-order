import { getToken } from '@/api/auth'
import axios from 'axios'
import { ElMessage } from 'element-plus'
const baseUrl = 'http://127.0.0.1:8080' // 这里设置您想要的固定基础URL
// 创建 axios 实例
const service = axios.create({
  baseURL: baseUrl,
  timeout: 15000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json;charset=utf-8'
  }
})

// 设置基础URL配置

// 请求重试配置
const retryConfig = {
  retries: 2, // 重试次数
  retryDelay: 1000, // 重试间隔
  retryableStatus: [408, 429, 500, 502, 503, 504] // 需要重试的状态码
}

// 存储取消请求的控制器
const pendingRequests = new Map()

// 生成请求的唯一key
const generateRequestKey = (config) => {
  const { url, method, params, data } = config
  return [url, method, JSON.stringify(params), JSON.stringify(data)].join('&')
}

// 添加请求到pending列表
const addPendingRequest = (config) => {
  const requestKey = generateRequestKey(config)
  if (!pendingRequests.has(requestKey)) {
    const controller = new AbortController()
    config.signal = controller.signal
    pendingRequests.set(requestKey, controller)
  }
}

// 移除请求从pending列表
const removePendingRequest = (config) => {
  const requestKey = generateRequestKey(config)
  if (pendingRequests.has(requestKey)) {
    pendingRequests.delete(requestKey)
  }
}

// 取消所有pending的请求
export const cancelAllRequests = () => {
  pendingRequests.forEach((controller) => {
    controller.abort()
  })
  pendingRequests.clear()
}

// 请求拦截器
service.interceptors.request.use(
  async (config) => {
    // 添加token到请求头
    const token = await getToken()

    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }

    // 添加请求到pending列表
    addPendingRequest(config)

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    // 从pending列表中移除请求
    removePendingRequest(response.config)

    const res = response.data

    // 这里可以根据后端的响应结构定制
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }

    return res
  },
  async (error) => {
    // 从pending列表中移除请求
    if (error.config) {
      removePendingRequest(error.config)
    }

    // 处理请求取消的情况
    if (axios.isCancel(error)) {
      return Promise.reject(new Error('请求已取消'))
    }

    // 处理网络错误
    if (!error.response) {
      ElMessage.error('网络错误，请检查您的网络连接')
      return Promise.reject(error)
    }

    const { response } = error
    const { config } = error

    // 处理需要重试的请求
    if (retryConfig.retryableStatus.includes(response.status) && config && config.__retryCount < retryConfig.retries) {
      config.__retryCount = config.__retryCount || 0
      config.__retryCount++

      // 延迟重试
      await new Promise((resolve) => setTimeout(resolve, retryConfig.retryDelay))
      return service(config)
    }

    // 处理其他错误
    switch (response.status) {
      case 401:
        ElMessage.error('未授权，请重新登录')
        // 可以在这里处理登出逻辑
        // localStorage.removeItem('token');
        // window.location.href = '/login';
        break
      case 403:
        ElMessage.error('拒绝访问')
        break
      case 404:
        ElMessage.error('请求的资源不存在')
        break
      case 500:
        ElMessage.error(response.data.error || response.data.message)
        break
      default:
        ElMessage.error(response.data.message || '请求失败')
    }

    return Promise.reject(error)
  }
)

// 封装请求方法
const request = async (config) => {
  try {
    const response = await service(config)
    return response
  } catch (error) {
    throw error
  }
}

// 封装GET请求
export const get = (path, params, config = {}) => {
  return request({
    method: 'get',
    url: `${baseUrl}${path}`,
    params,
    ...config
  })
}

// 封装POST请求
export const post = (path, data, config = {}) => {
  return request({
    method: 'post',
    url: `${baseUrl}${path}`,
    data,
    ...config
  })
}

// 封装PUT请求
export const put = (path, data, config = {}) => {
  return request({
    method: 'put',
    url: `${baseUrl}${path}`,
    data,
    ...config
  })
}

// 封装DELETE请求
export const del = (path, data, config = {}) => {
  return request({
    method: 'delete',
    url: `${baseUrl}${path}`,
    data,
    ...config
  })
}

// 封装上传文件请求
export const upload = (path, file, onProgress, config = {}) => {
  const formData = new FormData()
  formData.append('file', file)

  return request({
    method: 'post',
    url: `${baseUrl}${path}`,
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(percentCompleted)
      }
    },
    ...config
  })
}

export default {
  get,
  post,
  put,
  del,
  upload,
  cancelAllRequests
}
