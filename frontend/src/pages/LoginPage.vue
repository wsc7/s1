<template>
  <main class="container auth-wrap">
    <div class="auth-card">
      <div class="auth-header">
        <h2>会议管理系统</h2>
        <p style="color: #666; margin-top: 10px;">请登录您的账户</p>
      </div>

      <div v-if="errorMessage" class="messages">
        <div class="alert alert-danger">{{ errorMessage }}</div>
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="username">用户名</label>
          <input id="username" v-model.trim="form.username" type="text" class="form-control" placeholder="请输入用户名" required autofocus>
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input id="password" v-model="form.password" type="password" class="form-control" placeholder="请输入密码" required>
        </div>

        <button type="submit" class="btn btn-primary btn-login" :disabled="submitting">{{ submitting ? '登录中...' : '登录' }}</button>
      </form>

      <div style="text-align: center; margin-top: 20px;">
        <p style="color: #666; font-size: 14px;">
          还没有账户？ <RouterLink to="/register/">立即注册</RouterLink>
        </p>
      </div>
    </div>
  </main>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import request, { setTokens } from '../utils/request'

const router = useRouter()
const route = useRoute()
const submitting = ref(false)
const errorMessage = ref('')
const form = reactive({
  username: '',
  password: '',
})

const handleSubmit = async () => {
  submitting.value = true
  errorMessage.value = ''

  try {
    const { data } = await request.post('/auth/login/', form)
    setTokens(data)
    router.push(route.query.redirect || '/meetings')
  } catch (error) {
    errorMessage.value = error.message || '登录失败。'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.auth-wrap {
  max-width: 400px;
  margin: 2rem auto;
}

.auth-card {
  padding: 40px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.auth-header h2 {
  color: #333;
  margin: 0;
}

.form-group {
  margin-bottom: 20px;
}

.btn-login {
  width: 100%;
  padding: 12px;
  background-color: #337ab7;
  border: none;
  font-size: 16px;
}

.btn-login:hover {
  background-color: #286090;
}

.messages {
  margin-bottom: 20px;
}

.alert {
  margin-bottom: 0;
}
</style>
