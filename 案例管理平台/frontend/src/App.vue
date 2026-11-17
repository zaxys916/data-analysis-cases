<template>
  <el-container class="layout">
    <el-aside width="200px" class="aside">
      <div class="logo">
        <el-icon :size="22"><DataAnalysis /></el-icon>
        <span>案例管理平台</span>
      </div>
      <el-menu :default-active="activeMenu" router class="menu">
        <el-menu-item index="/">
          <el-icon><Odometer /></el-icon>
          <span>统计仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/cases">
          <el-icon><FolderOpened /></el-icon>
          <span>案例库</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span class="header-title">数据分析案例管理平台</span>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = computed(() => (route.path.startsWith('/cases') ? '/cases' : '/'))
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app { height: 100%; }
body { font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; }

.layout { height: 100%; }
.aside {
  background: #1d2530;
  display: flex;
  flex-direction: column;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 20px;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
}
.menu { border-right: none; background: transparent; }
.menu :deep(.el-menu-item) { color: #a6adb8; }
.menu :deep(.el-menu-item.is-active) { color: #409eff; background: rgba(64, 158, 255, 0.12); }
.menu :deep(.el-menu-item:hover) { background: rgba(255, 255, 255, 0.06); }

.header {
  height: 60px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  background: #fff;
}
.header-title { font-size: 16px; font-weight: 600; color: #303133; }
.main { background: #f5f7fa; padding: 20px; }
</style>
