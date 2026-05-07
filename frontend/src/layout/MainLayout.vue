<template>
  <!-- 外层纵向：header 全宽置顶 -->
  <el-container class="main-layout" direction="vertical">
    <!-- 全宽标题栏 -->
    <el-header class="header" height="64px">
      <AppHeader />
    </el-header>

    <!-- 主体横向：侧边栏 + 内容区 -->
    <el-container class="body-container">
      <el-aside width="180px" class="sidebar">
        <SideMenu />
      </el-aside>

      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <keep-alive :include="cachedViews">
            <component :is="Component" />
          </keep-alive>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import AppHeader from './AppHeader.vue'
import SideMenu from './SideMenu.vue'

// 需要缓存的页面组件名
const cachedViews = ['MeetingCreate', 'MeetingList']
</script>

<style lang="scss" scoped>
.main-layout {
  height: 100vh;
  overflow: hidden;
  flex-direction: column !important;
  background: url('../../image/background.png') center center / cover no-repeat #070e1a;
}

.header {
  height: 64px !important;
  min-height: 64px;
  padding: 0;
  display: flex;
  align-items: center;
  /* 背景图自然尺寸，左上对齐，显示顶部装饰条 */
  background: url('../../image/background.png') left top no-repeat #070e1a;
  border-bottom: none;
  box-shadow: none;
  z-index: 100;
  flex-shrink: 0;
}

.body-container {
  flex: 1;
  overflow: hidden;
  background: transparent !important;
  min-height: 0;
}

.sidebar {
  width: 180px !important;
  background-color: #0e1d38 !important;
  border-right: 1px solid rgba(38, 93, 223, 0.25);
  overflow: hidden;
  flex-shrink: 0;
  z-index: 10;
}

.main-content {
  /* 内容区第一层底色 */
  background: #0e1d38 !important;
  margin-left: 10px;
  padding: 0;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
  z-index: 1;
}
</style>
