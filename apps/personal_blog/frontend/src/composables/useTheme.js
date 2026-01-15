/**
 * Theme Composable for Personal Blog
 * 管理深色/亮色模式切换
 */

import { ref, watchEffect } from 'vue'

// 全局状态，确保在多个组件间共享
const isDark = ref(false)
let initialized = false

/**
 * 主题管理 composable
 * @returns {Object} - 包含 isDark 状态和 toggleTheme 方法
 */
export function useTheme() {
  const initTheme = () => {
    if (initialized) return
    
    // 检查本地存储或系统偏好
    isDark.value = localStorage.getItem('theme') === 'dark' ||
      (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)
    
    initialized = true
  }

  const toggleTheme = () => {
    isDark.value = !isDark.value
    localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
  }

  const setTheme = (dark) => {
    isDark.value = dark
    localStorage.setItem('theme', dark ? 'dark' : 'light')
  }

  // 监听变化并更新 DOM
  watchEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.classList.toggle('dark', isDark.value)
    }
  })

  // 初始化主题
  if (typeof window !== 'undefined') {
    initTheme()
  }

  return {
    isDark,
    toggleTheme,
    setTheme
  }
}
