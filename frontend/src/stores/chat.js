import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useChatStore = defineStore('chat', () => {
    const rooms = ref([])
    const currentRoom = ref(null)
    const messages = ref([])
    const loading = ref(false)

    const loadRooms = async () => {
        loading.value = true
        try {
            const response = await axios.get('http://127.0.0.1:8000/api/chat/rooms/')
            rooms.value = response.data
        } catch (error) {
            console.error('Ошибка загрузки чатов:', error)
        } finally {
            loading.value = false
        }
    }

    const loadMessages = async (roomId) => {
        try {
            const response = await axios.get(`http://127.0.0.1:8000/api/chat/rooms/${roomId}/messages/`)
            messages.value = response.data
            await loadRooms()
        } catch (error) {
            console.error('Ошибка загрузки сообщений:', error)
        }
    }

    const sendMessage = async (roomId, text) => {
        try {
            const response = await axios.post(`http://127.0.0.1:8000/api/chat/rooms/${roomId}/send/`, { text })
            messages.value.push(response.data)
            await loadRooms()
        } catch (error) {
            console.error('Ошибка отправки сообщения:', error)
        }
    }

    const createRoomWithMaster = async (masterId) => {
        const existing = rooms.value.find(r => r.master === masterId)
        if (existing) return existing.id
        try {
            await axios.post('http://127.0.0.1:8000/api/chat/rooms/', { master: masterId })
            await loadRooms()
            const newRoom = rooms.value.find(r => r.master === masterId)
            return newRoom ? newRoom.id : null
        } catch (error) {
            console.error('Ошибка создания чата:', error)
            return null
        }
    }

    return { rooms, currentRoom, messages, loading, loadRooms, loadMessages, sendMessage, createRoomWithMaster }
})