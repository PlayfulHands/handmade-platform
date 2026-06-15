<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useFollowStore } from '@/stores/follow'
import { useWishlistStore } from '@/stores/wishlist'
import axios from 'axios'

const authStore = useAuthStore()
const followStore = useFollowStore()
const wishlistStore = useWishlistStore()
const orders = ref([])
const loadingOrders = ref(true)

const activeTab = ref('orders')

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusText = (status) => {
  const statusMap = {
    'new': '🆕 Новый',
    'processing': '⚙️ В обработке',
    'completed': '✅ Выполнен',
    'cancelled': '❌ Отменён'
  }
  return statusMap[status] || status
}

const loadOrders = async () => {
  loadingOrders.value = true
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/orders/')
    orders.value = response.data
  } catch (error) {
    console.error('Ошибка загрузки заказов:', error)
  } finally {
    loadingOrders.value = false
  }
}

onMounted(() => {
  loadOrders()
  followStore.loadFollowing()
  wishlistStore.loadWishlist()
})
</script>

<template>
  <div class="container">
    <h1>Личный кабинет</h1>
    
    <div class="tabs">
      <button :class="{ active: activeTab === 'orders' }" @click="activeTab = 'orders'">
        📦 Мои заказы
      </button>
      <button :class="{ active: activeTab === 'following' }" @click="activeTab = 'following'">
        👥 Подписки ({{ followStore.count }})
      </button>
      <button :class="{ active: activeTab === 'wishlist' }" @click="activeTab = 'wishlist'">
        ❤️ Избранное ({{ wishlistStore.count }})
      </button>
      <button :class="{ active: activeTab === 'settings' }" @click="activeTab = 'settings'">
        ⚙️ Настройки
      </button>
    </div>
    
    <!-- Мои заказы -->
    <div v-if="activeTab === 'orders'" class="tab-content">
      <h2>Мои заказы</h2>
      
      <div v-if="loadingOrders" class="loading">Загрузка заказов...</div>
      
      <div v-else-if="orders.length === 0" class="empty">
        <p>У вас пока нет заказов</p>
        <router-link to="/" class="continue-btn">Перейти к покупкам</router-link>
      </div>
      
      <div v-else class="orders-list">
        <div v-for="order in orders" :key="order.id" class="order-card">
          <div class="order-header">
            <span class="order-number">Заказ #{{ order.id }}</span>
            <span class="order-status" :class="'status-' + order.status">
              {{ getStatusText(order.status) }}
            </span>
            <span class="order-date">{{ formatDate(order.created_at) }}</span>
          </div>
          
          <div class="order-items">
            <div v-for="item in order.items" :key="item.id" class="order-item">
              <span>{{ item.product_name }}</span>
              <span>{{ item.quantity }} шт × {{ item.product_price }} ₽</span>
              <span class="item-total">{{ item.quantity * item.product_price }} ₽</span>
            </div>
          </div>
          
          <div class="order-total">
            <strong>Общая сумма: {{ order.total_price }} ₽</strong>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Подписки -->
    <div v-if="activeTab === 'following'" class="tab-content">
      <h2>Мои подписки</h2>
      
      <div v-if="followStore.loading" class="loading">Загрузка...</div>
      
      <div v-else-if="followStore.following.length === 0" class="empty">
        <p>Вы пока ни на кого не подписаны</p>
        <router-link to="/feed" class="continue-btn">Посмотреть ленту</router-link>
      </div>
      
      <div v-else class="following-list">
        <div v-for="follow in followStore.following" :key="follow.id" class="following-item">
          <div class="master-avatar">
            <img v-if="follow.master.avatar" :src="follow.master.avatar" :alt="follow.master.shop_name">
            <div v-else class="avatar-placeholder">{{ follow.master.shop_name?.[0] }}</div>
          </div>
          <div class="master-info">
            <h3>{{ follow.master.shop_name }}</h3>
            <p>{{ follow.master.description?.slice(0, 60) }}...</p>
          </div>
          <button class="unfollow-btn" @click="followStore.toggle(follow.master.id)">
            Отписаться
          </button>
        </div>
      </div>
    </div>
    
    <!-- Избранное (краткая версия) -->
    <div v-if="activeTab === 'wishlist'" class="tab-content">
      <h2>Избранное</h2>
      
      <div v-if="wishlistStore.loading" class="loading">Загрузка...</div>
      
      <div v-else-if="wishlistStore.items.length === 0" class="empty">
        <p>У вас пока нет избранных товаров</p>
        <router-link to="/" class="continue-btn">Перейти к покупкам</router-link>
      </div>
      
      <div v-else class="wishlist-preview">
        <div v-for="item in wishlistStore.items.slice(0, 5)" :key="item.id" class="wishlist-preview-item">
          <span>{{ item.product.name }}</span>
          <span>{{ item.product.price }} ₽</span>
        </div>
        <router-link to="/wishlist" class="view-all">Посмотреть все →</router-link>
      </div>
    </div>
    
    <!-- Настройки профиля -->
    <div v-if="activeTab === 'settings'" class="tab-content">
      <h2>Настройки профиля</h2>
      
      <div v-if="authStore.user" class="settings-form">
        <div class="form-group">
          <label>Имя пользователя</label>
          <input type="text" v-model="authStore.user.username" disabled>
        </div>
        <div class="form-group">
          <label>Email</label>
          <input type="email" v-model="authStore.user.email" disabled>
        </div>
        <div class="form-group">
          <label>Имя</label>
          <input type="text" v-model="authStore.user.first_name">
        </div>
        <div class="form-group">
          <label>Фамилия</label>
          <input type="text" v-model="authStore.user.last_name">
        </div>
        <button class="save-btn" @click="alert('Функция в разработке')">Сохранить изменения</button>
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

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  border-bottom: 2px solid #E8DCC9; 
  padding-bottom: 10px;
  overflow-x: auto;
}

