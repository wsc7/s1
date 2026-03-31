<template>
  <div class="vue-toolbar">
    <button type="button" class="btn btn-primary" @click="open">新建会议</button>
    <a :href="fullPageUrl" class="btn btn-link btn-sm">或使用完整页面</a>

    <Teleport to="body">
      <div v-show="show" class="vue-modal-mask" @click.self="close">
        <div class="vue-modal-panel vue-modal-panel-wide">
          <div class="vue-modal-header">
            <h4 class="vue-modal-title">新建会议</h4>
            <button type="button" class="close" aria-label="关闭" @click="close">&times;</button>
          </div>
          <div class="vue-modal-body">
            <p v-if="errorMsg" class="text-danger small">{{ errorMsg }}</p>
            <div class="form-group">
              <label>会议主题 <span class="text-danger">*</span></label>
              <input v-model="form.title" type="text" class="form-control">
            </div>
            <div class="form-group">
              <label>发起人</label>
              <select v-model="form.organizer" class="form-control">
                <option value="">— 未指定 —</option>
                <option v-for="o in organizers" :key="o.id" :value="String(o.id)">{{ o.name }}</option>
              </select>
            </div>
            <div class="row-fields">
              <div class="form-group">
                <label>开始时间 <span class="text-danger">*</span></label>
                <input v-model="form.start_time" type="datetime-local" class="form-control">
              </div>
              <div class="form-group">
                <label>结束时间 <span class="text-danger">*</span></label>
                <input v-model="form.end_time" type="datetime-local" class="form-control">
              </div>
            </div>
            <div class="form-group">
              <label>地点</label>
              <input v-model="form.location" type="text" class="form-control">
            </div>
            <div class="form-group">
              <label>参会人数</label>
              <input v-model.number="form.attendee_count" type="number" min="0" class="form-control">
            </div>
            <div class="form-group">
              <label>状态</label>
              <select v-model="form.status" class="form-control">
                <option v-for="s in statusChoices" :key="s.value" :value="s.value">{{ s.label }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>说明</label>
              <textarea v-model="form.description" class="form-control" rows="3"></textarea>
            </div>
          </div>
          <div class="vue-modal-footer">
            <button type="button" class="btn btn-default" @click="close">取消</button>
            <button type="button" class="btn btn-primary" :disabled="submitting" @click="submit">
              {{ submitting ? '保存中…' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { getCsrfToken } from '../csrf.js'

const props = defineProps({
  apiUrl: { type: String, required: true },
  fullPageUrl: { type: String, default: '/meetings/add/' },
  organizers: { type: Array, default: () => [] },
})

const statusChoices = [
  { value: 'pending', label: '待审批' },
  { value: 'approved', label: '已通过' },
  { value: 'done', label: '已结束' },
  { value: 'cancelled', label: '已取消' },
]

const show = ref(false)
const submitting = ref(false)
const errorMsg = ref('')
const form = reactive({
  title: '',
  organizer: '',
  start_time: '',
  end_time: '',
  location: '',
  attendee_count: 0,
  status: 'pending',
  description: '',
})

function open() {
  errorMsg.value = ''
  Object.assign(form, {
    title: '',
    organizer: '',
    start_time: '',
    end_time: '',
    location: '',
    attendee_count: 0,
    status: 'pending',
    description: '',
  })
  show.value = true
}

function close() {
  show.value = false
}

function payload() {
  const body = {
    title: form.title,
    location: form.location,
    attendee_count: form.attendee_count || 0,
    status: form.status,
    description: form.description,
    start_time: form.start_time,
    end_time: form.end_time,
  }
  if (form.organizer) {
    body.organizer = form.organizer
  } else {
    body.organizer = ''
  }
  return body
}

async function submit() {
  if (!form.title.trim() || !form.start_time || !form.end_time) {
    errorMsg.value = '请填写主题、开始时间与结束时间。'
    return
  }
  submitting.value = true
  errorMsg.value = ''
  try {
    const token = getCsrfToken()
    const res = await fetch(props.apiUrl, {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'X-CSRFToken': token } : {}),
      },
      body: JSON.stringify(payload()),
    })
    const data = await res.json()
    if (data.ok) {
      window.location.reload()
      return
    }
    errorMsg.value = formatErrors(data.errors)
  } catch (e) {
    errorMsg.value = '网络错误，请稍后重试。'
  } finally {
    submitting.value = false
  }
}

function formatErrors(errors) {
  if (!errors || typeof errors !== 'object') {
    return '保存失败。'
  }
  const lines = []
  for (const [k, v] of Object.entries(errors)) {
    const msg = Array.isArray(v) ? v.join(' ') : String(v)
    lines.push(`${k}: ${msg}`)
  }
  return lines.join(' ') || '保存失败。'
}
</script>

<style scoped>
.vue-toolbar {
  display: inline-block;
  vertical-align: middle;
}
.vue-modal-mask {
  position: fixed;
  inset: 0;
  z-index: 1050;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}
.vue-modal-panel {
  background: #fff;
  border-radius: 6px;
  width: 100%;
  max-width: 560px;
  max-height: 90vh;
  overflow: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}
.vue-modal-panel-wide {
  max-width: 640px;
}
.vue-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #e5e5e5;
}
.vue-modal-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}
.vue-modal-body {
  padding: 16px;
}
.vue-modal-footer {
  padding: 12px 16px;
  border-top: 1px solid #e5e5e5;
  text-align: right;
}
.vue-modal-footer .btn + .btn {
  margin-left: 8px;
}
.row-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 12px;
}
@media (max-width: 600px) {
  .row-fields {
    grid-template-columns: 1fr;
  }
}
</style>
