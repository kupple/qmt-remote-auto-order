<template>
  <div class="order-container">
    <div class="order-header">
      <el-form :model="form" label-width="70px">
        <el-row :gutter="20">
          <el-col :span="7">
            <el-form-item label="日期选择">
              <el-date-picker @change="getDataSourceList" v-model="form.date" type="date" placeholder="请选择日期" />
            </el-form-item>
          </el-col>
          <el-col :span="9">
            <el-form-item label="时间选择">
              <el-time-picker @change="getDataSourceList" value-format="HH:mm" is-range v-model="form.time" range-separator="至" start-placeholder="开始时间" end-placeholder="结束时间" placeholder="选择时间范围"> </el-time-picker>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="任务列表">
              <el-select v-model="form.task" placeholder="请选择">
                <el-option v-for="item in taskList" :key="item.value" :label="item.label" :value="item.value"> </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="订单状态">
              <el-radio-group @change="getDataSourceList" v-model="form.run_params" aria-label="label position">
                <el-radio-button value="simple_backtest">回测</el-radio-button>
                <el-radio-button value="sim_trade">模拟/实盘</el-radio-button>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="证券代码">
              <div style="display: flex; align-items: center">
                <el-input style="width: 100px" v-model="form.security_code" clearable />
                <el-button type="primary" @click="getDataSourceList">搜索</el-button>
              </div>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </div>
    <el-auto-resizer class="order-table">
      <template #default="{ height }">
        <el-table :data="dataSource" :height="height" style="width: 100%">
          <el-table-column prop="created_time" label="下单时间" width="150" align="center" />
          <el-table-column prop="strategy_code" label="策略编号" width="150" />
          <el-table-column prop="security_code" label="证券代码" width="150" />
          <el-table-column prop="volume" label="下单数量" width="150" />
          <el-table-column prop="is_buy" label="方向" width="150">
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
import { reactive, ref, onMounted, watch, toRaw, computed } from 'vue'
import { getOrderList } from '@/api/comm_tube'
import dayjs from 'dayjs'
const scrollDelta = ref(0)
import { useCommonStore } from '@/store/common.js'
const scrollRows = ref(0)
const form = reactive({
  date: '',
  task: '',
  run_params: 'simple_backtest',
  platform: '',
  time: ['00:00', '23:59'],
  security_code: ''
})
const taskList = computed(() => {
  return useCommonStore().taskList
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
    time: form.time,
    pageSize: pageInfo.pageSize
  })
  dataSource.value = res.data.map((item) => ({
    ...item,
    created_time: dayjs(item.created_at).format('YYYY-MM-DD HH:mm:ss'),
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
  form.time = [dayjs().subtract(10, 'minute').format('HH:mm'), dayjs().format('HH:mm')]
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
