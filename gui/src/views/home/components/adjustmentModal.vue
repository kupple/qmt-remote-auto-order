<template>
  <el-dialog v-model="dialogVisible" title="调整金额" width="40vw" center>
    <el-form :model="form" label-width="120px">
      <el-form-item label="分配金额" required>
        <el-input v-model="form.allocation_amount" placeholder="请输入账号分配金额" type="number" :min="0" @input="handleAllocationAmountInput" />
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
import { QuestionFilled } from '@element-plus/icons-vue'
import { createTask, checkStrategyCodeExists } from '@/api/comm_tube'
import { ElMessage } from 'element-plus'
const taskList = computed(() => useCommonStore().taskList)
const emit = defineEmits(['getTaskList'])
const dialogVisible = ref(false)
const form = reactive({
  name: '',
  platform: 1,
  strategy_code: '',
  order_count_type: 1,
  strategy_amount: 0,
  allocation_amount: 0,
  service_charge: 0,
  lower_limit_of_fees: 0
})
const editDic = ref({})

const handleStrategyAmountInput = (value) => {
  const num = Number(value)
  if (!isNaN(num)) {
    form.strategy_amount = Number(num.toFixed(2))
  }
}

const handleAllocationAmountInput = (value) => {
  const num = Number(value)
  if (!isNaN(num)) {
    form.allocation_amount = Number(num.toFixed(2))
  }
}

const showModal = (dic) => {
  dialogVisible.value = true
  if (dic) {
    editDic.value = dic
    form.name = dic.name
    form.strategy_code = dic.strategy_code
    form.order_count_type = dic.order_count_type
    form.strategy_amount = dic.strategy_amount
    form.allocation_amount = dic.allocation_amount
  } else {
    editDic.value = null
  }
}
const handleSubmit = async () => {
  await createTask({
    id: editDic.value?.id || undefined,
    name: form.name,
    strategy_code: form.strategy_code,
    order_count_type: form.order_count_type,
    strategy_amount: form.strategy_amount,
    allocation_amount: form.allocation_amount,
    service_charge: form.service_charge,
    lower_limit_of_fees: form.lower_limit_of_fees
  })
  emit('getTaskList')
  dialogVisible.value = false
  ElMessage.success('修改成功')
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
.service_charge {
  display: flex;
  align-items: center;
  gap: 20px;
  .service_charge-item {
    display: flex;
    flex-direction: column;
  }
}
</style>
