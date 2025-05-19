// frontend/src/store/user.js
import {
    defineStore
} from 'pinia'

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
        setRemoteStore(params){
            if(params.type === 'test'){

            }else{
                this.connectState = params.state
            }
            // 模拟盘 回测 信号单
            if(params.data){
                let st = ""
                if(params.data.run_params=="simple_backtest"){
                    st = `接收到来自回测的信号单: `
                }else if(params.data.run_params=="full_backtest"){
                    st = `接收到来自回测的信号单: `
                }else if(params.data.run_params=="sim_trade"){
                    st = `接收到来自模拟的信号单: `
                }
                st += `任务编号为${params.data.strategy_id} 股票为${params.data.params.security} 数量为${params.data.params.value} 方向为${params.data.params.side}`
                params.message = st
                console.log(st)
            }else{
                this.clientId = params.unique_id
            }
            // console.log(params.message)
            this.messagesArr.push(params)
        }
    }
})