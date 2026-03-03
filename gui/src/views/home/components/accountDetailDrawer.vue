<template>
  <span>
    <el-button type="info" plain size="small" @click="openDrawerAction">详情</el-button>

    <el-drawer v-model="drawerVisible" :title="drawerTitle" size="280px">
      <el-descriptions direction="vertical" :column="2" border size="small">
        <el-descriptions-item label="可用金额">{{ fundsDic.cash }}</el-descriptions-item>
        <el-descriptions-item label="冻结金额">{{ fundsDic.frozen_cash }}</el-descriptions-item>
        <el-descriptions-item label="持仓市值">{{ fundsDic.market_value }}</el-descriptions-item>
        <el-descriptions-item label="总资产">{{ fundsDic.total_asset }}</el-descriptions-item>
      </el-descriptions>

      <el-button size="small" style="width: 100%; margin-top: 14px" @click="getAccountInfoAction">获取账号信息</el-button>
      <el-divider>功能</el-divider>

      <el-form :model="form" label-width="100px" v-if="account?.client_type == 2">
        <el-form-item label="自动逆回购">
          <el-switch size="small" v-model="form.auto_national_debt" @change="(e) => autoAutomaticReverseAtion(1, e)" />
          <el-tooltip effect="dark" content="开启后3点10分自动将盈余资金买入1天期国债逆回购，不占用资金" placement="top">
            <el-icon style="margin-left: 10px; color: #999; font-size: 18px"><QuestionFilled /></el-icon>
          </el-tooltip>
          <el-button size="small" type="primary" @click="runNationalDebtNowAction">立即</el-button>
        </el-form-item>
        <el-form-item label="自动打新股">
          <el-switch size="small" v-model="form.auto_buy_stock_ipo" @change="(e) => autoAutomaticReverseAtion(2, e)" />
          <el-tooltip effect="dark" content="开启后10点10分自动申购新股" placement="top">
            <el-icon style="margin-left: 10px; color: #999; font-size: 18px"><QuestionFilled /></el-icon>
          </el-tooltip>
          <el-button size="small" type="primary" @click="runNewStockNowAction">立即</el-button>
        </el-form-item>
        <el-form-item label="自动打债">
          <el-switch size="small" v-model="form.auto_buy_purchase_ipo" @change="(e) => autoAutomaticReverseAtion(3, e)" />
          <el-tooltip effect="dark" content="开启后10点10分自动申购新债" placement="top">
            <el-icon style="margin-left: 10px; color: #999; font-size: 18px"><QuestionFilled /></el-icon>
          </el-tooltip>
          <el-button size="small" type="primary" @click="runNewBondNowAction">立即</el-button>
        </el-form-item>
        <el-button type="danger" size="small" style="width: 100%" @click="clearAllAction">一键清仓</el-button>
        <el-divider>辅助</el-divider>
        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap">
          <el-button size="small" @click="showWindowAction">显示窗口</el-button>
          <el-button size="small" @click="hideWindowAction">隐藏窗口</el-button>
          <el-tag size="small" effect="light" type="info">pid:{{ qmtPid || '-' }}</el-tag>
        </div>
      </el-form>

      <div v-else class="ths-functional-area">
        <el-switch v-model="showTerminal" @change="(e) => controlThsWindow(e, account?.id)" active-text="显示终端" inactive-text="隐藏终端" />
        <el-button size="small" type="primary" style="width: 120px; margin-top: 10px" @click="openThsShortcutAction">打开同花顺下单</el-button>
      </div>

      <template #footer>
        <div style="display: flex; gap: 8px; width: 100%">
          <el-button type="primary" plain style="flex: 1" @click="emit('edit', account)">编辑账号</el-button>
          <el-button type="danger" plain style="flex: 1" @click="deleteAccountAction">删除账号</el-button>
        </div>
      </template>
    </el-drawer>
  </span>
</template>

