import axios from 'axios'

const API_BASE = ''  // ⬅️ Keep it empty for proxy

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (userData) => api.post('/auth/register', userData),
  getProfile: () => api.get('/auth/me'),
}

export const booksAPI = {
  getAll: () => api.get('/books'),
  search: (query) => api.get(`/ai/search?query=${query}`),
}

export const aiAPI = {
  getRecommendations: (userId) => api.get(`/ai/recommend/${userId}`),
}

export const healthAPI = {
  check: () => api.get('/health'),
}

export default api