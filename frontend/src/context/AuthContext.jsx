import React, { createContext, useContext, useState, useEffect } from 'react'
import { api } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token') || null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadUser() {
      const savedToken = localStorage.getItem('token')
      if (savedToken) {
        try {
          const profile = await api.auth.me()
          setUser(profile)
        } catch (err) {
          console.warn('Session expired or invalid token:', err)
          localStorage.removeItem('token')
          setToken(null)
          setUser(null)
        }
      }
      setLoading(false)
    }
    loadUser()
  }, [])

  const login = async (email, password) => {
    const data = await api.auth.login(email, password)
    localStorage.setItem('token', data.access_token)
    setToken(data.access_token)
    try {
      const profile = await api.auth.me()
      setUser(profile)
    } catch {
      setUser({ email, role: 'auditor' })
    }
    return data
  }

  const register = async (email, password, full_name) => {
    await api.auth.register(email, password, full_name)
    return login(email, password)
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token,
        loading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
