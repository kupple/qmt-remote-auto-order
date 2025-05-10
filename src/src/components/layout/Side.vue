<template>
  <el-aside width="200px" class="side-container">
    <img src="@/assets/images/logo.png" style="width:80px;height:80px">
    <el-menu
      active-text-color="#ffd04b"
      background-color="#545c64"
      text-color="#fff"
      class="el-menu-vertical"
      router
      @select="handleSelect"
    >
      <el-menu-item v-for="route in menuRoutes" :key="route.name" :index="route.name">
        <el-icon>
          <component :is="ElementPlusIconsVue[route.icon]" />
        </el-icon>
        <span >{{ route.chName }}</span>
      </el-menu-item>
    </el-menu>
  </el-aside>
</template>

<script setup>
import { computed,ref } from 'vue'
import { useRoute } from 'vue-router'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { routes } from '@/router/index.js'
import { useRouter } from 'vue-router'; // 引入useRouter函数
const router = useRouter(); // 使用useRouter函数创建router实例

const route = useRoute()
const activeMenu = ref('Home')
const menuRoutes = computed(() => {
  return routes.filter(route => route.name)
})
const handleSelect = (key) => {
  router.push({ name: key })
  activeMenu.value = key
}
</script>

<style scoped lang='less'>
.el-menu-vertical {
  border-right: none;
  // background: rgb(39, 39, 39);
  width: 100%;
  margin-top: 14px;
}
.side-container{
  background: #545c64;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 30px;
  // justify-content: center;
  // justify-content: center;
}
</style> 