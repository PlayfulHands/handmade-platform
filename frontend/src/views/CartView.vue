<script setup>
import { useCartStore } from '@/stores/cart'

const cartStore = useCartStore()

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(price)
}
</script>

<template>
  <div class="container">
    <h1>Корзина</h1>
    
    <div v-if="cartStore.items.length === 0" class="empty-cart">
      <p>Корзина пуста</p>
      <router-link to="/" class="continue-shopping">Продолжить покупки</router-link>
    </div>

    <div v-else class="cart-content">
      <div class="cart-items">
        <div v-for="item in cartStore.items" :key="item.id" class="cart-item">
          <div class="item-image">
            <img v-if="item.image" :src="item.image" :alt="item.name">
            <div v-else class="no-image">Нет фото</div>
          </div>
          
          <div class="item-info">
            <h3>{{ item.name }}</h3>
            <p class="item-price">{{ formatPrice(item.price) }}</p>
          </div>
          
          <div class="item-quantity">
            <button @click="cartStore.updateQuantity(item.id, item.quantity - 1)" class="quantity-btn">−</button>
            <span class="quantity">{{ item.quantity }}</span>
            <button @click="cartStore.updateQuantity(item.id, item.quantity + 1)" class="quantity-btn">+</button>
          </div>
          
          <div class="item-total">
            {{ formatPrice(item.price * item.quantity) }}
          </div>
          
          <button @click="cartStore.removeItem(item.id)" class="remove-btn">×</button>
        </div>
      </div>

      <div class="cart-summary">
        <h2>Итого</h2>
        <div class="summary-row">
          <span>Товаров:</span>
          <span>{{ cartStore.totalItems }} шт</span>
        </div>
        <div class="summary-row total">
          <span>Сумма:</span>
          <span>{{ formatPrice(cartStore.totalPrice) }}</span>
        </div>
        
        <router-link to="/checkout" class="checkout-btn">
          Оформить заказ
        </router-link>
        
        <button class="clear-btn" @click="cartStore.clearCart()">
          Очистить корзину
        </button>
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
  background: #C67B5C; /* был #42b883 (зелёный) */
  color: white;
  text-decoration: none;
  border-radius: 6px;
  transition: background 0.3s;
}

.continue-shopping:hover {
  background: #B56A4D; /* был #33a06f (тёмно-зелёный) */
}

.cart-content {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 30px;
  margin-top: 30px;
}

.cart-items {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 20px;
}

.cart-item {
  display: grid;
  grid-template-columns: 80px 1fr 120px 100px 30px;
  gap: 20px;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #E8DCC9; /* был #eee (серый), стал тёплый бежевый */
}

.cart-item:last-child {
  border-bottom: none;
}

.item-image {
  width: 80px;
  height: 80px;
  background: #f9f9f9;
  border-radius: 4px;
  overflow: hidden;
}

.item-image img {
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

.item-info h3 {
  font-size: 16px;
  margin-bottom: 5px;
}

.item-price {
  color: #666;
  font-size: 14px;
}

.item-quantity {
  display: flex;
  align-items: center;
  gap: 10px;
}

.quantity-btn {
  width: 30px;
  height: 30px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 18px;
}

.quantity-btn:hover {
  background: #f5f5f5;
}

.quantity {
  min-width: 30px;
  text-align: center;
}

.item-total {
  font-weight: bold;
  color: #2C2C2C; /* был #2c3e50 (холодный синий), стал нейтрально-чёрный */
}

.remove-btn {
  width: 30px;
  height: 30px;
  border: none;
  background: none;
  color: #999;
  font-size: 20px;
  cursor: pointer;
}

.remove-btn:hover {
  color: #ff4444;
}

.cart-summary {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 20px;
  height: fit-content;
}

.cart-summary h2 {
  margin-bottom: 20px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
}

.summary-row.total {
  font-size: 18px;
  font-weight: bold;
  border-top: 2px solid #E8DCC9; /* был #eee (серый), стал тёплый бежевый */
  margin-top: 10px;
  padding-top: 20px;
}

.checkout-btn {
  display: block;
  width: 100%;
  padding: 12px;
  background: #C67B5C; /* был #42b883 (зелёный) */
  color: white;
  text-decoration: none;
  text-align: center;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 10px;
  transition: background 0.3s;
}

.checkout-btn:hover {
  background: #B56A4D; /* был #33a06f (тёмно-зелёный) */
}

.clear-btn {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 10px;
  background: #f5f5f5;
  color: #666;
  transition: background 0.3s;
}

.clear-btn:hover {
  background: #e0e0e0;
}
</style>