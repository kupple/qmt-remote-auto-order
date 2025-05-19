<template>
  <div class="detail-container">
    <div class="detail-container-content">
      <div class="bottom-container-left">
        <div class="cur-position">
          <span class="section-title">当前持仓</span>
          <el-table :data="currentPositionList" stripe style="width: 100%; margin-top: 10px" size="small" height="100%">
            <el-table-column prop="date" label="股票代码" width="180" />
            <el-table-column prop="name" label="数量" width="180" />
            <el-table-column prop="address" label="现价" />
          </el-table>
        </div>
        <div class="place-orders">
          <div style="display: flex; flex-direction: row; align-items: center">
            <span class="section-title">今日委托</span>
            <el-radio-group v-model="run_params" size="small" @change="switchEntrustedTodayList">
              <el-radio-button label="模拟盘" value="sim_trade" />
              <el-radio-button label="编码回测" value="simple_backtest" />
              <el-radio-button label="回测" value="full_backtest" />
            </el-radio-group>
          </div>
          <el-table stripe :data="entrustedTodayList" size="small" height="100%">
            <el-table-column prop="create_time" label="委托时间" />
            <el-table-column prop="security_code" label="股票代码" />
            <el-table-column prop="price" label="价格" />
            <el-table-column prop="amount" label="数量" />
            <el-table-column prop="is_buy" label="方向" width="60">
              <template #default="{ row }">
                <el-tag :type="row.is_buy === 1 ? 'success' : 'danger'" size="small">{{ row.is_buy === 1 ? '买入' : '卖出' }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination size="small" v-model="entrustedTodayPageInfo.page" :page-sizes="[100, 200, 300, 400]" style="margin-top: 10px" :page-size="entrustedTodayPageInfo.pageSize" :pager-count="11" layout="total, prev, pager, next" :total="entrustedTodayPageInfo.total" @current-change="changeEntrustedTodayPage" />
        </div>
      </div>
      <div class="bottom-container-right">
        <el-descriptions :column="2">
          <el-descriptions-item>
            <template #label> 开始时间 </template>
            {{ taskDic.start_time }}
          </el-descriptions-item>
        </el-descriptions>
        <el-divider content-position="center">操作</el-divider>
        <div class="btn-container">
          <el-button class="btn" type="primary" @click="convertToCodeAction" plain>一键转换</el-button>
          <el-button class="btn" type="primary" @click="editTask" plain>编辑</el-button>
          <el-button class="btn" type="danger" @click="deleteStock" plain>删除</el-button>
        </div>
      </div>
    </div>
    <ListModal ref="listModalRef" />
  </div>
</template>

<script setup>
import { ArrowLeft } from '@element-plus/icons-vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import ListModal from './listModal.vue'
import { getOrderList, deleteTask, getTaskDetail, copyRequestCode } from '@/api/comm_tube'

import { ref, onMounted, reactive } from 'vue'
const router = useRouter()
const route = useRoute()
const listModalRef = ref(null)
const run_params = ref('sim_trade')
// 今日委托
const entrustedTodayList = ref([])
// 当前持仓
const currentPositionList = ref([])

const entrustedTodayPageInfo = reactive({
  page: 1,
  pageSize: 100,
  total: 0
})
const currentPositionPageInfo = reactive({
  page: 1,
  pageSize: 100,
  total: 0
})
onMounted(async () => {
  const taskId = route.query.id
  const res = await getTaskDetail({ id: taskId })
  taskDic.value = res
  await getEntrustedTodayList()
  // await getCurrentPositionList()
})

const changeEntrustedTodayPage = (page) => {
  entrustedTodayPageInfo.page = page
  getEntrustedTodayList()
}

const switchEntrustedTodayList = () => {
  entrustedTodayPageInfo.page = 1
  getEntrustedTodayList()
}

const getEntrustedTodayList = async () => {
  const orderDic = await getOrderList({
    strategy_code: taskDic.value.strategy_code,
    run_params: run_params.value,
    page: entrustedTodayPageInfo.page,
    pageSize: entrustedTodayPageInfo.pageSize
  })
  entrustedTodayList.value = orderDic.data
  entrustedTodayPageInfo.total = orderDic.total
}
const getCurrentPositionList = async () => {
  const orderDic = await getOrderList({
    strategy_code: taskDic.value.strategy_code,
    run_params: run_params.value,
    page: currentPositionPageInfo.page,
    pageSize: currentPositionPageInfo.pageSize
  })
  currentPositionList.value = orderDic.data.filter((item) => item.date === new Date().toLocaleDateString())
  currentPositionPageInfo.total = orderDic.total
}
const goToHome = () => {
  router.go(-1)
}
const taskDic = ref({})
const deleteStock = () => {
  ElMessageBox.prompt(`请输入任务名"${taskDic.value.name}"以确认删除`, '确认删除', {
    confirmButtonText: '是',
    cancelButtonText: '否'
  })
    .then(({ value }) => {
      if (value === taskDic.value.name) {
        deleteTask({ id: taskDic.value.id })
        ElMessage({
          type: 'success',
          message: '删除成功'
        })
        goToHome()
      } else {
        ElMessage({
          type: 'error',
          message: '输入错误'
        })
      }
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '输入取消'
      })
    })
}
const copyRequestCodeAction = async () => {
  const res = await copyRequestCode(taskDic.value)
  if (res) {
    ElMessage({
      type: 'success',
      message: '复制成功'
    })
  }
}
const convertToCodeAction = async () => {
  router.push(`/transition?id=${taskDic.value.id}`)
}
const editTask = async () => {
  listModalRef.value.showModal(taskDic.value)
}
</script>

<style scoped lang="less">
.detail-container {
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  // height: 100vh;
  height: 100%;
  overflow: hidden;
  .detail-container-header {
    display: flex;
    flex-direction: row;
    align-items: center;
    position: relative;
    background: #fff;
    padding: 10px;
    flex-shrink: 0;
    .title {
      font-size: 20px;
      font-weight: bold;
      color: #434343;
      position: absolute;
      left: 45%;
      transform: translateX(-50%);
    }
  }
  .detail-container-content {
    display: flex;
    flex-direction: row;
    padding: 10px;
    gap: 10px;
    flex: 1;
    overflow: hidden;
    .bottom-container-left {
      width: 70%;
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
      gap: 10px;
      height: 100%;
      .section-title {
        font-weight: bold;
        font-size: 14px;
        color: #434343;
        margin-right: 10px;
      }
      .cur-position {
        display: flex;
        flex-direction: column;
        background: #fff;
        flex: 1;
        padding: 7px;
        min-height: 0;
        .el-table {
          flex: 1;
          overflow: hidden;
        }
      }
      .place-orders {
        display: flex;
        flex-direction: column;
        flex: 1;
        padding: 7px;
        background: #fff;
        justify-content: center;
        min-height: 0;
        .el-table {
          flex: 1;
          overflow: hidden;
        }
      }
    }
    .bottom-container-right {
      flex: 2;
      background: #fff;
      padding: 10px;
      height: 100%;
      overflow: auto;
    }
  }
  .btn-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;
    align-items: flex-start;
    gap: 10px;
    .btn {
      margin-left: 0px;
    }
  }
}
</style>
