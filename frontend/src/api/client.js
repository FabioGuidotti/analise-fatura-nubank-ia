// Cliente HTTP central com injeção de token e refresh automático em 401.
import axios from 'axios'

const TOKEN_KEY = 'ff_access_token'
const REFRESH_KEY = 'ff_refresh_token'

export const tokenStore = {
  get access() {
    return localStorage.getItem(TOKEN_KEY)
  },
  get refresh() {
    return localStorage.getItem(REFRESH_KEY)
  },
  set({ access_token, refresh_token }) {
    if (access_token) localStorage.setItem(TOKEN_KEY, access_token)
    if (refresh_token) localStorage.setItem(REFRESH_KEY, refresh_token)
  },
  clear() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_KEY)
  },
}

const api = axios.create({
  baseURL: (import.meta.env.VITE_API_URL || '') + '/api',
})

api.interceptors.request.use((config) => {
  const token = tokenStore.access
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

let refreshing = null

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    const status = error.response?.status

    // Tenta um único refresh transparente quando o access token expira.
    if (status === 401 && !original._retry && tokenStore.refresh) {
      original._retry = true
      try {
        refreshing =
          refreshing ||
          axios.post((import.meta.env.VITE_API_URL || '') + '/api/auth/refresh', {
            refresh_token: tokenStore.refresh,
          })
        const { data } = await refreshing
        refreshing = null
        tokenStore.set(data)
        original.headers.Authorization = `Bearer ${data.access_token}`
        return api(original)
      } catch (e) {
        refreshing = null
        tokenStore.clear()
        if (!location.pathname.startsWith('/login')) location.href = '/login'
        return Promise.reject(e)
      }
    }
    return Promise.reject(error)
  }
)

// Extrai uma mensagem de erro amigável da resposta da API.
export const errorMessage = (err, fallback = 'Algo deu errado. Tente novamente.') => {
  const detail = err?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

export default api
