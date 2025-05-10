<template>
  <div class="home-container">
    <router-view />
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
const serverAddress = ref('http://127.0.0.1:5000')
import { useRemoteStore } from '@/store/remote.js'

const remoteStoreDic = computed(() => {
  return useRemoteStore()
})

const connectAction = () => {
  window.pywebview.api.connectWs(serverAddress.value).then((res) => {
    console.log(res)
  })
}
const stopConnectAction = () => {
  window.pywebview.api.disconnect()
}
const testConnectAction = () => {
  window.pywebview.api.testConnect(serverAddress.value)
}
</script>

<style scoped lang="less">



</style>
