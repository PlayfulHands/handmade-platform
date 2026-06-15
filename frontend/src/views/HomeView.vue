<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import PostCard from '@/components/PostCard.vue'

const products = ref([])
const categories = ref([])
const posts = ref([])
const newMasters = ref([])
const trends = ref([])
const loading = ref(true)
const selectedCategory = ref(null)
const searchQuery = ref('')
const suggestions = ref([])
const showSuggestions = ref(false)
let searchDebounceTimer = null
let blurTimer = null
let isSearching = ref(false)

const filteredProducts = ref([])

const loadNewMasters = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/masters/')
    newMasters.value = response.data.slice(0, 6)
  } catch (error) {
    console.error('Ошибка загрузки новых мастеров:', error)
  }
}

const loadTrends = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/products/?ordering=-views_count')
    trends.value = response.data.slice(0, 6)
  } catch (error) {
    console.error('Ошибка загрузки трендов:', error)
  }
}

const fetchSuggestions = async (query) => {
  if (!query.trim()) {
    suggestions.value = []
    showSuggestions.value = false
    return
  }
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/products/?search=${encodeURIComponent(query)}`)
    suggestions.value = response.data.slice(0, 5)
    showSuggestions.value = suggestions.value.length > 0
  } catch (error) {
    console.error('Ошибка получения подсказок:', error)
  }
}

const performSearch = async () => {
  if (isSearching.value) return
  isSearching.value = true
  try {
    if (!searchQuery.value.trim()) {
      if (selectedCategory.value) {
        const response = await axios.get(`http://127.0.0.1:8000/api/products/?category=${selectedCategory.value}`)
        filteredProducts.value = response.data
      } else {
        filteredProducts.value = products.value
      }
      showSuggestions.value = false
      return
    }

    let url = `http://127.0.0.1:8000/api/products/?search=${encodeURIComponent(searchQuery.value)}`
    if (selectedCategory.value) {
      url += `&category=${selectedCategory.value}`
    }
    const response = await axios.get(url)
    filteredProducts.value = response.data
    showSuggestions.value = false
  } catch (error) {
    console.error('Ошибка поиска товаров:', error)
  } finally {
    isSearching.value = false
  }
}

const handleSearchInput = () => {
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
  searchDebounceTimer = setTimeout(() => {
    fetchSuggestions(searchQuery.value)
  }, 200)
}

const selectSuggestion = (suggestion) => {
  if (blurTimer) clearTimeout(blurTimer)
  searchQuery.value = suggestion.name
  performSearch()
  showSuggestions.value = false
}

const onBlur = () => {
  blurTimer = setTimeout(() => {
    showSuggestions.value = false
  }, 150)
}

const onFocus = () => {
  if (blurTimer) clearTimeout(blurTimer)
  if (searchQuery.value.trim()) {
    fetchSuggestions(searchQuery.value)
  }
}

const selectCategory = async (categoryId) => {
  if (selectedCategory.value === categoryId) {
    selectedCategory.value = null
    if (searchQuery.value.trim()) {
      await performSearch()
    } else {
      filteredProducts.value = products.value
    }
  } else {
    selectedCategory.value = categoryId
    if (searchQuery.value.trim()) {
      await performSearch()
    } else {
      const response = await axios.get(`http://127.0.0.1:8000/api/products/?category=${categoryId}`)
      filteredProducts.value = response.data
    }
  }
}

