import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { authApi, type LoginPayload, type RegisterPayload } from '../api/auth.api'
import { tokenStorage } from '../api/axiosInstance'
import { usersApi } from '../api/users.api'
import type { User } from '../types/api'

interface AuthContextValue {
  user: User | null
  loading: boolean
  isAuthenticated: boolean
  isSuperAdmin: boolean
  isVenueManager: boolean
  isCritic: boolean
  login: (payload: LoginPayload) => Promise<void>
  oauthLogin: (provider: 'google' | 'facebook', token: string) => Promise<void>
  register: (payload: RegisterPayload) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const refreshUser = useCallback(async () => {
    if (!tokenStorage.getAccess()) {
      setUser(null)
      return
    }
    const { data } = await usersApi.me()
    setUser(data)
  }, [])

  useEffect(() => {
    refreshUser()
      .catch(() => {
        tokenStorage.clear()
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [refreshUser])

  const login = useCallback(async (payload: LoginPayload) => {
    const { data } = await authApi.login(payload)
    tokenStorage.setTokens(data.access, data.refresh)
    await refreshUser()
  }, [refreshUser])

  const oauthLogin = useCallback(
    async (provider: 'google' | 'facebook', token: string) => {
      if (provider === 'google') {
        await authApi.loginWithGoogle(token)
      } else {
        await authApi.loginWithFacebook(token)
      }
      await refreshUser()
    },
    [refreshUser],
  )

  const register = useCallback(async (payload: RegisterPayload) => {
    const { data } = await authApi.register(payload)
    tokenStorage.setTokens(data.access, data.refresh)
    setUser(data.user)
  }, [])

  const logout = useCallback(() => {
    tokenStorage.clear()
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({
      user,
      loading,
      isAuthenticated: !!user,
      isSuperAdmin: user?.role === 'super_admin',
      isVenueManager: user?.role === 'venue_manager' || user?.role === 'super_admin',
      isCritic: user?.role === 'critic',
      login,
      oauthLogin,
      register,
      logout,
      refreshUser,
    }),
    [user, loading, login, oauthLogin, register, logout, refreshUser],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