<script setup>
import { QuestionFilled } from '@element-plus/icons-vue'
import {
  controlThsWindow,
  deleteAccount,
  getAccountInfo,
  getThsWindowState,
  hideWindowByPid,
  openThsShortcut,
  showWindowByPid,
  updateAccount,
  runNationalDebtNow,
  runNewStockNow,
  runNewBondNow
} from '@/api/comm_tube'
import { ElMessage, ElMessageBox } from 'element-plus'
import { reactive, ref } from 'vue'

const props = defineProps({
  account: {
    type: Object,
    default: () => ({})
  },
  qmtPid: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['edit', 'deleted'])

const drawerVisible = ref(false)
const drawerTitle = ref('账号详情')
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

const syncFormFromAccount = (account) => {
  form.auto_national_debt = account?.auto_national_debt == 1
  form.auto_buy_stock_ipo = account?.auto_buy_stock_ipo == 1
  form.auto_buy_purchase_ipo = account?.auto_buy_purchase_ipo == 1
}

const getAccountInfoAction = async () => {
  if (!props.account?.id) return
  const res = await getAccountInfo(props.account.id)
  fundsDic.cash = Number(res?.cash || 0).toFixed(2)
  fundsDic.frozen_cash = Number(res?.frozen_cash || 0).toFixed(2)
  fundsDic.market_value = Number(res?.market_value || 0).toFixed(2)
  fundsDic.total_asset = Number(res?.total_asset || 0).toFixed(2)
}

const openDrawerAction = async () => {
  if (!props.account) return
  drawerTitle.value = `账号详情 - ${props.account.account_name || ''}`
  drawerVisible.value = true
  if (props.account.client_type === 1) {
    const state = await getThsWindowState(props.account.id)
    showTerminal.value = state === true || state?.show_terminal === true
  } else {
    syncFormFromAccount(props.account)
  }
  await getAccountInfoAction()
}

const openThsShortcutAction = async () => {
  if (!props.account?.id) return
  await openThsShortcut(props.account.id)
}

const autoAutomaticReverseAtion = async (type, e) => {
  if (!props.account?.id) return
  const subDic = {}
  if (type === 1) subDic.auto_national_debt = e ? 1 : 0
  if (type === 2) subDic.auto_buy_stock_ipo = e ? 1 : 0
  if (type === 3) subDic.auto_buy_purchase_ipo = e ? 1 : 0
  await updateAccount(props.account.id, subDic)
  Object.assign(props.account, subDic)
}

// 立即执行：国债逆回购 / 打新股 / 打新债
const runNationalDebtNowAction = async () => {
  if (!props.account?.id) return
  await runNationalDebtNow(props.account.id)
}

const runNewStockNowAction = async () => {
  if (!props.account?.id) return
  await runNewStockNow(props.account.id)
}

const runNewBondNowAction = async () => {
  if (!props.account?.id) return
  await runNewBondNow(props.account.id)
}

const showWindowAction = async () => {
  if (!props.qmtPid) {
    ElMessage.warning('当前账号未获取到QMT进程PID')
    return
  }
  const ok = await showWindowByPid(props.qmtPid)
  if (!ok) {
    ElMessage.error('显示窗口失败')
    return
  }
  ElMessage.success('显示窗口成功')
}

const hideWindowAction = async () => {
  if (!props.qmtPid) {
    ElMessage.warning('当前账号未获取到QMT进程PID')
    return
  }
  const ok = await hideWindowByPid(props.qmtPid)
  if (!ok) {
    ElMessage.error('隐藏窗口失败')
    return
  }
  ElMessage.success('隐藏窗口成功')
}

const clearAllAction = () => {
  ElMessage.warning('请在任务详情页按任务执行一键清仓')
}

const deleteAccountAction = async () => {
  if (!props.account?.id) return
  try {
    await ElMessageBox.confirm('确认删除该账号吗？', '提示', { type: 'warning' })
    await deleteAccount(props.account.id)
    ElMessage.success('删除成功')
    drawerVisible.value = false
    emit('deleted')
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
    ElMessage.error(error.message || '删除失败')
  }
}
</script>

<style scoped lang="less">
.ths-functional-area {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
</style>
