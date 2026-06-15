<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import PostCard from '@/components/PostCard.vue'

const posts = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/posts/feed/')
    posts.value = response.data
  } catch (error) {
    console.error('Ошибка загрузки ленты:', error)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="container">
    <h1>Лента мастеров</h1>
    <p class="subtitle">Истории создания, вдохновение и новые работы</p>
    
    <div v-if="loading" class="loading">Загрузка...</div>
    
    <div v-else-if="posts.length === 0" class="empty">
      <p>Пока нет публикаций</p>
      <p class="hint">Станьте мастером и поделитесь своими работами!</p>
    </div>
    
    <div v-else class="feed">
      <PostCard 
        v-for="post in posts" 
        :key="post.id" 
        :post="post"
      />
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
.subtitle {
  color: #666;
  margin-bottom: 30px;
}
.loading, .empty {
  text-align: center;
  padding: 60px;
  background: #FFFBF7;
  border: 1px solid #E8DCC9;
  border-radius: 8px;
  color: #666;
}
.hint {
  margin-top: 10px;
  font-size: 14px;
  color: #999;
}
.feed {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
</style>