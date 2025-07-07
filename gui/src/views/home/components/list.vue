<template>
  <div class="home-container">
    <div class="bottom-container">
      <div class="bottom-container-left">
        <div v-if="taskList.length == 0" style="text-align: center; margin-top: 20px">
          <el-empty description="暂无策略任务">
            <el-button type="primary" @click="openModal">创建一个跟随策略任务</el-button>
          </el-empty>
        </div>
        <el-button v-if="taskList.length > 0" type="primary" class="create-task-btn" @click="openModal">新建开仓</el-button>
        <div class="task-list" v-if="taskList.length > 0">
          <div v-for="(item, idx) in taskList" :key="idx" :class="{ 'task-cell': true, 'task-cell-activate': item.is_open == 1 }">
            <div class="cell-left">
              <div class="task-name">
                {{ item.name }}
                <span v-if="item.is_open == 1" style="margin-left: 10px">(运行中)</span>
                <!-- <span v-else style="margin-left: 10px">(未运行)</span> -->
              </div>
              <div class="strategy_code">
                <span
                  >{{ item.strategy_code }}<span style="margin-left: 6px" v-if="item.task_type == 2">from:{{ item.host_user_email }}</span></span
                >
              </div>
              <div class="cell-order_count_type">
                <el-tag style="margin-right: 5px" round effect="plain" disable-transitions v-if="item.platform == 10">API调用</el-tag>
                <el-tag style="margin-right: 5px" round effect="plain" disable-transitions v-else type="danger">聚宽</el-tag>
                <el-tag round effect="plain" disable-transitions v-if="item.task_type == 1 && item.platform != 10">自建策略</el-tag>
                <el-tag round effect="plain" disable-transitions v-if="item.task_type == 2 && item.platform != 10" type="danger">他人策略</el-tag>
                <el-tag round effect="plain" style="margin-left: 5px" disable-transitions v-if="item.order_count_type == 1" type="success">跟随策略</el-tag>
                <el-tag round effect="plain" style="margin-left: 5px" disable-transitions v-else type="primary">
                  动态调整->{{ item.dynamic_calculation_type == 1 ? '固定仓位' : '同步仓位' }}
                </el-tag>
                <!-- <span class="order_count_amount" v-if="item.order_count_type == 2"> 起始金额:{{ item.allocation_amount }} </span> -->
              </div>
            </div>
            <div class="cell-right">
              <div v-if="item.is_open === 0" class="cell-right-row" @click="handleEdit({ id: item.id, is_open: 1, name: item.name })">
                <!-- <el-icon color="#fff" size="20"><VideoPlay /></el-icon> -->
                <img src="@/assets/images/start.png" style="width: 30px; height: 30px" />
                <span class="cell-right-row-label" style="font-size: 12px; margin-right: 5px">开启策略</span>
              </div>
              <div v-else class="cell-right-row" @click="handleEdit({ id: item.id, is_open: 0, name: item.name })">
                <img src="@/assets/images/stop.png" style="width: 30px; height: 30px" />
                <span class="cell-right-row-label" style="font-size: 12px; margin-right: 5px">关闭策略</span>
              </div>
              <div class="cell-right-row" @click="goToDetail(item)">
                <el-icon color="#fff" size="18"><Setting /></el-icon>
                <span class="cell-right-row-label">详情/设置</span>
              </div>
              <div class="cell-right-row" @click="backtestAction(item)">
                <el-icon color="#fff" size="18"><Odometer /></el-icon>
                <span class="cell-right-row-label">查看回测</span>
              </div>
              <div class="cell-right-row" @click="convertToCodeAction(item)" v-if="!item.strategy_keys_id">
                <el-icon color="#fff" size="18"><Refresh /></el-icon>
                <span class="cell-right-row-label">代码转换</span>
              </div>
              <div class="cell-right-row" @click="shareAction(item)" v-if="!item.strategy_keys_id && form.run_model_type == 2">
                <el-icon color="#fff" size="18"><Promotion /></el-icon>
                <span class="cell-right-row-label">分享策略</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="bottom-container-right">
        <el-descriptions direction="vertical" :column="2" border size="small">
          <el-descriptions-item label="可用金额">{{ fundsDic.cash }}</el-descriptions-item>
          <el-descriptions-item label="冻结金额">{{ fundsDic.frozen_cash }}</el-descriptions-item>
          <el-descriptions-item label="持仓市值">{{ fundsDic.market_value }}</el-descriptions-item>
          <el-descriptions-item label="总资产">{{ fundsDic.total_asset }}</el-descriptions-item>
        </el-descriptions>
        <el-button size="small"  style="width: 100px; margin-top: 10px" @click="getAccountInfoAction">获取账号信息</el-button>
        <el-divider>功能</el-divider>
        <el-form :model="form" label-width="100px" v-if="settingConfig.client_type == 2">
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
          <!-- <el-divider>系统</el-divider>
          <el-form-item label="开机自启动">
            <el-switch size="small" v-model="form.auto_startup" @change="(e) => autoAutomaticReverseAtion(4, e)" />
          </el-form-item> -->
        </el-form>
        <div v-else class="ths-functional-area">
          <el-switch v-model="form.show_terminal" @change="(e) => controlThsWindow(e)" active-text="显示终端" inactive-text="隐藏终端" />
          <el-button size="small" type="primary" style="width: 100px; margin-top: 10px" @click="openThsShortcutAction">打开同花顺下单</el-button>
        </div>
      </div>
    </div>
    <ListModal ref="listModalRef" @getTaskList="getTaskListAction" />
  </div>
