// frontend/src/store/user.js
import router from '@/router/index.js'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'

import {
    defineStore
} from 'pinia'

import { clearAuth } from '@/api/auth'
export const useRemoteStore = defineStore('remote', {
    state: () => ({
        connectState: 0,
        messagesArr: [],
        clientId: null,
    }),
    actions: {
        changeConnectState(params) {
            this.connectState = params
        },
        changeClientId(params) {
            this.clientId = params
        },
        async setRemoteStore(params){
            if(params.type === 'test'){

            }else{
                if(params.state != undefined || params.state != null){
                    this.connectState = params.state    
                }
            }
            if(params.code){
                console.log(params.code)

                if(params.code == "-101"){
                    await clearAuth()
                    ElMessage.error('已有账号在其他地方登录')
                    router.push('/setting/login')
                }
            }
            // 模拟盘 回测 信号单
            if(params.data){
                let st = ""
                if(params.data.run_params=="simple_backtest"){
                    st = `接收到来自回测的信号单(不会受理下单): `
                }else if(params.data.run_params=="full_backtest"){
                    st = `接收到来自回测的信号单(不会受理下单): `
                }else if(params.data.run_params=="sim_trade"){
                    st = `接收到来自模拟的信号单: `
                }
                st += `任务编号为${params.data.strategy_code} 股票为${params.data.params.security} 数量为${params.data.params.amount} 方向为${params.data.params.is_buy ? '买入':'卖出'}`
                params.message = st
            }else{
                this.clientId = params.unique_id
            }
            // console.log(params.message)
            params.date = dayjs().format("MM-DD HH:mm:ss")
            this.messagesArr.push({
                message: params.message,
                status: params.status || 1,
                date: params.date,
            })
        }
    }
})