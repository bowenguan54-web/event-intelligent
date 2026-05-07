// Performance API polyfill — 修复部分浏览器环境缺少 clearMarks/clearMeasures 导致的运行时错误
if (typeof window !== 'undefined' && window.performance) {
  if (typeof window.performance.clearMarks !== 'function') {
    window.performance.clearMarks = () => {}
  }
  if (typeof window.performance.clearMeasures !== 'function') {
    window.performance.clearMeasures = () => {}
  }
  if (typeof window.performance.mark !== 'function') {
    window.performance.mark = () => {}
  }
  if (typeof window.performance.measure !== 'function') {
    window.performance.measure = () => {}
  }
}

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import './styles/global.scss'

const app = createApp(App)

// 注册所有 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })

app.mount('#app')
