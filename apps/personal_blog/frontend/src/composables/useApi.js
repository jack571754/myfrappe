/**
 * API Client Composables for Personal Blog
 * 使用 frappe-ui 的 createResource 封装后端 API 调用
 */

import { createResource } from 'frappe-ui'
import { computed, ref } from 'vue'

/**
 * 获取文章列表
 * @param {Object} options - 查询参数
 * @param {number} options.page - 页码
 * @param {number} options.page_size - 每页数量
 * @param {string} options.category - 分类筛选
 * @param {string} options.tag - 标签筛选
 * @param {string} options.status - 状态筛选
 */
export function usePosts(options = {}) {
  const params = ref({
    page: options.page || 1,
    page_size: options.page_size || 10,
    category: options.category || null,
    tag: options.tag || null,
    status: options.status || 'Published'
  })

  const resource = createResource({
    url: 'personal_blog.api.post.get_posts',
    params: params.value,
    auto: options.auto !== false
  })

  const posts = computed(() => resource.data?.posts || [])
  const total = computed(() => resource.data?.total || 0)
  const totalPages = computed(() => Math.ceil(total.value / params.value.page_size))

  const setPage = (page) => {
    params.value.page = page
    resource.fetch({ ...params.value, page })
  }

  const setCategory = (category) => {
    params.value.category = category
    params.value.page = 1
    resource.fetch(params.value)
  }

  const setTag = (tag) => {
    params.value.tag = tag
    params.value.page = 1
    resource.fetch(params.value)
  }

  const refresh = () => {
    resource.fetch(params.value)
  }

  return {
    ...resource,
    posts,
    total,
    totalPages,
    params,
    setPage,
    setCategory,
    setTag,
    refresh
  }
}


/**
 * 获取单篇文章详情
 * @param {string} slug - 文章 slug
 * @param {Object} options - 配置选项
 */
export function usePost(slug, options = {}) {
  const resource = createResource({
    url: 'personal_blog.api.post.get_post',
    params: { slug },
    auto: options.auto !== false
  })

  const post = computed(() => resource.data || null)

  const fetchBySlug = (newSlug) => {
    resource.fetch({ slug: newSlug })
  }

  const fetchById = (name) => {
    resource.fetch({ name })
  }

  return {
    ...resource,
    post,
    fetchBySlug,
    fetchById
  }
}

/**
 * 获取分类列表
 * @param {Object} options - 配置选项
 */
export function useCategories(options = {}) {
  const resource = createResource({
    url: 'personal_blog.api.category.get_categories',
    auto: options.auto !== false
  })

  const categories = computed(() => resource.data?.categories || [])

  return {
    ...resource,
    categories
  }
}

/**
 * 获取单个分类详情
 * @param {string} slug - 分类 slug
 * @param {Object} options - 配置选项
 */
export function useCategory(slug, options = {}) {
  const resource = createResource({
    url: 'personal_blog.api.category.get_category',
    params: { slug },
    auto: options.auto !== false
  })

  const category = computed(() => resource.data || null)

  return {
    ...resource,
    category
  }
}

/**
 * 获取标签列表
 * @param {Object} options - 配置选项
 */
export function useTags(options = {}) {
  const resource = createResource({
    url: 'personal_blog.api.tag.get_tags',
    auto: options.auto !== false
  })

  const tags = computed(() => resource.data?.tags || [])

  return {
    ...resource,
    tags
  }
}

/**
 * 获取单个标签详情
 * @param {string} slug - 标签 slug
 * @param {Object} options - 配置选项
 */
export function useTag(slug, options = {}) {
  const resource = createResource({
    url: 'personal_blog.api.tag.get_tag',
    params: { slug },
    auto: options.auto !== false
  })

  const tag = computed(() => resource.data || null)

  return {
    ...resource,
    tag
  }
}


/**
 * 获取文章评论列表
 * @param {string} postName - 文章 ID
 * @param {Object} options - 配置选项
 */
export function useComments(postName, options = {}) {
  const params = ref({
    post: postName,
    page: options.page || 1,
    page_size: options.page_size || 20
  })

  const resource = createResource({
    url: 'personal_blog.api.comment.get_comments',
    params: params.value,
    auto: options.auto !== false
  })

  const comments = computed(() => resource.data?.comments || [])
  const total = computed(() => resource.data?.total || 0)

  const setPage = (page) => {
    params.value.page = page
    resource.fetch(params.value)
  }

  const refresh = () => {
    resource.fetch(params.value)
  }

  return {
    ...resource,
    comments,
    total,
    params,
    setPage,
    refresh
  }
}

/**
 * 提交评论
 * @returns {Object} - 包含 submit 方法的对象
 */
export function useSubmitComment() {
  const resource = createResource({
    url: 'personal_blog.api.comment.submit_comment',
    method: 'POST'
  })

  const submit = async (data) => {
    return resource.fetch({
      post: data.post,
      nickname: data.nickname,
      email: data.email,
      content: data.content
    })
  }

  return {
    ...resource,
    submit
  }
}
