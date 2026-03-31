import { createApp } from 'vue'
import { getCsrfToken } from './csrf.js'

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

export async function submitJson(url, { method = 'POST', body } = {}) {
  const token = getCsrfToken()
  const response = await fetch(url, {
    method,
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'X-CSRFToken': token } : {}),
    },
    body: JSON.stringify(body),
  })
  return response.json()
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
