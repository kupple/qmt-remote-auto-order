<template>
  <div class="account-container">
    <div class="account-header">
      <el-button type="primary" @click="addAccountAction">添加账号</el-button>
    </div>
    <el-auto-resizer class="account-table">
      <template #default="{ height }">
        <el-table :data="dataSource" :height="height">
          <el-table-column prop="account_type" label="账号类型" width="140" />
          <el-table-column prop="account" label="账号" width="160" />
          <el-table-column prop="remark" label="备注" min-width="160" />
          <el-table-column label="客户端状态" width="140">
            <template #default="{ row }">
              <el-icon :color="row.client_state ? '#67C23A' : '#F56C6C'" size="18">
                <CircleCheckFilled v-if="row.client_state" />
                <CircleCloseFilled v-else />
              </el-icon>
            </template>
          </el-table-column>
          <el-table-column label="资金账号订阅状态" width="170">
            <template #default="{ row }">
              <el-icon :color="row.sub_state ? '#67C23A' : '#F56C6C'" size="18">
                <CircleCheckFilled v-if="row.sub_state" />
                <CircleCloseFilled v-else />
              </el-icon>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="320" fixed="right">
            <template #default="{ row }">
              <el-button type="info" link @click="openDrawerAction(row)">详情</el-button>
              <el-button type="primary" link @click="editAccountAction(row)">编辑</el-button>
              <el-button type="warning" link @click="hideWindowAction(row)">隐藏窗口</el-button>
              <el-button type="success" link @click="showWindowAction(row)">显示窗口</el-button>
              <el-button type="danger" link @click="deleteAccountAction(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </template>
    </el-auto-resizer>

    <el-drawer v-model="drawerVisible" :title="drawerTitle" size="300px">
      <el-descriptions direction="vertical" :column="2" border size="small">
        <el-descriptions-item label="可用金额">{{ fundsDic.cash }}</el-descriptions-item>
        <el-descriptions-item label="冻结金额">{{ fundsDic.frozen_cash }}</el-descriptions-item>
        <el-descriptions-item label="持仓市值">{{ fundsDic.market_value }}</el-descriptions-item>
        <el-descriptions-item label="总资产">{{ fundsDic.total_asset }}</el-descriptions-item>
      </el-descriptions>
      <el-row style="margin-top: 10px" :gutter="5">
        <el-col :span="24">
          <el-button size="small" style="width: 100%" @click="getAccountInfoAction">获取账号信息</el-button>
        </el-col>
      </el-row>
      <el-divider>功能</el-divider>
      <el-form :model="form" label-width="100px" v-if="currentAccount?.client_type == 2">
        <el-form-item label="自动逆回购">
          <el-switch size="small" v-model="form.auto_national_debt" @change="(e) => autoAutomaticReverseAtion(1, e)" />
          <el-tooltip effect="dark" content="开启后3点10分自动将盈余资金买入1天期国债逆回购，不占用资金" placement="top">
            <el-icon style="margin-left: 10px; color: #999; font-size: 18px"><QuestionFilled /></el-icon>
          </el-tooltip>
          <el-button type="primary" @click="immediatelyAction(1)" round size="small" style="margin-left:5px">立即</el-button>
        </el-form-item>
        <el-form-item label="自动打新股">
          <el-switch size="small" v-model="form.auto_buy_stock_ipo" @change="(e) => autoAutomaticReverseAtion(2, e)" />
          <el-tooltip effect="dark" content="开启后10点10分自动申购新股" placement="top">
            <el-icon style="margin-left: 10px; color: #999; font-size: 18px"><QuestionFilled /></el-icon>
          </el-tooltip>
          <el-button @click="immediatelyAction(2)" size="small" type="primary" round style="margin-left:5px">立即</el-button>
        </el-form-item>
        <el-form-item label="自动打债">
          <el-switch size="small" v-model="form.auto_buy_purchase_ipo" @change="(e) => autoAutomaticReverseAtion(3, e)" />
          <el-tooltip effect="dark" content="开启后10点10分自动申购新债" placement="top">
            <el-icon style="margin-left: 10px; color: #999; font-size: 18px"><QuestionFilled /></el-icon>
          </el-tooltip>
          <el-button size="small" @click="immediatelyAction(3)" type="primary" round style="margin-left:5px">立即</el-button>
        </el-form-item>
        <el-button type="danger" size="small" style="width: 100%" @click="clearAllAction">一键清仓</el-button>
      </el-form>
      <div v-else class="ths-functional-area">
        <el-switch v-model="showTerminal" @change="(e) => controlThsWindow(e, currentAccount?.id)" active-text="显示终端" inactive-text="隐藏终端" />
        <el-button size="small" type="primary" style="width: 120px; margin-top: 10px" @click="openThsShortcutAction">打开同花顺下单</el-button>
      </div>
    </el-drawer>

    <newModal ref="newModalRef" @callBack="getDataSourceList"></newModal>
  </div>
</template>

<script setup>
import { CircleCheckFilled, CircleCloseFilled, QuestionFilled } from '@element-plus/icons-vue'
import { controlThsWindow, deleteAccount, getAccountInfo, getAccountList, getThsWindowState, openThsShortcut, testConnect, updateAccount } from '@/api/comm_tube'
import { ElMessage, ElMessageBox } from 'element-plus'
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import newModal from './components/newModal.vue'

const dataSource = ref([])
const newModalRef = ref()
let timer = null

