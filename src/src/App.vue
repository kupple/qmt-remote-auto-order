<script setup>
import MainContainer from './components/layout/index.vue'
import { useRemoteStore } from '@/store/remote.js'

window["remoteCallBack"] = (res) => {
  const dic = JSON.parse(res);
  useRemoteStore().setRemoteStore(dic);
  
  
};

</script>

<template>
  <MainContainer/>
</template>


<style lang="less">
body{
  margin: 0px;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
  overflow: hidden;
}
</style>