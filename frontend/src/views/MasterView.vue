<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const activeTab = ref('products')
const products = ref([])
const profile = ref(null)
const loading = ref(true)
const editingProduct = ref(null)
const showEditModal = ref(false)
const orders = ref([])
const loadingOrders = ref(false)

// Статистика
const showStats = ref(false)
const stats = ref({
  total_orders: 0,
  total_revenue: 0,
  avg_order_value: 0,
  top_products: [],
  monthly_data: []
})

// Редактирование профиля
const showProfileEditModal = ref(false)
const profileEditForm = ref({
  shop_name: '',
  description: '',
  phone: '',
  email: '',
  avatar: null
})

// Форма для редактирования товара
const editForm = ref({
  name: '',
  description: '',
  price: '',
  category_id: '',
  image: null
})

// Форма для нового товара
const newProduct = ref({
  name: '',
  description: '',
  price: '',
  category_id: '',
  image: null
})

const categories = ref([])

// ===== ЗАГРУЗКА ДАННЫХ =====
onMounted(async () => {
  await loadData()
})

const loadData = async () => {
  loading.value = true
  try {
    const categoriesRes = await axios.get('http://127.0.0.1:8000/api/categories/')
    categories.value = categoriesRes.data
    
    // Используем masterId из стора, если нет — временно берём id=1
    const masterId = authStore.masterId || 1
    console.log('Loading products for master:', masterId) // Отладка
    
    const productsRes = await axios.get(`http://127.0.0.1:8000/api/products/?master=${masterId}`)
    products.value = productsRes.data
    
    // Загружаем профиль
    try {
      const profileRes = await axios.get('http://127.0.0.1:8000/api/masters/profile/')
      profile.value = profileRes.data
    } catch (profileError) {
      console.warn('Профиль мастера не найден, создайте его в админке')
      profile.value = null
    }
  } catch (error) {
    console.error('Ошибка загрузки:', error)
  } finally {
    loading.value = false
  }
}

// ===== ТОВАРЫ =====
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
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )
    
    const index = products.value.findIndex(p => p.id === editingProduct.value.id)
    if (index !== -1) {
      products.value[index] = response.data
    }
    
    showEditModal.value = false
    editingProduct.value = null
    alert('Товар успешно обновлён')
  } catch (error) {
    console.error('Ошибка при обновлении товара:', error)
    alert('Ошибка при обновлении товара')
  }
}

const handleEditImageUpload = (event) => {
  editForm.value.image = event.target.files[0]
}

