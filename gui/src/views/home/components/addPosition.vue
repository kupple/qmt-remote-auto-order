<template>
    <el-dialog v-model="dialogVisible" title="手动添加持仓" width="50vw" center>
      <el-form :model="form" label-width="140px">
        <el-form-item label="股票代码" required>
          <el-input v-model="form.security_code" placeholder="请输入股票代码" style="width: 200px;" maxlength="6" />
          <span style="color: red">* 不需要输入.SZ .SH 等后缀系统会自动添加</span>
        </el-form-item>
        <el-form-item label="数量" required>
          <el-input-number step-strictly :step="100" v-model="form.volume" placeholder="请输入数量" type="number" :min="100" />
        </el-form-item>
        <el-form-item label="平均成本(仅显示)" required>
          <el-input v-model="form.average_price" placeholder="请输入平均成本" type="number"  @input="handleAllocationAmountInput" style="width: 200px;"/>
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
  import { addPosition, checkPositionExists } from '@/api/comm_tube'
  import { ElMessage } from 'element-plus'

  const emit = defineEmits(['callBack'])
  const taskList = computed(() => useCommonStore().taskList)
  const dialogVisible = ref(false)
  const form = reactive({
    volume: 0,
    security_code: '',
    average_price: 0,
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
      form.average_price = Number(num.toFixed(2))
    }
  }
  
  const showModal = (task_id) => {
    dialogVisible.value = true
    form.volume = 0
    form.security_code = ''
    form.task_id = task_id
    form.average_price = 0
  }
  const handleSubmit = async () => {
    if (!form.security_code) {
      ElMessage.error('请输入股票代码')
      return
    }
    if (form.security_code.length !== 6) {
      ElMessage.error('股票代码长度必须为6')
      return
    }
    if (form.volume <= 0) {
      ElMessage.error('请输入数量')
      return
    }
    if (form.average_price <= 0) {
      ElMessage.error('请输入平均成本')
      return
    }
    const exists = await checkPositionExists(form.security_code, form.task_id)
    if (exists) {
      ElMessage.error('该股票已存在')
      return
    }
    await addPosition({
      security_code: form.security_code,
      volume: form.volume,
      task_id: form.task_id,
      is_mock: 0,
      average_price: form.average_price,
    })
    emit('callBack')
    dialogVisible.value = false
    ElMessage.success('添加成功')
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
  