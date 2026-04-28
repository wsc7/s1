<template>
  <main class="container reminder-settings-page my-4">
    <div class="page-header">
      <div class="page-header__inner">
        <div class="page-header__copy">
          <h2 class="page-header__title">提醒设置</h2>
          <span class="page-header__subtitle">自定义您的会议提醒偏好</span>
        </div>
        <RouterLink class="btn btn-default" to="/notifications/">返回通知中心</RouterLink>
      </div>
    </div>

    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
    <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>
    <div v-if="loading" class="text-muted">加载中...</div>

    <div v-else class="row">
      <div class="col-md-8 col-md-offset-2">
        <div class="card">
          <div class="card-body">
            <form @submit.prevent="saveSettings">
              <h4 class="form-section-title">通知方式</h4>
              <div class="form-group">
                <div class="checkbox">
                  <label>
                    <input v-model="form.email_notifications" type="checkbox">
                    邮件通知
                  </label>
                  <p class="help-block">通过邮件接收会议通知和提醒</p>
                </div>
                <div class="checkbox">
                  <label>
                    <input v-model="form.in_app_notifications" type="checkbox">
                    应用内通知
                  </label>
                  <p class="help-block">在系统内显示通知消息</p>
                </div>
                <div class="checkbox">
                  <label>
                    <input v-model="form.sms_notifications" type="checkbox">
                    短信通知
                  </label>
                  <p class="help-block">通过短信接收紧急提醒（需要配置短信服务）</p>
                </div>
              </div>

              <hr>

              <h4 class="form-section-title">免打扰时间</h4>
              <div class="row">
                <div class="col-md-6">
                  <div class="form-group">
                    <label>免打扰开始时间</label>
                    <input v-model="form.quiet_hours_start" type="time" class="form-control">
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="form-group">
                    <label>免打扰结束时间</label>
                    <input v-model="form.quiet_hours_end" type="time" class="form-control">
                  </div>
                </div>
              </div>
              <p class="help-block">在设定的时间段内不会发送通知提醒</p>

              <hr>

              <div class="form-group">
                <button type="submit" class="btn btn-primary">保存设置</button>
                <RouterLink to="/notifications/" class="btn btn-default">取消</RouterLink>
              </div>
            </form>
          </div>
        </div>

        <div class="card mt-4">
          <div class="card-header">
            <h5 class="mb-0">当前设置预览</h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-6">
                <h6>启用的通知方式：</h6>
                <ul class="list-unstyled">
                  <li><span :class="form.email_notifications ? 'text-success' : 'text-muted'">{{ form.email_notifications ? '✓' : '×' }}</span> 邮件通知</li>
                  <li><span :class="form.in_app_notifications ? 'text-success' : 'text-muted'">{{ form.in_app_notifications ? '✓' : '×' }}</span> 应用内通知</li>
                  <li><span :class="form.sms_notifications ? 'text-success' : 'text-muted'">{{ form.sms_notifications ? '✓' : '×' }}</span> 短信通知</li>
                </ul>
              </div>
              <div class="col-md-6">
                <h6>免打扰时间：</h6>
                <p v-if="form.quiet_hours_start && form.quiet_hours_end">{{ form.quiet_hours_start }} - {{ form.quiet_hours_end }}</p>
                <p v-else class="text-muted">未设置免打扰时间</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'

import request from '../utils/request'

const loading = ref(true)
const errorMessage = ref('')
const successMessage = ref('')
const form = reactive({
  email_notifications: true,
  in_app_notifications: true,
  sms_notifications: false,
  quiet_hours_start: '',
  quiet_hours_end: '',
})

const setForm = (data) => {
  Object.assign(form, {
    email_notifications: !!data.email_notifications,
    in_app_notifications: !!data.in_app_notifications,
    sms_notifications: !!data.sms_notifications,
    quiet_hours_start: data.quiet_hours_start || '',
    quiet_hours_end: data.quiet_hours_end || '',
  })
}

const loadSettings = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const { data } = await request.get('/reminder-settings/')
    setForm(data)
  } catch (error) {
    errorMessage.value = error.message || '提醒设置加载失败。'
  } finally {
    loading.value = false
  }
}

const saveSettings = async () => {
  errorMessage.value = ''
  try {
    const { data } = await request.patch('/reminder-settings/', form)
    setForm(data)
    successMessage.value = data.detail || '提醒设置已保存'
  } catch (error) {
    errorMessage.value = error.message || '提醒设置保存失败。'
  }
}

onMounted(loadSettings)
</script>

<style scoped>
.reminder-settings-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card {
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fff;
}

.card-header {
  padding: 10px 15px;
  border-bottom: 1px solid #ddd;
  background: #f5f5f5;
}

.card-body {
  padding: 15px;
}

.mt-4 {
  margin-top: 1.5rem;
}
</style>
