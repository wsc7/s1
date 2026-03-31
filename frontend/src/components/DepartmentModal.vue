<template>
  <div class="vue-toolbar">
    <button type="button" class="btn btn-primary" @click="open">新增部门</button>
    <a :href="fullPageUrl" class="btn btn-link btn-sm">或使用完整页面</a>

    <Teleport to="body">
      <div v-show="show" class="vue-modal-mask" @click.self="close">
        <div class="vue-modal-panel">
          <div class="vue-modal-header">
            <h4 class="vue-modal-title">新增部门</h4>
            <button type="button" class="close" aria-label="关闭" @click="close">&times;</button>
          </div>
          <div class="vue-modal-body">
            <p v-if="errorMsg" class="text-danger small">{{ errorMsg }}</p>
            <div class="form-group">
              <label>部门名称 <span class="text-danger">*</span></label>
              <input v-model="form.name" type="text" class="form-control" required>
            </div>
            <div class="form-group">
              <label>描述</label>
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
  fullPageUrl: { type: String, default: '/departments/add/' },
})

const show = ref(false)
const submitting = ref(false)
const errorMsg = ref('')
const form = reactive({
  name: '',
  description: '',
})

function open() {
  errorMsg.value = ''
  Object.assign(form, {
    name: '',
    description: '',
  })
  show.value = true
}

function close() {
  show.value = false
}

async function submit() {
  if (!form.name.trim()) {
    errorMsg.value = '请填写部门名称。'
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
      body: JSON.stringify(form),
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
  max-width: 520px;
  max-height: 90vh;
  overflow: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
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
</style>