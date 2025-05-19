<template>
  <div class="transition-container">
    <div class="transition-container-content">
      <span class="transition-container-content-title">请将聚宽代码复制到此处</span>
      <div class="transition-bottom">
        <textarea class="transition-input" v-model="textarea1" type="textarea" placeholder="请将代码复制到此处" />
        <el-button @click="transitionCodeAction">转换</el-button>
        <textarea class="transition-input" v-model="textarea2" type="textarea" placeholder="此处为生产的代码" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref,toRaw } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getTaskDetail, transitionCode } from '@/api/comm_tube'
const router = useRouter()
const route = useRoute()
const formRef = ref(null)
const textarea1 = ref('')
const textarea2 = ref('')
const taskDic = ref({})

onMounted(async () => {
  const id = route.query.id
  const res = await getTaskDetail({ id: id })
  taskDic.value = res
})

const transitionCodeAction = async () => {
  const res = await transitionCode(textarea1.value,toRaw(taskDic.value))
  textarea2.value = res
}
const goToHome = () => {
  router.go(-1)
}

onMounted(async () => {})
</script>

<style scoped lang="less">
.transition-container {
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  flex: 1;
  height: 90%;
  .transition-container-header {
    display: flex;
    flex-direction: row;
    align-items: center;
    position: relative;
    background: #fff;
    padding: 10px;
    .title {
      font-size: 20px;
      font-weight: bold;
      color: #434343;
      position: absolute;
      left: 45%;
      transform: translateX(-50%);
    }
  }
  .transition-container-content {
    display: flex;
    flex-direction: column;
    flex: 1;
    padding: 20px;
    .transition-container-content-title {
      font-size: 14px;
      color: #434343;
      margin-bottom: 10px;
    }
    .transition-bottom {
      flex: 1;
      display: flex;
      gap: 10px;
      align-items: center;
      .transition-input {
        resize: none; /* 禁用调整大小 */
        flex: 1;
        vertical-align: top; /* 文本从顶部开始 */
        outline: none; /* 移除默认的蓝色边框 */
        font-size: 14px;
        height: 100%;
      }
    }
  }
}
</style>
