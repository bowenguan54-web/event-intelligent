<template>
  <div class="side-menu">
    <!-- 导航菜单 -->
    <el-menu
      :default-active="activeMenu"
      background-color="transparent"
      text-color="#dee5f2"
      active-text-color="#dee5f2"
      router
      class="menu"
    >
      <el-menu-item index="/meeting/list">
        <el-icon><Calendar /></el-icon>
        <template #title>会议管理</template>
      </el-menu-item>

      <el-menu-item index="/archive">
        <el-icon><FolderOpened /></el-icon>
        <template #title>归档查询</template>
      </el-menu-item>

      <el-menu-item index="/meeting/archive">
        <el-icon><Finished /></el-icon>
        <template #title>会后事项管理</template>
      </el-menu-item>

      <el-menu-item index="/room/management">
        <el-icon><OfficeBuilding /></el-icon>
        <template #title>会议室管理</template>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style lang="scss" scoped>
.side-menu {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #0e1d38;
  padding-top: 12px;
}

/* ===== 菜单容器 ===== */
.menu {
  flex: 1;
  border-right: none !important;
  overflow-y: auto;
  background-color: transparent !important;
}

/* ===== 所有菜单项通用样式 ===== */
:deep(.el-menu-item) {
  height: 50px !important;
  line-height: 50px !important;
  padding-left: 26px !important;
  padding-right: 16px !important;
  font-size: 15px !important;
  font-weight: 540 !important;
  letter-spacing: 2px !important;
  color: #dee5f2 !important;
  background-color: transparent !important;
  transition: background-color 0.2s;

  .el-icon {
    width: 18px !important;
    height: 18px !important;
    font-size: 18px !important;
    color: #dee5f2 !important;
    margin-right: 10px;
  }
}

:deep(.el-menu-item:hover) {
  background-color: rgba(27, 48, 96, 0.45) !important;
  color: #dee5f2 !important;

  .el-icon { color: #dee5f2 !important; }
}

/* ===== 选中状态：margin 法实现 12px 内边矩形 ===== */
:deep(.el-menu-item.is-active) {
  /* 左右 12px margin 实现矩形距侧边栏两边 12px */
  margin: 5px 12px !important;
  /* 补偿左 margin 保持图标在 26px 处 */
  padding-left: 14px !important;
  padding-right: 4px !important;
  height: 40px !important;
  line-height: 40px !important;
  border-radius: 4px !important;
  background: #1b3060 !important;
  border: 1px solid #265ddf !important;
  color: #dee5f2 !important;
  font-size: 15px !important;
  font-weight: 540 !important;
  letter-spacing: 2px !important;

  .el-icon {
    color: #dee5f2 !important;
  }
}

/* ===== 二级菜单标题 ===== */
:deep(.el-sub-menu > .el-sub-menu__title) {
  height: 50px !important;
  line-height: 50px !important;
  padding-left: 26px !important;
  padding-right: 16px !important;
  font-size: 15px !important;
  font-weight: 540 !important;
  letter-spacing: 2px !important;
  color: #dee5f2 !important;
  background-color: transparent !important;

  .el-icon:not(.el-sub-menu__icon-arrow) {
    width: 18px !important;
    height: 18px !important;
    font-size: 18px !important;
    color: #dee5f2 !important;
    margin-right: 10px;
  }

  &:hover {
    background-color: rgba(27, 48, 96, 0.45) !important;
  }
}

/* 隐藏原生箭头，用 CSS 三角形替代（10x6 #8092c0） */
:deep(.el-sub-menu__icon-arrow) {
  display: none !important;
}

:deep(.el-sub-menu > .el-sub-menu__title::after) {
  content: '';
  position: absolute;
  right: 18px;
  top: 50%;
  transform: translateY(-50%);
  width: 0;
  height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 6px solid #8092c0;
  transition: transform 0.25s ease;
}

:deep(.el-sub-menu.is-opened > .el-sub-menu__title::after) {
  transform: translateY(-50%) rotate(180deg);
}

/* 二级子项 */
:deep(.el-menu--inline .el-menu-item) {
  padding-left: 52px !important;
}

/* 折叠直出弹出菜单 */
:deep(.el-menu--popup) {
  background-color: #0e1d38 !important;

  .el-menu-item {
    color: #dee5f2 !important;
    font-size: 14px !important;
  }
}

/* 分隔线 */
:deep(.el-divider) {
  border-color: rgba(38, 93, 223, 0.2) !important;
}
</style>
