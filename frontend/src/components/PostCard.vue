<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useFollowStore } from '@/stores/follow'

const props = defineProps({
  post: {
    type: Object,
    required: true
  }
})

const router = useRouter()
const authStore = useAuthStore()
const followStore = useFollowStore()
const post = ref(props.post)
const newComment = ref('')
const showComments = ref(false)
const commentAuthor = ref('')

// Редактирование
const showEditModal = ref(false)
const editTitle = ref('')
const editContent = ref('')

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const toggleLike = async () => {
  try {
    const response = await axios.post(`http://127.0.0.1:8000/api/posts/${post.value.id}/like/`)
    post.value.likes_count = response.data.count
    post.value.user_liked = response.data.liked
  } catch (error) {
    console.error('Ошибка при лайке:', error)
  }
}

const addComment = async () => {
  if (!newComment.value.trim()) return
  
  try {
    const response = await axios.post(`http://127.0.0.1:8000/api/posts/${post.value.id}/comment/`, {
      author_name: commentAuthor.value || 'Аноним',
      content: newComment.value
    })
    
    if (!post.value.comments) {
      post.value.comments = []
    }
    post.value.comments.unshift(response.data)
    post.value.comments_count++
    newComment.value = ''
  } catch (error) {
    console.error('Ошибка при добавлении комментария:', error)
  }
}

const goToMaster = () => {
  router.push(`/master/${post.value.master}`)
}

const toggleFollow = async () => {
  await followStore.toggle(post.value.master)
}

// Проверка, является ли текущий пользователь автором поста
const isAuthor = () => {
  if (!authStore.isAuthenticated) return false
  const currentUserId = authStore.user?.id
  // post.master может быть числом или объектом с полем id
  const postMasterId = post.value.master?.id ?? post.value.master
  return currentUserId === postMasterId
}

// Открыть модалку редактирования
const openEditModal = () => {
  editTitle.value = post.value.title
  editContent.value = post.value.content
  showEditModal.value = true
}

// Закрыть модалку
const closeEditModal = () => {
  showEditModal.value = false
  editTitle.value = ''
  editContent.value = ''
}

// Сохранить изменения
const updatePost = async () => {
  try {
    const response = await axios.put(`http://127.0.0.1:8000/api/posts/${post.value.id}/`, {
      title: editTitle.value,
      content: editContent.value
    })
    // Обновляем локальные данные
    post.value.title = response.data.title
    post.value.content = response.data.content
    closeEditModal()
  } catch (error) {
    console.error('Ошибка при обновлении поста:', error)
    alert('Не удалось обновить публикацию')
  }
}
</script>

