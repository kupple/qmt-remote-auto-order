<template>
  <div class="home-container">
    <div class="bottom-container">
      <div class="bottom-container-left">
        <el-button type="primary" style="float: right; margin-bottom: 5px" @click="openModal">新建任务</el-button>
        <el-table class="table-container" :data="taskList">
          <el-table-column prop="name" label="任务名称" />
          <el-table-column prop="strategy_code" label="任务编号"> </el-table-column>
          <el-table-column prop="allocation_amount" label="分配金额" />
          <el-table-column label="操作" width="200" align="center">
            <template #default="scope">
              <div style="display: flex; align-items: center">
                <el-button link v-if="scope.row.is_open === 0" type="primary" @click="handleEdit({ id: scope.row.id, is_open: 1 })">开始</el-button>
                <el-button link v-else type="danger" @click="handleEdit({ id: scope.row.id, is_open: 0 })">停止</el-button>
                <el-divider direction="vertical" />
                <el-button link type="primary" @click="goToDetail(scope.row)">详情</el-button>
                <el-divider direction="vertical" />
                <el-button link type="primary" @click="convertToCodeAction(scope.row)">代码转换</el-button>
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
    <ListModal ref="listModalRef" @getTaskList="getTaskListAction" />
  </div>
</template>

<script setup>
import ListModal from './listModal.vue'
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useCommonStore } from '@/store/common.js'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
import { getSettingConfig, runTask, getTaskList } from '@/api/comm_tube'
const serverAddress = ref('http://127.0.0.1:5000')

const router = useRouter() // 使用useRouter函数创建router实例
const route = useRoute()

const getConfig = async () => {
  const res = await getSettingConfig()
  serverAddress.value = res.server_url
}

const taskList = computed(() => {
  return useCommonStore().taskList
})

const convertToCodeAction = async (row) => {
  router.push(`/transition?id=${row.id}`)
}

const form = ref({
  is_open: false
})

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
    flex: 3;
    background: #fff;
    padding: 10px;
    min-width: 0;
    overflow: hidden;
  }
  .bottom-container-right {
    display: flex;
    flex: 1;
    padding: 10px;
    background: #fff;
    min-width: 200px;
  }
}
</style>
