<template>
  <div class="backtest-container">
    <el-table size="small" :default-expand-all="true" :data="tableData" :border="true" :preserve-expanded-content="true" style="width: 100%; height: 80vh">
      <el-table-column label="日期" prop="date" width="150"/>
      <el-table-column type="expand" label="持仓">
        <template #default="props">
          <el-table :data="props.row.positions" size="small">
            <el-table-column label="股票代码" prop="stock_code" />
            <el-table-column label="持仓量" prop="volume" />
            <el-table-column label="购入价格" prop="avg_price" />
          </el-table>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { count_strategy_analyzer } from '@/api/comm_tube'
const route = useRoute()
const tableData = ref([])

const getBacktestList = async () => {
  const backtest_id = route.query.id
  const res = await count_strategy_analyzer(null, backtest_id)
  console.log(res)
  tableData.value = res.daily_positions
}

onMounted(() => {
  getBacktestList()
})
</script>

<style scoped lang="less">
.backtest-container {
  padding: 10px;
}
</style>
