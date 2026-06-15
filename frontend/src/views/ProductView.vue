<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useCartStore } from '@/stores/cart'
import { useWishlistStore } from '@/stores/wishlist'

const route = useRoute()
const product = ref(null)
const loading = ref(true)
const cartStore = useCartStore()
const wishlistStore = useWishlistStore()
const mainImage = ref(null)
const selectedOption = ref({})
const otherProducts = ref([])
const relatedPosts = ref([])
const showImageModal = ref(false)
const modalImage = ref('')

// Галерея изображений (главное + дополнительные)
const galleryImages = computed(() => {
    if (!product.value) return []
    const images = product.value.images || []
    if (product.value.image) {
        return [product.value.image, ...images]
    }
    return images
})

// Инициализация выбранных опций
const initSelectedOptions = () => {
    if (product.value?.options && typeof product.value.options === 'object') {
        const opts = {}
        for (const [key, value] of Object.entries(product.value.options)) {
            if (Array.isArray(value) && value.length) {
                opts[key] = value[0]
            } else if (typeof value === 'object' && value.default) {
                opts[key] = value.default
            } else {
                opts[key] = ''
            }
        }
        selectedOption.value = opts
    } else {
        selectedOption.value = {}
    }
}

const addToCart = () => {
    if (product.value) {
        cartStore.addItem({
            id: product.value.id,
            name: product.value.name,
            price: product.value.price,
            image: product.value.image,
            customization: selectedOption.value
        })
        alert('✅ Товар добавлен в корзину!')
    }
}

const toggleWishlist = async () => {
    if (!product.value) return
    await wishlistStore.toggle(product.value.id)
}

const changeImage = (img) => {
    mainImage.value = img
}

const openImageModal = (img) => {
    modalImage.value = img
    showImageModal.value = true
}

const closeImageModal = () => {
    showImageModal.value = false
    modalImage.value = ''
}

const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    })
}

onMounted(async () => {
    try {
        const productId = route.params.id
        const response = await axios.get(`http://127.0.0.1:8000/api/products/${productId}/`)
        product.value = response.data
        mainImage.value = product.value.image
        initSelectedOptions()
        await wishlistStore.loadWishlist()

        // Загружаем другие товары этого мастера
        if (product.value.master?.id) {
            const masterRes = await axios.get(`http://127.0.0.1:8000/api/products/?master=${product.value.master.id}`)
            otherProducts.value = masterRes.data.filter(p => p.id !== product.value.id)
        }

        // Загружаем посты, связанные с этим товаром (история создания)
        try {
            const postsRes = await axios.get(`http://127.0.0.1:8000/api/posts/?product=${productId}`)
            relatedPosts.value = postsRes.data
        } catch (e) {
            console.warn('Нет постов для этого товара')
        }
    } catch (error) {
        console.error('Ошибка загрузки товара:', error)
    } finally {
        loading.value = false
    }
})
</script>

