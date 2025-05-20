<template>
  <el-container class="main-container">
    <LayoutSide />
    <el-container class="container">
      <LayoutHeader class="header" />
      <el-main class="main">
        <router-view></router-view>
      </el-main>
      <el-footer class="footer">
        <LayoutFooter />
      </el-footer>
    </el-container>
  </el-container>
</template>

<script setup>
import LayoutSide from './Side.vue'
import LayoutHeader from './Header.vue'
import LayoutFooter from './Footer.vue'

defineOptions({
  name: 'Layout'
})
</script>

<style lang="less" scoped>
.main-container {
  box-sizing: border-box;
  height: 100vh;
  overflow-y: hidden;
  .container {
    position: relative;
    // background: red;
    // height: 100vh;
    // width: 100vw;
    background: #f2f2f2;
    .header {
      position: absolute;
      width: 100%;
      z-index: 1000;
      height: 50px;
    }
    .main {
      padding: 0px;
      background: #f2f2f2;
      overflow: hidden;
      position: absolute;
      bottom: 0px;
      left: 0px;
      right: 0px;
      top: 50px;
      height: calc(100vh - 90px);
    }
    .footer {
      position: absolute;
      bottom: 0px;
      left: 0px;
      right: 0px;
      height: 40px;
      background: #545c64;
    }
  }
}
</style>
