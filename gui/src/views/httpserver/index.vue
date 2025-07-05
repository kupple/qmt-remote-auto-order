<template>
  <div class="api-container">
    <div class="api-container-top">
      <div class="setting-item">
        <div class="setting-item-title">HOST设置</div>
        <el-input style="width: 140px" :disabled="settindDic.open" class="setting-item-input" v-model="settindDic.host" />
      </div>
      <div class="setting-item">
        <div class="setting-item-title">端口设置</div>
        <el-input style="width: 80px" :disabled="settindDic.open" class="setting-item-input" v-model="settindDic.port" />
      </div>
      <el-tag disable-transitions v-if="settindDic.open" type="success" style="margin-right: 10px">服务正在运行</el-tag>
      <el-tag disable-transitions v-else type="danger" style="margin-right: 10px">服务未运行</el-tag>
      <el-button v-if="!settindDic.open" type="primary" @click="openHttpServerAction(true)">开启</el-button>
      <el-button v-else type="danger" @click="openHttpServerAction(false)">关闭</el-button>
    </div>
    <div class="api-container-bottom">
      <h5 style="margin: 10px 0px">api说明</h5>
      <el-collapse expand-icon-position="left">
        <el-collapse-item title="获取开仓信息" name="4">
          <div>Simplify the process: keep operating process simple and intuitive;</div>
          <div>Definite and clear: enunciate your intentions clearly so that the users can quickly understand and make decisions;</div>
          <div>Easy to identify: the interface should be straightforward, which helps the users to identify and frees them from memorizing and recalling.</div>
        </el-collapse-item>
        <el-collapse-item title="获取持仓列表" name="1">
          <div>Consistent with real life: in line with the process and logic of real life, and comply with languages and habits that the users are used to;</div>
          <div>Consistent within interface: all elements should be consistent, such as: design style, icons and texts, position of elements, etc.</div>
        </el-collapse-item>
        <el-collapse-item title="下单(买入/卖出)" name="2">
          <div>Operation feedback: enable the users to clearly perceive their operations by style updates and interactive effects;</div>
          <div>Visual feedback: reflect current state by updating or rearranging elements of the page.</div>
        </el-collapse-item>
        <el-collapse-item title="获取今日成交" name="3">
          <div>Simplify the process: keep operating process simple and intuitive;</div>
          <div>Definite and clear: enunciate your intentions clearly so that the users can quickly understand and make decisions;</div>
          <div>Easy to identify: the interface should be straightforward, which helps the users to identify and frees them from memorizing and recalling.</div>
        </el-collapse-item>
      </el-collapse>
    </div>
  </div>
</template>

<script setup>
import { isHttpServerRunning, openHttpServer } from '@/api/comm_tube'
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
const tableData = ref([])
const settindDic = reactive({
  host: '127.0.0.1',
  port: '8080',
  open: false
})
onMounted(() => {
  checkHttpServer()
})

const checkHttpServer = async () => {
  const res = await isHttpServerRunning()
  console.log(res)
  console.log('res')
  settindDic.open = res
}

const goToDetail = (row) => {
  router.push(`/backtestDetail?id=${row.id}`)
}

const openHttpServerAction = (open) => {
  settindDic.open = open
  openHttpServer(open, settindDic.host, settindDic.port)
}
</script>

<style scoped lang="less">
.api-container {
  padding: 10px;
  display: flex;
  flex-direction: column;
  // justify-content: flex-end;
  height: 100%;
  box-sizing: border-box;
  .table-container {
    flex: 1;
  }
  .api-container-top {
    display: flex;
    align-items: center;
    background: #fff;
    margin-bottom: 10px;
    padding: 8px;
    .setting-item {
      display: flex;
      align-items: center;
      .setting-item-title {
        width: 80px;
        margin-right: 10px;
      }
      .setting-item-input {
        width: 100px;
      }
      margin-right: 10px;
    }
  }
  .api-container-bottom {
    padding: 10px;
    background: #fff;
    // overflow-y: auto;
  }
}
</style>
