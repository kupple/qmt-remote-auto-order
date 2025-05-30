<template>
  <div class="home-container">
    <div class="bottom-container">
      <div class="bottom-container-left">
        <el-button type="primary" style="float: right; margin-bottom: 5px" @click="openModal">新建任务</el-button>
        <el-table class="table-container" :data="taskList">
          <el-table-column prop="name" label="任务名称" />
          <el-table-column prop="strategy_code" label="任务编号"> </el-table-column>
          <el-table-column prop="order_count_type" label="下单类型">
            <template #default="scope">
              <el-tag v-if="scope.row.order_count_type == 1" type="success">跟随策略</el-tag>
              <el-tag v-else type="primary">动态调整</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="allocation_amount" label="分配金额">
            <template #default="scope">
              <span v-if="scope.row.order_count_type == 1">-</span>
              <span v-else>{{ scope.row.allocation_amount }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="270" align="center">
            <template #default="scope">
              <div style="display: flex; align-items: center">
                <el-button link v-if="scope.row.is_open === 0" type="primary" @click="handleEdit({ id: scope.row.id, is_open: 1 })">开始</el-button>
                <el-button link v-else type="danger" @click="handleEdit({ id: scope.row.id, is_open: 0 })">停止</el-button>
                <el-divider direction="vertical" />
                <el-button link type="primary" @click="goToDetail(scope.row)">详情</el-button>
                <el-divider direction="vertical" />
                <el-button link type="primary" @click="convertToCodeAction(scope.row)">代码转换</el-button>
                <el-divider direction="vertical" v-if="scope.row.order_count_type == 2" />
                <el-button v-if="scope.row.order_count_type == 2" link type="primary" @click="openAdjustmentModal(scope.row)">调整金额</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div class="bottom-container-right">
        <el-divider>功能</el-divider>
        <el-form :model="form" label-width="100px">
          <el-form-item label="自动逆回购">
            <el-switch size="small" v-model="form.auto_national_debt" @change="(e) => autoAutomaticReverseAtion(1, e)" />
            <el-tooltip effect="dark" content="开启后3点10分自动将盈余资金买入1天期国债逆回购，不占用资金" placement="top">
              <el-icon style="margin-left: 10px; color: #999; font-size: 18px"><QuestionFilled /></el-icon>
            </el-tooltip>
          </el-form-item>
          <el-form-item label="自动打新股">
            <el-switch size="small" v-model="form.auto_buy_stock_ipo" @change="(e) => autoAutomaticReverseAtion(2, e)" />
            <el-tooltip effect="dark" content="开启后10点10分自动申购新股" placement="top">
              <el-icon style="margin-left: 10px; color: #999; font-size: 18px"><QuestionFilled /></el-icon>
            </el-tooltip>
          </el-form-item>
          <el-form-item label="自动打债">
            <el-switch size="small" v-model="form.auto_buy_purchase_ipo" @change="(e) => autoAutomaticReverseAtion(3, e)" />
            <el-tooltip effect="dark" content="开启后10点10分自动申购新债" placement="top">
              <el-icon style="margin-left: 10px; color: #999; font-size: 18px"><QuestionFilled /></el-icon>
            </el-tooltip>
          </el-form-item>
          <el-divider>系统</el-divider>
          <el-form-item label="开机自启动">
            <el-switch size="small" v-model="form.auto_startup" @change="(e) => autoAutomaticReverseAtion(4, e)" />
          </el-form-item>
        </el-form>
      </div>
    </div>
    <ListModal ref="listModalRef" @getTaskList="getTaskListAction" />
    <AdjustmentModal ref="adjustmentModalRef" @getTaskList="getTaskListAction" />
  </div>  
</template>

<script setup>
import ListModal from './listModal.vue'
import AdjustmentModal from './adjustmentModal.vue'
import { ref, computed, watch, nextTick, onMounted, onUnmounted, reactive } from 'vue'
import { QuestionFilled } from '@element-plus/icons-vue'
import { useCommonStore } from '@/store/common.js'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
import { getSettingConfig, runTask, getTaskList, saveConfig,  setAutomatically } from '@/api/comm_tube'

const router = useRouter() // 使用useRouter函数创建router实例
const route = useRoute()

// 自动逆回购
const autoAutomaticReverseAtion = async (type, e) => {
  let subDic = {}
  if (type === 1) {
    subDic['auto_national_debt'] = e ? 1 : 0
  }
  if (type === 2) {
    subDic['auto_buy_stock_ipo'] = e ? 1 : 0
  }
  if (type === 3) {
    subDic['auto_buy_purchase_ipo'] = e ? 1 : 0
  }
  if (type === 4) {
    subDic['auto_startup'] = e ? 1 : 0
    await setAutomatically(e)
  }
  
  await saveConfig(subDic)
}

const form = reactive({
  auto_national_debt: true,
  auto_buy_stock_ipo: true,
  auto_buy_purchase_ipo: true
})

const getConfig = async () => {
  const res = await getSettingConfig()
  form.auto_national_debt = res.auto_national_debt == 1 ? true : false
  form.auto_buy_stock_ipo = res.auto_buy_stock_ipo == 1 ? true : false
  form.auto_buy_purchase_ipo = res.auto_buy_purchase_ipo == 1 ? true : false
  form.auto_startup = res.auto_startup == 1 ? true : false
  
}

const taskList = computed(() => {
  return useCommonStore().taskList
})

const convertToCodeAction = async (row) => {
  router.push(`/transition?id=${row.id}`)
}

// 开始任务
const handleEdit = async (row) => {
  if (row.is_open === 0) {
    // 停止操作需要确认
    try {
      await ElMessageBox.confirm('确定要停止该任务吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
    } catch (e) {
      // 用户点击取消
      return
    }
  }

  const res = await runTask(row)
  if (res) {
    ElMessage.success('操作成功')
  } else {
    ElMessage.error('操作失败')
  }
  await getTaskListAction()
}

const listModalRef = ref(null)
const adjustmentModalRef = ref(null)

const openModal = () => {
  listModalRef.value.showModal()
}

const openAdjustmentModal = (dic) => {
  adjustmentModalRef.value.showModal(dic)
}

const getTaskListAction = async () => {
  const res = await getTaskList()
  useCommonStore().setTaskList(res)
}

const goToDetail = (row) => {
  router.push(`/home/detail?id=${row.id}`)
}

onMounted(async () => {
  await getConfig()
  await getTaskListAction()
})
</script>

<style scoped lang="less">
.home-container {
  padding: 10px;
  padding-bottom: 10px;
  width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
}

.bottom-container {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-top: 5px;
  height: 100%;
  min-width: 0;
  .table-container {
    width: 100%;
    :deep(.el-table) {
      width: 100% !important;
    }
  }
  .bottom-container-left {
    flex: 5;
    background: #fff;
    padding: 10px;
    min-width: 0;
    overflow: hidden;
  }
  .bottom-container-right {
    display: flex;
    flex-direction: column;
    flex: 1;
    padding: 10px;
    background: #fff;
    min-width: 200px;
  }
}
</style>
