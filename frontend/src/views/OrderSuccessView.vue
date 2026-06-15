<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const orderId = route.params.id

const order = ref(null)
const loading = ref(true)
const error = ref(null)

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const fetchOrder = async () => {
  try {
    loading.value = true
    const response = await axios.get(`http://127.0.0.1:8000/api/orders/${orderId}/`)
    console.log('📦 Ответ от сервера:', response.data) // ← ДОБАВИТЬ
    order.value = response.data
  } catch (err) {
    console.error('Ошибка загрузки заказа:', err)
    error.value = 'Не удалось загрузить информацию о заказе'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchOrder()
})
</script>

<template>
  <div class="container">
    <div v-if="loading" class="loading-card">
      <div class="loader"></div>
      <p>Загружаем информацию о заказе...</p>
    </div>

    <div v-else-if="error" class="error-card">
      <div class="error-icon">⚠️</div>
      <p>{{ error }}</p>
      <router-link to="/" class="continue-btn">Вернуться на главную</router-link>
    </div>

    <div v-else-if="order" class="success-card">
      <div class="success-icon">✅</div>
      <h1>Спасибо за заказ!</h1>
      <p class="order-number">Номер вашего заказа: <strong>#{{ order.id }}</strong></p>
      <p class="order-date">Дата: {{ formatDate(order.created_at) }}</p>
      <p class="order-status">Статус: 
        <span :class="order.status" class="status-badge">
          {{ order.status === 'awaiting_payment' ? 'Ожидает оплаты' : order.status }}
        </span>
      </p>

      <!-- Состав заказа -->
      <div class="order-items">
        <h3>Состав заказа</h3>
        <div v-for="item in order.items" :key="item.id" class="order-item">
          <div class="item-image">
            <img v-if="item.product_image" :src="item.product_image" :alt="item.product_name">
            <div v-else class="no-image">📦</div>
          </div>
          <div class="item-details">
            <div class="item-name">{{ item.product_name }}</div>
            <div class="item-meta">
              {{ item.quantity }} шт × {{ item.price }} ₽
            </div>
            <div class="item-total">Итого: {{ item.total_price }} ₽</div>
          </div>
        </div>
      </div>

      <div class="order-total">
        Общая сумма заказа: <strong>{{ order.total_amount }} ₽</strong>
      </div>

      <p class="note">Мы отправили подтверждение на ваш email</p>
      <p class="note">В ближайшее время с вами свяжется мастер для уточнения деталей</p>

      <router-link to="/" class="continue-btn">
        Продолжить покупки
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
}

.success-card,
.loading-card,
.error-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  padding: 40px;
  text-align: center;
  border: 1px solid #E8DCC9;
}

.loading-card, .error-card {
  text-align: center;
}

.success-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

h1 {
  margin-bottom: 20px;
  color: #2C2C2C;
}

.order-number {
  font-size: 18px;
  margin-bottom: 10px;
}

.order-date, .order-status {
  margin-bottom: 8px;
  color: #666;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  background: #F5E9D7;
  color: #2C2C2C;
}

.status-badge.awaiting_payment {
  background: #FFF3CD;
  color: #856404;
}

/* Состав заказа */
.order-items {
  text-align: left;
  margin: 30px 0 20px;
  border-top: 1px solid #E8DCC9;
  padding-top: 20px;
}

.order-items h3 {
  margin-bottom: 16px;
  font-size: 18px;
  color: #2C2C2C;
}

.order-item {
  display: flex;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid #E8DCC9;
}

.item-image {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
  background: #FFFBF7;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  font-size: 32px;
}

.item-details {
  flex: 1;
}

.item-name {
  font-weight: bold;
  margin-bottom: 8px;
  color: #2C2C2C;
}

.item-meta {
  font-size: 14px;
  color: #666;
  margin-bottom: 4px;
}

.item-total {
  font-size: 15px;
  font-weight: 500;
  color: #C67B5C;
}

.order-total {
  text-align: right;
  font-size: 20px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 2px solid #E8DCC9;
}

.order-total strong {
  color: #2C2C2C;
  font-size: 24px;
}

.note {
  color: #999;
  font-size: 14px;
  margin-top: 16px;
}

.continue-btn {
  display: inline-block;
  margin-top: 30px;
  padding: 12px 30px;
  background: #C67B5C;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-size: 16px;
  transition: background 0.3s;
}

.continue-btn:hover {
  background: #B56A4D;
}

.loader {
  border: 3px solid #F5E9D7;
  border-top: 3px solid #C67B5C;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>