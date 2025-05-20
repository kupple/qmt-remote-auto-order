<template>
  <el-dialog v-model="dialogVisible" :title="editDic ? '编辑任务' : '新建任务'" width="60vw" center>
    <el-form :model="form" label-width="120px">
      <el-form-item label="任务名称" required>
        <el-input style="width: 50%" v-model="form.name" placeholder="请输入任务名称" />
      </el-form-item>
      <el-form-item label="任务编号" >
        <el-input style="width: 50%" v-model="form.strategy_code" placeholder="请输入任务编号" maxlength="6" />
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
import { ref, computed, onMounted, reactive } from 'vue'
import { useCommonStore } from '@/store/common.js'
import { createTask } from '@/api/comm_tube'
const taskList = computed(() => useCommonStore().taskList)
const emit = defineEmits(['getTaskList'])
const dialogVisible = ref(false)
const form = reactive({
  name: '',
  strategy_code: '',
  orderCountType: 1,
  strategyAmount: 0,
  allocationAmount: 0
})
const editDic = ref({})

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

const showModal = (dic) => {
  dialogVisible.value = true
  if (dic) {
    editDic.value = dic
    form.name = dic.name
    form.strategy_code = dic.strategy_code
    form.orderCountType = dic.order_count_type
    form.strategyAmount = dic.strategy_amount
    form.allocationAmount = dic.allocation_amount
  } else {
    editDic.value = null
  }
}
const handleSubmit = async () => {
  await createTask({
    id: editDic.value?.id || undefined,
    name: form.name,
    strategy_code: form.strategy_code,
    orderCountType: form.orderCountType,
    strategyAmount: form.strategyAmount,
    allocationAmount: form.allocationAmount
  })
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
