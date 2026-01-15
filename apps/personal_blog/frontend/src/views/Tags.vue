<template>
  <div>
    <header class="text-center mb-12">
      <h1 class="text-4xl font-bold text-gray-900 dark:text-white mb-4">标签</h1>
      <p class="text-gray-600 dark:text-gray-300">浏览所有文章标签</p>
    </header>
    
    <div v-if="tags.loading" class="flex flex-wrap justify-center gap-3">
      <div v-for="i in 12" :key="i" class="animate-pulse">
        <div class="h-10 w-24 bg-gray-200 dark:bg-gray-700 rounded-full" />
      </div>
    </div>
    
    <div v-else-if="tags.data?.length" class="flex flex-wrap justify-center gap-3">
      <router-link 
        v-for="tag in tags.data" 
        :key="tag.name"
        :to="`/tag/${tag.slug}`"
        class="px-5 py-2.5 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-full hover:bg-primary-100 dark:hover:bg-primary-900/30 hover:text-primary-700 dark:hover:text-primary-400 transition-colors"
      >
        #{{ tag.tag_name }}
        <span v-if="tag.post_count" class="ml-1 text-gray-500 dark:text-gray-400 text-sm">
          ({{ tag.post_count }})
        </span>
      </router-link>
    </div>
    
    <div v-else class="text-center py-16">
      <p class="text-gray-500 dark:text-gray-400">暂无标签</p>
    </div>
  </div>
</template>

<script setup>
import { createResource } from 'frappe-ui'

const tags = createResource({
  url: 'personal_blog.api.tag.get_tags',
  auto: true,
})
</script>
