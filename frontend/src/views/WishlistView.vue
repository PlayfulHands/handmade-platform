<script setup>
import { onMounted } from 'vue'
import { useWishlistStore } from '@/stores/wishlist'
import { useRouter } from 'vue-router'

const wishlistStore = useWishlistStore()
const router = useRouter()

onMounted(() => {
  wishlistStore.loadWishlist()
})

const removeFromWishlist = async (productId) => {
  await wishlistStore.toggle(productId)
}
</script>

<template>
  <div class="container">
    <h1>Избранное</h1>
    
    <div v-if="wishlistStore.loading" class="loading">Загрузка...</div>
    
    <div v-else-if="wishlistStore.items.length === 0" class="empty">
      <p>У вас пока нет избранных товаров</p>
      <router-link to="/" class="continue-btn">Перейти к покупкам</router-link>
    </div>
    
    <div v-else class="wishlist-grid">
      <div v-for="item in wishlistStore.items" :key="item.id" class="wishlist-item">
        <div class="product-image" @click="router.push(`/product/${item.product.id}`)">
          <img v-if="item.product.image" :src="item.product.image" :alt="item.product.name">
          <div v-else class="no-image">Нет фото</div>
        </div>
        <div class="product-info">
          <h3 @click="router.push(`/product/${item.product.id}`)">{{ item.product.name }}</h3>
          <p class="price">{{ item.product.price }} ₽</p>
          <p class="category">Категория: {{ item.product.category?.name }}</p>
        </div>
        <div class="product-actions">
          <button class="remove-btn" @click="removeFromWishlist(item.product.id)">🗑️ Удалить</button>
          <button class="cart-btn" @click="router.push(`/product/${item.product.id}`)">🛒 В корзину</button>
        </div>
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

.loading, .empty {
  text-align: center;
  padding: 60px;
  background: #FFFBF7;
  border: 1px solid #E8DCC9;
  border-radius: 8px;
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

.wishlist-grid {
  display: grid;
  gap: 20px;
}

.wishlist-item {
  display: grid;
  grid-template-columns: 120px 1fr 200px;
  gap: 20px;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border: 1px solid #E8DCC9;
}

.product-image {
  width: 120px;
  height: 120px;
  background: #FFFBF7;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid #E8DCC9;
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
  color: #999;
  font-size: 12px;
}

.product-info h3 {
  font-size: 18px;
  margin-bottom: 8px;
  cursor: pointer;
  color: #2C2C2C;
}

.product-info h3:hover {
  color: #C67B5C;
}

.price {
  font-size: 20px;
  font-weight: bold;
  color: #C67B5C;
  margin-bottom: 5px;
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

.remove-btn, .cart-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}

.remove-btn {
  background: #FFF3E6;
  color: #C67B5C;
}

.remove-btn:hover {
  background: #FFE5D4;
}

.cart-btn {
  background: #C67B5C;
  color: white;
}

.cart-btn:hover {
  background: #B56A4D;
}
</style>