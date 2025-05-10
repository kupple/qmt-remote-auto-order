<template>
    <div class="ws-state-view" ref="wsStateView">
        <span v-for="(item, idx) in remoteStoreDic.messagesArr" :key="idx">
          <span class="tips">{{ item.message }}</span>
        </span>
      </div>
</template>

<script setup>
import { ref,computed } from 'vue'
import { useRemoteStore } from '@/store/remote.js'
const wsStateView = ref(null)
const remoteStore = useRemoteStore()
const remoteStoreDic = computed(() => {
  return remoteStore
})



</script>

<style scoped lang="less">
    .ws-state-view {
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
      padding: 10px;
      flex:1;
      background: #000;
      overflow-y: scroll;
      .tips {
        color: #fff;
        font-size: 12px;
      }
      .ws-state-view::-webkit-scrollbar {
        display: none;
      }
    }
</style>