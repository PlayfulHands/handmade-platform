import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useWishlistStore = defineStore('wishlist', () => {
  const items = ref([])
  const loading = ref(false)

  const count = computed(() => items.value.length)

  const loadWishlist = async () => {
    loading.value = true
    try {
      const response = await axios.get('http://127.0.0.1:8000/api/wishlist/list/')
      items.value = response.data
      console.log('Wishlist loaded:', items.value.length)
    } catch (error) {
      console.error('Ошибка загрузки избранного:', error)
    } finally {
      loading.value = false
    }
  }

  const toggle = async (productId) => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/wishlist/toggle/', {
        product_id: productId
      })
      
      if (response.data.wishlisted) {
        const productRes = await axios.get(`http://127.0.0.1:8000/api/products/${productId}/`)
        items.value.push({ product: productRes.data })
      } else {
        items.value = items.value.filter(item => item.product.id !== productId)
      }
      
      return response.data
    } catch (error) {
      console.error('Ошибка при добавлении в избранное:', error)
      throw error
    }
  }

  const isWishlisted = (productId) => {
    return items.value.some(item => item.product.id === productId)
  }

  return { items, count, loading, loadWishlist, toggle, isWishlisted }
})