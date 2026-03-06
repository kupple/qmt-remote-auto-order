<template>
  <div class="detail-container">
    <div class="detail-container-content">
      <div class="bottom-container-left">
        <div class="cur-position">
          <div style="display: flex; flex-direction: row; align-items: center; justify-content: space-between">
            <span class="section-title">当前持仓</span>
            <el-button  size="small" type="primary" @click="addPositionAction">手动添加</el-button>
          </div>
          <el-table :data="currentPositionList" stripe style="width: 100%; margin-top: 10px" size="small" height="100%">
            <el-table-column align="center" label="股票代码" width="140">
              <template #default="{ row }">
                {{ row.security_code }}
                ({{ row.security_name }})
              </template>
            </el-table-column>
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
            <el-table-column fixed="right" label="操作" align="center" :width="isEdit ? 200 : 100">
              <template #default="{ row }">
                <el-button v-if="!row.is_edit" @click="editPosition(row)" type="primary" size="small">编辑</el-button>
                <div v-else style="display: flex; align-items: center">
                  <el-button @click="savePosition(row)" type="success" size="small">保存</el-button>
                  <el-button @click="editPosition(row)" size="small">取消</el-button>
                  <el-button @click="deletePosition(row)" type="danger" size="small">删除</el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
          <div class="task-detail" v-if="taskDic.order_count_type == 2">
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
        <div class="remote-position-container">
          <span class="section-title">远程持股</span>
          <el-table max-height="30vh" :data="remotePositionList" stripe style="width: 100%; margin-top: 10px" size="small">
            <el-table-column prop="security" label="股票代码" />
            <el-table-column prop="total_amount" label="数量" />
          </el-table>
          <el-button style="margin-top: 10px" size="small" @click="resetRemotePositionAction" plain>一键重置持仓</el-button>
          <el-text style="font-size: 12px; display: block; margin-top: 10px">上一次更新: {{ taskDic['updated_at'] }}</el-text>
        </div>
        <div class="btn-container">
          <span class="section-title">操作</span>
          <div class="btn-container-inner">
            <el-button size="small" @click="convertToCodeAction" plain>一键转换代码</el-button>
            <el-button size="small" @click="editTask" plain>编辑</el-button>
            <el-button size="small" @click="syncPositionAction" plain>一键同步持仓</el-button>
            <el-button size="small" type="danger" @click="clearAllStockAction" plain>一键清仓</el-button>
            <el-button size="small" type="danger" @click="deleteStock" plain>删除</el-button>
          </div>
        </div>
      </div>
    </div>
    <ListModal ref="listModalRef" @callBack="getTaskDetailAction" />
    <AddPosition ref="addPositionRef" @callBack="getCurrentPositionList" />
    <AdjustmentModal ref="adjustmentModalRef" @callBack="getTaskDetailAction" />
  </div>
</template>

<script setup>
import { deletePositionById, deleteTask, getPositionByTaskId, getTaskDetail, queryTradeToday, updatePosition, clearAllStockByTaskId, syncPositionActionByTaskId } from '@/api/comm_tube'
import { unbindStrategyKey } from '@/api/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { get as apiGet, del as apiDelete } from '@/utils/api'
import AddPosition from './addPosition.vue'
import AdjustmentModal from './adjustmentModal.vue'
import ListModal from './listModal.vue'
const router = useRouter()
const route = useRoute()
const listModalRef = ref(null)
const run_params = ref('sim_trade')
const isEdit = ref(false)
// 今日委托
const todayTradeList = ref([])
// 当前持仓
const currentPositionList = ref([])
const addPositionRef = ref(null)
const adjustmentModalRef = ref(null)
const remotePositionList = ref([])

const getRemotePositionList = async () => {
  if (!taskDic.value.strategy_code) return
  const res = await apiGet('/api/v1/positions', {
    strategy_code: taskDic.value.strategy_code
  })
  // 后端返回的数据结构假设为数组，字段包含 security_code / security_name / volume
  remotePositionList.value = Array.isArray(res?.data) ? res.data : res
}

const resetRemotePositionAction = async () => {
  ElMessageBox.confirm('确定要重置远程持仓吗？此操作不可恢复。', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      await apiDelete('/api/v1/positions', {
        strategy_code: taskDic.value.strategy_code
      })
      ElMessage({
        type: 'success',
        message: '重置成功'
      })
      await getRemotePositionList()
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '已取消重置'
      })
    })
}

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
  await getRemotePositionList()
})

const queryTradeTodayAction = async () => {
  const list = await queryTradeToday(taskDic.value.id)
  console.log(list)
  todayTradeList.value = list
}
const editPosition = (row) => {
  if (!isEdit.value) {
    isEdit.value = true
  } else {
    isEdit.value = false
  }
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

const syncPositionAction = async () => {
  ElMessageBox.confirm('确定要同步持仓吗？此操作不可恢复。', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      await syncPositionActionByTaskId(taskDic.value.id)
      ElMessage({
        type: 'success',
        message: '同步成功'
      })
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '已取消同步'
      })
    })
}

const clearAllStockAction = async () => {
  ElMessageBox.confirm('确定要清仓吗？此操作不可恢复。', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      await clearAllStockByTaskId(taskDic.value.id)
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '已取消清仓'
      })
    })
}

const goToHome = () => {
  router.go(-1)
}

const taskDic = ref({})
const deleteStock = () => {
  ElMessageBox.confirm(`是否确认删除任务"${taskDic.value.name}"`, '确认删除', {
    confirmButtonText: '是',
    cancelButtonText: '否'
  })
    .then(async ({ value }) => {
      if (taskDic.value.task_type == 2) {
        await unbindStrategyKey({ strategy_keys_id: taskDic.value.strategy_keys_id })
      }
      deleteTask({ id: taskDic.value.id })
      ElMessage({
        type: 'success',
        message: '删除成功'
      })
      goToHome()
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
  isEdit.value = false
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
  isEdit.value = false
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
      width: 65%;
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
      flex: 1;
      min-height: 100%;

      .remote-position-container {
        padding: 10px;
        background: #fff;
      }
      .btn-container {
        padding: 10px;
        background: #fff;
        margin-top: 10px;
        display: flex;
        flex-direction: column;
        .btn-container-inner {
          display: flex;
          flex-wrap: wrap;
          background: #fff;
          gap: 10px;
          margin-top: 10px;
          justify-content: flex-start;
          .el-button + .el-button {
            margin-left: 0px;
          }
        }
      }
    }
  }
}
</style>
