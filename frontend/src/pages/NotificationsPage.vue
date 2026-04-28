<template>
  <main class="container notifications-page my-4">
    <div class="page-header">
      <div class="page-header__inner">
        <div class="page-header__copy">
          <h2 class="page-header__title">通知中心</h2>
          <span class="page-header__subtitle">查看系统通知与会议提醒</span>
        </div>
        <RouterLink class="btn btn-default" to="/">返回首页</RouterLink>
      </div>
    </div>

    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
    <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>
    <div v-if="loading" class="text-muted">加载中...</div>

    <div v-else class="card">
      <div class="card-body">
        <div v-if="notifications.length" class="list-group">
          <div
            v-for="notification in notifications"
            :key="notification.id"
            class="list-group-item"
            :class="{ 'list-group-item-info': notification.status === 'unread' }"
          >
            <div class="notification-item-layout">
              <div class="notification-item-body">
                <div class="notification-title-row">
                  <h5 class="mb-0 mr-2">
                    <span class="badge" :class="typeBadgeClass(notification.notification_type)">{{ notification.notification_type_label }}</span>
                    {{ notification.title }}
                  </h5>
                  <span v-if="notification.status === 'unread'" class="badge badge-danger">未读</span>
                </div>
                <p class="mb-2 notification-content">{{ notification.content }}</p>
                <p v-if="notification.meeting" class="mb-1">
                  <small class="text-muted">相关会议：{{ notification.meeting_title }}</small>
                </p>
                <small class="text-muted">{{ notification.created_at_display }}</small>
              </div>
              <div class="notification-actions">
                <button
                  v-if="notification.status === 'unread'"
                  type="button"
                  class="btn btn-sm btn-outline-primary"
                  @click="updateNotification(notification, 'mark_read')"
                >标记已读</button>
                <button type="button" class="btn btn-sm btn-outline-secondary" @click="updateNotification(notification, 'dismiss')">忽略</button>
                <div v-if="notification.meeting && notification.notification_type === 'invitation' && notification.status === 'unread'" class="mt-2">
                  <button type="button" class="btn btn-sm btn-success" @click="openRespondModal(notification)">回复邀请</button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-5">
          <h4 class="text-muted">暂无通知</h4>
          <p class="text-muted">当有新的会议邀请或提醒时，会在这里显示</p>
        </div>
      </div>
    </div>

    <ModalShell :show="respondModalVisible" title="回复会议邀请" @close="closeRespondModal">
      <p v-if="respondingNotification">{{ respondingNotification.meeting_title }}</p>
      <div class="form-group">
        <label>请选择您的回复</label>
        <select v-model="responseValue" class="form-control">
          <option value="accepted">已接受</option>
          <option value="declined">已拒绝</option>
        </select>
      </div>
      <template #footer>
        <button type="button" class="btn btn-default" @click="closeRespondModal">取消</button>
        <button type="button" class="btn btn-primary" @click="submitResponse">提交回复</button>
      </template>
    </ModalShell>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import ModalShell from '../components/ModalShell.vue'
import request from '../utils/request'

const loading = ref(true)
const errorMessage = ref('')
const successMessage = ref('')
const notifications = ref([])
const respondModalVisible = ref(false)
const respondingNotification = ref(null)
const responseValue = ref('accepted')

const loadNotifications = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const { data } = await request.get('/notifications/')
    notifications.value = data.results || []
  } catch (error) {
    errorMessage.value = error.message || '通知中心加载失败。'
  } finally {
    loading.value = false
  }
}

const typeBadgeClass = (type) => ({
  invitation: 'badge-primary',
  reminder: 'badge-warning',
  update: 'badge-info',
  cancellation: 'badge-danger',
}[type] || 'badge-default')

const updateNotification = async (notification, action) => {
  errorMessage.value = ''
  try {
    const { data } = await request.patch('/notifications/', {
      notification_id: notification.id,
      action,
    })
    Object.assign(notification, data.notification || {})
    successMessage.value = data.detail || '通知已更新'
  } catch (error) {
    errorMessage.value = error.message || '通知操作失败。'
  }
}

const openRespondModal = (notification) => {
  respondingNotification.value = notification
  responseValue.value = 'accepted'
  respondModalVisible.value = true
}

const closeRespondModal = () => {
  respondModalVisible.value = false
}

const submitResponse = async () => {
  if (!respondingNotification.value) {
    return
  }
  try {
    const { data } = await request.post(`/meetings/${respondingNotification.value.meeting}/respond/`, {
      response: responseValue.value,
    })
    respondModalVisible.value = false
    successMessage.value = data.detail || '您的回复已记录'
    await updateNotification(respondingNotification.value, 'mark_read')
  } catch (error) {
    errorMessage.value = error.message || '回复邀请失败。'
  }
}

onMounted(loadNotifications)
</script>

<style scoped>
.notifications-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card {
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fff;
}

.card-body {
  padding: 15px;
}

.notification-item-layout,
.notification-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.notification-title-row {
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 8px;
}

.notification-item-body {
  flex: 1;
  min-width: 0;
}

.notification-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  margin-left: 1rem;
}

.notification-content {
  white-space: pre-line;
}

.mb-0 {
  margin-bottom: 0;
}

.mb-1 {
  margin-bottom: .25rem;
}

.mb-2 {
  margin-bottom: .5rem;
}

.mr-2 {
  margin-right: .5rem;
}

.mt-2 {
  margin-top: .5rem;
}

.py-5 {
  padding-top: 3rem;
  padding-bottom: 3rem;
}

.badge-primary {
  background-color: #337ab7;
}

.badge-warning {
  background-color: #f0ad4e;
}

.badge-info {
  background-color: #5bc0de;
}

.badge-danger {
  background-color: #d9534f;
}

.badge-default {
  background-color: #777;
}

.btn-outline-primary,
.btn-outline-secondary {
  background: #fff;
}

@media (max-width: 767px) {
  .notification-item-layout {
    flex-direction: column;
  }

  .notification-actions {
    align-items: flex-start;
    margin-left: 0;
  }
}
</style>
