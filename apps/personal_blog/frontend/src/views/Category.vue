<template>
  <div>
    <!-- Category Header -->
    <header class="text-center mb-12">
      <h1 class="text-4xl font-bold text-gray-900 dark:text-white mb-4">
        {{ category.data?.category_name || '分类' }}
      </h1>
      <p v-if="category.data?.description" class="text-gray-600 dark:text-gray-300">
        {{ category.data.description }}
      </p>
    </header>
    
    <!-- Loading State -->
    <div v-if="posts.loading" class="grid md:grid-cols-2 gap-8">
      <PostCardSkeleton v-for="i in 4" :key="i" />
    </div>
    
    <!-- Posts Grid -->
    <div v-else-if="posts.data?.posts?.length" class="grid md:grid-cols-2 gap-8">
      <PostCard 
        v-for="post in posts.data.posts" 
        :key="post.name"
        :post="post"
      />
    </div>
    
    <!-- Empty State -->
    <div v-else class="text-center py-16">
      <p class="text-gray-500 dark:text-gray-400">该分类下暂无文章</p>
    </div>
  </div>
</template>

<script setup>
import { createResource } from 'frappe-ui'
import { useRoute } from 'vue-router'
import PostCard from '../components/PostCard.vue'
import PostCardSkeleton from '../components/PostCardSkeleton.vue'

const route = useRoute()

const category = createResource({
  url: 'personal_blog.api.category.get_category',
  params: {
    slug: route.params.slug,
  },
  auto: true,
})

const posts = createResource({
  url: 'personal_blog.api.post.get_posts',
  params: {
    category_slug: route.params.slug,
  },
  auto: true,
})
</script>
