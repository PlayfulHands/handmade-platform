<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { onMounted } from 'vue'

const cartStore = useCartStore()
const authStore = useAuthStore()

onMounted(() => {
  authStore.fetchCurrentUser()
})
</script>

<template>
  <div id="app">
    <header>
      <nav>
        <div class="nav-left">
          <RouterLink to="/">Главная</RouterLink>
          <RouterLink to="/feed">Лента</RouterLink>
        </div>
        <div class="nav-right">
          <RouterLink v-if="authStore.isAuthenticated" to="/wishlist" class="nav-link">❤️ Избранное</RouterLink>
          <RouterLink to="/cart" class="cart-link">🛒 Корзина<span v-if="cartStore.totalItems > 0" class="cart-badge">{{ cartStore.totalItems }}</span></RouterLink>
          
          <RouterLink v-if="!authStore.isAuthenticated" to="/login" class="nav-link">👤 Вход</RouterLink>
          <RouterLink v-else-if="authStore.masterId" to="/master/dashboard" class="nav-link master-link">🔨 Кабинет мастера</RouterLink>
          <RouterLink v-else to="/account" class="nav-link">👤 Кабинет</RouterLink>
        </div>
      </nav>
    </header>
    <main><RouterView /></main>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  /* Градиентный фон (запасной вариант) */
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
  /* Если хотите изображение с размытием – раскомментируйте и замените URL */
  /* background-image: url('/path/to/your-image.jpg'); */
  /* background-size: cover; */
  /* background-position: center; */
  /* background-attachment: fixed; */
  color: #1e1e1e;
  line-height: 1.5;
  /* Для плавного скролла */
  scroll-behavior: smooth;
}

/* Псевдоэлемент для размытия, если используется изображение */
/* body::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: inherit;
  filter: blur(8px);
  z-index: -1;
} */

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  /* Полупрозрачный фон для читаемости текста поверх градиента/изображения */
  background-color: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(2px); /* лёгкое размытие фона под контентом, работает в современных браузерах */
}

header {
  background-color: #FFFACD; /*#42b883*/
  color: #2C2C2C; /*white*/
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

nav {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.nav-left, .nav-right {
  display: flex;
  gap: 20px;
  align-items: center;
  flex-wrap: wrap;
}

nav a {
  color: #2C2C2C; /*white*/
  text-decoration: none;
  font-size: 1rem;
  font-weight: 500;
  transition: opacity 0.3s, background-color 0.2s;
  white-space: nowrap;
}

nav a:hover {
  opacity: 0.8;
  color: #1a1a1a; /*Добавил*/
}

.cart-link {
  position: relative;
}

.cart-badge {
  position: absolute;
  top: -8px;
  right: -12px;
  background: #D32F2F;/*#ff4444*/
  color: white;
  font-size: 12px;
  font-weight: bold;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 20px;
  text-align: center;
}

.nav-link {
  padding: 5px 10px;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.05); /*255,255,255,0.1*/
}

.nav-link:hover {
  background: rgba(0, 0, 0, 0.1); /*0, 0, 0, 0.1*/
}

.master-link {
  background: rgba(0, 0, 0, 0.1); /*255,255,255,0.2*/
}

main {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding: 20px;
}

/* Адаптивность для мобильных устройств */
@media (max-width: 768px) {
  nav {
    flex-direction: column;
    gap: 10px;
  }
  .nav-left, .nav-right {
    justify-content: center;
  }
  main {
    padding: 15px;
  }
}

/* Улучшенная читаемость ссылок на тёмном фоне (если фон тёмный) */
@media (prefers-color-scheme: dark) {
  body {
    background: linear-gradient(135deg, #1a2a3a, #0f1a24);
  }
  #app {
    background-color: rgba(0, 0, 0, 0.7);
  }
  .post-card, .product-card, .tab-content, .order-card, .review-card {
    background-color: rgba(30, 30, 30, 0.9);
    color: #eee;
  }
}
</style>