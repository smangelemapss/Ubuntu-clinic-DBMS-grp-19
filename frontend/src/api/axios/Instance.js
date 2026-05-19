import axios from 'axios'

/** Empty VITE_API_URL = same-origin (complete website on one port). */
function resolveApiBase() {
  const raw = import.meta.env.VITE_API_URL
  if (raw !== undefined && raw !== '') {
    return raw
  }
  return import.meta.env.DEV ? 'http://localhost:8000' : ''
}

const API_BASE = resolveApiBase()

const axiosInstance = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor to handle token refresh
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        const response = await axios.post(`${API_BASE}/api/v1/auth/token/refresh/`, {
          refresh: refreshToken,
        })
        localStorage.setItem('access_token', response.data.access)
        originalRequest.headers.Authorization = `Bearer ${response.data.access}`
        return axiosInstance(originalRequest)
      } catch (refreshError) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        const path = window.location.pathname
        const publicPaths = ['/login', '/staff/login', '/register', '/']
        if (!publicPaths.includes(path)) {
          window.location.href = path.startsWith('/staff') ? '/staff/login' : '/login'
        }
        return Promise.reject(refreshError)
      }
    }
    return Promise.reject(error)
  }
)

export default axiosInstance
