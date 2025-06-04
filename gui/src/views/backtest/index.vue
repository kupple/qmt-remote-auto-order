<template>
  <div class="backtest-container">
    <div class="btn-container">
      <el-button type="primary"   @click="openModal">设置回测参数</el-button>
    </div>  
    <el-table  :default-expand-all="true" :data="tableData"  :preserve-expanded-content="true" style="width: 100%;height:80vh">
      <el-table-column label="回测日期" prop="created_at" />
      <el-table-column prop="initial_capital" label="起始金额"/>
      <el-table-column prop="final_amount" label="结束金额"/>
      <el-table-column label="操作" width="330" align="center">
        <template #default="scope">
          <div style="display: flex; align-items: center">
            <el-button link type="primary" @click="goToDetail(scope.row)">详情</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>  
import { ref, computed,onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useRouter } from 'vue-router'
const route = useRoute()
const router = useRouter()
const tableData = ref([])
import { queryBacktestByTaskId } from '@/api/comm_tube'


const getBacktestList = async () => {
  const taskId = route.query.id
  const res = await queryBacktestByTaskId(taskId)
  console.log(res)
  tableData.value = res
}

onMounted(() => {
  getBacktestList()
})
  
const goToDetail = (row) => {
  router.push(`/backtestDetail?id=${row.id}`)
}

</script>

<style scoped lang="less">
.backtest-container {
  padding: 10px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  .btn-container{
    display: flex;
    justify-content: flex-end;
    background-color: #fff;
    padding:10px;
  }
}
</style>