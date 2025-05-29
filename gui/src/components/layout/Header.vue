<template>
  <el-header>
    <div class="header-left">
      <el-button
        v-if="showBack"
        type="text"
        @click="handleBack"
        class="back-button"
      >
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <span>{{ title }}</span>
    </div>
    <slot></slot>
  </el-header>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const title = ref('')
const showBack = ref(false)

// 监听路由变化，更新标题和返回按钮显示状态
watch(
  () => route.meta,
  (meta) => {
    title.value = meta.title || '默认标题'
    showBack.value = meta.showBack || false
  },
  { immediate: true }
)

const handleBack = () => {
  router.back()
}
</script>

<style scoped>
.el-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 4px;
  /* margin-top: 2px; */
  font-size: 16px;
}
</style> 