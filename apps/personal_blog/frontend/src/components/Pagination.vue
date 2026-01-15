<template>
  <nav v-if="totalPages > 1" class="flex items-center justify-center gap-2" aria-label="分页导航">
    <!-- Previous Button -->
    <button
      @click="goToPage(currentPage - 1)"
      :disabled="currentPage <= 1"
      class="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      aria-label="上一页"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
    </button>
    
    <!-- Page Numbers -->
    <div class="flex items-center gap-1">
      <!-- First page -->
      <button
        v-if="showFirstPage"
        @click="goToPage(1)"
        class="px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
      >
        1
      </button>
      
      <!-- Left ellipsis -->
      <span v-if="showLeftEllipsis" class="px-2 text-gray-400">...</span>
      
      <!-- Visible pages -->
      <button
        v-for="page in visiblePages"
        :key="page"
        @click="goToPage(page)"
        :class="[
          'px-4 py-2 rounded-lg transition-colors',
          page === currentPage
            ? 'bg-primary-600 text-white'
            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
        ]"
        :aria-current="page === currentPage ? 'page' : undefined"
      >
        {{ page }}
      </button>
      
      <!-- Right ellipsis -->
      <span v-if="showRightEllipsis" class="px-2 text-gray-400">...</span>
      
      <!-- Last page -->
      <button
        v-if="showLastPage"
        @click="goToPage(totalPages)"
        class="px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
      >
        {{ totalPages }}
      </button>
    </div>
    
    <!-- Next Button -->
    <button
      @click="goToPage(currentPage + 1)"
      :disabled="currentPage >= totalPages"
      class="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      aria-label="下一页"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
      </svg>
    </button>
  </nav>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  total: {
    type: Number,
    required: true
  },
  page: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 10
  },
  maxVisible: {
    type: Number,
    default: 5
  }
})

const emit = defineEmits(['change'])

const currentPage = computed(() => props.page)
const totalPages = computed(() => Math.ceil(props.total / props.pageSize))

// Calculate visible page numbers
const visiblePages = computed(() => {
  const pages = []
  const half = Math.floor(props.maxVisible / 2)
  
  let start = Math.max(2, currentPage.value - half)
  let end = Math.min(totalPages.value - 1, currentPage.value + half)
  
  // Adjust if we're near the start
  if (currentPage.value <= half + 1) {
    end = Math.min(totalPages.value - 1, props.maxVisible)
  }
  
  // Adjust if we're near the end
  if (currentPage.value >= totalPages.value - half) {
    start = Math.max(2, totalPages.value - props.maxVisible + 1)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

const showFirstPage = computed(() => {
  return totalPages.value > 1 && !visiblePages.value.includes(1)
})

const showLastPage = computed(() => {
  return totalPages.value > 1 && !visiblePages.value.includes(totalPages.value)
})

const showLeftEllipsis = computed(() => {
  return visiblePages.value.length > 0 && visiblePages.value[0] > 2
})

const showRightEllipsis = computed(() => {
  return visiblePages.value.length > 0 && visiblePages.value[visiblePages.value.length - 1] < totalPages.value - 1
})

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value && page !== currentPage.value) {
    emit('change', page)
  }
}
</script>
