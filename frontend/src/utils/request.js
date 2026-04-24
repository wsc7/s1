import axios from 'axios'

const ACCESS_TOKEN_KEY = 'meeting_access_token'
const REFRESH_TOKEN_KEY = 'meeting_refresh_token'

export const getAccessToken = () => localStorage.getItem(ACCESS_TOKEN_KEY)
export const getRefreshToken = () => localStorage.getItem(REFRESH_TOKEN_KEY)

export const setTokens = ({ access, refresh }) => {
  if (access) {
    localStorage.setItem(ACCESS_TOKEN_KEY, access)
  }
  if (refresh) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
  }
}

export const clearTokens = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
})

let isRefreshing = false
let pendingRequests = []

const flushPendingRequests = (token) => {
  pendingRequests.forEach((callback) => callback(token))
  pendingRequests = []
}

request.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config || {}
    const refreshToken = getRefreshToken()
    const status = error.response?.status

    if (status === 401 && refreshToken && !originalRequest._retry && !originalRequest.url?.includes('/auth/refresh/')) {
      originalRequest._retry = true

      if (isRefreshing) {
        return new Promise((resolve) => {
          pendingRequests.push((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(request(originalRequest))
          })
        })
      }

      isRefreshing = true
      try {
        const { data } = await axios.post('/api/v1/auth/refresh/', { refresh: refreshToken })
        setTokens({ access: data.access, refresh: refreshToken })
        flushPendingRequests(data.access)
        originalRequest.headers.Authorization = `Bearer ${data.access}`
        return request(originalRequest)
      } catch (refreshError) {
        clearTokens()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    const detail = error.response?.data?.detail
    const fieldErrors = error.response?.data
    const message = detail || (typeof fieldErrors === 'object' ? JSON.stringify(fieldErrors) : '') || '请求失败，请稍后重试。'

    return Promise.reject(new Error(message))
  },
)

export default request
