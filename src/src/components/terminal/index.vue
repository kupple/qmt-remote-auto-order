<template>
  <div class="ws-state-view" ref="listRef">
    <span v-for="(item, idx) in messagesArr" :key="idx">
      <span class="tips">{{ item.message }}</span>
    </span>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useRemoteStore } from '@/store/remote.js'
const listRef = ref(null)
const remoteStore = useRemoteStore()
const messagesArr = computed(() => {
  return remoteStore.messagesArr
})

watch(
  () => messagesArr,
  async (newVal) => {
    await nextTick()
    setTimeout(() => {
      if (listRef.value) {
        listRef.value.scrollTop = listRef.value.scrollHeight
      }
    }, 0)
  },
  { deep: true }
)
</script>

<style scoped lang="less">
.ws-state-view {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  padding: 10px;
  flex: 1;
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