</template>

<script setup>
import { getUserInfo } from '@/api/auth'
import {
  controlThsWindow,
  getAccountInfo,
  getSettingConfig,
  getTaskList,
  getThsWindowState,
  getUniqueID,
  openThsShortcut,
  runTask,
  saveConfig,
  setAutomatically
} from '@/api/comm_tube'
import { useCommonStore } from '@/store/common.js'
import { Odometer, Promotion, QuestionFilled, Refresh, Setting } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ListModal from './listModal.vue'

const router = useRouter() // 使用useRouter函数创建router实例
const route = useRoute()

const getThsWindowStateAction = async () => {
  const res = await getThsWindowState()
  form.show_terminal = res.show_terminal
}

const settingConfig = computed(() => {
  return useCommonStore().settingConfig
})

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

const openThsShortcutAction = () => {
  openThsShortcut()
}

const fundsDic = reactive({
  cash: 0,
  frozen_cash: 0,
  market_value: 0,
  total_asset: 0
})

const form = reactive({
  auto_national_debt: true,
  auto_buy_stock_ipo: true,
  auto_buy_purchase_ipo: true,
  run_model_type: 1,
  show_terminal: true
})

const getConfig = async () => {
  const res = await getSettingConfig()
  form.auto_national_debt = res.auto_national_debt == 1 ? true : false
  form.auto_buy_stock_ipo = res.auto_buy_stock_ipo == 1 ? true : false
  form.auto_buy_purchase_ipo = res.auto_buy_purchase_ipo == 1 ? true : false
  form.auto_startup = res.auto_startup == 1 ? true : false
  form.run_model_type = res.run_model_type
}

const taskList = computed(() => {
  return useCommonStore().taskList
})

const backtestAction = async (row) => {
  router.push(`/backtest?id=${row.id}`)
}

const convertToCodeAction = async (row) => {
  router.push(`/transition?id=${row.id}`)
}

const shareAction = (row) => {
  router.push(`/share?strategy_code=${row.strategy_code}`)
  return
}

const getAccountInfoAction = async () => {
  const res = await getAccountInfo()
  fundsDic.cash = res.cash
  fundsDic.frozen_cash = res.frozen_cash
  fundsDic.market_value = res.market_value
  fundsDic.total_asset = res.total_asset
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

const openModal = () => {
  listModalRef.value.showModal()
}

const getTaskListAction = async () => {
  let user_id = undefined
  const config = await getSettingConfig()
  if (config.run_model_type === 2) {
    const userInfo = await getUserInfo()
    user_id = userInfo.id
  } else {
    user_id = await getUniqueID()
  }
  const res = await getTaskList({
    user_id
  })
  useCommonStore().setTaskList(res)
}

const goToDetail = (row) => {
  router.push(`/home/detail?id=${row.id}`)
}

onMounted(async () => {
  await getConfig()
  await getTaskListAction()
  getThsWindowStateAction()
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
    // background: #fff;
    // padding: 10px;
    min-width: 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    gap: 10px;
    .create-task-btn {
      width: 100px;
      // align-self: flex-end;
    }
    .task-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
      overflow-y: auto;
      &::-webkit-scrollbar {
        display: none;
      }
      -ms-overflow-style: none;
      scrollbar-width: none;
      .task-cell {
        // height: 60px;
        background: linear-gradient(to right, #001629, rgb(140, 140, 140));
        border-radius: 10px;
        padding: 16px;
        padding-bottom: 6px;
        display: flex;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
        min-height: 90px;

        .cell-left {
          display: flex;
          flex-direction: column;
          position: relative;
          color: #fff;
          width: 50%;
          .task-name {
            font-size: 18px;
            font-weight: bold;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }
          .strategy_code {
            margin-top: 8px;
            font-size: 14px;
            cursor: pointer;
            display: flex;
            flex-direction: column;
          }
          .cell-order_count_type {
            margin-top: 10px;
            display: flex;
            margin-bottom: 6px;
          }
          .order_count_amount {
            font-size: 12px;
          }
        }
        .cell-right {
          display: flex;
          // background: red;
          margin-top: 30px;
          flex: 1;
          justify-content: flex-end;
          // min-width: 100px;
          .cell-right-row {
            display: flex;
            flex-direction: column;
            // justify-content: center;
            align-items: center;
            justify-content: flex-end;
            color: #fff;
            margin-left: 6px;
            cursor: pointer;
            // gap:10px;
            span {
              margin-top: 5px;
            }
            .cell-right-row-label {
              font-size: 10px;
              font-weight: bold;
            }
          }
        }
      }
      .task-cell-activate {
        /* 背景渐变色 - 原理2 */
        background: linear-gradient(-45deg, #af00f9, #01325e, #00559f, #00284b);
        /* 背景尺寸 - 原理3 */
        background-size: 600% 600%;
        /* 循环动画 - 原理4 */
        animation: gradientBG 5s ease infinite;
      }
      @keyframes gradientBG {
        0% {
          background-position: 0% 50%;
        }
        50% {
          background-position: 100% 50%;
        }
        100% {
          background-position: 0% 50%;
        }
      }
    }
  }
  .bottom-container-right {
    display: flex;
    flex-direction: column;
    flex: 1;
    padding: 10px;
    background: #fff;
    min-width: 200px;
    .ths-functional-area {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
    }
  }
}
</style>
