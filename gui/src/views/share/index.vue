<template>
  <div class="share-container">
    <div v-if="!isEmpty" class="share-container-content">
      <div class="bottom-container-left">
        <div class="bind-user-list">
          <span class="section-title">绑定用户列表</span>
          <el-table stripe :data="bindPeopleList" height="100%" size="small">
            <el-table-column prop="email" label="用户邮箱号" />
            <el-table-column label="备注">
              <template #default="{ row }">
                <div style="display: flex; align-items: center; gap: 5px" @click="editRemarkAction(row)">
                  <span>{{ row.remarks }}</span>
                  <el-icon size="20px"><Edit /></el-icon>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="加入日期">
              <template #default="{ row }">
                {{ dayjs(row.created_at).format('YYYY-MM-DD HH:mm:ss') }}
              </template>
            </el-table-column>
            <el-table-column label="是否开启">
              <template #default="{ row }">
                <el-switch @change="editUserOpenAction(row)" v-model="row.is_open" class="ml-2" style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949" />
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <div class="bottom-container-right">
        <el-divider content-position="center">信息</el-divider>
        <el-descriptions border :column="1">
          <el-descriptions-item>
            <template #label> 状态 </template>
            <div class="descriptions-item-section">
              <el-tag :type="strategyKeyDic.is_open ? 'success' : 'danger'">{{ strategyKeyDic.is_open ? '开启' : '关闭' }}</el-tag>
              <el-switch v-model="strategyKeyDic.is_open" style="margin-left: 10px" :before-change="againConfirmAction"></el-switch>
            </div>
          </el-descriptions-item>
          <el-descriptions-item>
            <template #label> 分享码 </template>
            <div class="descriptions-item-section">
              <span>{{ strategyKeyDic.secret_key }}</span>
              <el-button style="margin-left: 10px" link type="primary" @click="copyStrategyKey">复制</el-button>
            </div>
          </el-descriptions-item>
          <el-descriptions-item>
            <template #label> 用户数量 </template>
            <div class="descriptions-item-section">
              <span>{{ bindPeopleList.length }}</span>
            </div>
          </el-descriptions-item>
          <el-descriptions-item>
            <template #label> 用户数量限制 </template>
            <div class="descriptions-item-section">
              <span>{{ strategyKeyDic.max_users || 0 }}</span>
              <el-button style="margin-left: 10px" link type="primary" @click="editUserCountAction">修改</el-button>
            </div>
          </el-descriptions-item>
          <el-descriptions-item>
            <template #label> 过期时间设置 </template>
            <div class="descriptions-item-section">
              <span>{{ strategyKeyDic.expire_time ? dayjs(strategyKeyDic.expire_time).format('YYYY-MM-DD HH:mm:ss') : '无限制' }}</span>
              <el-button style="margin-left: 10px" link type="primary" @click="editExpireTimeAction">修改</el-button>
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </div>
    <el-empty v-else description="暂未创建分享码来一个？">
      <el-button type="primary" @click="createStrategyKeyAction">创建分享码</el-button>
    </el-empty>
    <DateSettingModal
      ref="dateSettingModalRef"
      @callBack="
        (e) =>
          updateStrategyKeyAction({
            id: strategyKeyDic.id,
            expire_time: e
          })
      "
    />
  </div>
</template>

<script setup>
import { ArrowLeft, Edit } from '@element-plus/icons-vue'
import DateSettingModal from './dateSettingModal.vue'
import { useRouter, useRoute } from 'vue-router'
import { ref, computed, watch, nextTick, onMounted, onUnmounted, reactive, h } from 'vue'
import { getBindPeopleList, getStrategyKeyByStrategyCode, createStrategyKey, updateBindPeople, updateStrategyKey } from '@/api/user'
import { ElMessageBox, ElMessage, ElLoading, ElDatePicker } from 'element-plus'
const router = useRouter()
const route = useRoute()
import dayjs from 'dayjs'
const isEmpty = ref(true)
const bindPeopleList = ref([])
const strategyKeyDic = ref({})
const dateSettingModalRef = ref(null)

