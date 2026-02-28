<template>
  <div class="home-container">
    <div class="bottom-container">
      <div class="bottom-container-left">
        <div v-if="accountTaskList.length == 0" style="text-align: center; margin-top: 20px">
          <el-empty description="暂无策略任务">
            <el-button type="primary" @click="openAccountModal">添加账号</el-button>
          </el-empty>
        </div>
        <section v-if="accountTaskList.length > 0" class="task-action-section">
          <el-button type="primary" class="create-task-btn" @click="openAccountModal">添加账号</el-button>
        </section>
        <div class="task-list" v-if="accountTaskList.length > 0">
          <div v-for="(account, accountIdx) in accountTaskList" :key="`account-${account.id ?? accountIdx}`" class="account-group">
            <div class="account-group-header">
              <div class="account-title-row">
                <el-tag disable-transitions :type="account.client_type === 1 ? 'success' : account.client_type === 2 ? 'primary' : 'warning'" effect="plain" size="small">
                  {{ account.client_type === 1 ? '同花顺' : account.client_type === 2 ? 'QMT' : '未关联账号' }}
                </el-tag>
                <span class="account-name">{{ account.account_name }}</span>
              </div>
              <div class="account-header-actions">
                <div class="account-status-row" v-if="account.id">
                  <el-tag disable-transitions size="small" effect="light" :type="taskStateDic[account.id]['isAccSubState'] ? 'success' : 'danger'">订阅状态: {{ taskStateDic[account.id]["isAccSubState"]  ? '已订阅' : '未订阅' }}</el-tag>
                </div>
                <el-button type="success" style="margin-right: 10px" @click="openModal(account.id)">新建策略</el-button>
                <AccountDetailDrawer v-if="account.id" :account="account" @edit="openAccountModal" @deleted="getTaskListAction" />
              </div>
            </div>
            <div v-if="!account.task_list || account.task_list.length === 0" class="account-empty">暂无策略</div>
            <div v-for="(item, idx) in account.task_list" :key="`task-${item.id}-${idx}`" :class="{ 'task-cell': true, 'task-cell-activate': item.is_open == 1 }">
              <div class="cell-left">
                <div class="task-name">
                  <div class="task-name-left">
                    {{ item.name }}
                    <span v-if="item.is_open == 1" style="margin-left: 10px">(运行中)</span>
                  </div>
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
                  <el-tag round effect="plain" style="margin-left: 5px" disable-transitions v-else type="primary">动态调整->{{ item.dynamic_calculation_type == 1 ? '固定仓位' : '同步仓位' }}</el-tag>
                </div>
              </div>
              <div class="cell-right">
                <div v-if="item.is_open === 0" class="cell-right-row" @click="handleEdit({ id: item.id, is_open: 1, name: item.name })">
                  <img src="@/assets/images/start.png" style="width: 30px; height: 30px" />
                  <span class="cell-right-row-label" style="font-size: 12px; margin-right: 5px">开启策略</span>
                </div>
                <div v-else class="cell-right-row" @click="handleEdit({ id: item.id, is_open: 0, name: item.name })">
                  <img src="@/assets/images/stop.png" style="width: 30px; height: 30px" />
                  <span class="cell-right-row-label" style="font-size: 12px; margin-right: 5px">关闭策略</span>
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
                <div class="cell-right-row" @click="goToDetail(item)">
                  <el-icon color="#fff" size="18"><Setting /></el-icon>
                  <span class="cell-right-row-label">详情/设置</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <ListModal ref="listModalRef" @getTaskList="getTaskListAction" />
    <AccountNewModal ref="accountNewModalRef" @callBack="getTaskListAction" />
  </div>
</template>

<script setup>
import { getUserInfo } from '@/api/auth'
import { getAccountTaskList, getSettingConfig, getUniqueID, runTask } from '@/api/comm_tube'
import { useCommonStore } from '@/store/common.js'
import { Odometer, Promotion, Refresh, Setting } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import ListModal from './listModal.vue'
import AccountNewModal from './accountNewModal.vue'
import AccountDetailDrawer from './accountDetailDrawer.vue'

const router = useRouter()