<template>
  <div class="post-card">
    <div class="post-header">
      <div class="master-info" @click="goToMaster">
        <div class="master-avatar">
          <img v-if="post.master_avatar" :src="post.master_avatar" :alt="post.master_name">
          <div v-else class="avatar-placeholder">{{ post.master_name?.[0] }}</div>
        </div>
        <div class="master-details">
          <span class="master-name">{{ post.master_name }}</span>
          <span class="post-date">{{ formatDate(post.created_at) }}</span>
        </div>
      </div>
      <div class="header-buttons">
        <button 
          v-if="authStore.isAuthenticated" 
          class="follow-btn" 
          :class="{ following: followStore.isFollowing(post.master) }"
          @click="toggleFollow"
        >
          {{ followStore.isFollowing(post.master) ? '✓ Подписан' : '+ Подписаться' }}
        </button>
        <button 
          v-if="isAuthor()" 
          class="edit-btn" 
          @click="openEditModal"
        >
          ✎ Редактировать
        </button>
      </div>
    </div>
    
    <div class="post-content">
      <h3>{{ post.title }}</h3>
      <p class="post-text">{{ post.content }}</p>
      
      <div v-if="post.image" class="post-image">
        <img :src="post.image" :alt="post.title">
      </div>
      
      <div v-if="post.video_url" class="post-video">
        <iframe 
          :src="post.video_url.replace('watch?v=', 'embed/')" 
          frameborder="0" 
          allowfullscreen
        ></iframe>
      </div>
    </div>
    
    <div class="post-stats">
      <span class="views">👁️ {{ post.views_count }}</span>
      <span class="comments-count">💬 {{ post.comments_count }}</span>
      <span class="likes-count">❤️ {{ post.likes_count }}</span>
    </div>
    
    <div class="post-actions">
      <button 
        class="like-btn" 
        :class="{ liked: post.user_liked }"
        @click="toggleLike"
      >
        {{ post.user_liked ? '❤️' : '🤍' }} Нравится
      </button>
      <button class="comment-btn" @click="showComments = !showComments">
        💬 Комментировать
      </button>
    </div>
    
    <div v-if="showComments" class="comments-section">
      <div class="add-comment">
        <input 
          type="text" 
          v-model="commentAuthor" 
          placeholder="Ваше имя"
          class="comment-author"
        >
        <div class="comment-input">
          <textarea 
            v-model="newComment" 
            placeholder="Напишите комментарий..."
            rows="2"
          ></textarea>
          <button @click="addComment">Отправить</button>
        </div>
      </div>
      
      <div v-if="post.comments?.length" class="comments-list">
        <div v-for="comment in post.comments" :key="comment.id" class="comment">
          <strong>{{ comment.author_name }}</strong>
          <p class="comment-text">{{ comment.content }}</p>
          <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
        </div>
      </div>
      <div v-else class="no-comments">
        Пока нет комментариев
      </div>
    </div>

    <!-- Модальное окно редактирования -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-content">
        <h3>Редактировать публикацию</h3>
        <input 
          type="text" 
          v-model="editTitle" 
          placeholder="Заголовок" 
          class="edit-input"
        />
        <textarea 
          v-model="editContent" 
          placeholder="Содержание" 
          rows="8" 
          class="edit-textarea"
        ></textarea>
        <div class="modal-buttons">
          <button @click="updatePost" class="save-btn">Сохранить</button>
          <button @click="closeEditModal" class="cancel-btn">Отмена</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.post-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 20px;
  overflow: hidden;
  transition: box-shadow 0.3s;
}
.post-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.post-header {
  padding: 16px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.master-info {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}
.master-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
  background: #42b883;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
}
.master-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.master-details {
  display: flex;
  flex-direction: column;
}
.master-name {
  font-weight: bold;
  color: #333;
}
.post-date {
  font-size: 12px;
  color: #999;
}
.header-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}
.follow-btn {
  padding: 6px 12px;
  border-radius: 20px;
  border: 1px solid #42b883;
  background: white;
  color: #42b883;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s;
}
.follow-btn.following {
  background: #42b883;
  color: white;
}
.follow-btn:hover {
  opacity: 0.8;
}
.edit-btn {
  padding: 6px 12px;
  border-radius: 20px;
  border: 1px solid #ffaa44;
  background: white;
  color: #ffaa44;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s;
}
.edit-btn:hover {
  background: #ffaa44;
  color: white;
}
.post-content {
  padding: 16px;
}
.post-content h3 {
  margin-bottom: 8px;
  color: #333;
}
.post-text {
  white-space: pre-wrap;
  word-break: break-word;
  color: #666;
  line-height: 1.6;
  margin-bottom: 16px;
}
.post-image {
  margin: 16px 0;
  border-radius: 8px;
  overflow: hidden;
}
.post-image img {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
}
.post-video {
  position: relative;
  padding-bottom: 56.25%;
  height: 0;
  overflow: hidden;
  border-radius: 8px;
}
.post-video iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
.post-stats {
  padding: 12px 16px;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
  display: flex;
  gap: 20px;
  color: #666;
  font-size: 14px;
}
.post-actions {
  padding: 12px 16px;
  display: flex;
  gap: 20px;
}
.like-btn, .comment-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #666;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  transition: all 0.3s;
}
.like-btn:hover, .comment-btn:hover {
  background: #f5f5f5;
}
.like-btn.liked {
  color: #ff4444;
}
.comments-section {
  padding: 16px;
  background: #f9f9f9;
  border-top: 1px solid #eee;
}
.add-comment {
  margin-bottom: 20px;
}
.comment-author {
  width: 100%;
  padding: 8px;
  margin-bottom: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}
.comment-input {
  display: flex;
  gap: 8px;
}
.comment-input textarea {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  resize: vertical;
}
.comment-input button {
  padding: 8px 16px;
  background: #42b883;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  align-self: flex-end;
}
.comment-input button:hover {
  background: #33a06f;
}
.comments-list {
  margin-top: 16px;
}
.comment {
  padding: 12px;
  background: white;
  border-radius: 8px;
  margin-bottom: 8px;
}
.comment strong {
  display: block;
  margin-bottom: 4px;
  color: #333;
}
.comment-text {
  white-space: pre-wrap;
  word-break: break-word;
  color: #666;
  margin-bottom: 4px;
}
.comment-date {
  font-size: 11px;
  color: #999;
}
.no-comments {
  text-align: center;
  color: #999;
  padding: 20px;
}

/* Модальное окно */
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
  padding: 24px;
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}
.modal-content h3 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #333;
}
.edit-input,
.edit-textarea {
  width: 100%;
  padding: 10px;
  margin-bottom: 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-family: inherit;
  font-size: 14px;
  box-sizing: border-box;
}
.edit-textarea {
  resize: vertical;
}
.modal-buttons {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}
.save-btn {
  background: #42b883;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}
.save-btn:hover {
  background: #33a06f;
}
.cancel-btn {
  background: #e0e0e0;
  color: #333;
  border: none;
  padding: 8px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}
.cancel-btn:hover {
  background: #ccc;
}
</style>