<template>
    <div class="container">
        <div v-if="loading" class="loading">Загрузка...</div>

        <div v-else-if="product" class="product-detail">
            <h1>{{ product.name }}</h1>

            <div class="product-info">
                <!-- Галерея изображений -->
                <div class="product-gallery">
                    <div class="main-image" @click="openImageModal(mainImage)">
                        <img :src="mainImage || product.image" :alt="product.name">
                    </div>
                    <div v-if="galleryImages.length > 1" class="thumbnails">
                        <div
                            v-for="(img, idx) in galleryImages"
                            :key="idx"
                            class="thumbnail"
                            :class="{ active: mainImage === img }"
                            @click="changeImage(img)"
                        >
                            <img :src="img" :alt="product.name">
                        </div>
                    </div>
                </div>

                <div class="product-meta">
                    <div class="price-row">
                        <p class="price">{{ product.price }} ₽</p>
                        <div class="button-group">
                            <button class="add-to-cart" @click="addToCart">
                                🛒 В корзину
                            </button>
                            <button
                                class="wishlist-btn"
                                :class="{ active: wishlistStore.isWishlisted(product.id) }"
                                @click="toggleWishlist"
                            >
                                {{ wishlistStore.isWishlisted(product.id) ? '❤️ В избранном' : '🤍 В избранное' }}
                            </button>
                        </div>
                    </div>
                    <p class="category">Категория: {{ product.category?.name }}</p>

                    <!-- Блок "Описание" -->
                    <div class="description">
                        <h2>Описание</h2>
                        <p>{{ product.description }}</p>
                    </div>

                    <!-- Опции кастомизации -->
                    <div v-if="product.options && Object.keys(product.options).length" class="customization">
                        <h2>Опции кастомизации</h2>
                        <div v-for="(option, key) in product.options" :key="key" class="option-group">
                            <label>{{ key }}:</label>
                            <!-- select -->
                            <select v-if="Array.isArray(option)" v-model="selectedOption[key]">
                                <option v-for="val in option" :key="val" :value="val">{{ val }}</option>
                            </select>
                            <!-- text input -->
                            <input v-else-if="option.type === 'text'" type="text" v-model="selectedOption[key]" :placeholder="option.placeholder || ''">
                            <!-- number input -->
                            <input v-else-if="option.type === 'number'" type="number" v-model="selectedOption[key]" :min="option.min" :max="option.max">
                            <!-- textarea -->
                            <textarea v-else-if="option.type === 'textarea'" v-model="selectedOption[key]" :placeholder="option.placeholder || ''" rows="2"></textarea>
                            <!-- просто строка -->
                            <span v-else class="simple-option">{{ option }}</span>
                        </div>
                    </div>

                    <!-- Блок "История создания" -->
                    <div v-if="relatedPosts.length" class="creation-story">
                        <h2>История создания</h2>
                        <div v-for="post in relatedPosts" :key="post.id" class="story-post">
                            <h3>{{ post.title }}</h3>
                            <p>{{ post.content }}</p>
                            <div v-if="post.image" class="story-image">
                                <img :src="post.image" :alt="post.title">
                            </div>
                            <div class="story-date">{{ formatDate(post.created_at) }}</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Блок отзывов -->
            <div class="reviews-section" v-if="product.reviews?.length || product.average_rating">
                <h2>Отзывы покупателей</h2>
                <div class="rating-summary" v-if="product.average_rating">
                    <span class="rating-stars">⭐ {{ product.average_rating.toFixed(1) }}</span>
                    <span class="rating-count">({{ product.reviews_count }} отзывов)</span>
                </div>
                <div class="reviews-list">
                    <div v-for="review in product.reviews" :key="review.id" class="review-card">
                        <div class="review-header">
                            <strong>{{ review.user_name }}</strong>
                            <span class="review-rating">⭐ {{ review.rating }}</span>
                        </div>
                        <p class="review-comment">{{ review.comment }}</p>
                        <span class="review-date">{{ new Date(review.created_at).toLocaleDateString('ru-RU') }}</span>
                    </div>
                </div>
            </div>

            <!-- Блок "Другие работы этого мастера" -->
            <div v-if="otherProducts.length" class="master-other-products">
                <h2>Другие работы мастера</h2>
                <div class="products-grid">
                    <div v-for="item in otherProducts.slice(0, 4)" :key="item.id" class="product-card">
                        <router-link :to="'/product/' + item.id">
                            <div class="card-image">
                                <img :src="item.image || '/placeholder.png'" :alt="item.name">
                            </div>
                            <div class="card-info">
                                <h3>{{ item.name }}</h3>
                                <p class="price">{{ item.price }} ₽</p>
                            </div>
                        </router-link>
                    </div>
                </div>
            </div>
        </div>

        <div v-else class="empty">Товар не найден</div>

        <!-- Модальное окно для полноэкранного просмотра фото -->
        <Teleport to="body">
            <div v-if="showImageModal" class="image-modal" @click="closeImageModal">
                <div class="modal-content" @click.stop>
                    <img :src="modalImage" alt="Full size">
                    <button class="close-modal" @click="closeImageModal">×</button>
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

.loading, .empty {
    text-align: center;
    padding: 60px;
    background: #FFFBF7;
    border: 1px solid #E8DCC9;
    border-radius: 8px;
    color: #666;
}

.product-detail {
    margin-top: 20px;
}

.product-info {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 40px;
    margin-top: 20px;
}

@media (max-width: 768px) {
    .product-info {
        grid-template-columns: 1fr;
        gap: 20px;
    }
}

/* Галерея */
.product-gallery {
    background: #FFFBF7;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #E8DCC9;
}

.main-image {
    width: 100%;
    height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    cursor: pointer;
}

.main-image img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    transition: transform 0.3s;
}

.main-image:hover img {
    transform: scale(1.02);
}

.thumbnails {
    display: flex;
    gap: 10px;
    margin-top: 15px;
    justify-content: center;
    flex-wrap: wrap;
}

.thumbnail {
    width: 60px;
    height: 60px;
    border-radius: 4px;
    overflow: hidden;
    cursor: pointer;
    border: 2px solid transparent;
    transition: all 0.3s;
}

.thumbnail.active {
    border-color: #C67B5C;
}

.thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.product-meta {
    padding: 0 20px;
}

.price-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 15px;
    margin-bottom: 10px;
}

.price {
    font-size: 32px;
    font-weight: bold;
    color: #C67B5C;
    margin: 0;
}

.button-group {
    display: flex;
    gap: 15px;
}

