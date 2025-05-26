import { useCommonStore } from '@/store/common.js'

export const getSettingConfig = async () => {
  const settingConfig = useCommonStore().settingConfig
  if(settingConfig === null || Object.keys(settingConfig).length <= 1){
    const res = await window.pywebview.api.getSettingConfig()
    await saveConfig(res)
    return res
  }
  return settingConfig
}
export const saveConfig = (params) => {
  useCommonStore().setSettingConfig(params)
  return window.pywebview.api.saveConfig(params)
}
export const getTaskList = () => {
  return window.pywebview.api.getTaskList()
}
export const getTaskDetail = (params) => {
  return window.pywebview.api.getTaskDetail(params)
}
export const runTask = (params) => {
  return window.pywebview.api.runTask(params)
}
export const getOrderList = (params) => {
  return window.pywebview.api.getOrderList(params)
}
export const transitionCode = (params,taskDic) => {
  return window.pywebview.api.transitionCode(params,taskDic)
}

export const revertTransitionCode = (data) => {
  return window.pywebview.api.revertTransitionCode(data)
}


export const connectWs = (params,ways=2) => {
  return window.pywebview.api.connectWs(params,ways)
}

export const connectQMT = async(params) => {
  const isAccSubSuccess = await window.pywebview.api.connectQMT(params)
  await useCommonStore().changeIsAccSubSuccess(isAccSubSuccess)
  return isAccSubSuccess
}

export const disconnect = () => {
  return window.pywebview.api.disconnect()
}


export const testConnect = (params) => {
  return window.pywebview.api.testConnect(params)
}

export const isProcessExist = () => {
  return window.pywebview.api.isProcessExist()
}
export const copyRequestCode = (params) => {
  return window.pywebview.api.copyRequestCode(params)
}

export const createTask = (params) => {
  return window.pywebview.api.createTask(params)
}

export const getRemoteState = () => {
  return window.pywebview.api.getRemoteState()
}

export const deleteTask = (params) => {
  return window.pywebview.api.deleteTask(params)
}

export const testQMTConnect = (path) => {
  return window.pywebview.api.testQMTConnect(path)
}

export const checkStrategyCodeExists = (strategy_code)=>{
  return window.pywebview.api.check_strategy_code_exists(strategy_code)
}

export const chooseDirectory = ()=>{
  return window.pywebview.api.open_directory_dialog()
}
// export const 