// frontend/src/store/user.js
import {
  defineStore
} from 'pinia'

export const useCommonStore = defineStore('common', {
  state: () => ({
    isLoggedIn: false,
    isQMTProcessExit: false,
    taskList: [],
    showTerminal: true,
    settingConfig: null
  }),
  actions: {
    changeIsQMTProcessExit(params) {
      this.isQMTProcessExit = params
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
      this.settingConfig = params
    }
  }
})