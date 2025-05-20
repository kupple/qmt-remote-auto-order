<template>
  <div class="footer-container">
    <div class="xuntou-khd">
      <span class="label-tips">mini迅投客户端:</span>
      <div v-if="isQMTProcessExit == true" class="footer-cell">
        <div class="tips">已打开</div>
        <el-icon color="green"><CircleCheckFilled /></el-icon>
      </div>
      <div v-else class="footer-cell">
        <div class="tips">暂未打开</div>
        <el-icon color="red"><CircleCloseFilled /></el-icon>
      </div>
    </div>
    <div class="ws-state">
      <span class="label-tips">远程连接:</span>
      <div v-if="isWSConnectedState == 1" class="footer-cell">
        <div class="tips">已连接</div>
        <el-icon color="green"><CircleCheckFilled /></el-icon>
      </div>
      <div v-else-if="isWSConnectedState == 2" class="footer-cell">
        <div class="tips">连接中/重连</div>
        <el-icon color="yellow"><CircleCheckFilled /></el-icon>
      </div>
      <div v-else class="footer-cell">
        <div class="tips">未连接</div>
        <el-icon color="red"><CircleCloseFilled /></el-icon>
      </div>
    </div>
    <div class="date-time-cell">
      <!-- 时间显示 -->
      <div class="time-cell">
        <span class="time">{{ time }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, computed } from 'vue'
import { useCommonStore } from '@/store/common.js'
import { useRemoteStore } from '@/store/remote.js'
import { CircleCheckFilled, CircleCloseFilled } from '@element-plus/icons-vue'
import { isProcessExist } from '@/api/comm_tube'
const time = ref('')
defineOptions({
  name: 'LayoutFooter'
})

const isQMTProcessExit = computed(() => useCommonStore().isQMTProcessExit)
const isWSConnectedState = computed(() => useRemoteStore().connectState)
onMounted(async () => {
  // setInterval(async () => {
  //   const res = await isProcessExist()
  //   useCommonStore().changeIsQMTProcessExit(res)
  // }, 2000)
  // setInterval(async () => {
  //   time.value = new Date().toLocaleString()
  // }, 1000)
})
</script>

<style lang="less" scoped>
.footer-container {
  display: flex;
  align-items: center;
  // justify-content: space-between;
  height: 100%;
  .label-tips {
    color: #fff;
    font-size: 12px;
    margin-right: 4px;
    font-weight: bold;
  }
  .footer-cell {
    display: flex;
    align-items: center;
    margin-top: 2px;
    .tips {
      color: #fff;
      margin-right: 4px;
      font-size: 12px;
      margin-top: -2px;
      font-weight: bold;
    }
  }
  .xuntou-khd {
    display: flex;
    align-items: center;
  }
  .ws-state {
    display: flex;
    align-items: center;
    margin-left: 30px;
  }
  .date-time-cell {
    display: flex;
    align-items: center;
    position: absolute;
    right: 10px;
    .time-cell {
      display: flex;
      color: #fff;
      font-size: 16px;
      margin-right: 4px;
      font-weight: bold;
    }
  }
}
</style>
