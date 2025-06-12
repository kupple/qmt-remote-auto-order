<template>
  <div class="order-container">
    <div class="order-header">
      <el-form :model="form" label-width="70px">
        <el-row >
          <el-col :span="8">
            <el-form-item label="日期选择">
              <el-date-picker @change="getDataSourceList" v-model="form.date" type="date" placeholder="请选择日期" />
            </el-form-item>
          </el-col>
          <el-col :span="11">
            <el-form-item label="日志级别">
              <el-radio-group v-model="form.level" @change="getDataSourceList">
                <el-radio-button label="全部" value="" />
                <el-radio-button label="info" value="INFO" />
                <el-radio-button label="warning" value="WARNING" />
                <el-radio-button label="error" value="ERROR" />
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-button type="danger" @click="clearLogAction">清除日志</el-button>
          </el-col>
        </el-row>
      </el-form>
    </div>
    <el-auto-resizer class="order-table">
      <template #default="{ height }">
        <el-table :data="dataSource" :height="height" style="width: 100%">
          <el-table-column prop="timestamp" label="时间戳" width="150" >
            <template #default="{ row }">
              {{ dayjs(row.timestamp).format('YYYY-MM-DD HH:mm:ss') }}
            </template>
          </el-table-column>
          <el-table-column prop="level" label="日志级别" width="150" >
            <template #default="{ row }">
              <el-tag :type="row.level === 'INFO' ? 'success' : row.level === 'WARNING' ? 'warning' : 'danger'" size="small">{{ row.level }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="message" label="日志消息" width="150" />
          <el-table-column prop="module" label="模块" width="150" />
          <el-table-column prop="func_name" label="函数名称" width="150" />
          <el-table-column prop="line_num" label="行号" width="150" />
        </el-table>
      </template>
    </el-auto-resizer>
    <el-pagination v-model="pageInfo.page" :page-sizes="[100, 200, 300, 400]" style="margin-top: 10px" :page-size="pageInfo.pageSize" :pager-count="11" layout="total, prev, pager, next" @current-change="changePageAction" />
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, watch, toRaw, computed } from 'vue'
import { queryLogList, clearLog } from '@/api/comm_tube'
import dayjs from 'dayjs'
import { ElMessage, ElMessageBox } from 'element-plus'

const scrollDelta = ref(0)
import { useCommonStore } from '@/store/common.js'
const scrollRows = ref(0)
const form = reactive({
  date: '',
  level: '',
})
const taskList = computed(() => {
  return useCommonStore().taskList
})

const pageInfo = reactive({
  page: 1,
  pageSize: 100
})


const dataSource = ref([])

const getDataSourceList = async () => {
  const res = await queryLogList({
    page: pageInfo.page,
    level: form.level ? form.level : undefined,
    date: form.date ? dayjs(form.date).format('YYYY-MM-DD') : undefined,
    pageSize: pageInfo.pageSize
  })
  dataSource.value = res.data
}

const changePageAction = (page) => {
  pageInfo.page = page
  getDataSourceList()
}
// 清除日志
const clearLogAction = () => {
  ElMessageBox.confirm(
    '确定要清除日志吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {  
    clearLog()
    ElMessage({
      type: 'success',
      message: '清除成功'
    })
     getDataSourceList()
  })
}

onMounted(async () => {
  await getDataSourceList()
})
</script>

<style scoped lang="less">
.order-container {
  display: flex;
  flex-direction: column;
  padding: 10px;
  height: 100%;
  box-sizing: border-box;
  .order-table {
    flex: 1;
  }
  .order-header {
    display: flex;
    align-items: center;
    width: 100%;
    // justify-content: space-between;
    // margin-bottom: 10px;
    // height: 100px;
    .el-form {
      width: 100%;
    }
  }
}
</style>
