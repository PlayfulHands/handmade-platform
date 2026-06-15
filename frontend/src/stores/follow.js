import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useFollowStore = defineStore('follow', () => {
  const following = ref([])
  const loading = ref(false)

  const count = computed(() => following.value.length)

  const loadFollowing = async () => {
    loading.value = true
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        console.warn('Нет токена для загрузки подписок')
        return
      }
      const response = await axios.get('http://127.0.0.1:8000/api/follows/following/', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      following.value = response.data
      console.log('Following loaded:', following.value.length)
    } catch (error) {
      console.error('Ошибка загрузки подписок:', error)
    } finally {
      loading.value = false
    }
  }

  const toggle = async (masterId) => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        console.warn('Нет токена для подписки')
        throw new Error('Не авторизован')
      }
      const response = await axios.post('http://127.0.0.1:8000/api/follows/toggle/', {
        master_id: masterId
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.data.followed) {
        const masterRes = await axios.get(`http://127.0.0.1:8000/api/masters/${masterId}/`)
        following.value.push({ master: masterRes.data })
      } else {
        following.value = following.value.filter(f => f.master.id !== masterId)
      }
      
      return response.data
    } catch (error) {
      console.error('Ошибка при подписке:', error)
      throw error
    }
  }

  const isFollowing = (masterId) => {
    return following.value.some(f => f.master.id === masterId)
  }

  return { following, count, loading, loadFollowing, toggle, isFollowing }
})