const addProduct = async () => {
  try {
    const formData = new FormData()
    formData.append('name', newProduct.value.name)
    formData.append('description', newProduct.value.description)
    formData.append('price', newProduct.value.price)
    formData.append('category_id', newProduct.value.category_id)
    if (profile.value?.id) {
      formData.append('master_id', profile.value.id)
    }
    
    if (newProduct.value.image) {
      formData.append('image', newProduct.value.image)
    }
    
    const response = await axios.post('http://127.0.0.1:8000/api/products/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    products.value.unshift(response.data)
    newProduct.value = { name: '', description: '', price: '', category_id: '', image: null }
    activeTab.value = 'products'
    alert('Товар успешно добавлен')
  } catch (error) {
    console.error('Ошибка добавления:', error)
    alert('Ошибка при добавлении товара')
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

const handleImageUpload = (event) => {
  newProduct.value.image = event.target.files[0]
}

// ===== ЗАКАЗЫ =====
const loadMasterOrders = async () => {
  loadingOrders.value = true
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/orders/')
    
    const masterProductIds = products.value.map(p => p.id)
    
    const masterOrders = response.data.filter(order => {
      return order.items?.some(item => masterProductIds.includes(item.product_id))
    })
    
    orders.value = masterOrders
  } catch (error) {
    console.error('Ошибка загрузки заказов:', error)
  } finally {
    loadingOrders.value = false
  }
}

const updateOrderStatus = async (orderId, newStatus) => {
  try {
    await axios.patch(`http://127.0.0.1:8000/api/orders/${orderId}/`, {
      status: newStatus
    })
    
    const order = orders.value.find(o => o.id === orderId)
    if (order) {
      order.status = newStatus
    }
  } catch (error) {
    console.error('Ошибка обновления статуса:', error)
    alert('Не удалось изменить статус заказа')
  }
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

const switchToOrders = async () => {
  activeTab.value = 'orders'
  await loadMasterOrders()
}

// ===== ПРОФИЛЬ =====
const openProfileEditModal = () => {
  if (!profile.value) {
    alert('Сначала создайте профиль в админке')
    return
  }
  profileEditForm.value = {
    shop_name: profile.value.shop_name,
    description: profile.value.description || '',
    phone: profile.value.phone,
    email: profile.value.email,
    avatar: null
  }
  showProfileEditModal.value = true
}

const updateProfile = async () => {
  try {
    const formData = new FormData()
    formData.append('shop_name', profileEditForm.value.shop_name)
    formData.append('description', profileEditForm.value.description)
    formData.append('phone', profileEditForm.value.phone)
    formData.append('email', profileEditForm.value.email)
    
    if (profileEditForm.value.avatar) {
      formData.append('avatar', profileEditForm.value.avatar)
    }
    
    const response = await axios.put(
      `http://127.0.0.1:8000/api/masters/profile/`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )
    
    profile.value = response.data
    showProfileEditModal.value = false
    alert('Профиль успешно обновлён')
  } catch (error) {
    console.error('Ошибка обновления профиля:', error)
    alert('Ошибка при обновлении профиля')
  }
}

const handleProfileImageUpload = (event) => {
  profileEditForm.value.avatar = event.target.files[0]
}

// ===== СТАТИСТИКА =====
const loadStats = async () => {
  try {
    const ordersRes = await axios.get('http://127.0.0.1:8000/api/orders/')
    const allOrders = ordersRes.data
    
    const masterProductIds = products.value.map(p => p.id)
    
    const masterOrders = allOrders.filter(order => {
      return order.items?.some(item => masterProductIds.includes(item.product_id))
    })
    
    let totalRevenue = 0
    const productSales = {}
    
    masterOrders.forEach(order => {
      totalRevenue += parseFloat(order.total_price)
      
      order.items.forEach(item => {
        if (masterProductIds.includes(item.product_id)) {
          if (!productSales[item.product_id]) {
            productSales[item.product_id] = {
              name: item.product_name,
              quantity: 0,
              revenue: 0
            }
          }
          productSales[item.product_id].quantity += item.quantity
          productSales[item.product_id].revenue += item.quantity * parseFloat(item.product_price)
        }
      })
    })
    
    const topProducts = Object.values(productSales)
      .sort((a, b) => b.revenue - a.revenue)
      .slice(0, 5)
    
    const monthlyStats = {}
    masterOrders.forEach(order => {
      const month = order.created_at.substring(0, 7)
      if (!monthlyStats[month]) {
        monthlyStats[month] = {
          month,
          orders: 0,
          revenue: 0
        }
      }
      monthlyStats[month].orders += 1
      monthlyStats[month].revenue += parseFloat(order.total_price)
    })
    
    stats.value = {
      total_orders: masterOrders.length,
      total_revenue: totalRevenue,
      avg_order_value: masterOrders.length ? (totalRevenue / masterOrders.length) : 0,
      top_products: topProducts,
      monthly_data: Object.values(monthlyStats).sort((a, b) => a.month.localeCompare(b.month))
    }
    
    showStats.value = true
    activeTab.value = 'stats'
  } catch (error) {
    console.error('Ошибка загрузки статистики:', error)
  }
}

// ===== ОБЩИЕ ФУНКЦИИ =====
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

const logout = () => {
  authStore.logout()
  router.push('/')  // или window.location.href = '/'
}
</script>

<template>
  <div class="container">
    <div class="master-header">
      <h1>Личный кабинет мастера</h1>
      <div class="header-actions">
        <button class="stats-btn" @click="loadStats()">
          📊 Статистика
        </button>
        <button @click="logout" class="logout-btn">Выйти</button>
      </div>
    </div>
    
    <div v-if="loading">Загрузка...</div>
    
    <div v-else class="master-content">
      <!-- Вкладки -->
      <div class="tabs">
        <button 
          :class="{ active: activeTab === 'products' }"
          @click="activeTab = 'products'"
        >
          Мои товары
        </button>
        <button 
          :class="{ active: activeTab === 'add' }"
          @click="activeTab = 'add'"
        >
          Добавить товар
        </button>
        <button 
          :class="{ active: activeTab === 'orders' }"
          @click="switchToOrders"
        >
          Заказы
        </button>
        <button 
          :class="{ active: activeTab === 'profile' }"
          @click="activeTab = 'profile'"
        >
          Профиль
        </button>
        <button 
          :class="{ active: activeTab === 'stats' }"
          @click="activeTab = 'stats'"
        >
          Статистика
        </button>
      </div>
      
      <!-- Вкладка: Мои товары -->
      <div v-if="activeTab === 'products'" class="tab-content">
        <h2>Мои товары</h2>
        <div v-if="products.length === 0" class="empty">
          У вас пока нет товаров
        </div>
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
      
      <!-- Вкладка: Добавить товар -->
      <div v-if="activeTab === 'add'" class="tab-content">
        <h2>Добавить новый товар</h2>
        <form @submit.prevent="addProduct" class="add-form">
          <div class="form-group">
            <label for="name">Название *</label>
            <input 
              type="text" 
              id="name" 
              v-model="newProduct.name"
              required
            >
          </div>
          
          <div class="form-group">
            <label for="description">Описание</label>
            <textarea 
              id="description" 
              v-model="newProduct.description"
              rows="4"
            ></textarea>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="price">Цена *</label>
              <input 
                type="number" 
                id="price" 
                v-model="newProduct.price"
                step="0.01"
                min="0"
                required
              >
            </div>
            
            <div class="form-group">
              <label for="category">Категория *</label>
              <select id="category" v-model="newProduct.category_id" required>
                <option value="">Выберите категорию</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
            </div>
          </div>
          
          <div class="form-group">
            <label for="image">Фото товара</label>
            <input 
              type="file" 
              id="image" 
              accept="image/*"
              @change="handleImageUpload"
            >
          </div>
          
          <button type="submit" class="submit-btn">Добавить товар</button>
        </form>
      </div>
      
      <!-- Вкладка: Заказы -->
      <div v-if="activeTab === 'orders'" class="tab-content">
        <h2>Заказы на мои товары</h2>
        
        <div v-if="loadingOrders" class="loading">Загрузка заказов...</div>
        
        <div v-else-if="orders.length === 0" class="empty">
          <p>У вас пока нет заказов</p>
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
            
            <div class="order-customer">
              <p><strong>{{ order.first_name }} {{ order.last_name }}</strong></p>
              <p>📞 {{ order.phone }}</p>
              <p>📧 {{ order.email }}</p>
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
            
            <div class="order-total">
              <strong>Общая сумма заказа: {{ order.total_price }} ₽</strong>
            </div>
            
            <div class="order-status-control">
              <label>Изменить статус:</label>
              <select 
                :value="order.status"
                @change="updateOrderStatus(order.id, $event.target.value)"
                class="status-select"
              >
                <option value="new">🆕 Новый</option>
                <option value="processing">⚙️ В обработке</option>
                <option value="completed">✅ Выполнен</option>
                <option value="cancelled">❌ Отменён</option>
              </select>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Вкладка: Профиль -->
      <div v-if="activeTab === 'profile'" class="tab-content">
        <div class="profile-header">
          <h2>Профиль мастера</h2>
          <button class="edit-profile-btn" @click="openProfileEditModal">
            ✏️ Редактировать профиль
          </button>
        </div>
        
        <div v-if="!profile" class="empty">
          <p>Профиль не найден. Создайте его в админке.</p>
        </div>
        
        <div v-else class="profile-info">
          <div class="avatar-section">
            <div class="avatar">
              <img v-if="profile.avatar" :src="profile.avatar" :alt="profile.shop_name">
              <div v-else class="no-avatar">{{ profile.shop_name?.[0] || 'М' }}</div>
            </div>
          </div>
          <div class="info-details">
            <div class="info-row">
              <span class="info-label">Название магазина:</span>
              <span class="info-value">{{ profile.shop_name }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Телефон:</span>
              <span class="info-value">{{ profile.phone }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Email:</span>
              <span class="info-value">{{ profile.email }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Описание:</span>
              <span class="info-value">{{ profile.description || '—' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Дата регистрации:</span>
              <span class="info-value">{{ formatDate(profile.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Вкладка: Статистика -->
      <div v-if="activeTab === 'stats'" class="tab-content">
        <h2>Статистика продаж</h2>
        
        <div v-if="!showStats" class="stats-preview">
          <p>Нажмите кнопку "Загрузить статистику" для просмотра данных</p>
          <button class="load-stats-btn" @click="loadStats">Загрузить статистику</button>
        </div>
        
        <div v-else class="stats-container">
          <!-- Основные показатели -->
          <div class="stats-cards">
            <div class="stat-card">
              <div class="stat-icon">📦</div>
              <div class="stat-content">
                <div class="stat-value">{{ stats.total_orders }}</div>
                <div class="stat-label">Всего заказов</div>
              </div>
            </div>
            
            <div class="stat-card">
              <div class="stat-icon">💰</div>
              <div class="stat-content">
                <div class="stat-value">{{ stats.total_revenue.toFixed(2) }} ₽</div>
                <div class="stat-label">Общая выручка</div>
              </div>
            </div>
            
            <div class="stat-card">
              <div class="stat-icon">📊</div>
              <div class="stat-content">
                <div class="stat-value">{{ stats.avg_order_value.toFixed(2) }} ₽</div>
                <div class="stat-label">Средний чек</div>
              </div>
            </div>
          </div>
          
          <!-- Динамика по месяцам -->
          <div class="stats-section">
            <h3>Динамика продаж по месяцам</h3>
            <div class="monthly-stats">
              <table class="stats-table">
                <thead>
                  <tr>
                    <th>Месяц</th>
                    <th>Заказов</th>
                    <th>Выручка</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="month in stats.monthly_data" :key="month.month">
                    <td>{{ month.month }}</td>
                    <td>{{ month.orders }}</td>
                    <td>{{ month.revenue.toFixed(2) }} ₽</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          
          <!-- Топ товаров -->
          <div class="stats-section">
            <h3>Топ-5 товаров по выручке</h3>
            <div class="top-products">
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
      </div>
    </div>
  </div>
  
  <!-- Модальное окно редактирования товара -->
  <Teleport to="body">
    <div v-if="showEditModal" class="modal-overlay" @click="showEditModal = false">
      <div class="modal-content" @click.stop>
        <h2>Редактировать товар</h2>
        
        <form @submit.prevent="updateProduct">
          <div class="form-group">
            <label>Название *</label>
            <input type="text" v-model="editForm.name" required>
          </div>
          
          <div class="form-group">
            <label>Описание</label>
            <textarea v-model="editForm.description" rows="4"></textarea>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Цена *</label>
              <input type="number" v-model="editForm.price" step="0.01" required>
            </div>
            
            <div class="form-group">
              <label>Категория *</label>
              <select v-model="editForm.category_id" required>
                <option value="">Выберите категорию</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
            </div>
          </div>
          
          <div class="form-group">
            <label>Новое фото (оставьте пустым, если не хотите менять)</label>
            <input type="file" accept="image/*" @change="handleEditImageUpload">
          </div>
          
          <div class="modal-actions">
            <button type="button" class="cancel-btn" @click="showEditModal = false">
              Отмена
            </button>
            <button type="submit" class="submit-btn">
              Сохранить изменения
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>

  <!-- Модальное окно редактирования профиля -->
  <Teleport to="body">
    <div v-if="showProfileEditModal" class="modal-overlay" @click="showProfileEditModal = false">
      <div class="modal-content" @click.stop>
        <h2>Редактировать профиль</h2>
        
        <form @submit.prevent="updateProfile">
          <div class="form-group">
            <label>Название магазина *</label>
            <input type="text" v-model="profileEditForm.shop_name" required>
          </div>
          
          <div class="form-group">
            <label>Телефон *</label>
            <input type="tel" v-model="profileEditForm.phone" required>
          </div>
          
          <div class="form-group">
            <label>Email *</label>
            <input type="email" v-model="profileEditForm.email" required>
          </div>
          
          <div class="form-group">
            <label>Описание</label>
            <textarea v-model="profileEditForm.description" rows="4"></textarea>
          </div>
          
          <div class="form-group">
            <label>Аватар</label>
            <input type="file" accept="image/*" @change="handleProfileImageUpload">
            <p class="file-hint" v-if="profile?.avatar">
              Текущий аватар: {{ profile.avatar.split('/').pop() }}
            </p>
          </div>
          
          <div class="modal-actions">
            <button type="button" class="cancel-btn" @click="showProfileEditModal = false">
              Отмена
            </button>
            <button type="submit" class="submit-btn">
              Сохранить изменения
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.master-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.stats-btn {
  padding: 8px 16px;
  background: #C67B5C;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
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

.logout-btn:hover {
  background: #cc0000;
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
  border-radius: 4px 4px 0 0;
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

.empty {
  text-align: center;
  color: #666;
  padding: 40px;
}

.loading {
  text-align: center;
  color: #666;
  padding: 40px;
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
  transition: box-shadow 0.3s;
  background: #FFFBF7;
}

.product-item:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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

.product-info h3 {
  font-size: 16px;
  margin-bottom: 5px;
}

.price {
  font-weight: bold;
  color: #C67B5C;
}

.category {
  color: #666;
  font-size: 14px;
}

.product-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.edit-btn, .delete-btn {
  padding: 5px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.3s;
}

.edit-btn {
  background: #F5E9D7;
}

.edit-btn:hover {
  background: #E8DCC9;
}

.delete-btn {
  background: #fee;
  color: #ff4444;
}

.delete-btn:hover {
  background: #fdd;
}

.add-form {
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
  color: #333;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #E8DCC9;
  border-radius: 4px;
  font-size: 16px;
  font-family: inherit;
  background: #FFFBF7;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #C67B5C;
}

.form-group textarea {
  resize: vertical;
}

.submit-btn {
  padding: 12px 30px;
  background: #C67B5C;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
}

.submit-btn:hover {
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

.status-new { background: #e3f2fd; color: #1976d2; }
.status-processing { background: #fff3e0; color: #f57c00; }
.status-completed { background: #e8f5e8; color: #388e3c; }
.status-cancelled { background: #ffebee; color: #d32f2f; }

.order-date {
  color: #666;
  font-size: 14px;
}

.order-customer {
  margin-bottom: 15px;
  padding: 10px;
  background: white;
  border-radius: 4px;
}

.order-customer p {
  margin: 5px 0;
  color: #333;
}

.order-items {
  margin-bottom: 15px;
}

.order-items h4 {
  margin-bottom: 10px;
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
}

.order-status-control {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px dashed #E8DCC9;
  display: flex;
  align-items: center;
  gap: 10px;
}

.order-status-control label {
  font-weight: 500;
  color: #666;
}

.status-select {
  padding: 5px 10px;
  border: 1px solid #E8DCC9;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  background: #FFFBF7;
  transition: border-color 0.3s;
}

.status-select:hover {
  border-color: #C67B5C; 
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.edit-profile-btn {
  padding: 8px 16px;
  background: #C67B5C;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: background 0.3s;
}

.edit-profile-btn:hover {
  background: #B56A4D;
}

.profile-info {
  display: flex;
  gap: 40px;
  align-items: flex-start;
}

.avatar-section {
  flex-shrink: 0;
}

.avatar {
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, #C67B5C, #2C2C2C);
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 48px;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-avatar {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #C67B5C, #2C2C2C);
  color: white;
  font-size: 48px;
  font-weight: bold;
}

.info-details {
  flex: 1;
  background: #FFFBF7;
  border-radius: 12px;
  padding: 25px;
  border: 1px solid #E8DCC9;
}

.info-row {
  display: flex;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #E8DCC9;
}

.info-row:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.info-label {
  width: 180px;
  font-weight: 600;
  color: #555;
}

.info-value {
  flex: 1;
  color: #2C2C2C;
}

.file-hint {
  font-size: 12px;
  color: #666;
  margin-top: 5px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
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

.stats-preview {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.load-stats-btn {
  margin-top: 20px;
  padding: 12px 30px;
  background: #C67B5C;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
}

.load-stats-btn:hover {
  background: #B56A4D;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 25px;
  color: white;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.stat-card:nth-child(2) {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-card:nth-child(3) {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon {
  font-size: 48px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.stats-section {
  margin-bottom: 30px;
  background: #FFFBF7;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #E8DCC9;
}

.stats-section h3 {
  margin-bottom: 20px;
  color: #2C2C2C;
}

.stats-table {
  width: 100%;
  border-collapse: collapse;
}

.stats-table th {
  text-align: left;
  padding: 12px;
  background: #F5E9D7;
  color: #2C2C2C;
  font-weight: 600;
}

.stats-table td {
  padding: 10px 12px;
  border-bottom: 1px solid #E8DCC9;
}

.stats-table tr:last-child td {
  border-bottom: none;
}

.stats-table tr:hover td {
  background: #F5E9D7;
}
</style>