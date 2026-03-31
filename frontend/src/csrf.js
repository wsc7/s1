export function getCookie(name) {
  if (!document.cookie) {
    return null
  }
  const parts = document.cookie.split(';')
  for (const part of parts) {
    const c = part.trim()
    if (c.startsWith(`${name}=`)) {
      return decodeURIComponent(c.substring(name.length + 1))
    }
  }
  return null
}

export function getCsrfToken() {
  return getCookie('csrftoken')
}
