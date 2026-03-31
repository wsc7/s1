<template>
  <div>
    <!-- Check if user is logged in -->
    <div v-if="!isLoggedIn">
      <login-form />
    </div>
    <div v-else>
      <!-- Navigation Bar -->
      <nav class="navbar navbar-default navbar-static-top">
        <div class="container">
          <div class="navbar-header">
            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar-collapse">
              <span class="sr-only">切换导航</span>
              <span class="icon-bar"></span>
              <span class="icon-bar"></span>
              <span class="icon-bar"></span>
            </button>
            <a class="navbar-brand" href="/">会议管理系统</a>
          </div>
          <div class="collapse navbar-collapse" id="navbar-collapse">
            <ul class="nav navbar-nav">
              <li><a href="/">首页</a></li>
              <li><a href="/people/">人员管理</a></li>
              <li><a href="/meetings/">会议管理</a></li>
            </ul>
            <ul class="nav navbar-nav navbar-right">
              <li class="dropdown">
                <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">
                  {{ username }} <span class="caret"></span>
                </a>
                <ul class="dropdown-menu">
                  <li><a href="#" @click.prevent="handleLogout">退出登录</a></li>
                </ul>
              </li>
            </ul>
          </div>
        </div>
      </nav>

      <!-- Main Content Area -->
      <router-view v-if="$route"></router-view>
      <div v-else class="container" style="padding-top: 2rem;">
        <!-- Default content when no router -->
        <div class="jumbotron">
          <h1>欢迎使用会议管理系统</h1>
          <p>您已成功登录系统。</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import LoginForm from './components/LoginForm.vue'

const isLoggedIn = ref(false)
const username = ref('')

// Check login status
const checkLoginStatus = async () => {
  try {
    const response = await fetch('/api/check-auth/', {
      credentials: 'include'
    })

    if (response.ok) {
      const data = await response.json()
      isLoggedIn.value = data.is_authenticated
      username.value = data.username || '用户'
    } else {
      isLoggedIn.value = false
    }
  } catch (error) {
    console.error('Auth check error:', error)
    isLoggedIn.value = false
  }
}

// Handle logout
const handleLogout = async () => {
  try {
    const response = await fetch('/logout/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
      },
      credentials: 'include'
    })

    if (response.ok) {
      isLoggedIn.value = false
      username.value = ''
      window.location.href = '/login/'
    }
  } catch (error) {
    console.error('Logout error:', error)
  }
}

// Helper function to get CSRF token
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

// Check login status on component mount
onMounted(() => {
  checkLoginStatus()
})
</script>
