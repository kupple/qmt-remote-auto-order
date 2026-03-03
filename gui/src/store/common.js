// frontend/src/store/user.js
import {
  defineStore
} from 'pinia';

export const useCommonStore = defineStore('common', {
  state: () => ({
    isLoggedIn: false,
    // isQmtState: false, //qmt连接状态
    // isAccSubState: false, //qmt账号订阅状态
    // isThsState: false, //同花顺连接状态
    taskList: [],
    showTerminal: true,
    taskStateDic:{},
    settingConfig: {
      client_type:1
    },
  }),
  actions: {
    changeisQmtState(params) {
            // 正确安全地复制对象属性，避免空对象或未定义抛错
      if (!this.taskStateDic[params.id]) {
        this.taskStateDic[params.id] = {};
      }
      this.taskStateDic[params.id]["isQmtState"] = params.status
      this.taskStateDic[params.id]["qmtIsVisible"] = params.qmtIsVisible
      this.taskStateDic[params.id]["qmtPid"] = params.pid
      
    },
    changeisAccSubState(params){
      
      // 正确安全地复制对象属性，避免空对象或未定义抛错
      if (!this.taskStateDic[params.id]) {
        this.taskStateDic[params.id] = {};
      }
      this.taskStateDic[params.id]["isAccSubState"] = params.status;
      console.log(this.taskStateDic)
      
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