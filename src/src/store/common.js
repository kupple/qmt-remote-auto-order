// frontend/src/store/user.js
import {
  defineStore
} from 'pinia'

export const useCommonStore = defineStore('common', {
  state: () => ({
    isLoggedIn: false,
    isQMTProcessExit: false,
    taskList: []
  }),
  actions: {
    changeIsQMTProcessExit(params) {
      this.isQMTProcessExit = params
    },
    setTaskList(params) {
      console.log(params)
      this.taskList = params
    },
    logout() {
      this.name = ''
      this.isLoggedIn = false
    }
  }
})