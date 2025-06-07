<template>
  <el-dialog v-model="dialogVisible" title="设置过期时间" width="40vw" center>
    <el-form :model="form" label-width="120px" style="margin-top:20px">
      <el-form-item label="过期时间" required>
        <el-date-picker v-model="form.expire_time" type="datetime" placeholder="选择日期时间" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button type="primary" @click="handleSubmit">保存</el-button>
      <el-button @click="dialogVisible = false">取消</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { bindStrategyKey } from '@/api/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
const emit = defineEmits(['callBack'])
const dialogVisible = ref(false)
const form = reactive({
  expire_time: ''
})

const handleSubmit = () => {
  const date = dayjs(form.expire_time)
  if (!date.isValid()) {
    emit('callBack', "-1")
    return
  }
  emit('callBack', date.format('YYYY-MM-DD HH:mm:ss'))
  dialogVisible.value = false
}

const showModal = (dic) => {
  dialogVisible.value = true
  form.expire_time = dic.expire_time
}

defineExpose({
  showModal 
})
</script>

<style scoped lang="less">

</style>
