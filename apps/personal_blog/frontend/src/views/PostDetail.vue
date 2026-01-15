<template>
  <article v-if="post.data" class="max-w-3xl mx-auto">
    <!-- Article Header -->
    <header class="mb-12 text-center">
      <router-link 
        v-if="post.data.category"
        :to="`/category/${post.data.category_slug}`"
        class="inline-block px-3 py-1 mb-4 text-sm font-medium text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/30 rounded-full hover:bg-primary-100 dark:hover:bg-primary-900/50 transition-colors"
      >
        {{ post.data.category_name }}
      </router-link>
      
      <h1 class="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-6 leading-tight">
        {{ post.data.title }}
      </h1>
      
      <div class="flex items-center justify-center gap-4 text-gray-500 dark:text-gray-400">
        <span>{{ post.data.author_name || post.data.author }}</span>
        <span>·</span>
        <time>{{ formatDate(post.data.published_at) }}</time>
        <span v-if="post.data.reading_time">·</span>
        <span v-if="post.data.reading_time">{{ post.data.reading_time }} 分钟阅读</span>
      </div>
    </header>
    
    <!-- Cover Image -->
    <div v-if="post.data.cover_image" class="mb-12 rounded-2xl overflow-hidden">
      <img 
        :src="post.data.cover_image" 
        :alt="post.data.title" 
        class="w-full"
      />
    </div>
    
    <!-- Article Content -->
    <div 
      class="prose prose-lg dark:prose-dark prose-headings:font-bold prose-a:text-primary-600 dark:prose-a:text-primary-400 prose-img:rounded-xl max-w-none"
      v-html="post.data.content_html || renderMarkdown(post.data.content)"
    />
    
    <!-- Tags -->
    <div v-if="post.data.tags?.length" class="mt-12 pt-8 border-t border-gray-200 dark:border-gray-700">
      <div class="flex flex-wrap gap-2">
        <router-link 
          v-for="tag in post.data.tags" 
          :key="tag.tag"
          :to="`/tag/${tag.tag_slug}`"
          class="px-4 py-2 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-full hover:bg-primary-100 dark:hover:bg-primary-900/30 hover:text-primary-700 dark:hover:text-primary-400 transition-colors"
        >
          #{{ tag.tag_name }}
        </router-link>
      </div>
    </div>
    
    <!-- Comments Section -->
    <CommentSection :post="post.data.name" class="mt-16" />
  </article>
  
  <!-- Loading State -->
  <div v-else-if="post.loading" class="max-w-3xl mx-auto">
    <div class="animate-pulse">
      <div class="h-8 w-24 bg-gray-200 dark:bg-gray-700 rounded-full mx-auto mb-4" />
      <div class="h-12 w-3/4 bg-gray-200 dark:bg-gray-700 rounded mx-auto mb-6" />
      <div class="h-6 w-1/2 bg-gray-200 dark:bg-gray-700 rounded mx-auto mb-12" />
      <div class="aspect-video bg-gray-200 dark:bg-gray-700 rounded-2xl mb-12" />
      <div class="space-y-4">
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded" />
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6" />
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-4/6" />
      </div>
    </div>
  </div>
  
  <!-- Error State -->
  <div v-else class="text-center py-16">
    <p class="text-gray-500 dark:text-gray-400">文章不存在或已被删除</p>
    <router-link to="/" class="mt-4 inline-block text-primary-600 dark:text-primary-400 hover:underline">
      返回首页
    </router-link>
  </div>
</template>

<script setup>
import { createResource } from 'frappe-ui'
import { useRoute } from 'vue-router'
import { marked } from 'marked'
import CommentSection from '../components/CommentSection.vue'

const route = useRoute()

const post = createResource({
  url: 'personal_blog.api.post.get_post',
  params: {
    slug: route.params.slug,
  },
  auto: true,
})

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

const renderMarkdown = (content) => {
  if (!content) return ''
  return marked(content)
}
</script>