.add-to-cart, .wishlist-btn {
    padding: 10px 20px;
    font-size: 16px;
    border-radius: 30px;
    cursor: pointer;
    transition: all 0.3s;
}

.add-to-cart {
    background: #C67B5C;
    color: white;
    border: none;
}

.add-to-cart:hover {
    background: #B56A4D;
}

.wishlist-btn {
    background: #F5E9D7;
    color: #666;
    border: none;
}

.wishlist-btn.active {
    background: #FFF3E6;
    color: #C67B5C;
}

.wishlist-btn:hover {
    background: #E8DCC9;
}

.category {
    color: #666;
    font-size: 14px;
    margin-bottom: 20px;
}

.description, .customization, .creation-story {
    margin: 25px 0;
    padding-top: 20px;
    border-top: 1px solid #E8DCC9;
}

.description h2, .customization h2, .creation-story h2 {
    font-size: 20px;
    margin-bottom: 12px;
    color: #2C2C2C;
}

.description p {
    line-height: 1.6;
    color: #555;
}

/* Опции кастомизации */
.customization .option-group {
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 15px;
    flex-wrap: wrap;
}

.customization label {
    font-weight: 500;
    min-width: 100px;
    color: #2C2C2C;
}

.customization select, .customization input, .customization textarea {
    padding: 8px 12px;
    border: 1px solid #E8DCC9;
    border-radius: 6px;
    font-size: 14px;
    width: 250px;
    background: #FFFBF7;
    transition: border-color 0.3s;
}

.customization select:focus, .customization input:focus, .customization textarea:focus {
    outline: none;
    border-color: #C67B5C;
}

.customization textarea {
    width: 100%;
    max-width: 400px;
}

/* История создания */
.story-post {
    background: #FFFBF7;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 20px;
    border: 1px solid #E8DCC9;
}

.story-post h3 {
    margin-bottom: 10px;
    color: #C67B5C;
}

.story-post p {
    color: #555;
    line-height: 1.5;
}

.story-image {
    margin: 15px 0;
    border-radius: 8px;
    overflow: hidden;
}

.story-image img {
    width: 100%;
    max-height: 200px;
    object-fit: cover;
}

.story-date {
    font-size: 12px;
    color: #999;
    margin-top: 10px;
}

/* Отзывы */
.reviews-section {
    margin-top: 50px;
    padding-top: 30px;
    border-top: 1px solid #E8DCC9;
}

.reviews-section h2 {
    margin-bottom: 20px;
    color: #2C2C2C;
}

.rating-summary {
    margin-bottom: 20px;
    font-size: 18px;
}

.rating-stars {
    font-weight: bold;
    color: #D4A574;
}

.rating-count {
    color: #666;
    margin-left: 10px;
}

.reviews-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.review-card {
    background: #FFFBF7;
    border-radius: 8px;
    padding: 15px;
    border: 1px solid #E8DCC9;
}

.review-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
}

.review-rating {
    color: #D4A574;
}

.review-comment {
    color: #2C2C2C;
    margin-bottom: 8px;
}

.review-date {
    font-size: 12px;
    color: #999;
}

/* Другие работы мастера */
.master-other-products {
    margin-top: 50px;
    padding-top: 30px;
    border-top: 1px solid #E8DCC9;
}

.master-other-products h2 {
    margin-bottom: 20px;
    color: #2C2C2C;
}

.products-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
}

.product-card {
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: transform 0.3s;
    border: 1px solid #E8DCC9;
}

.product-card:hover {
    transform: translateY(-4px);
}

.product-card a {
    text-decoration: none;
    color: inherit;
}

.card-image {
    height: 150px;
    overflow: hidden;
}

.card-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.card-info {
    padding: 12px;
}

.card-info h3 {
    font-size: 14px;
    margin-bottom: 5px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    color: #2C2C2C;
}

.card-info .price {
    font-size: 16px;
    font-weight: bold;
    color: #C67B5C;
    margin: 0;
}

/* Модальное окно для фото */
.image-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
    cursor: pointer;
}

.modal-content {
    position: relative;
    max-width: 90vw;
    max-height: 90vh;
    background: white;
    border-radius: 12px;
    padding: 10px;
}

.modal-content img {
    width: auto;
    height: auto;
    max-width: 100%;
    max-height: 90vh;
    object-fit: contain;
    border-radius: 8px;
}

.close-modal {
    position: absolute;
    top: -40px;
    right: -40px;
    background: #C67B5C;
    border: none;
    font-size: 40px;
    color: white;
    cursor: pointer;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.3s;
}

.close-modal:hover {
    background: #B56A4D;
}

@media (max-width: 768px) {
    .close-modal {
        top: -30px;
        right: 0;
    }
}
</style>