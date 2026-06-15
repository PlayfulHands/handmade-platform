<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { useFollowStore } from '@/stores/follow'
import { useWishlistStore } from '@/stores/wishlist'
import { useChatStore } from '@/stores/chat'

const route = useRoute()
const router = useRouter()

const authStore = useAuthStore()
const followStore = useFollowStore()
const wishlistStore = useWishlistStore()
const chatStore = useChatStore()

// Данные
const orders = ref([])
const loadingOrders = ref(true)
const activeTab = ref('orders')
const newMessageText = ref('')

// Профиль (пользователь)
const profile = ref({
    first_name: '',
    last_name: '',
    email: ''
})
const profileLoading = ref(false)

// Адреса
const addresses = ref([])
const addressesLoading = ref(false)
const showAddressForm = ref(false)
const editingAddress = ref(null)
const addressForm = reactive({
    title: '',
    address_line: '',
    city: '',
    postal_code: '',
    is_default: false
})

// Уведомления
const notificationSettings = ref({
    email_notifications: true,
    sms_notifications: false,
    order_updates: true,
    promotions: false
})
const notifLoading = ref(false)

// Загрузка данных
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

const loadProfile = async () => {
    if (!authStore.user) return
    profile.value = {
        first_name: authStore.user.first_name || '',
        last_name: authStore.user.last_name || '',
        email: authStore.user.email || ''
    }
}

const updateProfile = async () => {
    profileLoading.value = true
    try {
        const response = await axios.patch('http://127.0.0.1:8000/api/auth/me/', {
            first_name: profile.value.first_name,
            last_name: profile.value.last_name,
            email: profile.value.email
        })
        authStore.user = response.data.user
        alert('Профиль обновлён')
    } catch (error) {
        console.error('Ошибка обновления профиля:', error)
        alert('Ошибка при обновлении')
    } finally {
        profileLoading.value = false
    }
}

const loadAddresses = async () => {
    addressesLoading.value = true
    try {
        const response = await axios.get('http://127.0.0.1:8000/api/addresses/')
        addresses.value = response.data
    } catch (error) {
        console.error('Ошибка загрузки адресов:', error)
    } finally {
        addressesLoading.value = false
    }
}

const saveAddress = async () => {
    try {
        let url = 'http://127.0.0.1:8000/api/addresses/'
        let method = 'post'
        if (editingAddress.value) {
            url += `${editingAddress.value.id}/`
            method = 'put'
        }
        const response = await axios[method](url, addressForm)
        if (method === 'post') {
            addresses.value.push(response.data)
        } else {
            const index = addresses.value.findIndex(a => a.id === editingAddress.value.id)
            if (index !== -1) addresses.value[index] = response.data
        }
        closeAddressForm()
    } catch (error) {
        console.error('Ошибка сохранения адреса:', error)
        alert('Ошибка')
    }
}

const deleteAddress = async (id) => {
    if (!confirm('Удалить адрес?')) return
    try {
        await axios.delete(`http://127.0.0.1:8000/api/addresses/${id}/`)
        addresses.value = addresses.value.filter(a => a.id !== id)
    } catch (error) {
        console.error('Ошибка удаления:', error)
    }
}

const setDefaultAddress = async (id) => {
    try {
        await axios.post(`http://127.0.0.1:8000/api/addresses/${id}/set-default/`)
        await loadAddresses()
    } catch (error) {
        console.error('Ошибка установки адреса по умолчанию:', error)
    }
}

const editAddress = (address) => {
    editingAddress.value = address
    Object.assign(addressForm, address)
    showAddressForm.value = true
}

const closeAddressForm = () => {
    showAddressForm.value = false
    editingAddress.value = null
    addressForm.title = ''
    addressForm.address_line = ''
    addressForm.city = ''
    addressForm.postal_code = ''
    addressForm.is_default = false
}

