import { createApp } from 'vue'
import { getAccessToken } from './utils/request'

const getCsrfToken = () => {
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]*)/)
  return match ? match[1] : null
}

export function toSpaApiUrl(url) {
  return url.replace(/^\/api\/v1/, '') || '/'
}

export function formatErrors(errors, labelMap = {}) {
  if (!errors || typeof errors !== 'object') {
    return '保存失败。'
  }
  const lines = []
  for (const [key, value] of Object.entries(errors)) {
    const msg = Array.isArray(value) ? value.join(' ') : String(value)
    lines.push(`${labelMap[key] || key}: ${msg}`)
  }
  return lines.join(' ') || '保存失败。'
}

function buildErrorMessage(data) {
  if (!data || typeof data !== 'object') {
    return '请求失败，请稍后重试。'
  }
  if (data.detail) {
    return data.detail
  }
  if (data.errors) {
    return formatErrors(data.errors)
  }
  return formatErrors(data)
}

export async function submitJson(url, { method = 'POST', body } = {}) {
  const token = getCsrfToken()
  const accessToken = getAccessToken()
  const response = await fetch(url, {
    method,
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'X-CSRFToken': token } : {}),
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
    },
    body: JSON.stringify(body),
  })
  const text = await response.text()
  const data = text ? JSON.parse(text) : {}
  if (!response.ok) {
    const error = new Error(buildErrorMessage(data))
    error.response = response
    error.data = data
    throw error
  }
  return data
}

function onReady(callback) {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', callback, { once: true })
    return
  }
  callback()
}

export function mountById(id, Component, getProps) {
  onReady(() => {
    const el = document.getElementById(id)
    if (!el) {
      return
    }
    createApp(Component, getProps(el)).mount(el)
  })
}

export function mountBySelector(selector, Component, getProps) {
  onReady(() => {
    document.querySelectorAll(selector).forEach((el) => {
      const props = getProps(el)
      if (!props) {
        return
      }
      createApp(Component, props).mount(el)
    })
  })
}

export function readJsonScript(id, fallback = []) {
  const el = document.getElementById(id)
  if (!el || !el.textContent) {
    return fallback
  }
  try {
    return JSON.parse(el.textContent.trim())
  } catch {
    return fallback
  }
}