onMounted(async () => {
  try {
    const [productsRes, categoriesRes, postsRes] = await Promise.all([
      axios.get('http://127.0.0.1:8000/api/products/'),
      axios.get('http://127.0.0.1:8000/api/categories/'),
      axios.get('http://127.0.0.1:8000/api/posts/feed/')
    ])
    products.value = productsRes.data
    filteredProducts.value = productsRes.data
    categories.value = categoriesRes.data
    posts.value = postsRes.data.slice(0, 5) // последние 5 постов

    await Promise.all([loadNewMasters(), loadTrends()])
  } catch (error) {
    console.error('Ошибка загрузки:', error)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="container">
    <h1 class="page-title">Маркетплейс ручных изделий</h1>
    
    <!-- Поиск -->
    <div class="search-section">
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          @input="handleSearchInput"
          @focus="onFocus"
          @blur="onBlur"
          placeholder="Поиск товаров по названию или описанию..."
          class="search-input"
        />
        <button @click.prevent="performSearch" class="search-btn" :disabled="isSearching">🔍</button>
        <ul v-if="showSuggestions" class="suggestions-list">
          <li v-for="suggestion in suggestions" :key="suggestion.id" @mousedown.prevent="selectSuggestion(suggestion)">
            {{ suggestion.name }}
          </li>
        </ul>
      </div>
    </div>
    
    <div v-if="loading" class="loader">Загрузка...</div>
    
    <div v-else>
      <!-- Тренды -->
      <section class="trends-section">
        <h2 class="section-title">✨ Тренды сезона</h2>
        <div class="trends-grid">
          <div v-for="trend in trends" :key="trend.id" class="trend-card animate-fade-in">
            <router-link :to="'/product/' + trend.id">
              <img :src="trend.image || '/placeholder.png'" :alt="trend.name">
              <span>{{ trend.name }}</span>
            </router-link>
          </div>
        </div>
      </section>
      
      <!-- Категории -->
      <section class="categories-section">
        <h2 class="section-title">📂 Категории</h2>
        <div class="category-list">
          <button 
            class="category-tag" 
            :class="{ active: !selectedCategory }"
            @click="selectCategory(null)"
          >
            Все товары
          </button>
          <button 
            v-for="cat in categories" 
            :key="cat.id" 
            class="category-tag"
            :class="{ active: selectedCategory === cat.id }"
            @click="selectCategory(cat.id)"
          >
            {{ cat.name }}
          </button>
        </div>
      </section>
      
      <!-- Блок товаров -->
      <section class="products-section">
        <h2 class="section-title">🛍️ Популярные товары</h2>
        <div class="products-grid">
          <div v-for="product in filteredProducts" :key="product.id" class="product-card animate-fade-in">
            <router-link :to="'/product/' + product.id">
              <div class="product-image">
                <img v-if="product.image" :src="product.image" :alt="product.name">
                <div v-else class="no-image">Нет фото</div>
              </div>
              <div class="product-info">
                <h3>{{ product.name }}</h3>
                <p class="price">{{ product.price }} ₽</p>
                <p class="category">{{ product.category?.name }}</p>
              </div>
            </router-link>
          </div>
        </div>
        <div v-if="filteredProducts.length === 0" class="empty">Нет товаров</div>
      </section>
      
      <!-- Блок публикаций (лента) -->
      <section class="posts-section">
        <h2 class="section-title">📝 Лента мастеров</h2>
        <div v-if="posts.length === 0" class="empty">Пока нет публикаций</div>
        <div class="posts-grid">
          <PostCard v-for="post in posts" :key="post.id" :post="post" class="animate-fade-in" />
        </div>
      </section>
      
      <!-- Новые мастера -->
      <section class="masters-section">
        <h2 class="section-title">🌟 Новые мастера</h2>
        <div class="masters-grid">
          <div v-for="master in newMasters" :key="master.id" class="master-card animate-fade-in">
            <router-link :to="'/master/' + master.id">
              <div class="master-avatar">
                <img v-if="master.avatar" :src="master.avatar" :alt="master.shop_name">
                <div v-else class="avatar-placeholder">{{ master.shop_name?.[0] }}</div>
              </div>
              <h3>{{ master.shop_name }}</h3>
              <p class="master-bio">{{ master.description?.slice(0, 60) }}...</p>
            </router-link>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  text-align: center;
  margin-bottom: 30px;
  color: #2C2C2C; /* был #2c3e50 (холодный синий), стал нейтрально-чёрный */
  font-size: 2rem;
}

.section-title {
  font-size: 1.6rem;
  margin-bottom: 20px;
  color: #333;
  border-left: 4px solid #C67B5C; /* был #42b883 (зелёный) */
  padding-left: 15px;
}

/* Поиск */
.search-section {
  margin-bottom: 40px;
  display: flex;
  justify-content: center;
}
.search-box {
  position: relative;
  width: 100%;
  max-width: 600px;
}
.search-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #E8DCC9; /* был #ddd (серый), стал тёплый бежевый */
  border-radius: 30px;
  font-size: 16px;
  outline: none;
  transition: border-color 0.3s, box-shadow 0.3s;
  background: #FFFBF7; /* был white, стал тёплый бежевый */
}
.search-input:focus {
  border-color: #C67B5C; /* был #42b883 (зелёный) */
  box-shadow: 0 0 0 3px rgba(198, 123, 92, 0.2); /* был rgba(66, 184, 131, 0.2) */
}
.search-btn {
  position: absolute;
  right: 5px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
  padding: 8px 12px;
  border-radius: 30px;
  transition: color 0.2s;
}
.search-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.search-btn:hover:not(:disabled) {
  color: #C67B5C; /* был #42b883 (зелёный) */
}
.suggestions-list {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #FFFBF7; /* был white, стал тёплый бежевый */
  border: 1px solid #E8DCC9; /* был #ddd (серый), стал тёплый бежевый */
  border-radius: 12px;
  margin-top: 4px;
  padding: 0;
  list-style: none;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  max-height: 250px;
  overflow-y: auto;
}
.suggestions-list li {
  padding: 10px 16px;
  cursor: pointer;
  transition: background 0.2s;
}
.suggestions-list li:hover {
  background: #F5E9D7; /* был #f0f0f0 (холодный), стал тёплый бежевый */
}

/* Тренды */
.trends-section {
  margin-bottom: 50px;
}
.trends-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 20px;
}
.trend-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}
.trend-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 20px rgba(0,0,0,0.15);
}
.trend-card a {
  text-decoration: none;
  color: inherit;
}
.trend-card img {
  width: 100%;
  height: 120px;
  object-fit: cover;
  transition: transform 0.3s;
}
.trend-card:hover img {
  transform: scale(1.05);
}
.trend-card span {
  display: block;
  padding: 12px;
  text-align: center;
  font-weight: 500;
  background: white;
}