const editUserCountAction = () => {
  ElMessageBox.prompt(`请输入用户最大订阅数量。注意：输入0表示无限制`, '修改用户数量', {
    confirmButtonText: '是',
    cancelButtonText: '否'
  })
    .then(async ({ value }) => {
      if (value) {
        await updateStrategyKey({ id: strategyKeyDic.value.id, max_users: parseInt(value) })
        ElMessage({
          type: 'success',
          message: '修改成功'
        })
        await getStrategyKeyByStrategyCodeAction()
        return true
      } else {
        ElMessage({
          type: 'error',
          message: '输入错误'
        })
        return true
      }
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '输入取消'
      })
    })
}

const editExpireTimeAction = () => {
  dateSettingModalRef.value.showModal(strategyKeyDic.value)
}

const editRemarkAction = (row) => {
  ElMessageBox.prompt(`请输入备注`, '修改备注', {
    confirmButtonText: '是',
    cancelButtonText: '否'
  })
    .then(async ({ value }) => {
      if (value) {
        await updateBindPeople({ strategy_keys_id: strategyKeyDic.value.id, remarks: value, map_user_id: row.id })
        ElMessage({
          type: 'success',
          message: '修改成功'
        })
        // await getBindPeopleListAction()
        return true
      } else {
        ElMessage({
          type: 'error',
          message: '输入错误'
        })
        return true
      }
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '输入取消'
      })
    })
}

const againConfirmAction = async () => {
  const curState = !strategyKeyDic.value.is_open
  if (!curState) {
    ElMessageBox.confirm(`警告 关闭后不会对已绑定的用户发送下单信息！`, '提示', {
      confirmButtonText: '是',
      cancelButtonText: '否',
      type: 'danger'
    })
      .then(async () => {
        await updateStrategyKeyAction({
          id: strategyKeyDic.value.id,
          is_open: curState
        })
        strategyKeyDic.value.is_open = false
      })
      .catch(() => {
        strategyKeyDic.value.is_open = true
      })
  } else {
    await updateStrategyKeyAction({
      id: strategyKeyDic.value.id,
      is_open: curState
    })
    strategyKeyDic.value.is_open = true
  }
}

const updateStrategyKeyAction = async (value) => {
  ElLoading.service({
    lock: true,
    text: 'Loading'
  })
  await updateStrategyKey(value)
  ElLoading.service().close()
  await getStrategyKeyByStrategyCodeAction()
}

const getBindPeopleListAction = async () => {
  const strategy_code = route.query.strategy_code
  const res = await getBindPeopleList({ strategy_code: strategy_code })
  bindPeopleList.value = res.data
}

const getStrategyKeyByStrategyCodeAction = async () => {
  const res = await getStrategyKeyByStrategyCode(route.query.strategy_code)
  if (res.data) {
    strategyKeyDic.value = res.data
    isEmpty.value = false
  } else {
    isEmpty.value = true
  }
}

const createStrategyKeyAction = async () => {
  const res = await createStrategyKey({ strategy_code: route.query.strategy_code })
  if (res.data) {
    await getStrategyKeyByStrategyCodeAction()
    isEmpty.value = false
  }
}
const editUserOpenAction = async (row) => {
  await updateBindPeople({ strategy_keys_id: strategyKeyDic.value.id, is_open: row.is_open, map_user_id: row.id })
  ElMessage({
    type: 'success',
    message: '修改成功'
  })
  await getBindPeopleListAction()
}

onMounted(async () => {
  await getStrategyKeyByStrategyCodeAction()
  await getBindPeopleListAction()
})
</script>

<style scoped lang="less">
.share-container {
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  // height: 100vh;
  height: 100%;
  width: 100%;
  overflow: hidden;
  .share-container-header {
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
  .share-container-content {
    display: flex;
    flex-direction: row;
    padding: 10px;
    gap: 10px;
    flex: 1;
    overflow: hidden;
    .bottom-container-left {
      flex: 2;
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
      gap: 10px;
      height: 100%;
      .section-title {
        font-weight: bold;
        font-size: 16px;
        color: #434343;
        margin-left: 10px;
        margin-bottom: 10px;
      }
      .bind-user-list {
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
      background: #fff;
      padding: 10px;
      height: 100%;
      overflow: auto;
      .descriptions-item-section {
        display: flex;
        align-items: center;
        justify-content: space-between;
      }
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
