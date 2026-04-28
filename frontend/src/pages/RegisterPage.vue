<template>
  <main class="container auth-wrap">
    <div class="auth-card">
      <div class="auth-header">
        <h2>会议管理系统</h2>
        <p style="color: #666; margin-top: 10px;">创建新账户</p>
      </div>

      <div v-if="errorMessage" class="messages">
        <div class="alert alert-danger">{{ errorMessage }}</div>
      </div>
      <div v-if="successMessage" class="messages">
        <div class="alert alert-success">{{ successMessage }}</div>
      </div>

      <form @submit.prevent="submitRegister">
        <div class="form-group">
          <label for="username">用户名</label>
          <input id="username" v-model.trim="form.username" type="text" class="form-control" placeholder="请输入用户名" required autofocus>
          <div class="form-note">用户名只能包含字母、数字和@/./+/-/_符号</div>
        </div>

        <div class="form-group">
          <label for="email">邮箱（可选）</label>
          <input id="email" v-model.trim="form.email" type="email" class="form-control" placeholder="请输入邮箱">
        </div>

        <div class="form-group">
          <label for="password1">密码</label>
          <input id="password1" v-model="form.password1" type="password" class="form-control" placeholder="请输入密码" required>
        </div>

        <div class="form-group">
          <label for="password2">确认密码</label>
          <input id="password2" v-model="form.password2" type="password" class="form-control" placeholder="请再次输入密码" required>
        </div>

        <div class="form-group">
          <label for="name">真实姓名</label>
          <input id="name" v-model.trim="form.name" type="text" class="form-control" placeholder="请输入真实姓名" required>
          <div class="form-note">此姓名将用于会议系统和人员管理</div>
        </div>

        <div class="form-group">
          <label for="employee_no">工号（可选）</label>
          <input id="employee_no" v-model.trim="form.employee_no" type="text" class="form-control" placeholder="请输入工号">
        </div>

        <div class="form-group">
          <label for="department">部门（可选）</label>
          <input id="department" v-model.trim="form.department" type="text" class="form-control" placeholder="请输入部门">
        </div>

        <button type="submit" class="btn btn-success btn-register" :disabled="submitting">{{ submitting ? '注册中...' : '注册' }}</button>
      </form>

      <div style="text-align: center; margin-top: 20px;">
        <p style="color: #666; font-size: 14px;">
          已有账户？ <RouterLink to="/login">立即登录</RouterLink>
        </p>
      </div>
    </div>
  </main>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import request, { setTokens } from '../utils/request'

const router = useRouter()
const submitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const form = reactive({
  username: '',
  email: '',
  password1: '',
  password2: '',
  name: '',
  employee_no: '',
  department: '',
})

const submitRegister = async () => {
  submitting.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    const { data } = await request.post('/auth/register/', form)
    setTokens({ access: data.access, refresh: data.refresh })
    successMessage.value = data.detail || '注册成功'
    router.push('/')
  } catch (error) {
    errorMessage.value = error.message || '注册失败，请稍后重试。'
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

.btn-register {
  width: 100%;
  padding: 12px;
  background-color: #5cb85c;
  border: none;
  font-size: 16px;
}

.btn-register:hover {
  background-color: #449d44;
}

.messages {
  margin-bottom: 20px;
}

.alert {
  margin-bottom: 0;
}

.form-note {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}
</style>
