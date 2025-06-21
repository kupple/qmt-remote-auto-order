// frontend/src/store/user.js
import {
  defineStore
} from 'pinia'

export const useCommonStore = defineStore('common', {
  state: () => ({
    isLoggedIn: false,
    isQmtState: false, //qmt连接状态
    isAccSubState: false, //qmt账号订阅状态
    isThsState: false, //同花顺连接状态
    taskList: [],
    showTerminal: true,
    settingConfig: {
      client_type:1
    },
  }),
  actions: {
    changeisQmtState(params) {
      this.isQmtState = params
    },
    changeisAccSubState(params){
      this.isAccSubState = params
    },
    changeisThsState(params){
      this.isThsState = params
    },
    setTaskList(params) {
      this.taskList = params
    },
    logout() {
      this.name = ''
      this.isLoggedIn = false
    },
    changeShowTerminal(params) {
      this.showTerminal = params
    },
    setSettingConfig(params) {
      this.settingConfig = {
        ...this.settingConfig,
        ...params
      }
    }
  }
})