/* Категории */
.categories-section {
  margin-bottom: 50px;
}
.category-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.category-tag {
  background: #F5E9D7; /* был #f0f0f0 (холодный), стал тёплый бежевый */
  padding: 8px 20px;
  border: none;
  border-radius: 30px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  color: #333;
}
.category-tag:hover {
  background: #C67B5C; /* был #42b883 (зелёный) */
  color: white;
  transform: translateY(-2px);
}
.category-tag.active {
  background: #C67B5C; /* был #42b883 (зелёный) */
  color: white;
  box-shadow: 0 2px 6px rgba(198, 123, 92, 0.3); /* был rgba(66,184,131,0.3) */
}

/* Товары – красивая сетка */
.products-section {
  margin-bottom: 60px;
}
.products-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

@media (max-width: 1024px) {
  .products-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
@media (max-width: 768px) {
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 480px) {
  .products-grid {
    grid-template-columns: 1fr;
  }
}

.product-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}
.product-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 20px rgba(0,0,0,0.15);
}
.product-card a {
  text-decoration: none;
  color: inherit;
}
.product-image {
  height: 200px;
  overflow: hidden;
  position: relative;
}
.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s;
}
.product-card:hover .product-image img {
  transform: scale(1.05);
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
  padding: 16px;
}
.product-info h3 {
  font-size: 18px;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.price {
  font-weight: bold;
  color: #C67B5C; /* был #42b883 (зелёный) */
  margin-bottom: 6px;
  font-size: 18px;
}
.category {
  color: #666;
  font-size: 13px;
}

/* Публикации – вертикальный список по одному */
.posts-section {
  margin-bottom: 60px;
}
.posts-grid {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Новые мастера */
.masters-section {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #E8DCC9; /* был #eee (серый), стал тёплый бежевый */
}
.masters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 24px;
}
.master-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}
.master-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 20px rgba(0,0,0,0.15);
}
.master-card a {
  text-decoration: none;
  color: inherit;
}
.master-avatar {
  width: 80px;
  height: 80px;
  margin: 0 auto 12px;
  border-radius: 50%;
  overflow: hidden;
  background: #C67B5C; /* был #42b883 (зелёный) */
  transition: transform 0.3s;
}
.master-card:hover .master-avatar {
  transform: scale(1.05);
}
.master-avatar img {
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
  font-size: 32px;
  font-weight: bold;
}
.master-card h3 {
  font-size: 18px;
  margin-bottom: 8px;
}
.master-bio {
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}

/* Анимации */
.animate-fade-in {
  animation: fadeInUp 0.5s ease-out;
}
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.loader {
  text-align: center;
  padding: 60px;
  font-size: 1.2rem;
  color: #666;
}

.empty {
  text-align: center;
  padding: 40px;
  background: #FFFBF7; /* был #f9f9f9 (холодный), стал тёплый бежевый */
  border: 1px solid #E8DCC9; /* новая граница для гармонии */
  border-radius: 12px;
  color: #666;
}
</style>