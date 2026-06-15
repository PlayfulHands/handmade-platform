<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'

const authStore = useAuthStore()
const chatStore = useChatStore()
const router = useRouter()

const activeTab = ref('products')
const products = ref([])
const profile = ref(null)
const loading = ref(true)
const orders = ref([])
const loadingOrders = ref(false)
const myPosts = ref([])

// Форма для нового товара
const newProduct = ref({
  name: '',
  description: '',
  price: '',
  category_id: '',
  image: null
})

// Форма для нового поста
const newPost = ref({
  title: '',
  content: '',
  image: null,
  video_url: '',
  product_id: null
})

const categories = ref([])

// Редактирование товара
const editingProduct = ref(null)
const showEditModal = ref(false)
const editForm = ref({
  name: '',
  description: '',
  price: '',
  category_id: '',
  image: null
})

// Статистика
const showStats = ref(false)
const stats = ref({
  total_orders: 0,
  total_revenue: 0,
  avg_order_value: 0,
  top_products: [],
  monthly_data: []
})

// Чаты
const newMessageText = ref('')

onMounted(async () => {
  await loadData()
  await loadMyPosts()
  await chatStore.loadRooms()
})

const loadData = async () => {
  loading.value = true
  try {
    const categoriesRes = await axios.get('http://127.0.0.1:8000/api/categories/')
    categories.value = categoriesRes.data
    
    const masterId = authStore.masterId || 1
    const productsRes = await axios.get(`http://127.0.0.1:8000/api/products/?master=${masterId}`)
    products.value = productsRes.data
    
    try {
      const profileRes = await axios.get('http://127.0.0.1:8000/api/masters/profile/')
      profile.value = profileRes.data
    } catch (profileError) {
      console.warn('Профиль мастера не найден')
      profile.value = null
    }
  } catch (error) {
    console.error('Ошибка загрузки:', error)
  } finally {
    loading.value = false
  }
}

const loadMyPosts = async () => {
  try {
    const masterId = authStore.masterId || 1
    const response = await axios.get(`http://127.0.0.1:8000/api/posts/master/${masterId}/`)
    myPosts.value = response.data
  } catch (error) {
    console.error('Ошибка загрузки постов:', error)
  }
}

