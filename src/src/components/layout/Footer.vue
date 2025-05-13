<template>
  <div class="footer-container">
    <div class="xuntou-khd">
      <span class="xuntou-tips">mini迅投客户端:</span>
      <div v-if="isQMTProcessExit == true" class="footer-cell">
        <div class="tips">已打开</div>
        <el-icon color="green"><CircleCheckFilled /></el-icon>
      </div>
      <div v-else class="footer-cell">
        <div class="tips">暂未打开</div>
        <el-icon color="red" ><CircleCloseFilled /></el-icon>
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
import { onMounted, reactive, ref, computed } from "vue";
import { useCommonStore } from '@/store/common.js'
import { CircleCheckFilled,CircleCloseFilled } from '@element-plus/icons-vue'

const time = ref('')
defineOptions({
  name: 'LayoutFooter'
})

const isQMTProcessExit = computed(() => useCommonStore().isQMTProcessExit);


onMounted(async () => {
  setInterval(async () => {
    const res =  await window.pywebview.api.isProcessExist()
    useCommonStore().changeIsQMTProcessExit(res)
  }, 2000);
  setInterval(async () => {
    time.value = new Date().toLocaleString()
  }, 1000);
});
</script>

<style lang="less" scoped>
.footer-container{
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  .xuntou-khd{
      display: flex;
      align-items: center;
      .xuntou-tips{
        color: #fff;
        font-size: 12px;
        margin-right: 4px;
        font-weight: bold;
      }
     .footer-cell{
      display: flex;
      align-items: center;
      margin-top: 2px;
      .tips{
        color: #fff;
        margin-right: 4px;
        font-size: 12px;
        margin-top: -2px;
        font-weight: bold;
      }
    }
  }
  .date-time-cell{
    display: flex;
    align-items: center;
    .time-cell{
      display: flex;
      color: #fff;
      font-size: 16px;
      margin-right: 4px;
      font-weight: bold;
    }
  }
}
</style>