<template>
  <div class="account-container">
    <div class="account-header">
      <el-button type="primary" @click="addAccountAction">添加账号</el-button>
    </div>
    <el-auto-resizer class="account-table">
      <template #default="{ height }">
        <el-table :data="dataSource" :height="height">
          <el-table-column prop="account_type" label="账号类型" width="150" />
          <el-table-column prop="account" label="账号" width="150" />
          <el-table-column prop="remark" label="备注" width="150" />
          <el-table-column prop="status" label="状态" width="150" />
        </el-table>
      </template>
    </el-auto-resizer>
    <newModal ref="newModalRef"></newModal>
  </div>
</template>

<script setup>
import { queryLogList } from '@/api/comm_tube'
import dayjs from 'dayjs'
import { onMounted, ref } from 'vue'
import newModal from './components/newModal.vue'
const dataSource = ref([])

const newModalRef = ref()
// 添加账号
const addAccountAction = ()=>{
  newModalRef.value.showModal()
}

// 获取数据
const getDataSourceList = async () => {
  const res = await queryLogList({
    page: pageInfo.page,
    level: form.level ? form.level : undefined,
    date: form.date ? dayjs(form.date).format('YYYY-MM-DD') : undefined,
    pageSize: pageInfo.pageSize
  })
  dataSource.value = res.data
}


onMounted(async () => {
  await getDataSourceList()
})
</script>

<style scoped lang="less">
.account-container {
  display: flex;
  flex-direction: column;
  padding: 10px;
  height: 100%;
  box-sizing: baccount-box;
  .account-table {
    flex: 1;
  }
  .account-header {
    display: flex;
    align-items: center;
    width: 100%;
    margin-bottom: 10px;
    .el-form {
      width: 100%;
    }
  }
}
</style>
