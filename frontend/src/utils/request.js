import axios from 'axios'

const ACCESS_TOKEN_KEY = 'meeting_access_token'
const REFRESH_TOKEN_KEY = 'meeting_refresh_token'

const getCookie = (name) => {
  const value = document.cookie
    .split('; ')
    .find((row) => row.startsWith(`${name}=`))

  return value ? decodeURIComponent(value.split('=').slice(1).join('=')) : ''
}

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

export const getSessionTokens = async () => {
  const { data } = await axios.get('/api/v1/auth/session-token/', {
    withCredentials: true,
  })
  setTokens(data)
  return data
}

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  withCredentials: true,
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

  const method = (config.method || 'get').toLowerCase()
  if (['post', 'put', 'patch', 'delete'].includes(method)) {
    const csrfToken = getCookie('csrftoken')
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }
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

    const data = error.response?.data
    const detail = data?.detail
    const message = detail || (typeof data === 'object' ? Object.entries(data).map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join('，') : value}`).join('；') : '') || '请求失败，请稍后重试。'

    const wrappedError = new Error(message)
    wrappedError.response = error.response
    wrappedError.data = data
    return Promise.reject(wrappedError)
  },
)

export default request