const drawerVisible = ref(false)
const drawerTitle = ref('账号详情')
const currentAccount = ref(null)
const showTerminal = ref(true)
const form = reactive({
  auto_national_debt: true,
  auto_buy_stock_ipo: true,
  auto_buy_purchase_ipo: true
})
const fundsDic = reactive({
  cash: 0,
  frozen_cash: 0,
  market_value: 0,
  total_asset: 0
})

const addAccountAction = () => newModalRef.value.showModal()
const editAccountAction = (row) => newModalRef.value.showModal(row)

const syncFormFromAccount = (account) => {
  form.auto_national_debt = account?.auto_national_debt == 1
  form.auto_buy_stock_ipo = account?.auto_buy_stock_ipo == 1
  form.auto_buy_purchase_ipo = account?.auto_buy_purchase_ipo == 1
}

const openDrawerAction = async (row) => {
  currentAccount.value = row
  drawerTitle.value = `账号详情 - ${row.account}`
  drawerVisible.value = true
  if (row.client_type === 1) {
    const state = await getThsWindowState(row.id)
    showTerminal.value = state === true || state?.show_terminal === true
  } else {
    syncFormFromAccount(row)
  }
  await getAccountInfoAction()
}

const openThsShortcutAction = async () => {
  if (!currentAccount.value) return
  await openThsShortcut(currentAccount.value.id)
}

const showWindowAction = async (row) => {
  if (row.client_type !== 1) return ElMessage.warning('仅同花顺账号支持窗口显示/隐藏')
  await controlThsWindow(true, row.id)
  ElMessage.success('已显示窗口')
}

const hideWindowAction = async (row) => {
  if (row.client_type !== 1) return ElMessage.warning('仅同花顺账号支持窗口显示/隐藏')
  await controlThsWindow(false, row.id)
  ElMessage.success('已隐藏窗口')
}

const immediatelyAction = () => {
  ElMessage.success('该功能尚未开发')
}

const autoAutomaticReverseAtion = async (type, e) => {
  if (!currentAccount.value?.id) return
  const subDic = {}
  if (type === 1) {
    subDic.auto_national_debt = e ? 1 : 0
  }
  if (type === 2) {
    subDic.auto_buy_stock_ipo = e ? 1 : 0
  }
  if (type === 3) {
    subDic.auto_buy_purchase_ipo = e ? 1 : 0
  }
  await updateAccount(currentAccount.value.id, subDic)

  Object.assign(currentAccount.value, subDic)
  dataSource.value = dataSource.value.map((item) =>
    item.id === currentAccount.value.id ? { ...item, ...subDic } : item
  )
}

const clearAllAction = async () => {
  ElMessage.warning('请在任务详情页按任务执行一键清仓')
}

const getAccountInfoAction = async () => {
  if (!currentAccount.value) return
  const res = await getAccountInfo(currentAccount.value.id)
  fundsDic.cash = Number(res?.cash || 0).toFixed(2)
  fundsDic.frozen_cash = Number(res?.frozen_cash || 0).toFixed(2)
  fundsDic.market_value = Number(res?.market_value || 0).toFixed(2)
  fundsDic.total_asset = Number(res?.total_asset || 0).toFixed(2)
}

const refreshAccountStates = async () => {
  const next = await Promise.all(dataSource.value.map(async (item) => {
    const cloned = { ...item }
    if (item.client_type === 2) {
      try {
        const res = await testConnect(item.mini_qmt_path, 2)
        cloned.client_state = !!res?.is_connect
        cloned.sub_state = Array.isArray(res?.account_arr) && res.account_arr.includes(item.client_id)
      }catch {
        cloned.client_state = false
        cloned.sub_state = false
      }
    }else {
      try {
        const state = await getThsWindowState(item.id)
        const opened = state === true || state?.show_terminal === true
        cloned.client_state = !!opened
        cloned.sub_state = !!opened
      }catch {
        cloned.client_state = false
        cloned.sub_state = false
      }
    }
    return cloned
  }))
  dataSource.value = next
}

const deleteAccountAction = async (row) => {
  try {
    await ElMessageBox.confirm('确认删除该账号吗？', '提示', { type: 'warning' })
    await deleteAccount(row.id)
    ElMessage.success('删除成功')
    await getDataSourceList()
  }catch (error) {
    if (error === 'cancel' || error === 'close') return
    ElMessage.error(error.message || '删除失败')
  }
}

const getDataSourceList = async () => {
  const res = await getAccountList()
  dataSource.value = (res || []).map((item) => ({
    ...item,
    account_type: item.client_type === 1 ? '同花顺' : 'QMT',
    account: item.client_type === 1 ? item.ths_client_id : item.client_id,
    client_state: item.is_connected === 1,
    sub_state: item.is_connected === 1
  }))
  await refreshAccountStates()
}

onMounted(async () => {
  await getDataSourceList()
  timer = setInterval(refreshAccountStates, 5000)
})

onBeforeUnmount(() => timer && clearInterval(timer))
</script>

<style scoped lang="less">
.account-container {
  display: flex;
  flex-direction: column;
  padding: 10px;
  height: 100%;
  box-sizing: baccount-box;
  .account-table {
    flex: 1;
  }
  .account-header {
    display: flex;
    align-items: center;
    width: 100%;
    margin-bottom: 10px;
  }
}
.ths-functional-area {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
</style>
