<template>
  <el-dialog v-model="visible" title="新建回测任务" width="50%">
    <el-form :model="form" :rules="rules" ref="formRef" label-width="170px">
      <el-form-item label="回测名称" prop="strategyName">
        <el-input v-model="form.name" placeholder="请输入策略名称" />
      </el-form-item>

      <el-form-item label="初始资金" prop="initialCapital">
        <el-input-number v-model="form.initial_capital" :min="10000" :step="10000" />
      </el-form-item>

      <el-form-item label="回测频率" prop="frequency">
        <el-select v-model="form.frequency" placeholder="请选择回测频率">
          <el-option label="日线" value="daily" />
          <el-option label="分钟线" value="minute" />
        </el-select>
      </el-form-item>
      <el-form-item label="手续费设置" required>
        <div class="service_charge">
          <div class="service_charge-item">
            <span>费率(万分之几)</span>
            <el-input style="width: 200px;" v-model="form.service_charge" placeholder="请输入账号分配金额" type="number" :min="0" />
          </div>
          <div class="service_charge-item">
            <span>最低手续费(免5输入0)</span>
            <el-input style="width: 200px;" v-model="form.lower_limit_of_fees" placeholder="请输入账号分配金额" type="number" :min="0" />
          </div>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="closeModal">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { createBacktest } from '@/api/comm_tube'

const emit = defineEmits(['update:modelValue', 'submit'])
const visible = ref(false)
const formRef = ref(null)
const task_id = ref('')

const form = reactive({
  name: '',
  initial_capital: 100000,
  frequency: '',
  task_id: '',
  service_charge: '',
  lower_limit_of_fees: ''
})

const rules = {
  initial_capital: [{ required: true, message: '请输入初始资金', trigger: 'change' }],
  name: [{ required: true, message: '请输入回测名称', trigger: 'change' }],
  frequency: [{ required: true, message: '请选择回测频率', trigger: 'change' }]
}

const closeModal = () => {
  visible.value = false
}

const handleSubmit = () => {
  formRef.value.validate((valid) => {
    if (valid) {
      emit('submit', { ...form })
      visible.value = false
      formRef.value.resetFields()
      createBacktest({
        initial_capital: form.initial_capital,
        name: form.name,
        frequency: form.frequency,
        service_charge: form.service_charge,
        lower_limit_of_fees: form.lower_limit_of_fees,
        task_id: task_id.value
      })
    }
  })
}

const showModal = (task_id) => {
  visible.value = true
  task_id.value = task_id
}
defineExpose({ showModal })
</script>

<style scoped lang="less">
.dialog-footer {
  text-align: right;
}
.service_charge {
  display: flex;
  flex-direction: column;
  align-items: center;
  .service_charge-item {
    display: flex;
    flex-direction: column;
  }
}
</style>
