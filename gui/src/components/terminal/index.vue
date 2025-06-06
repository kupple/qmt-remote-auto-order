<template>
  <div class="ws-state-view">
    <div class="up-icon" @click="upIconClick" v-if="commonStore.showTerminal">
      <el-icon><ArrowDown /></el-icon>
    </div>
    <div v-else class="down-icon" @click="downIconClick">
      <el-icon><ArrowUp /></el-icon>
    </div>
    <div class="terminal-container" ref="listRef">
      <span v-for="(item, idx) in messagesArr" :key="idx">
        <span class="tips" :style="{ color: item.status === 2 ? 'red' : 'white' }">{{ item.date }}-{{ item.message }}</span>
      </span>
    </div>
    <el-button v-show="showTerminal" class="clear-btn" @click="clearAction">清除</el-button>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick,defineProps } from 'vue'
import { useRemoteStore } from '@/store/remote.js'
import { ArrowUp, ArrowDown } from '@element-plus/icons-vue'
import { useCommonStore } from '@/store/common.js'

const props = defineProps({
  showTerminal: {
    type: Boolean,
    default: false
  }
})



const listRef = ref(null)
const remoteStore = useRemoteStore()
const commonStore = useCommonStore()
const messagesArr = computed(() => {
  return remoteStore.messagesArr
})
const upIconClick = () => {
  commonStore.changeShowTerminal(!commonStore.showTerminal)
  listRef.value.scrollTop = listRef.value.scrollHeight
}
const downIconClick = () => {
  commonStore.changeShowTerminal(!commonStore.showTerminal)
  listRef.value.scrollTop = listRef.value.scrollHeight
}
// 清除
const clearAction = ()=>{
  remoteStore.clearMessagesArr()
}
watch(
  () => messagesArr,
  async (newVal) => {
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
  // overflow-y: scroll;
  position: relative;
  .terminal-container {
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    padding: 10px;
    flex: 1;
    background: #000;
    overflow-y: scroll;
    position: relative;
  }
  .tips {
    color: #fff;
    font-size: 12px;
  }
  .ws-state-view::-webkit-scrollbar {
    display: none;
  }
  .up-icon {
    z-index: 30;
    background: #22a1e0;
    height: 30px;
    width: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    position: absolute;
    left: calc(50% - 15px);
    top: -15px;
    cursor: pointer;
    color: #fff;
  }
  .down-icon {
    z-index: 30;

    background: #22a1e0;
    height: 30px;
    width: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    position: absolute;
    left: calc(50% - 15px);
    top: -15px;
    cursor: pointer;
    color: #fff;
  }
}
.clear-btn{
  position: absolute;
  bottom: 10px;
  right: 40px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 4px;
  padding: 5px 10px;
  color: #fff;
  cursor: pointer;
  transition: all 0.3s;
  &:hover {
    background: #fff;
    color: #000;
  }
}
</style>
