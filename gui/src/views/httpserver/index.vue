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
        <el-collapse-item title="获取持仓列表" name="1">
          <div class="api-introduction">
            <h4>请求：</h4>
            <code>
              <span style="color: purple">GET</span> <span style="color: #26a69a">{{ settindDic.host }}:{{ settindDic.port }}/api/positions</span>?strategy_code=<span style="color: #42a5f5">123456</span>
            </code>
            <h4>说明：</h4>
            <code>strategy_code: 策略唯一编号</code>
            <h4>返回：</h4>
            <code> security_code: 证券代码,<br> volume: 证券数量,<br> price: 证券价格,<br> amount: 证券金额,<br> average_price: 平均价格,<br> created_at: 创建时间,<br> updated_at: 更新时间,<br> delete_time: 删除时间 </code>
          </div>
        </el-collapse-item>
        <el-collapse-item title="下单(买入/卖出)" name="2">
          <div class="api-introduction">
            <h4>请求：</h4>
            <code>
              <span style="color: purple">POST</span> <span style="color: #26a69a">{{ settindDic.host }}:{{ settindDic.port }}/api/order</span>
              <br>Content-Type: application/json
            </code>
            <pre>
Body 请求体：
{
    "strategy_code": "123456",
    "stock_code": "600031.SH",
    "volume": 100,
    "price": 20,
    "order_type": 1,
    "is_buy": true
}
            </pre>
            <h4>说明：</h4>
            <code>
              strategy_code: 策略唯一编号
              <br>stock_code: 证券代码
              <br>volume: 证券数量
              <br>price: 证券价格
              <br>order_type: 1: 市价单 2: 限价单
              <br>is_buy: true: 买入 false: 卖出
            </code>
          </div>
        </el-collapse-item>
        <!-- <el-collapse-item title="获取今日成交" name="3">
          <div>Simplify the process: keep operating process simple and intuitive;</div>
          <div>Definite and clear: enunciate your intentions clearly so that the users can quickly understand and make decisions;</div>
          <div>Easy to identify: the interface should be straightforward, which helps the users to identify and frees them from memorizing and recalling.</div>
        </el-collapse-item> -->
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
.api-introduction{
  display: flex;
  flex-direction: column;
  padding: 10px;
  user-select: text;
  background: #f5f5f5;
  h4{
    margin:15px 0px;
    font-size: 16px;
    font-weight: 900;
  }
}
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
    overflow-y: auto;
  }
}
</style>
