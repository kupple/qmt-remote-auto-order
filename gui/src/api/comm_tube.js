import { useCommonStore } from '@/store/common.js'

export const getSettingConfig = async () => {
  const settingConfig = useCommonStore().settingConfig
  if(settingConfig === null || Object.keys(settingConfig).length <= 1){
    const res = await window.pywebview.api.get_setting_config()
    await saveConfig(res)
    return res
  }
  return settingConfig
}
export const saveConfig = (params) => {
  useCommonStore().setSettingConfig(params)
  return window.pywebview.api.save_config(params)
}
export const getTaskList = (params) => {
  return window.pywebview.api.get_task_list(params)
}
export const getTaskDetail = (params) => {
  return window.pywebview.api.get_task_detail(params)
}
export const runTask = (params) => {
  return window.pywebview.api.run_task(params)
}
export const getOrderList = (params) => {
  return window.pywebview.api.get_order_list(params)
}
export const transitionCode = (params,taskDic) => {
  return window.pywebview.api.transition_code(params,taskDic)
}

export const revertTransitionCode = (data) => {
  return window.pywebview.api.revert_transition_code(data)
}


export const connectWs = (params,ways=2,is_login = false) => {
  return window.pywebview.api.connect_ws(params,ways,is_login)
}

export const connectQMT = async(params) => {
  const isAccSubState = await window.pywebview.api.connect_qmt(params)
  // await useCommonStore().changeisAccSubState(isAccSubState)
  // return isAccSubState
}

export const disconnect = () => {
  return window.pywebview.api.disconnect()
}


export const isProcessExist = () => {
  return window.pywebview.api.is_process_exist_action()
}

export const createTask = (params) => {
  return window.pywebview.api.create_task(params)
}

export const getRemoteState = () => {
  return window.pywebview.api.get_remote_state()
}

export const deleteTask = (params) => {
  return window.pywebview.api.delete_task(params)
}

export const testConnect = (path,type) => {
  return window.pywebview.api.test_connect(path,type)
}

export const checkStrategyCodeExists = (strategy_code)=>{
  return window.pywebview.api.check_strategy_code_exists(strategy_code)
}

export const chooseDirectory = (client_type)=>{
  return window.pywebview.api.open_directory_dialog(client_type)
}

export const setAutomatically = ()=>{
  return window.pywebview.api.set_automatically()
}
// export const 

export const createBacktest = (params) => {
  return window.pywebview.api.create_backtest(params)
}

export const queryBacktestByTaskId = (task_id) => {
  return window.pywebview.api.query_backtest_by_task_id(task_id)
}
export const countStrategyAnalyzer = (task_id,backtest_id) => {
  return window.pywebview.api.count_strategy_analyzer(task_id,backtest_id)
}
export const getPositionByTaskId = (task_id) => {
  return window.pywebview.api.get_position_by_task_id(task_id)
}
export const deletePositionById = (id) => {
  return window.pywebview.api.delete_position_by_id(id)
}
export const updatePosition = (id, params) => {
  return window.pywebview.api.update_position(id, params)
}
export const addPosition = (params) => {
  return window.pywebview.api.add_position(params)
}
export const checkPositionExists = (security_code, task_id) => {
  return window.pywebview.api.check_position_exists(security_code, task_id)
}
  
export const updateTaskCanUseAmount = (task_id, can_use_amount) => {
  return window.pywebview.api.update_task(task_id, can_use_amount)
}

export const queryTradeToday = (task_id) => {
  return window.pywebview.api.query_trade_today(task_id)
}

export const system_getAppInfo = ()=>{
  return window.pywebview.api.system_getAppInfo()
}
export const queryLogList = (params) => {
  return window.pywebview.api.query_log_list(params)
}

export const clearLog = () => {
  return window.pywebview.api.clear_log()
}

export const getUniqueID = () => {
  return window.pywebview.api.get_unique_id()
}
  
export const getAccountInfo = () => {
  return window.pywebview.api.get_account_info()
}

export const openThsShortcut = () => {
  return window.pywebview.api.open_ths_shortcut()
}