<template>
  <div class="transition-container">
    <div class="transition-container-content">
      <span class="transition-container-content-title">请将聚宽代码复制到此处 <span style="margin-left:10px">任务名称（{{taskDic?.name || ''}}）</span></span>
      <div class="transition-bottom">
        <div class="transition-bottom-cell">
          <textarea class="transition-input" v-model="textarea1" type="textarea" placeholder="请将代码复制到此处" />
          <el-button type="primary" class="copy-btn">一键复制</el-button>
        </div>
        <div class="mid-btns">
          <el-button type="primary" @click="transitionCodeAction"
            >转换<el-icon><DArrowRight /></el-icon
          ></el-button>
          <el-button @click="revertTransitionCodeAction"
            ><el-icon><DArrowLeft /></el-icon>复原</el-button>
        </div>
        <div class="transition-bottom-cell">
          <textarea class="transition-input" v-model="textarea2" type="textarea" placeholder="此处为生产的代码" />
          <el-button type="primary" class="copy-btn">一键复制</el-button>
        </div>
      </div>
    </div>
    <div class="transition-container-bottom">
      <span style="color:red">⚠️⚠️⚠️请注意转完后的代码不要转发，发布在任务讨论上⚠️⚠️⚠️</span>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, toRaw } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft, DArrowRight, DArrowLeft } from '@element-plus/icons-vue'
import { getTaskDetail, transitionCode, revertTransitionCode } from '@/api/comm_tube'
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

const revertTransitionCodeAction = async () => {
  const res = await revertTransitionCode(textarea2.value)
  textarea1.value = res
}

const transitionCodeAction = async () => {
  const res = await transitionCode(textarea1.value, toRaw(taskDic.value))
  textarea2.value = res
}
const goToHome = () => {
  router.go(-1)
}

onMounted(async () => {})
</script>

<style scoped lang="less">
.mid-btns {
  display: flex;
  flex-direction: column;
  .el-button {
    margin-left: 0px;
    margin-top: 50px;
  }
}
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
      .transition-bottom-cell {
        display: flex;
        flex-direction: column;
        height: 100%;
        flex:1;
        .transition-input {
          resize: none; /* 禁用调整大小 */
          flex: 1;
          vertical-align: top; /* 文本从顶部开始 */
          outline: none; /* 移除默认的蓝色边框 */
          font-size: 14px;
          height: 100%;
        }
        .copy-btn{
          margin-top: 10px;
        }
      }
    }
  }
  .transition-container-bottom{
    padding: 0px 20px;
  }
}
</style>
