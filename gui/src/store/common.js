// frontend/src/store/user.js
import {
  defineStore
} from 'pinia'

export const useCommonStore = defineStore('common', {
  state: () => ({
    isLoggedIn: false,
    isQmtState: false,
    isAccSubState: false,
    taskList: [],
    showTerminal: true,
    settingConfig: null,
  }),
  actions: {
    changeisQmtState(params) {
      this.isQmtState = params
    },
    changeisAccSubState(params){
      this.isAccSubState = params
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