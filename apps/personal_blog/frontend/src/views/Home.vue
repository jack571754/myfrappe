<template>
  <div>
    <!-- Hero Section -->
    <section class="text-center mb-16">
      <h1 class="text-5xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
        Welcome to My Blog
      </h1>
      <p class="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
        分享技术见解、开发经验和生活感悟
      </p>
    </section>
    
    <!-- Filter Bar -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
      <div class="flex flex-wrap gap-2">
        <button 
          @click="selectedCategory = ''"
          :class="[
            'px-4 py-2 rounded-full text-sm font-medium transition-colors',
            !selectedCategory 
              ? 'bg-primary-600 text-white' 
              : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
          ]"
        >
          全部
        </button>
        <button 
          v-for="cat in categories.data || []" 
          :key="cat.name"
          @click="selectedCategory = cat.name"
          :class="[
            'px-4 py-2 rounded-full text-sm font-medium transition-colors',
            selectedCategory === cat.name 
              ? 'bg-primary-600 text-white' 
              : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
          ]"
        >
          {{ cat.category_name }}
        </button>
      </div>
    </div>
    
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
      <p class="text-gray-500 dark:text-gray-400">暂无文章</p>
    </div>
    
    <!-- Pagination -->
    <div v-if="posts.data?.total > pageSize" class="mt-12">
      <Pagination 
        :total="posts.data.total"
        :page="currentPage"
        :page-size="pageSize"
        @change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { createResource } from 'frappe-ui'
import PostCard from '../components/PostCard.vue'
import PostCardSkeleton from '../components/PostCardSkeleton.vue'
import Pagination from '../components/Pagination.vue'

const currentPage = ref(1)
const pageSize = ref(10)
const selectedCategory = ref('')

const handlePageChange = (page) => {
  currentPage.value = page
}

const posts = createResource({
  url: 'personal_blog.api.post.get_posts',
  params: {
    page: currentPage.value,
    page_size: pageSize.value,
    category: selectedCategory.value || undefined,
  },
  auto: true,
})

const categories = createResource({
  url: 'personal_blog.api.category.get_categories',
  auto: true,
})

watch([currentPage, selectedCategory], () => {
  posts.update({
    params: {
      page: currentPage.value,
      page_size: pageSize.value,
      category: selectedCategory.value || undefined,
    },
  })
  posts.reload()
})

watch(selectedCategory, () => {
  currentPage.value = 1
})
</script>
