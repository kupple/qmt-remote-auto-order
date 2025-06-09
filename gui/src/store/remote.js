// frontend/src/store/user.js
import router from '@/router/index.js'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'
import { defineStore } from 'pinia'

import { clearAuth } from '@/api/auth'
export const useRemoteStore = defineStore('remote', {
  state: () => ({
    connectState: 0,
    messagesArr: [],
    clientId: null
  }),
  actions: {
    changeConnectState(params) {
      this.connectState = params
    },
    changeClientId(params) {
      this.clientId = params
    },
    clearMessagesArr() {
      this.messagesArr = []
    },
    async setRemoteStore(params) {
      if (params.show && params.show === true) {
        if (params.showType) {
          ElMessage({
            message: params.message,
            type: params.showType
          })
        } else {
          ElMessage.info(params.message)
        }
      }

      // 事件处理
      if (params.type) {
        if (params.type == 'logout') {
          await clearAuth()
          ElMessage.error('已有账号在其他地方登录')
          router.push('/setting/login')
        }
        if (params.type === 'login') {
          this.connectState = 1
        }
        if (params.type == 'loss') {
          this.connectState = 2
        }
        if (params.type == 'exit') {
          this.connectState = 0
        }
        if (params.type == 'logout') {
          this.connectState = 0
        }
        
      }
      // 模拟盘 回测 信号单
      if (params.data) {
        let st = ''
        if (params.data.run_params == 'simple_backtest') {
          st = `接收到来自回测的信号单(不会受理下单): `
        } else if (params.data.run_params == 'full_backtest') {
          st = `接收到来自回测的信号单(不会受理下单): `
        } else if (params.data.run_params == 'sim_trade') {
          st = `接收到来自模拟的信号单: `
        }
        st += `任务编号为${params.data.strategy_code} 股票为${params.data.params.security} 数量为${params.data.params.amount} 方向为${params.data.params.is_buy ? '买入' : '卖出'}`
        params.message = st
      } else {
        this.clientId = params.unique_id
      }
      if (params.message && params.message.length > 2) {
        params.date = dayjs().format('MM-DD HH:mm:ss')
        this.messagesArr.push({
          message: params.message,
          date: params.date
        })
      }
    }
  }
})
