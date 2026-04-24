<template>
  <div class="row">
    <div class="col-sm-6 col-sm-offset-3">
      <div class="panel panel-default">
        <div class="panel-heading">
          <h3 class="panel-title">登录</h3>
        </div>
        <div class="panel-body">
          <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
          <form @submit.prevent="handleSubmit">
            <div class="form-group">
              <label for="username">用户名</label>
              <input id="username" v-model.trim="form.username" type="text" class="form-control" required>
            </div>
            <div class="form-group">
              <label for="password">密码</label>
              <input id="password" v-model="form.password" type="password" class="form-control" required>
            </div>
            <button class="btn btn-primary btn-block" type="submit" :disabled="submitting">
              {{ submitting ? '登录中...' : '登录' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

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
