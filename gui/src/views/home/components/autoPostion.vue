<template>
  <el-dialog v-model="dialogVisible" title="自动添加持仓" width="50vw" center>
    <el-button @click="getAccountPostionAction">获取账号持仓</el-button>

    <div class="position-scroll-box" v-if="positionList.length">
      <div class="position-row" v-for="item in positionList" :key="item.stock_code">
        <span class="stock-code">{{ item.stock_code }}</span>
        <el-input-number
          v-model="selectedVolumeMap[item.stock_code]"
          :min="0"
          :max="item.volume"
          controls-position="right"
        />
        <el-button type="warning" plain @click="resetVolume(item.stock_code)">归0</el-button>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">批量添加</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { batchAddPositions, getAccountPostion } from '@/api/comm_tube'
import { useCommonStore } from '@/store/common.js'
import { ElMessage } from 'element-plus'
import { computed, reactive, ref } from 'vue'

const emit = defineEmits(['callBack'])
const taskList = computed(() => useCommonStore().taskList)
const dialogVisible = ref(false)
const positionList = ref([])
const selectedVolumeMap = ref({})

const form = reactive({
  volume: 0,
  security_code: '',
  average_price: 0
})
const editDic = ref({})

const getAccountPostionAction = async () => {
  const res = await getAccountPostion(form.account_id)
  const list = Array.isArray(res) ? res : Array.isArray(res?.data) ? res.data : []
  positionList.value = list

  const map = {}
  list.forEach((item) => {
    map[item.stock_code] = Number(item.volume) || 0
  })
  selectedVolumeMap.value = map
}

const resetVolume = (stockCode) => {
  selectedVolumeMap.value[stockCode] = 0
}

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

const showModal = ({ account_id, task_id }) => {
  dialogVisible.value = true
  form.volume = 0
  form.security_code = ''
  form.account_id = account_id
  form.task_id = task_id
  form.average_price = 0
  positionList.value = []
  selectedVolumeMap.value = {}
}

const handleSubmit = async () => {
  if (!positionList.value.length) {
    ElMessage.error('请先获取账号持仓')
    return
  }

  const payload = positionList.value
    .map((item) => {
      const volume = Number(selectedVolumeMap.value[item.stock_code]) || 0
      return {
        security_code: item.stock_code,
        volume,
        task_id: form.task_id,
        is_mock: 0,
        average_price: Number(item.avg_price ?? item.open_price ?? 0)
      }
    })
    .filter((item) => item.volume > 0)

  if (!payload.length) {
    ElMessage.error('请选择要添加的持仓数量')
    return
  }

  await batchAddPositions(payload)
  emit('callBack')
  dialogVisible.value = false
  ElMessage.success('批量添加成功')
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

.position-scroll-box {
  margin-top: 12px;
  max-height: 320px;
  overflow-y: auto;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 10px;
}

.position-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;

  &:last-child {
    margin-bottom: 0;
  }
}

.stock-code {
  width: 90px;
  font-weight: 500;
}
</style>
