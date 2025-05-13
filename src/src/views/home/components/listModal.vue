<template>
  <el-dialog v-model="dialogVisible" title="新建任务" width="60vw" center>
    <el-form :model="form" label-width="120px">
      <el-form-item label="任务名称">
        <el-input style="width: 50%" v-model="form.name" placeholder="请输入任务名称" />
      </el-form-item>
      <el-form-item label="下单类型">
        <el-radio-group v-model="form.orderCountType">
          <el-radio :label="1">跟随策略下单数量</el-radio>
          <el-radio :label="2">策略实际按比例数量下单</el-radio>
        </el-radio-group>
      </el-form-item>
      <div v-if="form.orderCountType === 2" class="amount-container" style="display: flex; justify-content: space-between">
        <el-form-item label="策略金额">
          <el-input v-model="form.strategyAmount" placeholder="请输入策略金额" type="number" :min="0" @input="handleStrategyAmountInput" />
        </el-form-item>
        <el-form-item label="实际分配金额">
          <el-input v-model="form.allocationAmount" placeholder="请输入账号分配金额" type="number" :min="0" @input="handleAllocationAmountInput" />
        </el-form-item>
      </div>
      <el-form-item v-else label="实际分配金额">
        <el-input style="width: 50%" v-model="form.allocationAmount" placeholder="请输入账号分配金额" type="number" :min="0" @input="handleAllocationAmountInput" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSubmit">保存</el-button>
        <el-button @click="dialogVisible = false">取消</el-button>
      </el-form-item>
    </el-form>
  </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCommonStore } from '@/store/common.js'

const taskList = computed(() => useCommonStore().taskList)
const emit = defineEmits(['getTaskList'])
const dialogVisible = ref(false)
const form = ref({
  name: '',
  orderCountType: 1,
  strategyAmount: 0,
  allocationAmount: 0
})

const handleStrategyAmountInput = (value) => {
  const num = Number(value)
  if (!isNaN(num)) {
    form.value.strategyAmount = Number(num.toFixed(2))
  }
}

const handleAllocationAmountInput = (value) => {
  const num = Number(value)
  if (!isNaN(num)) {
    form.value.allocationAmount = Number(num.toFixed(2))
  }
}

const showModal = () => {
  dialogVisible.value = true
}
const handleSubmit = async () => {
  await window.pywebview.api.createTask(form.value)
  emit('getTaskList')
  dialogVisible.value = false
}

defineExpose({
  showModal
})
</script>

<style scoped lang="less">
.list-container-modal {
  padding: 20px;
  background: #fff;
}
</style>
