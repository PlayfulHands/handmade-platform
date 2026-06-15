<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { useFollowStore } from '@/stores/follow'
import { useCartStore } from '@/stores/cart'
import { useChatStore } from '@/stores/chat'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const followStore = useFollowStore()
const cartStore = useCartStore()
const chatStore = useChatStore()

const master = ref(null)
const products = ref([])
const posts = ref([])
const categories = ref([])
const reviews = ref([])
const loading = ref(true)
const activeTab = ref('products')
const selectedCategory = ref(null)

// Фильтрованные товары по категории
const filteredProducts = computed(() => {
  if (!selectedCategory.value) return products.value
  return products.value.filter(p => p.category?.id === selectedCategory.value)
})

onMounted(async () => {
  try {
    const masterId = route.params.id
    
    const [masterRes, productsRes, postsRes, categoriesRes, reviewsRes] = await Promise.all([
      axios.get(`http://127.0.0.1:8000/api/masters/${masterId}/`),
      axios.get(`http://127.0.0.1:8000/api/products/?master=${masterId}`),
      axios.get(`http://127.0.0.1:8000/api/posts/master/${masterId}/`),
      axios.get('http://127.0.0.1:8000/api/categories/'),
      axios.get(`http://127.0.0.1:8000/api/reviews/?master=${masterId}`).catch(() => ({ data: [] }))
    ])
    
    master.value = masterRes.data
    products.value = productsRes.data
    posts.value = postsRes.data
    categories.value = categoriesRes.data
    reviews.value = reviewsRes.data || []
  } catch (error) {
    console.error('Ошибка загрузки профиля мастера:', error)
  } finally {
    loading.value = false
  }
})

const toggleFollow = async () => {
  if (!master.value) return
  await followStore.toggle(master.value.id)
}

const addToCart = (product) => {
  cartStore.addItem({
    id: product.id,
    name: product.name,
    price: product.price,
    image: product.image
  })
  alert('✅ Товар добавлен в корзину!')
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', { 
    day: 'numeric', 
    month: 'long', 
    year: 'numeric' 
  })
}

const startChat = async () => {
  if (!master.value) return
  const roomId = await chatStore.createRoomWithMaster(master.value.id)
  if (roomId) {
    router.push('/account?tab=chats')
  }
}
</script>

