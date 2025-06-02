<template>
  <div class="backtest-container">
    <div style="margin-bottom: 10px;">
      <el-button type="primary"  @click="openModal">新建回测任务</el-button>
    </div>  
    <el-table size="small" :default-expand-all="true" :data="tableData" :border="true" :preserve-expanded-content="true" style="width: 100%;height:80vh">
      <el-table-column type="expand">
        <template #default="props">
            <el-table :data="props.row.family" size="small">
              <el-table-column label="Name" prop="name" />
              <el-table-column label="State" prop="state" />
              <el-table-column label="City" prop="city" />
              <el-table-column label="Address" prop="address" />
              <el-table-column label="Zip" prop="zip" />
            </el-table>
        </template>
      </el-table-column>
      <el-table-column label="日期" prop="date" />
    </el-table>
    <NewModal ref="newModalRef" />
  </div>
</template>

<script setup>  
import { ref, computed } from 'vue'
import NewModal from './components/newModal.vue'
import { useRoute } from 'vue-router'
const route = useRoute()
const tableData = ref([])
const newModalRef = ref(null)

const openModal = () => {
  const taskId = route.query.id
  newModalRef.value.showModal(taskId)
}

</script>

<style scoped lang="less">
.backtest-container {
  padding: 10px;
}
</style>