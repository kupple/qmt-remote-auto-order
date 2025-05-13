<template>
  <div class="detail-container">
    <div class="detail-container-header">
      <el-button link type="primary" style="width: 100px" :icon="ArrowLeft" @click="goToHome">返回首页</el-button>
      <span class="title">{{ taskDic.name }}</span>
    </div>
    <div class="detail-container-content">
      <div class="bottom-container-left">
        <div class="cur-position">
          <span class="section-title">当前持仓</span>
          <el-table :data="tableData" stripe style="width: 100%; margin-top: 10px" size="small">
            <el-table-column prop="date" label="股票代码" width="180" />
            <el-table-column prop="name" label="数量" width="180" />
            <el-table-column prop="address" label="现价" />
          </el-table>
        </div>
        <div class="place-orders" style="margin-top: 10px">
          <span class="section-title">今日委托</span>
          <el-table :data="tableData" stripe style="width: 100%; margin-top: 10px" size="small">
            <el-table-column prop="date" label="日期" />
            <el-table-column prop="name" label="委托时间" />
            <el-table-column prop="address" label="股票代码" />
            <el-table-column prop="address" label="交易类型" />
            <el-table-column prop="address" label="成交数量" />
            <el-table-column prop="address" label="成交价" />
            <el-table-column prop="address" label="成交额" />
          </el-table>
        </div>
      </div>
      <div class="bottom-container-right">
        <el-descriptions class="margin-top" :column="2" :size="small">
          <el-descriptions-item>
            <template #label> 开始时间 </template>
            {{ taskDic.start_time }}
          </el-descriptions-item>
        </el-descriptions>
        <el-divider content-position="center">操作</el-divider>
        <el-button link type="danger" @click="deleteStock" plain>删除</el-button>
        <el-button link type="primary" @click="copyRequestCode" plain>复制请求代码</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ArrowLeft } from '@element-plus/icons-vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ref, onMounted } from 'vue'
const router = useRouter()
const route = useRoute()
onMounted(async () => {
  const taskId = route.query.id
  const res = await window.pywebview.api.getTaskDetail({ id: taskId })
  taskDic.value = res
})
const goToHome = () => {
  router.go(-1)
}
const taskDic = ref({})
const deleteStock = () => {
  ElMessageBox.prompt(`请输入任务名"${taskDic.value.name}"以确认删除`, '确认删除', {
    confirmButtonText: '是',
    cancelButtonText: '否'
  })
    .then(({ value }) => {
      if (value === taskDic.value.name) {
        window.pywebview.api.deleteTask({ id: taskDic.value.id })
        ElMessage({
          type: 'success',
          message: '删除成功'
        })
        goToHome()
      } else {
        ElMessage({
          type: 'error',
          message: '输入错误'
        })
      }
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '输入取消'
      })
    })
}
const copyRequestCode = async () => {
  const res = await window.pywebview.api.copyRequestCode(taskDic.value)
  if (res) {
    ElMessage({
      type: 'success',
      message: '复制成功'
    })
  }
}
</script>

<style scoped lang="less">
.detail-container {
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  flex: 1;
  .detail-container-header {
    display: flex;
    flex-direction: row;
    align-items: center;
    position: relative;
    background: #fff;
    padding: 10px;
    .title {
      font-size: 20px;
      font-weight: bold;
      color: #434343;
      position: absolute;
      left: 45%;
      transform: translateX(-50%);
    }
  }
  .detail-container-content {
    display: flex;
    flex-direction: row;
    padding: 10px;
    gap: 10px;
    .bottom-container-left {
      width: 70%;
      // background: #fff;
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      // gap:1px;
      .section-title {
        font-weight: bold;
        font-size: 14px;
        color: #434343;
      }
      .cur-position {
        display: flex;
        flex-direction: column;
        background: #fff;
        flex: 1;
        padding: 7px;
        .el-table {
          flex: 1;
        }
      }
      .place-orders {
        display: flex;
        flex-direction: column;
        background: #fff;
        flex: 1;
        padding: 7px;
        // margin-top: 7px;
        .el-table {
          flex: 1;
        }
      }
    }
    .bottom-container-right {
      flex: 2;
      background: #fff;
      padding: 10px;
      height: 100%;
      // margin-top: 33px;
    }
  }
}
</style>