const loadNotificationSettings = async () => {
    notifLoading.value = true
    try {
        const response = await axios.get('http://127.0.0.1:8000/api/notification-settings/my/')
        notificationSettings.value = response.data
    } catch (error) {
        console.error('Ошибка загрузки настроек уведомлений:', error)
    } finally {
        notifLoading.value = false
    }
}

const updateNotificationSettings = async () => {
    notifLoading.value = true
    try {
        const response = await axios.put('http://127.0.0.1:8000/api/notification-settings/my/', notificationSettings.value)
        notificationSettings.value = response.data
        alert('Настройки сохранены')
    } catch (error) {
        console.error('Ошибка сохранения настроек:', error)
        alert('Ошибка')
    } finally {
        notifLoading.value = false
    }
}

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

// Чаты
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

const logout = () => {
    authStore.logout()
}

onMounted(async () => {
    await loadOrders()
    await followStore.loadFollowing()
    await wishlistStore.loadWishlist()
    await chatStore.loadRooms()
    await loadProfile()
    await loadAddresses()
    await loadNotificationSettings()

    if (route.query.tab === 'chats') {
        activeTab.value = 'chats'
    }
})
</script>

<template>
    <div class="container">
        <div class="page-header">
            <h1>Личный кабинет</h1>
            <button class="logout-btn" @click="logout">🚪 Выйти</button>
        </div>

        <div class="tabs">
            <button :class="{ active: activeTab === 'orders' }" @click="activeTab = 'orders'">📦 Мои заказы ({{ orders.length }})</button>
            <button :class="{ active: activeTab === 'following' }" @click="activeTab = 'following'">👥 Подписки ({{ followStore.count }})</button>
            <button :class="{ active: activeTab === 'wishlist' }" @click="activeTab = 'wishlist'">❤️ Избранное ({{ wishlistStore.count }})</button>
            <button :class="{ active: activeTab === 'chats' }" @click="activeTab = 'chats'">💬 Чаты ({{ chatStore.rooms.length }})</button>
            <button :class="{ active: activeTab === 'settings' }" @click="activeTab = 'settings'">⚙️ Настройки</button>
        </div>

        <!-- Заказы -->
        <div v-if="activeTab === 'orders'" class="tab-content">
            <div v-if="loadingOrders" class="loading">Загрузка...</div>
            <div v-else-if="orders.length === 0" class="empty">
                <p>У вас пока нет заказов</p>
                <router-link to="/" class="continue-btn">Перейти к покупкам</router-link>
            </div>
            <div v-else class="orders-list">
                <div v-for="order in orders" :key="order.id" class="order-card">
                    <div class="order-header">
                        <span class="order-number">Заказ #{{ order.id }}</span>
                        <span class="order-status" :class="'status-' + order.status">{{ getStatusText(order.status) }}</span>
                        <span class="order-date">{{ formatDate(order.created_at) }}</span>
                    </div>
                    <div class="order-items">
                        <div v-for="item in order.items" :key="item.id" class="order-item">
                            <span>{{ item.product_name }}</span>
                            <span>{{ item.quantity }} шт × {{ item.product_price }} ₽</span>
                            <span class="item-total">{{ item.quantity * item.product_price }} ₽</span>
                        </div>
                    </div>
                    <div class="order-total"><strong>Общая сумма: {{ order.total_price }} ₽</strong></div>
                </div>
            </div>
        </div>

        <!-- Подписки -->
        <div v-if="activeTab === 'following'" class="tab-content">
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
                        <h3><router-link :to="'/master/' + follow.master.id">{{ follow.master.shop_name }}</router-link></h3>
                        <p>{{ follow.master.description?.slice(0, 60) }}...</p>
                    </div>
                    <button class="unfollow-btn" @click="followStore.toggle(follow.master.id)">Отписаться</button>
                </div>
            </div>
        </div>

        <!-- Избранное -->
        <div v-if="activeTab === 'wishlist'" class="tab-content">
            <div v-if="wishlistStore.loading" class="loading">Загрузка...</div>
            <div v-else-if="wishlistStore.items.length === 0" class="empty">
                <p>У вас пока нет избранных товаров</p>
                <router-link to="/" class="continue-btn">Перейти к покупкам</router-link>
            </div>
            <div v-else class="wishlist-list">
                <div v-for="item in wishlistStore.items" :key="item.id" class="wishlist-item">
                    <div class="product-image" @click="router.push('/product/' + item.product.id)">
                        <img v-if="item.product.image" :src="item.product.image" :alt="item.product.name">
                        <div v-else class="no-image">Нет фото</div>
                    </div>
                    <div class="product-info">
                        <h3 @click="router.push('/product/' + item.product.id)">{{ item.product.name }}</h3>
                        <p class="price">{{ item.product.price }} ₽</p>
                    </div>
                    <button class="remove-btn" @click="wishlistStore.toggle(item.product.id)">🗑️ Удалить</button>
                </div>
                <router-link to="/wishlist" class="view-all">Посмотреть все →</router-link>
            </div>
        </div>

        <!-- Чаты -->
        <div v-if="activeTab === 'chats'" class="tab-content">
            <div class="chats-header">
                <h2>Чаты с мастерами</h2>
                <button class="refresh-rooms-btn" @click="refreshRooms" title="Обновить список чатов">🔄 Обновить список</button>
            </div>
            <div v-if="chatStore.loading" class="loading">Загрузка...</div>
            <div v-else-if="chatStore.rooms.length === 0" class="empty">
                <p>У вас пока нет чатов с мастерами</p>
                <router-link to="/" class="continue-btn">Начать покупки</router-link>
            </div>
            <div v-else class="chats-layout">
                <div class="rooms-list">
                    <div v-for="room in chatStore.rooms" :key="room.id"
                         :class="['room-item', { active: chatStore.currentRoom?.id === room.id }]"
                         @click="selectRoom(room)">
                        <div class="room-avatar">
                            <img v-if="room.master_avatar" :src="room.master_avatar" :alt="room.master_name">
                            <div v-else>{{ room.master_name?.[0] }}</div>
                        </div>
                        <div class="room-info">
                            <div class="room-name">{{ room.master_name }}</div>
                            <div class="room-last-message">{{ room.last_message?.text?.slice(0, 30) || 'Нет сообщений' }}</div>
                        </div>
                        <div v-if="room.unread_count > 0" class="unread-badge">{{ room.unread_count }}</div>
                    </div>
                </div>
                <div class="chat-window" v-if="chatStore.currentRoom">
                    <div class="chat-header">
                        <strong>{{ chatStore.currentRoom.master_name }}</strong>
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

        <!-- Настройки -->
        <div v-if="activeTab === 'settings'" class="tab-content">
            <h2>Настройки профиля</h2>

            <!-- Персональные данные -->
            <div class="settings-section">
                <h3>Личные данные</h3>
                <div class="form-group">
                    <label>Имя</label>
                    <input type="text" v-model="profile.first_name" placeholder="Имя">
                </div>
                <div class="form-group">
                    <label>Фамилия</label>
                    <input type="text" v-model="profile.last_name" placeholder="Фамилия">
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" v-model="profile.email" placeholder="Email">
                </div>
                <button class="save-btn" @click="updateProfile" :disabled="profileLoading">Сохранить</button>
            </div>

            <!-- Адреса доставки -->
            <div class="settings-section">
                <h3>Адреса доставки</h3>
                <button class="add-address-btn" @click="closeAddressForm(); showAddressForm = true">+ Добавить адрес</button>

                <div v-if="addressesLoading" class="loading">Загрузка...</div>
                <div v-else class="addresses-list">
                    <div v-for="addr in addresses" :key="addr.id" class="address-card">
                        <div class="address-info">
                            <div><strong>{{ addr.title || 'Адрес' }}</strong> {{ addr.is_default ? '(по умолчанию)' : '' }}</div>
                            <div>{{ addr.address_line }}, {{ addr.city }}</div>
                            <div v-if="addr.postal_code">Индекс: {{ addr.postal_code }}</div>
                        </div>
                        <div class="address-actions">
                            <button class="edit-btn" @click="editAddress(addr)">✏️</button>
                            <button class="delete-btn" @click="deleteAddress(addr.id)">🗑️</button>
                            <button v-if="!addr.is_default" class="default-btn" @click="setDefaultAddress(addr.id)">Сделать по умолчанию</button>
                        </div>
                    </div>
                </div>

                <!-- Форма добавления/редактирования адреса -->
                <div v-if="showAddressForm" class="address-form-modal">
                    <div class="modal-overlay" @click="closeAddressForm"></div>
                    <div class="modal-content">
                        <h3>{{ editingAddress ? 'Редактировать адрес' : 'Новый адрес' }}</h3>
                        <div class="form-group">
                            <label>Название (например, Дом, Работа)</label>
                            <input type="text" v-model="addressForm.title">
                        </div>
                        <div class="form-group">
                            <label>Адрес *</label>
                            <input type="text" v-model="addressForm.address_line" required>
                        </div>
                        <div class="form-group">
                            <label>Город *</label>
                            <input type="text" v-model="addressForm.city" required>
                        </div>
                        <div class="form-group">
                            <label>Почтовый индекс</label>
                            <input type="text" v-model="addressForm.postal_code">
                        </div>
                        <div class="form-group checkbox">
                            <label>
                                <input type="checkbox" v-model="addressForm.is_default"> Сделать адресом по умолчанию
                            </label>
                        </div>
                        <div class="modal-actions">
                            <button class="cancel-btn" @click="closeAddressForm">Отмена</button>
                            <button class="save-btn" @click="saveAddress">Сохранить</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Настройки уведомлений -->
            <div class="settings-section">
                <h3>Уведомления</h3>
                <div v-if="notifLoading" class="loading">Загрузка...</div>
                <div v-else>
                    <div class="checkbox">
                        <label>
                            <input type="checkbox" v-model="notificationSettings.email_notifications"> Email уведомления
                        </label>
                    </div>
                    <div class="checkbox">
                        <label>
                            <input type="checkbox" v-model="notificationSettings.sms_notifications"> SMS уведомления
                        </label>
                    </div>
                    <div class="checkbox">
                        <label>
                            <input type="checkbox" v-model="notificationSettings.order_updates"> Обновления заказов
                        </label>
                    </div>
                    <div class="checkbox">
                        <label>
                            <input type="checkbox" v-model="notificationSettings.promotions"> Акции и новости
                        </label>
                    </div>
                    <button class="save-btn" @click="updateNotificationSettings">Сохранить настройки</button>
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

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.logout-btn {
    background: #ff4444;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    transition: background 0.3s;
}
.logout-btn:hover {
    background: #cc0000;
}

.tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 30px;
    border-bottom: 2px solid #E8DCC9; /* был #eee (серый), стал тёплый бежевый */
    padding-bottom: 10px;
    flex-wrap: wrap;
    align-items: center;
}
.tabs button {
    padding: 10px 20px;
    background: none;
    border: none;
    font-size: 16px;
    cursor: pointer;
    color: #666;
    position: relative;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}
.tabs button.active {
    color: #C67B5C; /* был #42b883 (зелёный) */
    font-weight: bold;
    border-bottom: 3px solid #C67B5C; /* был #42b883 (зелёный) */
}

.tab-content {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    padding: 30px;
}

.loading, .empty {
    text-align: center;
    padding: 40px;
    color: #666;
}

.continue-btn {
    display: inline-block;
    margin-top: 20px;
    padding: 10px 20px;
    background: #C67B5C; /* был #42b883 (зелёный) */
    color: white;
    text-decoration: none;
    border-radius: 6px;
    transition: background 0.3s;
}
.continue-btn:hover {
    background: #B56A4D; /* был #33a06f (тёмно-зелёный) */
}

/* Заказы */
.orders-list {
    display: flex;
    flex-direction: column;
    gap: 20px;
}
.order-card {
    border: 1px solid #E8DCC9; /* был #eee (серый), стал тёплый бежевый */
    border-radius: 8px;
    padding: 20px;
    background: #FFFBF7; /* был #fafafa (холодный серый), стал тёплый бежевый */
}
.order-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 1px solid #E8DCC9; /* был #eee (серый), стал тёплый бежевый */
}
.order-number {
    font-weight: bold;
    font-size: 18px;
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
.order-item {
    display: flex;
    justify-content: space-between;
    padding: 5px 0;
    border-bottom: 1px dotted #E8DCC9; /* был #ddd (серый), стал тёплый бежевый */
}
.item-total {
    font-weight: bold;
    color: #C67B5C; /* был #42b883 (зелёный) */
}
.order-total {
    text-align: right;
    padding: 10px 0;
    border-top: 2px solid #E8DCC9; /* был #ddd (серый), стал тёплый бежевый */
    margin-top: 10px;
}

/* Подписки */
.following-list {
    display: grid;
    gap: 15px;
}
.following-item {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 15px;
    border: 1px solid #E8DCC9; /* был #eee (серый), стал тёплый бежевый */
    border-radius: 8px;
}
.master-avatar {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    overflow: hidden;
    background: #C67B5C; /* был #42b883 (зелёный) */
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
.master-info h3 a {
    text-decoration: none;
    color: #333;
}
.unfollow-btn {
    padding: 6px 12px;
    background: #fee;
    color: #ff4444;
    border: none;
    border-radius: 6px;
    cursor: pointer;
}

/* Избранное */
.wishlist-list {
    display: grid;
    gap: 15px;
}
.wishlist-item {
    display: grid;
    grid-template-columns: 80px 1fr auto;
    gap: 15px;
    align-items: center;
    padding: 15px;
    border: 1px solid #E8DCC9; /* был #eee (серый), стал тёплый бежевый */
    border-radius: 8px;
}
.product-image {
    width: 80px;
    height: 80px;
    background: #FFFBF7; /* был #f9f9f9 (холодный), стал тёплый бежевый */
    border-radius: 4px;
    overflow: hidden;
    cursor: pointer;
}
.product-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}
.product-info h3 {
    cursor: pointer;
}
.product-info h3:hover {
    color: #C67B5C; /* был #42b883 (зелёный) */
}
.price {
    font-weight: bold;
    color: #C67B5C; /* был #42b883 (зелёный) */
}
.remove-btn {
    padding: 6px 12px;
    background: #fee;
    color: #ff4444;
    border: none;
    border-radius: 6px;
    cursor: pointer;
}
.view-all {
    display: inline-block;
    margin-top: 20px;
    color: #C67B5C; /* был #42b883 (зелёный) */
    text-decoration: none;
}
.view-all:hover {
    color: #B56A4D; /* был #33a06f (тёмно-зелёный) */
}

/* Чаты */
.chats-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}
.refresh-rooms-btn {
    background: #f0f0f0;
    border: none;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
}
.refresh-rooms-btn:hover {
    background: #e0e0e0;
}
.chats-layout {
    display: grid;
    grid-template-columns: 300px 1fr;
    gap: 20px;
    height: 500px;
}
.rooms-list {
    background: #FFFBF7; /* был #f9f9f9 (холодный), стал тёплый бежевый */
    border-radius: 8px;
    overflow-y: auto;
}
.room-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    cursor: pointer;
    border-bottom: 1px solid #E8DCC9; /* был #eee (серый), стал тёплый бежевый */
    position: relative;
}
.room-item.active {
    background: #FFF3E6; /* был #e8f5e9 (зеленоватый), стал тёплый персиковый */
}
.room-avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: #C67B5C; /* был #42b883 (зелёный) */
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 20px;
    overflow: hidden;
}
.room-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
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
    border-bottom: 1px solid #E8DCC9; /* был #eee (серый), стал тёплый бежевый */
    background: #FFFBF7; /* был #f9f9f9 (холодный), стал тёплый бежевый */
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
}
.refresh-msg-btn:hover {
    background: #e0e0e0;
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
    background: #f0f0f0;
    align-self: flex-start;
}
.message.outgoing {
    background: #C67B5C; /* был #42b883 (зелёный) */
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
    border-top: 1px solid #E8DCC9; /* был #eee (серый), стал тёплый бежевый */
}
.chat-input input {
    flex: 1;
    padding: 8px;
    border: 1px solid #E8DCC9; /* был #ddd (серый), стал тёплый бежевый */
    border-radius: 20px;
    background: #FFFBF7; /* был white, стал тёплый бежевый */
}
.chat-input input:focus {
    outline: none;
    border-color: #C67B5C;
}
.chat-input button {
    background: #C67B5C; /* был #42b883 (зелёный) */
    border: none;
    border-radius: 50%;
    width: 36px;
    cursor: pointer;
}
.chat-input button:hover {
    background: #B56A4D; /* был #33a06f (тёмно-зелёный) */
}
.chat-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    background: white;
    border-radius: 8px;
    color: #999;
}

