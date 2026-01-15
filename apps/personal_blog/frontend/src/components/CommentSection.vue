<template>
  <section class="border-t border-gray-200 dark:border-gray-700 pt-12">
    <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-8">评论</h2>
    
    <!-- Comment Form -->
    <form @submit.prevent="submitComment" class="mb-12 p-6 bg-gray-50 dark:bg-gray-800/50 rounded-2xl">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">发表评论</h3>
      
      <div class="grid md:grid-cols-2 gap-4 mb-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            昵称 <span class="text-red-500">*</span>
          </label>
          <input 
            v-model="form.nickname"
            type="text"
            required
            class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
            placeholder="你的昵称"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            邮箱 <span class="text-red-500">*</span>
          </label>
          <input 
            v-model="form.email"
            type="email"
            required
            class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
            placeholder="your@email.com"
          />
        </div>
      </div>
      
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          评论内容 <span class="text-red-500">*</span>
        </label>
        <textarea 
          v-model="form.content"
          required
          rows="4"
          class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors resize-none"
          placeholder="写下你的评论..."
        />
      </div>
      
      <div class="flex items-center justify-between">
        <p class="text-sm text-gray-500 dark:text-gray-400">
          评论需要审核后才会显示
        </p>
        <button 
          type="submit"
          :disabled="submitResource.loading"
          class="px-6 py-2 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ submitResource.loading ? '提交中...' : '提交评论' }}
        </button>
      </div>
      
      <!-- Success Message -->
      <div v-if="submitSuccess" class="mt-4 p-4 bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-lg">
        评论提交成功，审核通过后将会显示。
      </div>
      
      <!-- Error Message -->
      <div v-if="submitError" class="mt-4 p-4 bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-lg">
        {{ submitError }}
      </div>
    </form>
    
    <!-- Comments List -->
    <div v-if="comments.loading" class="space-y-6">
      <div v-for="i in 3" :key="i" class="animate-pulse">
        <div class="flex gap-4">
          <div class="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-full" />
          <div class="flex-1 space-y-2">
            <div class="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded" />
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded" />
            <div class="h-4 w-3/4 bg-gray-200 dark:bg-gray-700 rounded" />
          </div>
        </div>
      </div>
    </div>
    
    <div v-else-if="comments.data?.comments?.length" class="space-y-6">
      <div 
        v-for="comment in comments.data.comments" 
        :key="comment.name"
        class="flex gap-4"
      >
        <div class="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 rounded-full flex items-center justify-center font-semibold">
          {{ comment.nickname.charAt(0).toUpperCase() }}
        </div>
        <div class="flex-1">
          <div class="flex items-center gap-2 mb-1">
            <span class="font-medium text-gray-900 dark:text-white">{{ comment.nickname }}</span>
            <span class="text-sm text-gray-500 dark:text-gray-400">{{ formatDate(comment.created_at) }}</span>
          </div>
          <p class="text-gray-700 dark:text-gray-300">{{ comment.content }}</p>
        </div>
      </div>
    </div>
    
    <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400">
      暂无评论，来发表第一条评论吧！
    </div>
  </section>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { createResource } from 'frappe-ui'

const props = defineProps({
  post: {
    type: String,
    required: true,
  },
})

const form = reactive({
  nickname: '',
  email: '',
  content: '',
})

const submitSuccess = ref(false)
const submitError = ref('')

const comments = createResource({
  url: 'personal_blog.api.comment.get_comments',
  params: {
    post: props.post,
  },
  auto: true,
})

const submitResource = createResource({
  url: 'personal_blog.api.comment.submit_comment',
  onSuccess() {
    submitSuccess.value = true
    submitError.value = ''
    form.nickname = ''
    form.email = ''
    form.content = ''
    setTimeout(() => {
      submitSuccess.value = false
    }, 5000)
  },
  onError(error) {
    submitError.value = error.messages?.[0] || '提交失败，请稍后重试'
    submitSuccess.value = false
  },
})

const submitComment = () => {
  submitError.value = ''
  submitResource.submit({
    post: props.post,
    nickname: form.nickname,
    email: form.email,
    content: form.content,
  })
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>