<template>
  <div class="container">
    <div v-if="loading" class="loading">Загрузка...</div>
    
    <div v-else-if="master" class="master-profile">
      <!-- Обложка -->
      <div class="cover">
        <img v-if="master.cover" :src="master.cover" :alt="master.shop_name">
        <div v-else class="cover-placeholder"></div>
      </div>
      
      <!-- Информация о мастере -->
      <div class="profile-header">
        <div class="avatar">
          <img v-if="master.avatar" :src="master.avatar" :alt="master.shop_name">
          <div v-else class="avatar-placeholder">{{ master.shop_name?.[0] }}</div>
        </div>
        
        <div class="info">
          <h1>{{ master.shop_name }}</h1>
          
          <!-- Блок «О мастере» – расширенное описание -->
          <div class="about-master">
            <h2>О мастере</h2>
            <p>{{ master.description || 'Мастер ручной работы' }}</p>
          </div>
          
          <!-- Кнопки действий -->
          <div class="actions">
            <button 
              v-if="authStore.isAuthenticated && authStore.masterId !== master.id" 
              class="follow-btn" 
              :class="{ following: followStore.isFollowing(master.id) }"
              @click="toggleFollow"
            >
              {{ followStore.isFollowing(master.id) ? '✓ Подписан' : '+ Подписаться' }}
            </button>
            <button 
              v-if="authStore.isAuthenticated && authStore.masterId !== master.id" 
              class="message-btn"
              @click="startChat"
            >
              💬 Написать сообщение
            </button>
          </div>
        </div>
        
        <!-- Блок статистики (правый) -->
        <div class="stats-block">
          <div class="stat">
            <span class="stat-value">{{ followStore.isFollowing(master.id) ? followStore.count : master.followers_count || 0 }}</span>
            <span class="stat-label">подписчиков</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ master.products_sold || 0 }}</span>
            <span class="stat-label">продано</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ master.rating?.toFixed(1) || '—' }}</span>
            <span class="stat-label">рейтинг</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ reviews.length }}</span>
            <span class="stat-label">отзывов</span>
          </div>
        </div>
      </div>
      
      <!-- Вкладки -->
      <div class="tabs">
        <button :class="{ active: activeTab === 'products' }" @click="activeTab = 'products'">
          Товары ({{ products.length }})
        </button>
        <button :class="{ active: activeTab === 'posts' }" @click="activeTab = 'posts'">
          Блог ({{ posts.length }})
        </button>
      </div>
      
      <!-- Товары -->
      <div v-if="activeTab === 'products'">
        <!-- Фильтр по категориям -->
        <div class="category-filter">
          <button 
            class="filter-tag" 
            :class="{ active: !selectedCategory }"
            @click="selectedCategory = null"
          >
            Все товары
          </button>
          <button 
            v-for="cat in categories" 
            :key="cat.id"
            class="filter-tag"
            :class="{ active: selectedCategory === cat.id }"
            @click="selectedCategory = cat.id"
          >
            {{ cat.name }}
          </button>
        </div>

        <div class="products-grid">
          <div v-for="product in filteredProducts" :key="product.id" class="product-card">
            <router-link :to="'/product/' + product.id">
              <div class="product-image">
                <img v-if="product.image" :src="product.image" :alt="product.name">
                <div v-else class="no-image">Нет фото</div>
              </div>
              <div class="product-info">
                <h3>{{ product.name }}</h3>
                <p class="price">{{ product.price }} ₽</p>
              </div>
            </router-link>
            <button class="add-to-cart-btn" @click="addToCart(product)">В корзину</button>
          </div>
          <div v-if="filteredProducts.length === 0" class="empty">Нет товаров в этой категории</div>
        </div>
      </div>
      
      <!-- Блог (публикации) -->
      <div v-if="activeTab === 'posts'" class="posts-list">
        <div v-for="post in posts" :key="post.id" class="post-card">
          <div class="post-header">
            <span class="post-date">{{ formatDate(post.created_at) }}</span>
          </div>
          <h3>{{ post.title }}</h3>
          <p>{{ post.content }}</p>
          <div v-if="post.image" class="post-image">
            <img :src="post.image" :alt="post.title">
          </div>
          <div class="post-stats">
            <span>👁️ {{ post.views_count }}</span>
            <span>❤️ {{ post.likes_count }}</span>
            <span>💬 {{ post.comments_count }}</span>
          </div>
        </div>
        <div v-if="posts.length === 0" class="empty">У мастера пока нет публикаций</div>
      </div>

      <!-- Отзывы -->
      <div v-if="reviews.length" class="reviews-section">
        <h2>Отзывы покупателей</h2>
        <div class="reviews-list">
          <div v-for="review in reviews" :key="review.id" class="review-card">
            <div class="review-header">
              <strong>{{ review.user_name }}</strong>
              <span class="review-rating">⭐ {{ review.rating }}</span>
            </div>
            <p>{{ review.comment }}</p>
            <span class="review-date">{{ formatDate(review.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="empty">Мастер не найден</div>
  </div>
</template>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.loading, .empty {
  text-align: center;
  padding: 60px;
  background: #FFFBF7; /* был white, стал тёплый бежевый */
  border: 1px solid #E8DCC9; /* новая граница для гармонии */
  border-radius: 8px;
  color: #666;
}

/* Обложка */
.cover {
  height: 200px;
  background: linear-gradient(135deg, #C67B5C, #2C2C2C); /* был #42b883 и #2c3e50, стал терракотовый градиент */
  border-radius: 12px 12px 0 0;
  overflow: hidden;
}

.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #C67B5C, #2C2C2C); /* был #42b883 и #2c3e50 */
}

/* Профиль */
.profile-header {
  display: flex;
  gap: 30px;
  padding: 0 30px 30px 30px;
  margin-top: -60px;
  position: relative;
  z-index: 1;
  flex-wrap: wrap;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid white;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  flex-shrink: 0;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #C67B5C; /* был #42b883 (зелёный) */
  color: white;
  font-size: 48px;
  font-weight: bold;
}

.info {
  flex: 2;
  padding-top: 20px;
}

.info h1 {
  font-size: 28px;
  margin-bottom: 8px;
  color: #2C2C2C; /* был #333, стал чуть темнее для контраста */
}

.about-master {
  margin: 15px 0;
  padding: 12px 0;
  border-bottom: 1px solid #E8DCC9; /* был #eee (серый), стал тёплый бежевый */
}
.about-master h2 {
  font-size: 18px;
  margin-bottom: 8px;
  color: #C67B5C; /* был #42b883 (зелёный) */
}
.about-master p {
  color: #555;
  line-height: 1.5;
}

.actions {
  display: flex;
  gap: 15px;
  margin-top: 10px;
}

/* Блок статистики */
.stats-block {
  display: flex;
  gap: 25px;
  background: white;
  padding: 12px 25px;
  border-radius: 40px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  align-self: center;
  margin-left: auto;
}
.stat {
  text-align: center;
}
.stat-value {
  display: block;
  font-size: 20px;
  font-weight: bold;
  color: #C67B5C; /* был #42b883 (зелёный) */
}
.stat-label {
  font-size: 12px;
  color: #666;
}

/* Кнопки */
.follow-btn, .message-btn {
  padding: 8px 24px;
  border-radius: 30px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}
.follow-btn {
  background: #C67B5C; /* был #42b883 (зелёный) */
  color: white;
  border: none;
}
.follow-btn.following {
  background: #F5E9D7; /* был #f0f0f0 (холодный), стал тёплый бежевый */
  color: #666;
}
.message-btn {
  background: white;
  color: #C67B5C; /* был #42b883 (зелёный) */
  border: 1px solid #C67B5C; /* был #42b883 (зелёный) */
}
.message-btn:hover {
  background: #C67B5C; /* был #42b883 (зелёный) */
  color: white;
}

/* Вкладки */
.tabs {
  display: flex;
  gap: 20px;
  margin: 30px 0;
  border-bottom: 2px solid #E8DCC9; /* был #eee (серый), стал тёплый бежевый */
}
.tabs button {
  padding: 10px 20px;
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #666;
}
.tabs button.active {
  color: #C67B5C; /* был #42b883 (зелёный) */
  font-weight: bold;
  border-bottom: 3px solid #C67B5C; /* был #42b883 (зелёный) */
}

/* Фильтр категорий */
.category-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
}
.filter-tag {
  background: #F5E9D7; /* был #f0f0f0 (холодный), стал тёплый бежевый */
  padding: 6px 16px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}
.filter-tag.active {
  background: #C67B5C; /* был #42b883 (зелёный) */
  color: white;
}
.filter-tag:hover {
  background: #C67B5C; /* был #42b883 (зелёный) */
  color: white;
}

/* Товары */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}
.product-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.3s;
}
.product-card:hover {
  transform: translateY(-4px);
}
.product-card a {
  text-decoration: none;
  color: inherit;
}
.product-image {
  height: 200px;
  overflow: hidden;
}
.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.no-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FFFBF7; /* был #f5f5f5 (холодный), стал тёплый бежевый */
  color: #999;
}
.product-info {
  padding: 12px;
}
.product-info h3 {
  font-size: 16px;
  margin-bottom: 5px;
}
.price {
  font-weight: bold;
  color: #C67B5C; /* был #42b883 (зелёный) */
}
.add-to-cart-btn {
  width: 100%;
  padding: 10px;
  background: #C67B5C; /* был #42b883 (зелёный) */
  color: white;
  border: none;
  cursor: pointer;
  transition: background 0.3s;
}
.add-to-cart-btn:hover {
  background: #B56A4D; /* был #33a06f (тёмно-зелёный) */
}

