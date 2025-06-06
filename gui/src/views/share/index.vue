<template>
  <div class="share-container">
    
    <el-button @click="createStrategy">创建</el-button>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { getStrategyKeyByStrategyCode,createStrategyKey } from '@/api/user'
import { useRoute } from 'vue-router'

const route = useRoute()
// 获取策略
const getStrategyKey= async()=>{
  const strategy_code = route.query.strategy_code
  const res = await getStrategyKeyByStrategyCode(strategy_code)
  console.log(res)
}
const createStrategy = async () => {
  const strategy_code = route.query.strategy_code
  const res = await createStrategyKey({strategy_code})
  console.log(res)
}
onMounted(()=>{
  getStrategyKey()
})

</script>

<style scoped lang="less">
.share-container{

}
</style>
