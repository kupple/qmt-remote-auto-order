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
            this.clientId = params.unique_id
            this.messagesArr.push(params)
        }
    }
})