/**
 * Error Handler Composable for Personal Blog
 * 统一处理 API 错误和用户提示
 */

import { toast } from 'frappe-ui'

/**
 * 错误处理 composable
 * @returns {Object} - 包含错误处理方法
 */
export function useErrorHandler() {
  /**
   * 处理 API 错误
   * @param {Error|Object} error - 错误对象
   * @param {string} fallbackMessage - 默认错误消息
   */
  const handleError = (error, fallbackMessage = '操作失败') => {
    let message = fallbackMessage
    
    if (error) {
      // Frappe API 错误格式
      if (error.messages && error.messages.length > 0) {
        message = error.messages[0]
      } else if (error.message) {
        message = error.message
      } else if (typeof error === 'string') {
        message = error
      }
    }

    toast({
      title: '错误',
      text: message,
      icon: 'alert-circle',
      iconClasses: 'text-red-500',
      position: 'top-right'
    })

    console.error('Error:', error)
  }

  /**
   * 显示成功提示
   * @param {string} message - 成功消息
   */
  const showSuccess = (message) => {
    toast({
      title: '成功',
      text: message,
      icon: 'check-circle',
      iconClasses: 'text-green-500',
      position: 'top-right'
    })
  }

  /**
   * 显示警告提示
   * @param {string} message - 警告消息
   */
  const showWarning = (message) => {
    toast({
      title: '警告',
      text: message,
      icon: 'alert-triangle',
      iconClasses: 'text-yellow-500',
      position: 'top-right'
    })
  }

  /**
   * 显示信息提示
   * @param {string} message - 信息消息
   */
  const showInfo = (message) => {
    toast({
      title: '提示',
      text: message,
      icon: 'info',
      iconClasses: 'text-blue-500',
      position: 'top-right'
    })
  }

  return {
    handleError,
    showSuccess,
    showWarning,
    showInfo
  }
}