// ===== ТОВАРЫ =====
const addProduct = async () => {
  if (!newProduct.value.name) {
    alert('Введите название товара')
    return
  }
  if (!newProduct.value.price) {
    alert('Введите цену товара')
    return
  }
  if (!newProduct.value.category_id) {
    alert('Выберите категорию')
    return
  }
  
  try {
    const formData = new FormData()
    formData.append('name', newProduct.value.name)
    formData.append('description', newProduct.value.description || '')
    formData.append('price', newProduct.value.price)
    formData.append('category_id', newProduct.value.category_id)
    formData.append('master_id', authStore.masterId || 1)
    
    if (newProduct.value.image) {
      formData.append('image', newProduct.value.image)
    }
    
    const response = await axios.post('http://127.0.0.1:8000/api/products/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    products.value.unshift(response.data)
    newProduct.value = { name: '', description: '', price: '', category_id: '', image: null }
    activeTab.value = 'products'
    alert('Товар успешно добавлен')
  } catch (error) {
    console.error('Ошибка добавления:', error.response?.data || error)
    alert(`Ошибка при добавлении товара: ${JSON.stringify(error.response?.data)}`)
  }
}

const deleteProduct = async (id) => {
  if (!confirm('Удалить товар?')) return
  try {
    await axios.delete(`http://127.0.0.1:8000/api/products/${id}/`)
    products.value = products.value.filter(p => p.id !== id)
    alert('Товар удалён')
  } catch (error) {
    console.error('Ошибка удаления:', error)
    alert('Ошибка при удалении товара')
  }
}

const openEditModal = (product) => {
  editingProduct.value = product
  editForm.value = {
    name: product.name,
    description: product.description,
    price: product.price,
    category_id: product.category?.id,
    image: null
  }
  showEditModal.value = true
}

const updateProduct = async () => {
  try {
    const formData = new FormData()
    formData.append('name', editForm.value.name)
    formData.append('description', editForm.value.description)
    formData.append('price', editForm.value.price)
    formData.append('category_id', editForm.value.category_id)
    if (editForm.value.image) {
      formData.append('image', editForm.value.image)
    }
    
    const response = await axios.put(
      `http://127.0.0.1:8000/api/products/${editingProduct.value.id}/`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
    
    const index = products.value.findIndex(p => p.id === editingProduct.value.id)
    if (index !== -1) products.value[index] = response.data
    
    showEditModal.value = false
    editingProduct.value = null
    alert('Товар обновлён')
  } catch (error) {
    console.error('Ошибка обновления:', error)
    alert('Ошибка при обновлении товара')
  }
}

const handleImageUpload = (event) => {
  newProduct.value.image = event.target.files[0]
}

const handleEditImageUpload = (event) => {
  editForm.value.image = event.target.files[0]
}

// ===== ПУБЛИКАЦИИ =====
const handlePostImageUpload = (event) => {
  newPost.value.image = event.target.files[0]
}

const createPost = async () => {
  if (!newPost.value.title) {
    alert('Введите заголовок')
    return
  }
  
  try {
    const formData = new FormData()
    formData.append('title', newPost.value.title)
    formData.append('content', newPost.value.content || '')
    formData.append('master', authStore.masterId || 1)
    if (newPost.value.image) formData.append('image', newPost.value.image)
    if (newPost.value.video_url) formData.append('video_url', newPost.value.video_url)
    if (newPost.value.product_id) formData.append('product', newPost.value.product_id)
    
    const response = await axios.post('http://127.0.0.1:8000/api/posts/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    myPosts.value.unshift(response.data)
    newPost.value = { title: '', content: '', image: null, video_url: '', product_id: null }
    alert('Публикация создана!')
  } catch (error) {
    console.error('Ошибка создания поста:', error)
    alert('Ошибка при создании публикации')
  }
}

const deletePost = async (id) => {
  if (!confirm('Удалить публикацию?')) return
  try {
    await axios.delete(`http://127.0.0.1:8000/api/posts/${id}/`)
    myPosts.value = myPosts.value.filter(p => p.id !== id)
    alert('Публикация удалена')
  } catch (error) {
    console.error('Ошибка удаления:', error)
    alert('Ошибка при удалении публикации')
  }
}

// ===== ЗАКАЗЫ =====
const loadMasterOrders = async () => {
  loadingOrders.value = true
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/orders/')
    const masterProductIds = products.value.map(p => p.id)
    orders.value = response.data.filter(order => 
      order.items?.some(item => masterProductIds.includes(item.product_id))
    )
  } catch (error) {
    console.error('Ошибка загрузки заказов:', error)
  } finally {
    loadingOrders.value = false
  }
}

const updateOrderStatus = async (orderId, newStatus) => {
  try {
    await axios.patch(`http://127.0.0.1:8000/api/orders/${orderId}/`, { status: newStatus })
    const order = orders.value.find(o => o.id === orderId)
    if (order) order.status = newStatus
  } catch (error) {
    console.error('Ошибка обновления статуса:', error)
    alert('Не удалось изменить статус заказа')
  }
}

// ===== СТАТИСТИКА =====
const loadStats = async () => {
  try {
    const ordersRes = await axios.get('http://127.0.0.1:8000/api/orders/')
    const masterProductIds = products.value.map(p => p.id)
    const masterOrders = ordersRes.data.filter(order => 
      order.items?.some(item => masterProductIds.includes(item.product_id))
    )
    
    let totalRevenue = 0
    const productSales = {}
    
    masterOrders.forEach(order => {
      totalRevenue += parseFloat(order.total_price)
      order.items.forEach(item => {
        if (masterProductIds.includes(item.product_id)) {
          if (!productSales[item.product_id]) {
            productSales[item.product_id] = { name: item.product_name, quantity: 0, revenue: 0 }
          }
          productSales[item.product_id].quantity += item.quantity
          productSales[item.product_id].revenue += item.quantity * parseFloat(item.product_price)
        }
      })
    })
    
    stats.value = {
      total_orders: masterOrders.length,
      total_revenue: totalRevenue,
      avg_order_value: masterOrders.length ? totalRevenue / masterOrders.length : 0,
      top_products: Object.values(productSales).sort((a, b) => b.revenue - a.revenue).slice(0, 5),
      monthly_data: []
    }
    showStats.value = true
    activeTab.value = 'stats'
  } catch (error) {
    console.error('Ошибка загрузки статистики:', error)
  }
}

// ===== ЧАТЫ =====
const selectRoom = (room) => {
  chatStore.currentRoom = room
  chatStore.loadMessages(room.id)
}

const sendMessage = async () => {
  if (!newMessageText.value.trim() || !chatStore.currentRoom) return
  await chatStore.sendMessage(chatStore.currentRoom.id, newMessageText.value)
  newMessageText.value = ''
  setTimeout(() => {
    const container = document.querySelector('.chat-messages')
    if (container) container.scrollTop = container.scrollHeight
  }, 50)
}

const refreshMessages = () => {
  if (chatStore.currentRoom) {
    chatStore.loadMessages(chatStore.currentRoom.id)
  }
}

const refreshRooms = () => {
  chatStore.loadRooms()
}

// ===== ОБЩИЕ ФУНКЦИИ =====
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

const getStatusText = (status) => {
  const map = { 'new': '🆕 Новый', 'processing': '⚙️ В обработке', 'completed': '✅ Выполнен', 'cancelled': '❌ Отменён' }
  return map[status] || status
}

const logout = () => {
  authStore.logout()
  router.push('/')
}
</script>

<template>
  <div class="container">
    <div class="dashboard-header">
      <h1>Панель управления мастера</h1>
      <div class="header-actions">
        <router-link to="/" class="view-site-btn">Перейти на сайт</router-link>
        <button class="stats-btn" @click="loadStats">📊 Статистика</button>
        <button @click="logout" class="logout-btn">Выйти</button>
      </div>
    </div>
    
    <div v-if="loading" class="loading">Загрузка...</div>
    
    <div v-else class="dashboard-content">
      <div class="tabs">
        <button :class="{ active: activeTab === 'products' }" @click="activeTab = 'products'">Мои товары</button>
        <button :class="{ active: activeTab === 'add' }" @click="activeTab = 'add'">Добавить товар</button>
        <button :class="{ active: activeTab === 'posts' }" @click="activeTab = 'posts'">Публикации</button>
        <button :class="{ active: activeTab === 'orders' }" @click="activeTab = 'orders'; loadMasterOrders()">Заказы</button>
        <button :class="{ active: activeTab === 'stats' }" @click="activeTab = 'stats'">Статистика</button>
        <button :class="{ active: activeTab === 'chats' }" @click="activeTab = 'chats'">💬 Чаты ({{ chatStore.rooms.length }})</button>
        <router-link :to="'/master/' + (authStore.masterId || 1)" class="profile-link">Публичная страница</router-link>
      </div>
      
      <!-- Мои товары -->
      <div v-if="activeTab === 'products'" class="tab-content">
        <h2>Мои товары</h2>
        <div v-if="products.length === 0" class="empty">У вас пока нет товаров</div>
        <div v-else class="products-list">
          <div v-for="product in products" :key="product.id" class="product-item">
            <div class="product-image">
              <img v-if="product.image" :src="product.image" :alt="product.name">
              <div v-else class="no-image">Нет фото</div>
            </div>
            <div class="product-info">
              <h3>{{ product.name }}</h3>
              <p class="price">{{ product.price }} ₽</p>
              <p class="category">Категория: {{ product.category?.name }}</p>
            </div>
            <div class="product-actions">
              <button class="edit-btn" @click="openEditModal(product)">✏️</button>
              <button class="delete-btn" @click="deleteProduct(product.id)">🗑️</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Добавить товар -->
      <div v-if="activeTab === 'add'" class="tab-content">
        <h2>Добавить новый товар</h2>
        <form @submit.prevent="addProduct" class="add-form">
          <div class="form-group"><label>Название *</label><input type="text" v-model="newProduct.name" required></div>
          <div class="form-group"><label>Описание</label><textarea v-model="newProduct.description" rows="4"></textarea></div>
          <div class="form-row">
            <div class="form-group"><label>Цена *</label><input type="number" v-model="newProduct.price" step="0.01" required></div>
            <div class="form-group"><label>Категория *</label><select v-model="newProduct.category_id" required>
              <option value="">Выберите категорию</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select></div>
          </div>
          <div class="form-group"><label>Фото</label><input type="file" accept="image/*" @change="handleImageUpload"></div>
          <button type="submit" class="submit-btn">Добавить товар</button>
        </form>
      </div>
      
      <!-- Публикации -->
      <div v-if="activeTab === 'posts'" class="tab-content">
        <h2>Мои публикации</h2>
        
        <form @submit.prevent="createPost" class="add-post-form">
          <div class="form-group">
            <label>Заголовок *</label>
            <input type="text" v-model="newPost.title" required>
          </div>
          <div class="form-group">
            <label>Содержание</label>
            <textarea v-model="newPost.content" rows="5"></textarea>
          </div>
          <div class="form-group">
            <label>Изображение</label>
            <input type="file" accept="image/*" @change="handlePostImageUpload">
          </div>
          <div class="form-group">
            <label>Ссылка на видео (YouTube)</label>
            <input type="url" v-model="newPost.video_url" placeholder="https://youtube.com/watch?v=...">
          </div>
          <div class="form-group">
            <label>Связанный товар (опционально)</label>
            <select v-model="newPost.product_id">
              <option :value="null">Не выбрано</option>
              <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
          </div>
          <button type="submit" class="submit-btn">Опубликовать</button>
        </form>
        
        <div class="posts-list" v-if="myPosts.length">
          <div v-for="post in myPosts" :key="post.id" class="post-item">
            <div class="post-header">
              <h3>{{ post.title }}</h3>
              <span class="post-date">{{ formatDate(post.created_at) }}</span>
            </div>
            <p>{{ post.content?.slice(0, 150) }}...</p>
            <div class="post-stats">
              <span>👁️ {{ post.views_count }}</span>
              <span>❤️ {{ post.likes_count }}</span>
              <span>💬 {{ post.comments_count }}</span>
            </div>
            <div class="post-actions">
              <button @click="deletePost(post.id)" class="delete-btn">Удалить</button>
            </div>
          </div>
        </div>
        <div v-else class="empty">У вас пока нет публикаций</div>
      </div>
      
      <!-- Заказы -->
      <div v-if="activeTab === 'orders'" class="tab-content">
        <h2>Заказы на мои товары</h2>
        <div v-if="loadingOrders" class="loading">Загрузка заказов...</div>
        <div v-else-if="orders.length === 0" class="empty">У вас пока нет заказов</div>
        <div v-else class="orders-list">
          <div v-for="order in orders" :key="order.id" class="order-card">
            <div class="order-header">
              <span class="order-number">Заказ #{{ order.id }}</span>
              <span class="order-status" :class="'status-' + order.status">{{ getStatusText(order.status) }}</span>
              <span class="order-date">{{ formatDate(order.created_at) }}</span>
            </div>
            <div class="order-customer">
              <p><strong>{{ order.first_name }} {{ order.last_name }}</strong> | 📞 {{ order.phone }} | 📧 {{ order.email }}</p>
              <p>📍 {{ order.address }}</p>
              <p v-if="order.comment">💬 {{ order.comment }}</p>
            </div>
            <div class="order-items">
              <h4>Товары из вашего магазина:</h4>
              <div v-for="item in order.items" :key="item.id" class="order-item">
                <span>{{ item.product_name }}</span>
                <span>{{ item.quantity }} шт × {{ item.product_price }} ₽</span>
                <span class="item-total">{{ item.quantity * item.product_price }} ₽</span>
              </div>
            </div>
            <div class="order-total"><strong>Общая сумма: {{ order.total_price }} ₽</strong></div>
            <div class="order-status-control">
              <label>Изменить статус:</label>
              <select :value="order.status" @change="updateOrderStatus(order.id, $event.target.value)" class="status-select">
                <option value="new">🆕 Новый</option>
                <option value="processing">⚙️ В обработке</option>
                <option value="completed">✅ Выполнен</option>
                <option value="cancelled">❌ Отменён</option>
              </select>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Статистика -->
      <div v-if="activeTab === 'stats'" class="tab-content">
        <h2>Статистика продаж</h2>
        <div v-if="!showStats" class="stats-preview">
          <button class="load-stats-btn" @click="loadStats">Загрузить статистику</button>
        </div>
        <div v-else>
          <div class="stats-cards">
            <div class="stat-card">
              <div class="stat-icon">📦</div>
              <div>
                <div class="stat-value">{{ stats.total_orders }}</div>
                <div class="stat-label">Всего заказов</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">💰</div>
              <div>
                <div class="stat-value">{{ stats.total_revenue.toFixed(2) }} ₽</div>
                <div class="stat-label">Общая выручка</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">📊</div>
              <div>
                <div class="stat-value">{{ stats.avg_order_value.toFixed(2) }} ₽</div>
                <div class="stat-label">Средний чек</div>
              </div>
            </div>
          </div>
          
          <div class="stats-section">
            <h3>Топ-5 товаров</h3>
            <table class="stats-table">
              <thead>
                <tr>
                  <th>Товар</th>
                  <th>Продано</th>
                  <th>Выручка</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="product in stats.top_products" :key="product.name">
                  <td>{{ product.name }}</td>
                  <td>{{ product.quantity }} шт</td>
                  <td>{{ product.revenue.toFixed(2) }} ₽</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      <!-- Чаты -->
      <div v-if="activeTab === 'chats'" class="tab-content">
        <div class="chats-header">
          <h2>Сообщения от покупателей</h2>
          <button class="refresh-rooms-btn" @click="refreshRooms" title="Обновить список чатов">🔄 Обновить список</button>
        </div>
        <div v-if="chatStore.loading" class="loading">Загрузка...</div>
        <div v-else-if="chatStore.rooms.length === 0" class="empty">
          <p>У вас пока нет чатов с покупателями</p>
        </div>
        <div v-else class="chats-layout">
          <div class="rooms-list">
            <div v-for="room in chatStore.rooms" :key="room.id"
                 :class="['room-item', { active: chatStore.currentRoom?.id === room.id }]"
                 @click="selectRoom(room)">
              <div class="room-avatar">
                <div class="avatar-placeholder">{{ room.customer_name?.[0] || 'П' }}</div>
              </div>
              <div class="room-info">
                <div class="room-name">{{ room.customer_name }}</div>
                <div class="room-last-message">{{ room.last_message?.text?.slice(0, 30) || 'Нет сообщений' }}</div>
              </div>
              <div v-if="room.unread_count > 0" class="unread-badge">{{ room.unread_count }}</div>
            </div>
          </div>
          <div class="chat-window" v-if="chatStore.currentRoom">
            <div class="chat-header">
              <strong>{{ chatStore.currentRoom.customer_name }}</strong>
              <button class="refresh-msg-btn" @click="refreshMessages" title="Обновить сообщения">🔄</button>
            </div>
            <div class="chat-messages">
              <div v-for="msg in chatStore.messages" :key="msg.id"
                   :class="['message', msg.is_owner ? 'outgoing' : 'incoming']">
                <div class="message-text">{{ msg.text }}</div>
                <div class="message-time">{{ new Date(msg.created_at).toLocaleTimeString() }}</div>
              </div>
            </div>
            <div class="chat-input">
              <input type="text" v-model="newMessageText" placeholder="Напишите сообщение..." @keyup.enter="sendMessage">
              <button @click="sendMessage">📤</button>
            </div>
          </div>
          <div v-else class="chat-placeholder">Выберите чат для начала общения</div>
        </div>
      </div>
    </div>
    
    <!-- Модальное окно редактирования товара -->
    <Teleport to="body">
      <div v-if="showEditModal" class="modal-overlay" @click="showEditModal = false">
        <div class="modal-content" @click.stop>
          <h2>Редактировать товар</h2>
          <form @submit.prevent="updateProduct">
            <div class="form-group"><label>Название</label><input type="text" v-model="editForm.name" required></div>
            <div class="form-group"><label>Описание</label><textarea v-model="editForm.description" rows="4"></textarea></div>
            <div class="form-row">
              <div class="form-group"><label>Цена</label><input type="number" v-model="editForm.price" step="0.01" required></div>
              <div class="form-group"><label>Категория</label><select v-model="editForm.category_id" required>
                <option value="">Выберите категорию</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
              </select></div>
            </div>
            <div class="form-group"><label>Новое фото (оставьте пустым, если не хотите менять)</label><input type="file" accept="image/*" @change="handleEditImageUpload"></div>
            <div class="modal-actions"><button type="button" class="cancel-btn" @click="showEditModal = false">Отмена</button><button type="submit" class="submit-btn">Сохранить</button></div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.container { 
  max-width: 1200px; 
  margin: 0 auto; 
  padding: 20px; 
}

.dashboard-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: 30px; 
}

.header-actions { 
  display: flex; 
  gap: 10px; 
}

.view-site-btn { 
  padding: 8px 16px; 
  background: #3498db; 
  color: white; 
  border: none; 
  border-radius: 4px; 
  text-decoration: none; 
}

.stats-btn { 
  padding: 8px 16px; 
  background: #C67B5C;
  color: white; 
  border: none; 
  border-radius: 4px; 
  cursor: pointer;
  transition: background 0.3s;
}
.stats-btn:hover {
  background: #B56A4D;
}

.logout-btn { 
  padding: 8px 16px; 
  background: #ff4444; 
  color: white; 
  border: none; 
  border-radius: 4px; 
  cursor: pointer; 
}

.tabs { 
  display: flex; 
  gap: 10px; 
  margin-bottom: 30px; 
  border-bottom: 2px solid #E8DCC9;
  padding-bottom: 10px; 
  overflow-x: auto; 
  align-items: center; 
}

.tabs button, 
.profile-link { 
  padding: 10px 20px; 
  background: none; 
  border: none; 
  font-size: 16px; 
  cursor: pointer; 
  color: #666; 
  text-decoration: none; 
  display: inline-flex; 
  align-items: center; 
  gap: 8px; 
}

.tabs button.active, 
.profile-link { 
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

.empty, 
.loading { 
  text-align: center; 
  padding: 40px; 
  color: #666; 
}

.products-list { 
  display: grid; 
  gap: 15px; 
}

.product-item { 
  display: grid; 
  grid-template-columns: 80px 1fr 100px; 
  gap: 15px; 
  align-items: center; 
  padding: 15px; 
  border: 1px solid #E8DCC9;
  border-radius: 8px; 
  background: #FFFBF7;
}

.product-image { 
  width: 80px; 
  height: 80px; 
  background: #FFFBF7;
  border-radius: 4px; 
  overflow: hidden; 
}

.product-image img { 
  width: 100%; 
  height: 100%; 
  object-fit: cover; 
}

.price { 
  font-weight: bold; 
  color: #C67B5C;
}

.product-actions { 
  display: flex; 
  gap: 10px; 
  justify-content: flex-end; 
}

.edit-btn, 
.delete-btn { 
  padding: 5px 10px; 
  border: none; 
  border-radius: 4px; 
  cursor: pointer; 
}

.edit-btn { 
  background: #F5E9D7;
}

.delete-btn { 
  background: #fee; 
  color: #ff4444; 
}

.add-form, 
.add-post-form { 
  max-width: 600px; 
}

.form-group { 
  margin-bottom: 20px; 
}

.form-row { 
  display: grid; 
  grid-template-columns: 1fr 1fr; 
  gap: 20px; 
}

.form-group label { 
  display: block; 
  margin-bottom: 5px; 
  font-weight: 500; 
}

.form-group input, 
.form-group textarea, 
.form-group select { 
  width: 100%; 
  padding: 10px; 
  border: 1px solid #E8DCC9;
  border-radius: 4px; 
  background: #FFFBF7;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #C67B5C;
}

.submit-btn { 
  padding: 12px 30px; 
  background: #C67B5C;
  color: white; 
  border: none; 
  border-radius: 6px; 
  cursor: pointer;
  transition: background 0.3s;
}
.submit-btn:hover {
  background: #B56A4D;
}

.posts-list { 
  margin-top: 30px; 
  display: flex; 
  flex-direction: column; 
  gap: 20px; 
}

.post-item { 
  border: 1px solid #E8DCC9;
  border-radius: 8px; 
  padding: 20px; 
  background: #FFFBF7;
}

.post-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: 10px; 
}

.post-header h3 { 
  font-size: 18px; 
  margin: 0; 
}

.post-date { 
  font-size: 12px; 
  color: #999; 
}

.post-stats { 
  display: flex; 
  gap: 15px; 
  margin-top: 10px; 
  color: #666; 
  font-size: 14px; 
}

.post-actions { 
  margin-top: 10px; 
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
}

.order-status { 
  padding: 4px 12px; 
  border-radius: 20px; 
  font-size: 14px; 
}

.status-new { background: #e3f2fd; color: #1976d2; }
.status-processing { background: #fff3e0; color: #f57c00; }
.status-completed { background: #e8f5e8; color: #388e3c; }
.status-cancelled { background: #ffebee; color: #d32f2f; }

.order-customer { 
  margin-bottom: 15px; 
  padding: 10px; 
  background: white; 
  border-radius: 4px; 
}

.order-items { 
  margin-bottom: 15px; 
}

.order-item { 
  display: flex; 
  justify-content: space-between; 
  padding: 5px 0; 
  border-bottom: 1px dotted #E8DCC9;
}

.item-total { 
  font-weight: bold; 
  color: #C67B5C;
}

.order-total { 
  text-align: right; 
  padding: 10px 0; 
  border-top: 2px solid #E8DCC9;
}

.order-status-control { 
  margin-top: 15px; 
  padding-top: 15px; 
  border-top: 1px dashed #E8DCC9;
  display: flex; 
  gap: 10px; 
}

.stats-cards { 
  display: grid; 
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
  gap: 20px; 
  margin-bottom: 40px; 
}

.stat-card { 
  background: linear-gradient(135deg, #667eea, #764ba2); 
  border-radius: 12px; 
  padding: 25px; 
  color: white; 
  display: flex; 
  align-items: center; 
  gap: 20px; 
}
.stat-card:nth-child(2) { 
  background: linear-gradient(135deg, #f093fb, #f5576c); 
}
.stat-card:nth-child(3) { 
  background: linear-gradient(135deg, #4facfe, #00f2fe); 
}

.stat-icon { 
  font-size: 48px; 
}

.stat-value { 
  font-size: 28px; 
  font-weight: bold; 
}

.stats-section { 
  background: #FFFBF7;
  border-radius: 8px; 
  padding: 20px; 
  margin-bottom: 20px; 
}

.stats-table { 
  width: 100%; 
  border-collapse: collapse; 
}

.stats-table th { 
  text-align: left; 
  padding: 12px; 
  background: #F5E9D7;
}

.stats-table td { 
  padding: 10px 12px; 
  border-bottom: 1px solid #E8DCC9;
}

.modal-overlay { 
  position: fixed; 
  top: 0; 
  left: 0; 
  width: 100%; 
  height: 100%; 
  background: rgba(0,0,0,0.5); 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  z-index: 1000; 
}

.modal-content { 
  background: white; 
  border-radius: 8px; 
  padding: 30px; 
  max-width: 600px; 
  width: 90%; 
  max-height: 90vh; 
  overflow-y: auto; 
}

.modal-actions { 
  display: flex; 
  gap: 10px; 
  justify-content: flex-end; 
  margin-top: 20px; 
}

.cancel-btn { 
  padding: 10px 20px; 
  background: #F5E9D7;
  border: none; 
  border-radius: 6px; 
  cursor: pointer;
  transition: background 0.3s;
}
.cancel-btn:hover {
  background: #E8DCC9;
}

.chats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.refresh-rooms-btn {
  background: #F5E9D7;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}
.refresh-rooms-btn:hover {
  background: #E8DCC9;
}

.chats-layout { 
  display: grid; 
  grid-template-columns: 300px 1fr; 
  gap: 20px; 
  height: 500px; 
}

.rooms-list { 
  background: #FFFBF7;
  border-radius: 8px; 
  overflow-y: auto; 
}

.room-item { 
  display: flex; 
  align-items: center; 
  gap: 12px; 
  padding: 12px; 
  cursor: pointer; 
  border-bottom: 1px solid #E8DCC9;
  position: relative; 
}

.room-item.active { 
  background: #FFF3E6;
}

.room-avatar { 
  width: 48px; 
  height: 48px; 
  border-radius: 50%; 
  background: #C67B5C;
  color: white; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  font-weight: bold; 
  font-size: 20px; 
  overflow: hidden; 
}

.avatar-placeholder { 
  width: 100%; 
  height: 100%; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  background: #C67B5C;
  color: white; 
  font-weight: bold; 
  font-size: 20px; 
}

.room-info { 
  flex: 1; 
}

.room-name { 
  font-weight: bold; 
}

.room-last-message { 
  font-size: 12px; 
  color: #666; 
}

.unread-badge { 
  background: #ff4444; 
  color: white; 
  border-radius: 10px; 
  padding: 2px 6px; 
  font-size: 10px; 
  min-width: 20px; 
  text-align: center; 
}

.chat-window { 
  display: flex; 
  flex-direction: column; 
  background: white; 
  border-radius: 8px; 
  overflow: hidden; 
  height: 100%; 
}

.chat-header { 
  padding: 12px; 
  border-bottom: 1px solid #E8DCC9;
  background: #FFFBF7;
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
}

.refresh-msg-btn { 
  background: none; 
  border: none; 
  font-size: 18px; 
  cursor: pointer; 
  padding: 4px 8px; 
  border-radius: 4px;
  transition: background 0.3s;
}
.refresh-msg-btn:hover { 
  background: #E8DCC9;
}

.chat-messages { 
  flex: 1; 
  overflow-y: auto; 
  padding: 12px; 
  display: flex; 
  flex-direction: column; 
  gap: 8px; 
}

.message { 
  max-width: 70%; 
  padding: 8px 12px; 
  border-radius: 12px; 
  font-size: 14px; 
}

.message.incoming { 
  background: #F5E9D7;
  align-self: flex-start; 
}

.message.outgoing { 
  background: #C67B5C;
  color: white; 
  align-self: flex-end; 
}

.message-time { 
  font-size: 10px; 
  opacity: 0.7; 
  margin-top: 4px; 
}

.chat-input { 
  display: flex; 
  gap: 8px; 
  padding: 12px; 
  border-top: 1px solid #E8DCC9;
}

.chat-input input { 
  flex: 1; 
  padding: 8px; 
  border: 1px solid #E8DCC9;
  border-radius: 20px; 
  background: #FFFBF7;
  transition: border-color 0.3s;
}
.chat-input input:focus {
  outline: none;
  border-color: #C67B5C;
}

.chat-input button { 
  background: #C67B5C;
  border: none; 
  border-radius: 50%; 
  width: 36px; 
  cursor: pointer;
  transition: background 0.3s;
}
.chat-input button:hover {
  background: #B56A4D;
}

.chat-placeholder { 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  background: white; 
  border-radius: 8px; 
  color: #999; 
}
</style>