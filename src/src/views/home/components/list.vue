<template>
  <div class="home-container">
    <el-form-item class="connect-div" label="远程服务器地址" prop="serverAddress">
      <div class="input-wrapper">
        <el-input v-model="serverAddress" placeholder="请输入远程服务器地址" />
        <el-button v-if="remoteStoreDic.connectState == 0" @click="connectAction" type="primary">连接</el-button>
        <el-button v-if="remoteStoreDic.connectState == 1" @click="stopConnectAction" type="danger">停止</el-button>
        <el-button v-if="remoteStoreDic.connectState == 1" @click="testConnectAction" type="warning">测试</el-button>
      </div>
    </el-form-item>
    <div class="bottom-container">
      <div class="list-container">
        <ListModal ref="listModalRef" @getTaskList="getTaskList" />
        <div class="bottom-container">
          <div class="bottom-container-left">
            <el-button type="primary" size="small" style="float: right; margin-bottom: 5px" @click="openModal">新建任务</el-button>
            <el-table class="table-container" :data="taskList" style="width: 100%">
              <el-table-column prop="name" label="任务名称" />
              <el-table-column prop="code" label="任务编号"> </el-table-column>
              <el-table-column prop="allocation_amount" label="分配金额" />
              <el-table-column label="操作" width="120">
                <template #default="scope">
                  <div style="display: flex; align-items: center">
                    <el-button link v-if="scope.row.is_open === 0" type="primary" @click="handleEdit({ id: scope.row.id, is_open: 1 })">开始</el-button>
                    <el-button link v-else type="danger" @click="handleEdit({ id: scope.row.id, is_open: 0 })">停止</el-button>
                    <el-divider direction="vertical" />
                    <el-button link type="primary" @click="goToDetail(scope.row)">详情</el-button>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <div class="bottom-container-right">
            <el-form :model="form" label-width="100px">
              <el-form-item label="自动逆回购">
                <el-switch v-model="form.is_open" />
              </el-form-item>
            </el-form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import ListModal from './listModal.vue'
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useCommonStore } from '@/store/common.js'
import { ElMessage } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
const serverAddress = ref('http://127.0.0.1:5000')
import { useRemoteStore } from '@/store/remote.js'

const router = useRouter() // 使用useRouter函数创建router实例
const route = useRoute()

const remoteStoreDic = computed(() => {
  return useRemoteStore()
})

const getTaskLists = async () => {
  await getTaskList()
}

const connectAction = () => {
  window.pywebview.api.connectWs(serverAddress.value).then((res) => {
    console.log(res)
  })
}
const stopConnectAction = () => {
  window.pywebview.api.disconnect()
}
const testConnectAction = () => {
  window.pywebview.api.testConnect(serverAddress.value)
}

const taskList = computed(() => {
  return useCommonStore().taskList
})

const form = ref({
  is_open: false
})

// 开始任务
const handleEdit = async (row) => {
  const res = await window.pywebview.api.runTask(row)
  if (res) {
    ElMessage.success('操作成功')
  } else {
    ElMessage.error('操作失败')
  }
  await getTaskList()
}

const listModalRef = ref(null)
const openModal = () => {
  listModalRef.value.showModal()
}

const getTaskList = async () => {
  console.log("lkasdjasljd;a")
  const res = await window.pywebview.api.getTaskList()
  useCommonStore().setTaskList(res)
}

const goToDetail = (row) => {
  router.push(`/home/detail?id=${row.id}`)
}

const getRemoteState = async () => {
  const res = await window.pywebview.api.getRemoteState()
  useRemoteStore().setRemoteStore({
    state: res.state == true ? 1 : 0,
    unique_id: res.unique_id
  })
}

onMounted(async () => {
  await getRemoteState()
  await getTaskList()
})
</script>

<style scoped lang="less">
.home-container {
  padding: 10px;
  height: 100%;
  padding-bottom: 10px;
  display: flex;
  flex-direction: column;
}
.input-wrapper {
  display: flex;
  .el-button {
    margin-left: 10px;
  }
}
.connect-div {
  background: #fff;
  padding: 14px;
  margin-bottom: 10px;
}

.el-form-item {
  margin-bottom: 0px;
}

.bottom-container {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-top: 5px;
  .table-container {
    flex: 3;
  }
  .bottom-container-left {
    flex: 3;
    background: #fff;
    padding: 10px;
  }
  .bottom-container-right {
    display: flex;
    flex: 1;
    padding: 10px;
    background: #fff;
  }
}
</style>