/* Настройки */
.settings-section {
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 1px solid #E8DCC9; /* был #eee (серый), стал тёплый бежевый */
}
.settings-section h3 {
    margin-bottom: 15px;
    font-size: 1.2rem;
}
.form-group {
    margin-bottom: 15px;
}
.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: 500;
}
.form-group input[type="text"],
.form-group input[type="email"],
.form-group input[type="checkbox"] {
    width: 100%;
    max-width: 400px;
    padding: 8px 12px;
    border: 1px solid #E8DCC9; /* был #ddd (серый), стал тёплый бежевый */
    border-radius: 6px;
    background: #FFFBF7; /* был white, стал тёплый бежевый */
}
.form-group input[type="text"]:focus,
.form-group input[type="email"]:focus {
    outline: none;
    border-color: #C67B5C;
}
.checkbox {
    margin: 10px 0;
}
.checkbox label {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
}
.save-btn {
    background: #C67B5C; /* был #42b883 (зелёный) */
    color: white;
    border: none;
    padding: 8px 20px;
    border-radius: 6px;
    cursor: pointer;
    margin-top: 10px;
    transition: background 0.3s;
}
.save-btn:hover:not(:disabled) {
    background: #B56A4D; /* был #33a06f (тёмно-зелёный) */
}
.save-btn:disabled {
    opacity: 0.5;
}
.add-address-btn {
    background: #C67B5C; /* был #42b883 (зелёный) */
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
    margin-bottom: 15px;
    transition: background 0.3s;
}
.add-address-btn:hover {
    background: #B56A4D; /* был #33a06f (тёмно-зелёный) */
}
.addresses-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}
.address-card {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #FFFBF7; /* был #f9f9f9 (холодный), стал тёплый бежевый */
    padding: 12px;
    border-radius: 8px;
    border: 1px solid #E8DCC9; /* был #eee (серый), стал тёплый бежевый */
}
.address-info {
    flex: 1;
}
.address-actions {
    display: flex;
    gap: 8px;
}
.address-actions button {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 16px;
    padding: 4px 8px;
    border-radius: 4px;
}
.edit-btn { background: #f0f0f0; }
.delete-btn { background: #fee; color: #ff4444; }
.default-btn { background: #e0e0e0; color: #333; }
.address-form-modal .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 1000;
}
.address-form-modal .modal-content {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 24px;
    border-radius: 12px;
    width: 90%;
    max-width: 500px;
    z-index: 1001;
    max-height: 80vh;
    overflow-y: auto;
}
.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
}
.cancel-btn {
    background: #f5f5f5;
    border: none;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
}
</style>