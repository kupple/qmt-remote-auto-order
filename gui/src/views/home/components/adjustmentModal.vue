<template>
  <el-dialog v-model="dialogVisible" title="调整金额" width="40vw" center>
    <el-form :model="form" label-width="120px">
      <el-form-item label="可用资金" required>
        <el-input v-model="form.can_use_amount" placeholder="请输入可用资金" type="number" :min="0" @input="handleAllocationAmountInput" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSubmit">保存</el-button>
        <el-button @click="dialogVisible = false">取消</el-button>
      </el-form-item>
    </el-form>
    <span style="color: red">* 修改金额后累计金额会重置</span>
  </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useCommonStore } from '@/store/common.js'
import { QuestionFilled } from '@element-plus/icons-vue'
import { createTask, checkStrategyCodeExists, updateTaskCanUseAmount } from '@/api/comm_tube'
import { ElMessage } from 'element-plus'
const taskList = computed(() => useCommonStore().taskList)
const emit = defineEmits(['callBack'])
const dialogVisible = ref(false)
const form = reactive({
  can_use_amount: 0,
  task_id: null
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
    form.can_use_amount = Number(num.toFixed(2))
  }
}

const showModal = (dic) => {
  console.log(dic)
  dialogVisible.value = true
  if (dic) {
    editDic.value = dic
    form.task_id = dic.id
    form.can_use_amount = dic.can_use_amount
  } else {
    editDic.value = null
  }
}
const handleSubmit = async () => {
  await updateTaskCanUseAmount(editDic.value?.id, form.can_use_amount)
  emit('callBack')
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
