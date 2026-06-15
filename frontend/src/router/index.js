import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ProductView from '../views/ProductView.vue'
import CartView from '../views/CartView.vue'
import CheckoutView from '../views/CheckoutView.vue'
import OrderSuccessView from '../views/OrderSuccessView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import FeedView from '../views/FeedView.vue'
import WishlistView from '../views/WishlistView.vue'
import CustomerDashboard from '../views/CustomerDashboard.vue'
import MasterDashboard from '../views/MasterDashboard.vue'
import MasterProfile from '../views/MasterProfile.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/product/:id', name: 'product', component: ProductView },
    { path: '/cart', name: 'cart', component: CartView },
    { path: '/checkout', name: 'checkout', component: CheckoutView },
    { path: '/order-success/:id', name: 'order-success', component: OrderSuccessView },
    { path: '/feed', name: 'feed', component: FeedView },
    { path: '/master/:id', name: 'master-profile', component: MasterProfile },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/register', name: 'register', component: RegisterView },
    
    { path: '/wishlist', name: 'wishlist', component: WishlistView, meta: { requiresAuth: true } },
    { path: '/account', name: 'customer-dashboard', component: CustomerDashboard, meta: { requiresAuth: true } },
    { path: '/master/dashboard', name: 'master-dashboard', component: MasterDashboard, meta: { requiresAuth: true } },
  ]
})

// Защита маршрутов
router.beforeEach(async (to, from) => {
  const authStore = useAuthStore()
  
  await authStore.fetchCurrentUser()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return '/login'
  }
  
  return true
})

export default router