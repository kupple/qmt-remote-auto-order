<template>
  <div class="backtest-container">
    <div class="btn-container">
      <span>当前回测参数</span>
      <el-descriptions :column="3" border title="">
        <!-- order_count_type -->
        <el-descriptions-item label="任务类型">
          <el-tag disable-transitions	 v-if="taskDetail.order_count_type == 1" type="success">跟随策略</el-tag>
          <el-tag disable-transitions	  v-else type="primary">动态调整</el-tag>
        </el-descriptions-item>
        <el-descriptions-item v-if="taskDetail.order_count_type == 2" label="初始金额">{{ taskDetail.mock_allocation_amount }}</el-descriptions-item>
        <el-descriptions-item v-if="taskDetail.order_count_type == 2" label="手续费">{{ taskDetail.mock_service_charge }}</el-descriptions-item>
        <el-descriptions-item v-if="taskDetail.order_count_type == 2" label="手续费下限">{{ taskDetail.mock_lower_limit_of_fees }}</el-descriptions-item>
        <el-descriptions-item v-if="taskDetail.order_count_type == 1" label="说明">资金跟随策略，不统计盈亏和手续费</el-descriptions-item>
        <el-descriptions-item v-if="taskDetail.order_count_type == 2" label="说明">保留资金记录</el-descriptions-item>
      </el-descriptions>
      <el-button v-if="taskDetail.order_count_type == 2" class="sub-btn" type="primary" @click="openModal">设置回测参数</el-button>
    </div>
    <el-table class="table-container" :default-expand-all="true" :data="tableData" :preserve-expanded-content="true" >
      <el-table-column label="回测日期" prop="created_at" />
      <el-table-column v-if="taskDetail.order_count_type == 2" prop="initial_capital" label="起始金额" />
      <el-table-column v-if="taskDetail.order_count_type == 2" prop="final_amount" label="结束金额" />
      <el-table-column prop="state" label="状态" >
        <template #default="scope">
          <el-tag disable-transitions	 v-if="scope.row.state == 'run'" type="danger">运行中/未结束</el-tag>
          <el-tag disable-transitions	  v-else type="success">已完成</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作"  align="center">
        <template #default="scope">
          <div style="display: flex; align-items: center">
            <el-button link type="primary" @click="goToDetail(scope.row)">详情</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>
    <NewModal ref="listModalRef" :isBacktest="true" @callBack="getTaskDetailAction" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useRouter } from 'vue-router'
const route = useRoute()
const router = useRouter()
const tableData = ref([])
const taskDetail = ref({})
import { queryBacktestByTaskId, getTaskDetail } from '@/api/comm_tube'
import NewModal from '@/views/backtest/components/newModal.vue'

const listModalRef = ref(null)
const getBacktestList = async () => {
  const taskId = route.query.id
  const res = await queryBacktestByTaskId(taskId)
  tableData.value = res
}
const getTaskDetailAction = async () => {
  const res = await getTaskDetail({ id: route.query.id })
  taskDetail.value = res
}
const openModal = async () => {
  listModalRef.value.showModal(taskDetail.value)
}
onMounted(() => {
  getTaskDetailAction()
  getBacktestList()
})

const goToDetail = (row) => {
  router.push(`/backtestDetail?id=${row.id}`)
}
</script>

<style scoped lang="less">
.backtest-container {
  padding: 10px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  height: 100%;
  box-sizing: border-box;
  .table-container{
    flex:1;
  }
  .btn-container {
    display: flex;
    // justify-content: space-between;
    align-items: center;
    background-color: #fff;
    padding: 10px;
    position: relative;
    margin-bottom: 10px;
    span {
      // font-weight: bold;
      font-size: 16px;
      margin-right: 10px;
    }
    .sub-btn {
      position: absolute;
      right: 10px;
    }
  }
}
</style>
