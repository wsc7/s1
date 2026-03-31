<template>
  <div class="login-form">
    <div class="login-card">
      <div class="login-header">
        <h2>会议管理系统</h2>
        <p>请登录您的账户</p>
      </div>

      <div v-if="error" class="alert alert-danger alert-dismissible fade in">
        <button type="button" class="close" @click="error = ''" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        {{ error }}
      </div>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            type="text"
            class="form-control"
            id="username"
            v-model="username"
            placeholder="请输入用户名"
            required
            autofocus
            :disabled="loading"
          >
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            type="password"
            class="form-control"
            id="password"
            v-model="password"
            placeholder="请输入密码"
            required
            :disabled="loading"
          >
        </div>

        <button
          type="submit"
          class="btn btn-primary btn-login"
          :disabled="loading"
        >
          <span v-if="loading">
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            登录中...
          </span>
          <span v-else>登录</span>
        </button>
      </form>

      <div class="login-footer">
        <p>还没有账户？请联系管理员</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const handleLogin = async (e) => {
  e.preventDefault()

  if (!username.value || !password.value) {
    error.value = '请输入用户名和密码'
    return
  }

  loading.value = true
  error.value = ''

  try {
    // Get CSRF token
    const csrfToken = getCookie('csrftoken')

    const response = await fetch('/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrfToken,
      },
      body: new URLSearchParams({
        username: username.value,
        password: password.value,
        csrfmiddlewaretoken: csrfToken
      }),
      credentials: 'include'
    })

    if (response.ok) {
      // Login successful, redirect to home
      window.location.href = '/'
    } else {
      // Login failed
      const data = await response.text()
      if (response.status === 401 || response.status === 403) {
        error.value = '用户名或密码错误'
      } else {
        error.value = '登录失败，请稍后重试'
      }
    }
  } catch (err) {
    console.error('Login error:', err)
    error.value = '网络错误，请检查连接'
  } finally {
    loading.value = false
  }
}

// Helper function to get CSRF token from cookies
function getCookie(name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}
</script>

<style scoped>
.login-form {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  color: #333;
  margin: 0 0 10px 0;
  font-size: 24px;
}

.login-header p {
  color: #666;
  margin: 0;
  font-size: 14px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: normal;
}

.form-control {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-control:focus {
  border-color: #337ab7;
  outline: none;
  box-shadow: 0 0 0 2px rgba(51, 122, 183, 0.25);
}

.btn-login {
  width: 100%;
  padding: 12px;
  background-color: #337ab7;
  border: none;
  border-radius: 4px;
  color: white;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-login:hover:not(:disabled) {
  background-color: #286090;
}

.btn-login:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.login-footer {
  text-align: center;
  margin-top: 20px;
}

.login-footer p {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.alert {
  padding: 12px;
  margin-bottom: 20px;
  border: 1px solid transparent;
  border-radius: 4px;
}

.alert-danger {
  color: #a94442;
  background-color: #f2dede;
  border-color: #ebccd1;
}

.close {
  float: right;
  font-size: 21px;
  font-weight: bold;
  line-height: 1;
  color: #000;
  text-shadow: 0 1px 0 #fff;
  opacity: 0.2;
  background: transparent;
  border: 0;
  padding: 0;
  cursor: pointer;
}

.close:hover {
  opacity: 0.5;
}

.spinner-border {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  vertical-align: text-bottom;
  border: 0.2em solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spinner-border .75s linear infinite;
}

@keyframes spinner-border {
  to { transform: rotate(360deg); }
}
</style>