.tabs button {
  padding: 10px 20px;
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #666;
  white-space: nowrap;
}

.tabs button.active {
  color: #C67B5C; 
  font-weight: bold;
  border-bottom: 3px solid #C67B5C; 
}

.tab-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 30px;
}

.loading, .empty {
  text-align: center;
  padding: 60px;
  color: #666;
}

.continue-btn {
  display: inline-block;
  margin-top: 20px;
  padding: 10px 20px;
  background: #C67B5C; 
  color: white;
  text-decoration: none;
  border-radius: 6px;
  transition: background 0.3s;
}

.continue-btn:hover {
  background: #B56A4D; 
}

.orders-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.order-card {
  border: 1px solid #E8DCC9; 
  border-radius: 8px;
  padding: 20px;
  background: #FFFBF7; 
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #E8DCC9; 
}

.order-number {
  font-weight: bold;
  font-size: 18px;
  color: #333;
}

.order-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

/* Статусы оставляем как есть — они семантические */
.status-new { background: #e3f2fd; color: #1976d2; }
.status-processing { background: #fff3e0; color: #f57c00; }
.status-completed { background: #e8f5e8; color: #388e3c; }
.status-cancelled { background: #ffebee; color: #d32f2f; }

.order-date { 
  color: #666; 
  font-size: 14px; 
}

.order-item {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  border-bottom: 1px dotted #E8DCC9; 
  font-size: 14px;
}

.item-total {
  font-weight: bold;
  color: #C67B5C; 
}

.order-total {
  text-align: right;
  font-size: 16px;
  padding: 10px 0;
  border-top: 2px solid #E8DCC9; 
  margin-top: 10px;
}

.following-list {
  display: grid;
  gap: 15px;
}

.following-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border: 1px solid #E8DCC9; 
  border-radius: 8px;
}

.master-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  background: #C67B5C; 
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  font-weight: bold;
}

.master-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.master-info {
  flex: 1;
}

.master-info h3 {
  margin-bottom: 5px;
  color: #333;
}

.master-info p {
  color: #666;
  font-size: 14px;
}

.unfollow-btn {
  padding: 6px 12px;
  background: #fee;
  color: #ff4444;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.wishlist-preview {
  padding: 10px 0;
}

.wishlist-preview-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #E8DCC9; 
}

.view-all {
  display: inline-block;
  margin-top: 15px;
  color: #C67B5C; 
  text-decoration: none;
}

.view-all:hover {
  color: #B56A4D;
}

.settings-form {
  max-width: 500px;
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
}

.form-group input:focus {
  outline: none;
  border-color: #C67B5C;
}

.save-btn {
  padding: 12px 30px;
  background: #C67B5C; 
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}

.save-btn:hover {
  background: #B56A4D; 
}
</style>