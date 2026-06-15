<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import axios from 'axios'

const router = useRouter()
const cartStore = useCartStore()

const form = ref({
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  address: '',
  comment: ''
})

const loading = ref(false)
const errors = ref({})

const totalPrice = computed(() => {
  return cartStore.totalPrice
})

const validateForm = () => {
  const newErrors = {}
  
  if (!form.value.firstName) newErrors.firstName = 'Введите имя'
  if (!form.value.lastName) newErrors.lastName = 'Введите фамилию'
  if (!form.value.email) {
    newErrors.email = 'Введите email'
  } else if (!/\S+@\S+\.\S+/.test(form.value.email)) {
    newErrors.email = 'Некорректный email'
  }
  if (!form.value.phone) newErrors.phone = 'Введите телефон'
  if (!form.value.address) newErrors.address = 'Введите адрес доставки'
  
  errors.value = newErrors
  return Object.keys(newErrors).length === 0
}

const submitOrder = async () => {
  if (!validateForm()) return
  
  if (cartStore.items.length === 0) {
    alert('Корзина пуста')
    return
  }
  
  loading.value = true
  
  try {
    const orderData = {
      first_name: form.value.firstName,
      last_name: form.value.lastName,
      email: form.value.email,
      phone: form.value.phone,
      address: form.value.address,
      comment: form.value.comment,
      items: cartStore.items.map(item => ({
        product_id: item.id,
        product_name: item.name,
        product_price: item.price,
        quantity: item.quantity
      }))
    }
    
    const response = await axios.post('http://127.0.0.1:8000/api/orders/', orderData)
    
    if (response.data.success) {
      cartStore.clearCart()
      router.push(`/order-success/${response.data.order_id}`)
    }
  } catch (error) {
    console.error('Ошибка при создании заказа:', error)
    alert('Произошла ошибка. Попробуйте позже.')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="container">
    <h1>Оформление заказа</h1>
    
    <div v-if="cartStore.items.length === 0" class="empty-cart">
      <p>Корзина пуста</p>
      <router-link to="/" class="continue-shopping">Вернуться к покупкам</router-link>
    </div>
    
    <div v-else class="checkout-content">
      <div class="order-form">
        <h2>Контактные данные</h2>
        
        <div class="form-group">
          <label for="firstName">Имя *</label>
          <input 
            type="text" 
            id="firstName" 
            v-model="form.firstName"
            :class="{ error: errors.firstName }"
          >
          <span v-if="errors.firstName" class="error-text">{{ errors.firstName }}</span>
        </div>
        
        <div class="form-group">
          <label for="lastName">Фамилия *</label>
          <input 
            type="text" 
            id="lastName" 
            v-model="form.lastName"
            :class="{ error: errors.lastName }"
          >
          <span v-if="errors.lastName" class="error-text">{{ errors.lastName }}</span>
        </div>
        
        <div class="form-group">
          <label for="email">Email *</label>
          <input 
            type="email" 
            id="email" 
            v-model="form.email"
            :class="{ error: errors.email }"
          >
          <span v-if="errors.email" class="error-text">{{ errors.email }}</span>
        </div>
        
        <div class="form-group">
          <label for="phone">Телефон *</label>
          <input 
            type="tel" 
            id="phone" 
            v-model="form.phone"
            placeholder="+7 (999) 123-45-67"
            :class="{ error: errors.phone }"
          >
          <span v-if="errors.phone" class="error-text">{{ errors.phone }}</span>
        </div>
        
        <div class="form-group">
          <label for="address">Адрес доставки *</label>
          <textarea 
            id="address" 
            v-model="form.address"
            rows="3"
            :class="{ error: errors.address }"
          ></textarea>
          <span v-if="errors.address" class="error-text">{{ errors.address }}</span>
        </div>
        
        <div class="form-group">
          <label for="comment">Комментарий к заказу</label>
          <textarea 
            id="comment" 
            v-model="form.comment"
            rows="3"
          ></textarea>
        </div>
      </div>
      
      <div class="order-summary">
        <h2>Ваш заказ</h2>
        
        <div class="order-items">
          <div v-for="item in cartStore.items" :key="item.id" class="order-item">
            <span class="item-name">{{ item.name }} x {{ item.quantity }}</span>
            <span class="item-price">{{ item.price * item.quantity }} ₽</span>
          </div>
        </div>
        
        <div class="total">
          <span>Итого:</span>
          <span class="total-price">{{ totalPrice }} ₽</span>
        </div>
        
        <button 
          class="submit-btn" 
          @click="submitOrder"
          :disabled="loading"
        >
          {{ loading ? 'Оформление...' : 'Подтвердить заказ' }}
        </button>
        
        <router-link to="/cart" class="back-link">← Вернуться в корзину</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.empty-cart {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.continue-shopping {
  display: inline-block;
  margin-top: 20px;
  padding: 10px 20px;
  background: #C67B5C; 
  color: white;
  text-decoration: none;
  border-radius: 6px;
  transition: background 0.3s;
}

.continue-shopping:hover {
  background: #B56A4D; 
}

.checkout-content {
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 30px;
  margin-top: 30px;
}

.order-form {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 30px;
}

.order-form h2 {
  margin-bottom: 20px;
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

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #E8DCC9; 
  border-radius: 4px;
  font-size: 16px;
  font-family: inherit;
  background: #FFFBF7; 
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #C67B5C; 
}

.form-group input.error,
.form-group textarea.error {
  border-color: #ff4444; 
}

.error-text {
  color: #ff4444;
  font-size: 14px;
  margin-top: 5px;
  display: block;
}

.order-summary {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 30px;
  height: fit-content;
}

.order-summary h2 {
  margin-bottom: 20px;
}

.order-items {
  margin-bottom: 20px;
}

.order-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #E8DCC9; 
}

.item-name {
  color: #333;
}

.item-price {
  font-weight: 500;
  color: #2C2C2C; 
}

.total {
  display: flex;
  justify-content: space-between;
  padding: 20px 0;
  font-size: 18px;
  font-weight: bold;
  border-top: 2px solid #E8DCC9; 
}

.total-price {
  color: #C67B5C; 
}

.submit-btn {
  width: 100%;
  padding: 15px;
  background: #C67B5C; 
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s;
  margin-bottom: 15px;
}

.submit-btn:hover:not(:disabled) {
  background: #B56A4D; 
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.back-link {
  display: block;
  text-align: center;
  color: #666;
  text-decoration: none;
  font-size: 14px;
}

.back-link:hover {
  color: #C67B5C; 
}
</style>