<template>
  <div>
    <header class="text-center mb-12">
      <h1 class="text-4xl font-bold text-gray-900 dark:text-white mb-4">分类</h1>
      <p class="text-gray-600 dark:text-gray-300">浏览所有文章分类</p>
    </header>
    
    <div v-if="categories.loading" class="grid md:grid-cols-3 gap-6">
      <div v-for="i in 6" :key="i" class="animate-pulse">
        <div class="h-32 bg-gray-200 dark:bg-gray-700 rounded-2xl" />
      </div>
    </div>
    
    <div v-else-if="categories.data?.length" class="grid md:grid-cols-3 gap-6">
      <router-link 
        v-for="cat in categories.data" 
        :key="cat.name"
        :to="`/category/${cat.slug}`"
        class="group p-6 bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 hover:shadow-lg hover:border-primary-200 dark:hover:border-primary-800 transition-all"
      >
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
          {{ cat.category_name }}
        </h2>
        <p v-if="cat.description" class="text-gray-600 dark:text-gray-300 text-sm line-clamp-2">
          {{ cat.description }}
        </p>
        <p class="mt-4 text-sm text-gray-500 dark:text-gray-400">
          {{ cat.post_count || 0 }} 篇文章
        </p>
      </router-link>
    </div>
    
    <div v-else class="text-center py-16">
      <p class="text-gray-500 dark:text-gray-400">暂无分类</p>
    </div>
  </div>
</template>

<script setup>
import { createResource } from 'frappe-ui'

const categories = createResource({
  url: 'personal_blog.api.category.get_categories',
  auto: true,
})
</script>