/* Публикации */
.posts-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.post-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.post-header {
  margin-bottom: 10px;
  color: #666;
  font-size: 12px;
}
.post-card h3 {
  margin-bottom: 10px;
  color: #2C2C2C; /* был #333, стал чуть темнее */
}
.post-card p {
  color: #666;
  line-height: 1.5;
}
.post-image {
  margin: 15px 0;
  border-radius: 8px;
  overflow: hidden;
}
.post-image img {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
}
.post-stats {
  display: flex;
  gap: 15px;
  margin-top: 15px;
  padding-top: 10px;
  border-top: 1px solid #E8DCC9; /* был #eee (серый), стал тёплый бежевый */
  color: #666;
  font-size: 14px;
}

/* Отзывы */
.reviews-section {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #E8DCC9; /* был #eee (серый), стал тёплый бежевый */
}
.reviews-section h2 {
  margin-bottom: 20px;
  font-size: 1.4rem;
  color: #2C2C2C;
}
.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.review-card {
  background: #FFFBF7; /* был #f9f9f9 (холодный), стал тёплый бежевый */
  border-radius: 8px;
  padding: 15px;
  border: 1px solid #E8DCC9; /* новая граница для гармонии */
}
.review-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}
.review-rating {
  color: #D4A574; /* был #f5a623 (оранжевый), стал тёплый золотисто-бежевый для гармонии */
}
.review-date {
  font-size: 12px;
  color: #999;
}
</style>