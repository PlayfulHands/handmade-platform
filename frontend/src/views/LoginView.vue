<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const login = async () => {
  loading.value = true
  error.value = ''
  
  const result = await authStore.login(username.value, password.value)
  
  if (result.success) {
    await authStore.fetchCurrentUser()
    
    if (authStore.masterId) {
      router.push('/master/dashboard')
    } else {
      router.push('/account')
    }
  } else {
    error.value = result.error
  }
  
  loading.value = false
}
</script>

<template>
  <div class="container">
    <div class="login-card">
      <h1>Вход</h1>
      
      <form @submit.prevent="login">
        <div class="form-group">
          <label for="username">Логин</label>
          <input 
            type="text" 
            id="username" 
            v-model="username"
            required
          >
        </div>
        
        <div class="form-group">
          <label for="password">Пароль</label>
          <input 
            type="password" 
            id="password" 
            v-model="password"
            required
          >
        </div>
        
        <div v-if="error" class="error">{{ error }}</div>
        
        <button type="submit" class="login-btn" :disabled="loading">
          {{ loading ? 'Вход...' : 'Войти' }}
        </button>
      </form>
      
      <p class="register-link">
        Нет аккаунта? 
        <router-link to="/register">Зарегистрироваться</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 400px;
  margin: 40px auto;
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 30px;
}

.login-card h1 {
  margin-bottom: 30px;
  text-align: center;
  color: #2C2C2C;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #E8DCC9;
  border-radius: 4px;
  font-size: 16px;
  background: #FFFBF7;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #C67B5C;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background: #C67B5C;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
}

.login-btn:hover:not(:disabled) {
  background: #B56A4D;
}

.login-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error {
  color: #ff4444;
  margin-bottom: 15px;
  text-align: center;
}

.register-link {
  margin-top: 20px;
  text-align: center;
  color: #666;
  font-size: 14px;
}

.register-link a {
  color: #C67B5C;
  text-decoration: none;
  transition: color 0.3s;
}

.register-link a:hover {
  color: #B56A4D;
  text-decoration: underline;
}
</style>