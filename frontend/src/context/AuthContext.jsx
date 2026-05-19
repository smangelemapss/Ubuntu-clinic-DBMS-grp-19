import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import axiosInstance from '../api/axios/Instance'

const AuthContext = createContext()

export const useAuth = () => useContext(AuthContext)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchCurrentUser = useCallback(async () => {
    const response = await axiosInstance.get('/api/v1/auth/me/')
    return response.data
  }, [])

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setLoading(false)
      return
    }

    fetchCurrentUser()
      .then((data) => setUser(data))
      .catch(() => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [fetchCurrentUser])

  const login = async (userData) => {
    setUser(userData)
    try {
      const full = await fetchCurrentUser()
      setUser(full)
      return full
    } catch {
      return userData
    }
  }

  const logout = async () => {
    const refresh = localStorage.getItem('refresh_token')
    try {
      if (refresh) {
        await axiosInstance.post('/api/v1/auth/logout/', { refresh })
      }
    } catch {
      /* ignore */
    }
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
  }

  const refreshUser = async () => {
    const full = await fetchCurrentUser()
    setUser(full)
    return full
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export { AuthContext }
