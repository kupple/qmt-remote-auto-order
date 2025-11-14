<template>
  <el-dialog v-model="dialogVisible" :title="editDic ? '编辑任务' : '新建开仓'" width="60vw" center>
    <el-form :model="form" label-width="120px">
      <el-form-item label="任务名称" required>
        <el-input style="width: 50%" v-model="form.name" placeholder="请输入任务名称" />
      </el-form-item>
      <el-form-item label="下单平台">
        <el-radio-group v-model="form.platform">
          <el-radio  :value="1">聚宽</el-radio>
          <el-radio  :value="10">API调用方式</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="创建类型" required v-if="isEdit == false && form.platform != 10">
        <el-radio-group v-model="form.task_type">
          <el-radio label="创建策略" :value="1" />
          <el-radio label="导入他人分享策略" :value="2" />
        </el-radio-group>
      </el-form-item>
      <el-form-item label="任务编号" v-if="form.task_type == 1 && isEdit == false">
        <el-input style="width: 50%" v-model="form.strategy_code" placeholder="请输入任务编号,不输入则随机生成" maxlength="6" />
      </el-form-item>
      <el-form-item label="分享码" v-if="form.task_type == 2 && isEdit == false">
        <el-input style="width: 50%" v-model="form.share_secret" placeholder="请输入分享秘钥" maxlength="6" />
      </el-form-item>
      <el-form-item label="下单类型" v-if="isEdit == false && form.platform != 10">
        <el-radio-group v-model="form.order_count_type">
          <el-radio style="margin-right: 5px" :value="1">仓位跟随策略</el-radio>
          <el-tooltip effect="dark" content="仓位分配完全跟随端策略，优点简单快速" placement="top">
            <el-icon style="color: #999; font-size: 18px; margin-right: 40px"><QuestionFilled /></el-icon>
          </el-tooltip>
          <el-radio :value="2" style="margin-right: 5px">动态调整模式</el-radio>
          <el-tooltip effect="dark" content="可以动态分配资金控制仓位，优点灵活" placement="top">
            <el-icon style="color: #999; font-size: 18px"><QuestionFilled /></el-icon>
          </el-tooltip>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="比例调整(倍数)" v-if="form.order_count_type === 1">
        <el-input-number step="0.1" min="0" max="100000" v-model="form.position_ratio" placeholder="请输入仓位调整金额" type="number"/>
      </el-form-item>
      <el-form-item label="动态资金模式" v-if="form.order_count_type === 2 && form.platform != 10">
        <el-radio-group v-model="form.dynamic_calculation_type">
          <el-radio style="margin-right: 5px" :value="1">固定模式</el-radio>
          <el-tooltip effect="dark" content="交易金额不会超过分配金额" placement="top">
            <el-icon style="color: #999; font-size: 18px; margin-right: 40px"><QuestionFilled /></el-icon>
          </el-tooltip>
          <el-radio :value="2" style="margin-right: 5px">根据盈亏分配</el-radio>
          <el-tooltip effect="dark" content="分配金额会根据盈亏动态调整" placement="top">
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
      <el-form-item label="手续费设置" required  v-if="form.order_count_type === 2">
        <div class="service_charge">
          <div class="service_charge-item">
            <span>费率(万分之几)</span>
            <el-input v-model="form.service_charge" placeholder="请输入账号分配金额" type="number" :min="0" />
          </div>
          <div class="service_charge-item">
            <span>最低手续费(免5输入0)</span>
            <el-input v-model="form.lower_limit_of_fees" placeholder="请输入账号分配金额" type="number" :min="0" />
          </div>
        </div>
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
import { getUserInfo } from '@/api/auth'
import { createTask, getSettingConfig, getUniqueID } from '@/api/comm_tube'
import { bindStrategyKey } from '@/api/user'
import { useCommonStore } from '@/store/common.js'
import { QuestionFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, reactive, ref } from 'vue'
const taskList = computed(() => useCommonStore().taskList)
const emit = defineEmits(['getTaskList', 'callBack'])
const dialogVisible = ref(false)
const props = defineProps({
  isBacktest: {
    type: String,
    default: ''
  }
})
const isEdit = ref(false)
const form = reactive({
  name: '',
  platform: 1,
  strategy_code: '',
  order_count_type: 1,
  dynamic_calculation_type: 1,
  strategy_amount: 0,
  allocation_amount: 0,
  service_charge: 0,
  lower_limit_of_fees: 0,
  task_type: 1,
  share_secret: '',
  position_ratio: 1
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
    isEdit.value = true
    editDic.value = dic
    form.name = dic.name
    form.strategy_code = dic.strategy_code
    form.order_count_type = dic.order_count_type
    form.dynamic_calculation_type = dic.dynamic_calculation_type
    form.strategy_amount = dic.strategy_amount
    form.allocation_amount = dic.allocation_amount
    form.service_charge = dic.service_charge
    form.lower_limit_of_fees = dic.lower_limit_of_fees
    form.task_type = dic.task_type
    form.share_secret = dic.share_secret
    form.host_user_email = dic.host_user_email
    form.strategy_keys_id = dic.strategy_keys_id
    form.platform = dic.platform
    form.position_ratio = dic.position_ratio
  } else {
    editDic.value = null
    isEdit.value = false
    form.mock_allocation_amount = 100000
    form.mock_service_charge = 0.00025
    form.mock_lower_limit_of_fees = 5
    form.service_charge = 0.00025
    form.lower_limit_of_fees = 5
    form.allocation_amount = 100000
    form.position_ratio = 1
  }
}
const handleSubmit = async () => {
  if (isEdit.value == true) {
    if (editDic.value.strategy_code != form.strategy_code) {
      const confirm = await ElMessageBox.confirm('注意：修改了任务编号,会造成对远程策略的影响,请谨慎操作!', '确认', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'danger'
      }).catch(() => {
        ElMessage.info('取消修改')
      })
      if (!confirm) return
    }
  }
  let host_user_email = ''
  let strategy_keys_id = null
  let strategy_code = form.strategy_code
  if (form.task_type == 2) {
    const res = await bindStrategyKey({ secret_key: form.share_secret })
    if (res.code != 200) {
      ElMessage.error(res.message)
      return
    }
    host_user_email = res.data.host_user_email
    strategy_keys_id = res.data.id
    strategy_code = res.data.strategy_code
  }
  let user_id = undefined
  const config = await getSettingConfig()
  if(config.run_model_type === 2){
    const  userInfo = await getUserInfo()
    user_id = userInfo.id
  }else{
    user_id = await getUniqueID()
  }
  let dic = {
    id: editDic.value?.id || undefined,
    name: form.name,
    strategy_code: strategy_code,
    order_count_type: form.order_count_type,
    dynamic_calculation_type: form.dynamic_calculation_type,
    strategy_amount: form.strategy_amount,
    allocation_amount: form.allocation_amount,
    service_charge: form.service_charge,
    lower_limit_of_fees: form.lower_limit_of_fees,
    task_type: form.task_type,
    share_secret: form.share_secret,
    host_user_email: host_user_email,
    strategy_keys_id: strategy_keys_id,
    user_id: user_id,
    platform: form.platform,
    position_ratio: form.position_ratio
  }
  if (dic.id === undefined) {
    dic.mock_allocation_amount = 100000
    dic.mock_service_charge = 0.00025
    dic.mock_lower_limit_of_fees = 5
    dic.accruing_amounts = dic.allocation_amount
    dic.can_use_amount = dic.allocation_amount
    dic.position_ratio = 1
  }
  await createTask(dic)
  emit('getTaskList')
  emit('callBack')
  dialogVisible.value = false
  ElMessage.success('保存成功')
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