const getThsWindowStateAction = async () => {
  const res = await getThsWindowState()
  form.show_terminal = res.show_terminal
}

const settingConfig = computed(() => {
  return useCommonStore().settingConfig
})

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
  run_model_type: 1,
  show_terminal: true
})

const getConfig = async () => {
  const res = await getSettingConfig()
  form.run_model_type = res.run_model_type
}

const accountTaskList = computed(() => {
  return useCommonStore().taskList
})

const taskStateDic = computed(() => {
  return useCommonStore().taskStateDic
})

const backtestAction = async (row) => {
  router.push(`/backtest?id=${row.id}`)
}

const convertToCodeAction = async (row) => {
  router.push(`/transition?id=${row.id}`)
}

const shareAction = (row) => {
  router.push(`/share?strategy_code=${row.strategy_code}`)
}

const getAccountInfoAction = async () => {
  const res = await getAccountInfo()
  fundsDic.cash = Number(res.cash || 0).toFixed(2)
  fundsDic.frozen_cash = Number(res.frozen_cash || 0).toFixed(2)
  fundsDic.market_value = Number(res.market_value || 0).toFixed(2)
  fundsDic.total_asset = Number(res.total_asset || 0).toFixed(2)
}

const handleEdit = async (row) => {
  if (row.is_open === 0) {
    try {
      await ElMessageBox.confirm('确定要停止该任务吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
    } catch (e) {
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
const accountNewModalRef = ref(null)

const openModal = (accountId) => {
  listModalRef.value.showModal(undefined, accountId)
}

const openAccountModal = (row) => {
  accountNewModalRef.value?.showModal(row)
}

const getTaskListAction = async () => {
  let user_id
  const config = await getSettingConfig()
  if (config.run_model_type === 2) {
    const userInfo = await getUserInfo()
    user_id = userInfo.id
  } else {
    user_id = await getUniqueID()
  }
  const res = await getAccountTaskList({ user_id })
  useCommonStore().setTaskList(res || [])
}

const goToDetail = (row) => {
  router.push(`/home/detail?id=${row.id}`)
}

onMounted(async () => {
  await getConfig()
  await getTaskListAction()
  // getThsWindowStateAction()
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

.account-header-actions {
  display: flex;
  align-items: center;
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
    min-width: 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    gap: 10px;
    .task-action-section {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 10px;
      background: #fff;
      border: 1px solid #e8edf3;
      border-radius: 10px;
      margin-bottom: 2px;
    }

    .create-task-btn {
      min-width: 96px;
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

      .account-group {
        display: flex;
        flex-direction: column;
        gap: 10px;
        background: #f7f9fc;
        border: 1px solid #e8edf3;
        border-radius: 12px;
        padding: 10px;
      }

      .account-group-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        padding: 8px 10px;
        border-radius: 10px;
        background: #001629;
      }

      .account-title-row {
        display: flex;
        align-items: center;
        gap: 8px;
        min-width: 0;
      }

      .account-name {
        font-size: 13px;
        color: #ffffff;
        font-weight: 600;
        max-width: 220px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .account-status-row {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-right: 20px;
      }

      .account-empty {
        font-size: 12px;
        color: #94a3b8;
        padding: 6px 2px 2px;
      }

      .task-cell {
        background: linear-gradient(to right, #001629, rgb(140, 140, 140));
        border-radius: 10px;
        padding: 16px;
        padding-bottom: 6px;
        display: flex;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
        min-height: 90px;
        margin-left: 22px;
        .cell-left {
          display: flex;
          flex-direction: column;
          position: relative;
          color: #fff;
          width: 50%;
          .task-name {
            font-size: 18px;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            .task-name-left {
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }
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
        }

        .cell-right {
          display: flex;
          margin-top: 30px;
          flex: 1;
          justify-content: flex-end;
          .cell-right-row {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-end;
            color: #fff;
            margin-left: 6px;
            cursor: pointer;
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
        background: linear-gradient(-45deg, #af00f9, #01325e, #00559f, #00284b);
        background-size: 600% 600%;
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
    min-width: 220px;
    .ths-functional-area {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
    }
  }
}
</style>
