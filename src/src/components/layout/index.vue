<template>
    <el-container class="main-container">
      <LayoutSide>Aside</LayoutSide>
      <el-container class="container">
        <!-- <el-header style="position: fixed; width: 100%; z-index: 1000;">
          <LayoutHeader>Header</LayoutHeader>
        </el-header> -->
        <el-main class="main">
          <router-view></router-view>
        </el-main>
        <el-footer class="footer">
          <LayoutFooter/>
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
.main-container{
  box-sizing: border-box;
  height: 100vh;
  overflow-y: hidden;
  .container{
    position: relative;
    // background: red;
    // height: 100vh;
    // width: 100vw;
    background: #f2f2f2;

    .main{
      padding: 0px;
      background: #f2f2f2;
      overflow: hidden;
      position: absolute;
      bottom: 0px;
      left: 0px;
      right: 0px;
      top: 0px;
      height: calc(100vh - 40px);
    }
    .footer{
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