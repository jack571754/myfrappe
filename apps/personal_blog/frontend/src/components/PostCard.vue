<template>
  <article class="group bg-white dark:bg-gray-800 rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 border border-gray-100 dark:border-gray-700">
    <!-- Cover Image -->
    <router-link v-if="post.cover_image" :to="`/post/${post.slug}`" class="block aspect-video overflow-hidden">
      <img 
        :src="post.cover_image" 
        :alt="post.title"
        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
      />
    </router-link>
    
    <div class="p-6">
      <!-- Category & Date -->
      <div class="flex items-center gap-2 mb-3">
        <router-link 
          v-if="post.category_name"
          :to="`/category/${post.category_slug}`"
          class="px-2.5 py-1 text-xs font-medium text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/30 rounded-full hover:bg-primary-100 dark:hover:bg-primary-900/50 transition-colors"
        >
          {{ post.category_name }}
        </router-link>
        <span class="text-sm text-gray-400 dark:text-gray-500">
          {{ formatDate(post.published_at) }}
        </span>
      </div>
      
      <!-- Title -->
      <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
        <router-link :to="`/post/${post.slug}`">
          {{ post.title }}
        </router-link>
      </h2>
      
      <!-- Summary -->
      <p class="text-gray-600 dark:text-gray-300 line-clamp-2 mb-4">
        {{ post.summary }}
      </p>
      
      <!-- Tags -->
      <div v-if="post.tags?.length" class="flex flex-wrap gap-2">
        <router-link 
          v-for="tag in post.tags.slice(0, 3)" 
          :key="tag.tag"
          :to="`/tag/${tag.tag_slug}`"
          class="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
        >
          #{{ tag.tag_name }}
        </router-link>
        <span v-if="post.tags.length > 3" class="text-xs px-2 py-1 text-gray-500 dark:text-gray-400">
          +{{ post.tags.length - 3 }}
        </span>
      </div>
    </div>
  </article>
</template>

<script setup>
defineProps({
  post: {
    type: Object,
    required: true,
  },
})

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}
</script>
