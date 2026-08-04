import axios from 'axios'

const ACCESS_KEY = 'okten_access'
const REFRESH_KEY = 'okten_refresh'

export const tokenStorage = {
  getAccess: () => localStorage.getItem(ACCESS_KEY),
  getRefresh: () => localStorage.getItem(REFRESH_KEY),
  setTokens: (access: string, refresh: string) => {
    localStorage.setItem(ACCESS_KEY, access)
    localStorage.setItem(REFRESH_KEY, refresh)
  },
  clear: () => {
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
  },
}

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = tokenStorage.getAccess()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  // Let the browser set multipart/form-data with the correct boundary.
  // The global JSON content-type would otherwise break file uploads.
  if (config.data instanceof FormData) {
    config.headers.delete('Content-Type')
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (error.response?.status !== 401 || original._retry) {
      return Promise.reject(error)
    }

    original._retry = true
    const refresh = tokenStorage.getRefresh()

    if (refresh) {
      try {
        const { data } = await axios.post<{ access: string }>('/api/auth/token/refresh/', {
          refresh,
        })
        tokenStorage.setTokens(data.access, refresh)
        original.headers.Authorization = `Bearer ${data.access}`
        return api(original)
      } catch {
        tokenStorage.clear()
      }
    } else {
      tokenStorage.clear()
    }

    // Invalid/expired JWT makes DRF return 401 even on public endpoints.
    // Retry once as anonymous so catalog pages still load.
    delete original.headers.Authorization
    return api(original)
  },
)

export default api
