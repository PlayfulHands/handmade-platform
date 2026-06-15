import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const masterId = ref(null)
  const master = ref(null)
  const accessToken = ref(localStorage.getItem('access_token'))
  const refreshToken = ref(localStorage.getItem('refresh_token'))
  const loading = ref(false)
  const initialized = ref(false)

  const isAuthenticated = computed(() => !!accessToken.value)

  // Устанавливаем токен в axios при инициализации
  if (accessToken.value) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`
  }

  const setTokens = (access, refresh) => {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    axios.defaults.headers.common['Authorization'] = `Bearer ${access}`
  }

  const clearTokens = () => {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    masterId.value = null
    master.value = null
    initialized.value = false
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    delete axios.defaults.headers.common['Authorization']
  }

  const register = async (userData) => {
    loading.value = true
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/auth/register/', userData)
      setTokens(response.data.access, response.data.refresh)
      user.value = response.data.user
      masterId.value = response.data.master_id
      initialized.value = true
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        errors: error.response?.data || { detail: 'Ошибка регистрации' }
      }
    } finally {
      loading.value = false
    }
  }

  const login = async (username, password) => {
    loading.value = true
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/auth/login/', {
        username,
        password
      })
      
      setTokens(response.data.access, response.data.refresh)
      user.value = response.data.user
      masterId.value = response.data.master_id
      initialized.value = true
      
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Ошибка входа'
      }
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    if (refreshToken.value) {
      try {
        await axios.post('http://127.0.0.1:8000/api/auth/logout/', {
          refresh: refreshToken.value
        })
      } catch (error) {
        console.error('Ошибка при выходе:', error)
      }
    }
    clearTokens()
    window.location.href = '/'
  }

  const fetchCurrentUser = async () => {
    if (initialized.value) return user.value
    
    if (!accessToken.value) {
      initialized.value = true
      return null
    }
    
    try {
      const response = await axios.get('http://127.0.0.1:8000/api/auth/me/')
      user.value = response.data.user
      masterId.value = response.data.master_id
      master.value = response.data.master
      initialized.value = true
      return response.data
    } catch (error) {
      if (error.response?.status === 401) {
        clearTokens()
      }
      initialized.value = true
      return null
    }
  }

  const refreshAccessToken = async () => {
    if (!refreshToken.value) return false
    
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/auth/token/refresh/', {
        refresh: refreshToken.value
      })
      
      accessToken.value = response.data.access
      localStorage.setItem('access_token', response.data.access)
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`
      return true
    } catch (error) {
      clearTokens()
      return false
    }
  }

  // Перехватчик для обработки ошибок 401
  axios.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config
      
      if (error.response?.status === 401 && 
          !originalRequest.url.includes('/auth/token/refresh/') && 
          !originalRequest._retry) {
        originalRequest._retry = true
        
        try {
          const refreshed = await refreshAccessToken()
          if (refreshed) {
            originalRequest.headers['Authorization'] = `Bearer ${accessToken.value}`
            return axios(originalRequest)
          }
        } catch (refreshError) {
          console.error('Ошибка обновления токена:', refreshError)
        }
      }
      
      if (error.response?.status === 401 && originalRequest._retry) {
        clearTokens()
        window.location.href = '/login'
      }
      
      return Promise.reject(error)
    }
  )

  return {
    user,
    masterId,
    master,
    loading,
    initialized,
    isAuthenticated,
    register,
    login,
    logout,
    fetchCurrentUser,
    refreshAccessToken
  }
})