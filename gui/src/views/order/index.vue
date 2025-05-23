<template>
  <div class="order-container">
    <div class="order-header">
      <el-form :inline="true" :model="form" label-width="100px">
        <el-form-item label="日期选择">
          <el-date-picker @change="getDataSourceList" style="width: 150px" v-model="form.date" type="date" placeholder="请选择日期" />
        </el-form-item>
        <el-form-item label="订单状态">
          <el-radio-group @change="getDataSourceList" v-model="form.run_params" aria-label="label position">
            <el-radio-button value="simple_backtest">简单回测</el-radio-button>
            <el-radio-button value="full_backtest">全量回测</el-radio-button>
            <el-radio-button style="color: red" value="sim_trade">模拟交易</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="证券代码">
          <div style="display: flex; align-items: center">
            <el-input style="width: 150px" v-model="form.security_code" clearable />
            <el-button type="primary" @click="getDataSourceList">搜索</el-button>
          </div>
        </el-form-item>
      </el-form>
    </div>
    <el-auto-resizer class="order-table">
      <template #default="{ height }">
        <el-table :data="dataSource" :height="height" style="width: 100%">
          <el-table-column prop="create_time" label="下单时间" width="150" align="center" />
          <el-table-column prop="security_code" label="证券代码" width="150" />
          <el-table-column prop="volume" label="下单数量" width="150" />
          <el-table-column prop="is_buy" label="方向" width="150" >
            <template #default="{ row }">
              <el-tag :type="row.is_buy === 1 ? 'success' : 'danger'" size="small">{{ row.is_buy === 1 ? '买入' : '卖出' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="price" label="价格" width="150" />
          <el-table-column prop="run_params" label="触发类型" width="150" />
          <el-table-column prop="status" label="订单状态" width="150" />
        </el-table>
      </template>
    </el-auto-resizer>
    <el-pagination v-model="pageInfo.page" :page-sizes="[100, 200, 300, 400]" style="margin-top: 10px" :page-size="pageInfo.pageSize" :pager-count="11" layout="total, prev, pager, next" :total="pageInfo.total" @current-change="changePageAction" />
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, watch, toRaw } from 'vue'
import { getOrderList } from '@/api/comm_tube'
import dayjs from 'dayjs'
const scrollDelta = ref(0)
const scrollRows = ref(0)
const form = reactive({
  date: '',
  run_params: 'simple_backtest',
  platform: '',
  security_code: ''
})

const pageInfo = reactive({
  page: 1,
  pageSize: 100,
  total: 0
})

const dataSource = ref([])

const getDataSourceList = async () => {
  const res = await getOrderList({
    ...toRaw(form),
    date: form.date ? dayjs(form.date).format('YYYY-MM-DD') : null,
    page: pageInfo.page,
    pageSize: pageInfo.pageSize
  })
  dataSource.value = res.data.map((item) => ({
    ...item,
    create_time: dayjs(item.created_at).format('YYYY-MM-DD HH:mm:ss'),
    run_params: item.run_params === 'simple_backtest' ? '简单回测' : item.run_params === 'full_backtest' ? '全量回测' : '模拟交易'
  }))
  pageInfo.total = res.total
}

const changePageAction = (page) => {
  pageInfo.page = page
  getDataSourceList()
}

onMounted(async () => {
  form.date = new Date()
  await getDataSourceList()
})
</script>

<style scoped lang="less">
.order-container {
  display: flex;
  flex-direction: column;
  padding: 10px;
  height: 100%;
  box-sizing: border-box;
  .order-table {
    flex: 1;
  }
  .order-header {
    display: flex;
    align-items: center;
    width: 100%;
    // justify-content: space-between;
    // margin-bottom: 10px;
    // height: 100px;
    .el-form {
      width: 100%;
    }
  }
}
</style>
