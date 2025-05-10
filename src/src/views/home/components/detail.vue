<template>
  <div class="detail-container">
    <el-button type="primary" style="width: 100px" :icon="ArrowLeft" @click="goToHome">返回首页</el-button>
    <div class="detail-container-content">
      <div class="bottom-container-left">
        <div class="cur-position">
          <span class="section-title">当前持仓</span>
          <el-table :data="tableData" stripe style="width: 100%" size="small">
            <el-table-column prop="date" label="股票代码" width="180" />
            <el-table-column prop="name" label="数量" width="180" />
            <el-table-column prop="address" label="现价" />
          </el-table>
        </div>
        <div class="place-orders">
          <span class="section-title">今日委托</span>
          <el-table :data="tableData" stripe style="width: 100%" size="small">
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
            <template #label> Username </template>
            kooriookami
          </el-descriptions-item>
          <el-descriptions-item>
            <template #label> Telephone </template>
            18100000000
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ArrowLeft } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
const router = useRouter()
const goToHome = () => {
  router.go(-1)
}
</script>

<style scoped lang="less">
.detail-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  box-sizing: border-box;
  flex: 1;
  .detail-container-content {
    display: flex;
    flex-direction: row;
    gap: 10px;
    &-left {
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
    &-right {
      flex: 2;
      background: #fff;
      padding: 10px;
    }
  }
}
</style>
