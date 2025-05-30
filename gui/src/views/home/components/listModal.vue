<template>
  <el-dialog v-model="dialogVisible" :title="editDic ? '编辑任务' : '新建任务'" width="60vw" center>
    <el-form :model="form" label-width="120px">
      <el-form-item label="任务名称" required>
        <el-input style="width: 50%" v-model="form.name" placeholder="请输入任务名称" />
      </el-form-item>
      <el-form-item label="任务编号">
        <el-input style="width: 50%" v-model="form.strategy_code" placeholder="请输入任务编号" maxlength="6" />
      </el-form-item>
      <el-form-item label="下单类型">
        <el-radio-group v-model="form.order_count_type">
          <el-radio style="margin-right: 5px" :label="1">资金跟随策略</el-radio>
          <el-tooltip effect="dark" content="资金分配完全跟随端策略，不易产生剩余资金" placement="top">
            <el-icon style="color: #999; font-size: 18px; margin-right: 40px"><QuestionFilled /></el-icon>
          </el-tooltip>
          <el-radio :label="2" style="margin-right: 5px">动态调整模式</el-radio>
          <el-tooltip effect="dark" content="可以动态分配资金控制仓位暂未开放" placement="top">
            <el-icon style="color: #999; font-size: 18px"><QuestionFilled /></el-icon>
          </el-tooltip>
        </el-radio-group>
      </el-form-item>
      <div v-if="form.order_count_type === 2" class="amount-container" style="display: flex; justify-content: space-between">
        <!-- <el-form-item label="策略金额">
          <el-input v-model="form.strategyAmount" placeholder="请输入策略金额" type="number" :min="0" @input="handleStrategyAmountInput" />
        </el-form-item> -->
        <el-form-item label="分配金额" required>
          <el-input v-model="form.allocation_amount" placeholder="请输入账号分配金额" type="number" :min="0" @input="handleAllocationAmountInput" />
        </el-form-item>
      </div>
      <el-form-item label="手续费设置" v-if="form.order_count_type === 2" required>
        <div class="service_charge">
          <div class="service_charge-item">
            <span>费率(万分之几)</span>
            <el-input v-model="form.service_charge" placeholder="请输入账号分配金额" type="number" :min="0"  />
          </div>
          <div class="service_charge-item">
            <span>最低手续费(免5输入0)</span>
            <el-input v-model="form.lower_limit_of_fees" placeholder="请输入账号分配金额" type="number" :min="0" />
          </div>
        </div>
      </el-form-item>
      <el-form-item label="下单平台">
        <el-radio-group v-model="form.platform">
          <el-radio disabled :label="1">聚宽</el-radio>
        </el-radio-group>
      </el-form-item>
      <!-- <el-form-item v-else label="实际分配金额">
        <el-input style="width: 50%" v-model="form.allocationAmount" placeholder="请输入账号分配金额" type="number" :min="0" @input="handleAllocationAmountInput" />
      </el-form-item> -->
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
  service_charge:0,
  lower_limit_of_fees:0
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
  if(editDic.value?.id){
    
  }else{
    const judege = await checkStrategyCodeExists(form.strategy_code)
    if (judege) {
      ElMessage.error('任务编号已存在,请重新输入')
      return
    }
  }
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
