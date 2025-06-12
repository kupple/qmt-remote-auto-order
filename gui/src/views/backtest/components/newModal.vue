<template>
  <el-dialog v-model="dialogVisible" title="回测参数设置" width="60vw" center>
    <el-form :model="form" label-width="120px">
      <div class="amount-container" style="display: flex; justify-content: space-between">
        <el-form-item label="分配金额" required>
          <el-input v-model="form.mock_allocation_amount" placeholder="请输入账号分配金额" type="number" :min="0" @input="handleAllocationAmountInput" />
        </el-form-item>
      </div>
      <el-form-item label="手续费设置" required>
        <div class="service_charge">
          <div class="service_charge-item">
            <span>费率(万分之几)</span>
            <el-input v-model="form.mock_service_charge" placeholder="请输入账号分配金额" type="number" :min="0"  />
          </div>
          <div class="service_charge-item">
            <span>最低手续费(免5输入0)</span>
            <el-input v-model="form.mock_lower_limit_of_fees" placeholder="请输入账号分配金额" type="number" :min="0" />
          </div>
        </div>
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
const emit = defineEmits(['callBack'])
const dialogVisible = ref(false)
const editDic = ref({})
const props = defineProps({
  isBacktest: {
    type: String,
    default: ''
  }
})
const form = reactive({
  mock_service_charge:0,
  mock_lower_limit_of_fees:0,
  mock_allocation_amount:0
})


const handleAllocationAmountInput = (value) => {
  const num = Number(value)
  if (!isNaN(num)) {
    form.mock_allocation_amount = Number(num.toFixed(2))
  }
}

const showModal = (dic) => {
  dialogVisible.value = true
  editDic.value = dic
  if (dic) {
    form.mock_service_charge = dic.mock_service_charge
    form.mock_lower_limit_of_fees = dic.mock_lower_limit_of_fees
    form.mock_allocation_amount = dic.mock_allocation_amount
  }
}
const handleSubmit = async () => {
  
  await createTask({
    id: editDic.value?.id || undefined,
    mock_service_charge: form.mock_service_charge,
    mock_lower_limit_of_fees: form.mock_lower_limit_of_fees,
    mock_allocation_amount: form.mock_allocation_amount,
  })
  dialogVisible.value = false
  ElMessage.success('保存成功')
  emit('callBack')
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
.service_charge{
  display: flex;
  align-items: center;
  gap:20px;
  .service_charge-item{
    display: flex;
    flex-direction: column;
  }
}
</style>
