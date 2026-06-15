<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: '',
  password2: '',
  email: '',
  first_name: '',
  last_name: '',
  shop_name: '',
  phone: ''
})

const errors = ref({})
const loading = ref(false)

const register = async () => {
  loading.value = true
  errors.value = {}
  
  const result = await authStore.register(form.value)
  
  if (result.success) {
    router.push('/master')
  } else {
    errors.value = result.errors
  }
  
  loading.value = false
}
</script>

<template>
  <div class="container">
    <div class="register-card">
      <h1>Регистрация мастера</h1>
      
      <form @submit.prevent="register">
        <div class="form-row">
          <div class="form-group">
            <label for="username">Логин *</label>
            <input 
              type="text" 
              id="username" 
              v-model="form.username"
              required
            >
            <span v-if="errors.username" class="error-text">{{ errors.username[0] }}</span>
          </div>
          
          <div class="form-group">
            <label for="email">Email *</label>
            <input 
              type="email" 
              id="email" 
              v-model="form.email"
              required
            >
            <span v-if="errors.email" class="error-text">{{ errors.email[0] }}</span>
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label for="first_name">Имя</label>
            <input 
              type="text" 
              id="first_name" 
              v-model="form.first_name"
            >
          </div>
          
          <div class="form-group">
            <label for="last_name">Фамилия</label>
            <input 
              type="text" 
              id="last_name" 
              v-model="form.last_name"
            >
          </div>
        </div>
        
        <div class="form-group">
          <label for="shop_name">Название магазина *</label>
          <input 
            type="text" 
            id="shop_name" 
            v-model="form.shop_name"
            required
          >
          <span v-if="errors.shop_name" class="error-text">{{ errors.shop_name[0] }}</span>
        </div>
        
        <div class="form-group">
          <label for="phone">Телефон *</label>
          <input 
            type="tel" 
            id="phone" 
            v-model="form.phone"
            required
            placeholder="+7 (999) 123-45-67"
          >
          <span v-if="errors.phone" class="error-text">{{ errors.phone[0] }}</span>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label for="password">Пароль *</label>
            <input 
              type="password" 
              id="password" 
              v-model="form.password"
              required
            >
            <span v-if="errors.password" class="error-text">{{ errors.password[0] }}</span>
          </div>
          
          <div class="form-group">
            <label for="password2">Подтверждение пароля *</label>
            <input 
              type="password" 
              id="password2" 
              v-model="form.password2"
              required
            >
          </div>
        </div>
        
        <div v-if="errors.non_field_errors" class="error">
          {{ errors.non_field_errors[0] }}
        </div>
        
        <button type="submit" class="register-btn" :disabled="loading">
          {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
        </button>
      </form>
      
      <p class="login-link">
        Уже есть аккаунт? 
        <router-link to="/login">Войти</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 600px;
  margin: 40px auto;
  padding: 20px;
}

.register-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 30px;
  border: 1px solid #E8DCC9;
}

.register-card h1 {
  margin-bottom: 30px;
  text-align: center;
  color: #2C2C2C;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
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

.register-btn {
  width: 100%;
  padding: 12px;
  background: #C67B5C;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
  margin-top: 10px;
}

.register-btn:hover:not(:disabled) {
  background: #B56A4D;
}

.register-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error {
  color: #ff4444;
  margin-bottom: 15px;
  text-align: center;
}

.error-text {
  color: #ff4444;
  font-size: 12px;
  margin-top: 3px;
  display: block;
}

.login-link {
  margin-top: 20px;
  text-align: center;
  color: #666;
  font-size: 14px;
}

.login-link a {
  color: #C67B5C;
  text-decoration: none;
  transition: color 0.3s;
}

.login-link a:hover {
  color: #B56A4D;
  text-decoration: underline;
}
</style>