<template>
  <div class="detail-container">
    <div class="detail-container-content">
      <div class="bottom-container-left">
        <div class="cur-position">
          <div style="display: flex; flex-direction: row; align-items: center; justify-content: space-between">
            <span class="section-title">当前持仓</span>
            <el-button v-if="taskDic.order_count_type == 2" size="small" type="primary" @click="addPositionAction">手动添加</el-button>
          </div>
          <el-table :data="currentPositionList" stripe style="width: 100%; margin-top: 10px" size="small" height="100%">
            <el-table-column align="center" prop="security_code" label="股票代码" />
            <el-table-column align="center" label="数量" width="150">
              <template #default="{ row }">
                <span v-if="!row.is_edit">{{ row.volume }}</span>
                <el-input-number size="small" v-else v-model="row.volume" :min="0" @change="handleChange" />
              </template>
            </el-table-column>
            <el-table-column align="center" label="股价(仅参考)" width="150">
              <template #default="{ row }">
                {{ row.average_price.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column align="center" label="市值">
              <template #default="{ row }">
                {{ (row.average_price * row.volume).toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column fixed="right" label="操作" align="center" width="200" v-if="taskDic.order_count_type == 2">
              <template #default="{ row }">
                <el-button v-if="!row.is_edit" @click="editPosition(row)" type="primary" size="small">编辑</el-button>
                <div v-else style="display: flex; align-items: center">
                  <el-button @click="savePosition(row)" type="success" size="small">保存</el-button>
                  <el-button @click="editPosition(row)" type="info" size="small">取消</el-button>
                  <el-button @click="deletePosition(row)" type="danger" size="small">删除</el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
          <div class="task-detail" v-if="taskDic.order_count_type == 2">
            <span>估算总收益: {{ total_amount }}</span>
            <div style="display: flex; align-items: center">
              <span>可用资金: {{ taskDic.can_use_amount }}</span>
              <el-button @click="openAdjustmentModal()" style="margin-left: 10px" size="small" type="primary">编辑</el-button>
            </div>
          </div>
        </div>
        <div class="place-orders">
          <div style="display: flex; flex-direction: row; align-items: center">
            <span class="section-title">今日委托</span>
          </div>
          <el-table stripe :data="todayTradeList" size="small" height="100%">
            <el-table-column prop="created_at" label="时间" />
            <el-table-column prop="stock_code" label="股票代码" />
            <el-table-column label="价格">
              <template #default="{ row }">
                {{ row.traded_price.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="traded_volume" label="数量" />
            <el-table-column label="金额">
              <template #default="{ row }">
                {{ row.traded_amount.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="方向">
              <template #default="{ row }">
                <el-tag :type="row.order_type === 23 ? 'success' : 'danger'" size="small">{{ row.order_type === 23 ? '买入' : '卖出' }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
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
    <ListModal ref="listModalRef" @callBack="getTaskDetailAction" />
    <AddPosition ref="addPositionRef" @callBack="getCurrentPositionList" />
    <AdjustmentModal ref="adjustmentModalRef" @callBack="getTaskDetailAction" />
  </div>
</template>

<script setup>
import { ArrowLeft } from '@element-plus/icons-vue'
import { useRouter, useRoute } from 'vue-router'
import AdjustmentModal from './adjustmentModal.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import ListModal from './listModal.vue'
import { getOrderList, deleteTask, getTaskDetail, getPositionByTaskId, deletePositionById, updatePosition, queryTradeToday } from '@/api/comm_tube'
import AddPosition from './addPosition.vue'
import { ref, onMounted, reactive, computed } from 'vue'
import { unbindStrategyKey } from '@/api/user'
const router = useRouter()
const route = useRoute()
const listModalRef = ref(null)
const run_params = ref('sim_trade')
// 今日委托
const todayTradeList = ref([])
// 当前持仓
const currentPositionList = ref([])
const addPositionRef = ref(null)
const adjustmentModalRef = ref(null)

const total_amount = computed(() => {
  let total = 0
  for (const item of currentPositionList.value) {
    total += item.volume * item.average_price
  }
  return (taskDic.value.can_use_amount + total).toFixed(2)
})

const openAdjustmentModal = () => {
  adjustmentModalRef.value.showModal({
    ...taskDic.value
  })
}

const getTaskDetailAction = async () => {
  const taskId = route.query.id
  const res = await getTaskDetail({ id: route.query.id })
  taskDic.value = res
}
onMounted(async () => {
  await getTaskDetailAction()
  await queryTradeTodayAction()
  await getCurrentPositionList()
})

const queryTradeTodayAction = async () => {
  const list = await queryTradeToday(taskDic.value.id)
  console.log(list)
  todayTradeList.value = list
}
const editPosition = (row) => {
  currentPositionList.value = currentPositionList.value.map((item) => {
    if (item.security_code === row.security_code) {
      return {
        ...item,
        is_edit: !item.is_edit
      }
    }
    return item
  })
}
const getCurrentPositionList = async () => {
  const positions = await getPositionByTaskId(taskDic.value.id)
  currentPositionList.value = positions
    .filter((item) => item.volume > 0)
    .map((item) => {
      return {
        ...item,
        is_edit: false
      }
    })
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
    .then(async ({ value }) => {
      if (value === taskDic.value.name) {
        if (taskDic.value.task_type == 2) {
          await unbindStrategyKey({ strategy_keys_id: taskDic.value.strategy_keys_id })
        }
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

const convertToCodeAction = async () => {
  router.push(`/transition?id=${taskDic.value.id}`)
}
const editTask = async () => {
  listModalRef.value.showModal(taskDic.value)
}
const savePosition = async (row) => {
  await updatePosition(row.id, {
    volume: row.volume
  })
  await getCurrentPositionList()
  ElMessage({
    type: 'success',
    message: '保存成功'
  })
}
const addPositionAction = () => {
  addPositionRef.value.showModal(taskDic.value.id)
}
const deletePosition = async (row) => {
  await deletePositionById(row.id)
  await getCurrentPositionList()
  ElMessage({
    type: 'success',
    message: '删除成功'
  })
}
</script>

<style scoped lang="less">
.detail-container {
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  // height: 100vh;
  height: 100%;
  width: 100%;
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
        padding-bottom: 0;
        min-height: 0;
        .el-table {
          flex: 1;
          overflow: hidden;
        }
        .task-detail {
          display: flex;
          // padding: 5px;
          font-size: 13px;
          height: 30px;
          align-items: center;
          color: #434343;
          justify-content: space-between;
          // background: red;
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
