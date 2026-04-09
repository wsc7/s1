<template>
  <div class="vue-toolbar">
    <button type="button" class="btn btn-xs btn-default" @click="open">编辑</button>

    <ModalShell :show="show" title="编辑部门" @close="close">
      <p v-if="errorMsg" class="text-danger small">{{ errorMsg }}</p>
      <div class="form-group">
        <label>部门名称 <span class="text-danger">*</span></label>
        <input v-model="form.name" type="text" class="form-control" required>
      </div>
      <div class="form-group">
        <label>描述</label>
        <textarea v-model="form.description" class="form-control" rows="3"></textarea>
      </div>

      <template #footer>
        <button type="button" class="btn btn-default" @click="close">取消</button>
        <button type="button" class="btn btn-primary" :disabled="submitting" @click="submit">
          {{ submitting ? '保存中…' : '保存' }}
        </button>
      </template>
    </ModalShell>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import ModalShell from './ModalShell.vue'
import { formatErrors, submitJson } from '../modal-utils.js'

const props = defineProps({
  departmentId: { type: [String, Number], required: true },
  apiUrl: { type: String, required: true },
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
  loadDepartmentData()
  show.value = true
}

function close() {
  show.value = false
}

async function loadDepartmentData() {
  try {
    const response = await fetch(`${props.apiUrl}${props.departmentId}/`, {
      credentials: 'same-origin',
    })
    if (response.ok) {
      const departmentData = await response.json()
      Object.assign(form, {
        name: departmentData.name || '',
        description: departmentData.description || '',
      })
    } else {
      errorMsg.value = '加载部门信息失败，请刷新页面重试。'
    }
  } catch (e) {
    errorMsg.value = '网络错误，请稍后重试。'
  }
}

async function submit() {
  if (!form.name.trim()) {
    errorMsg.value = '请填写部门名称。'
    return
  }
  submitting.value = true
  errorMsg.value = ''
  try {
    const data = await submitJson(`${props.apiUrl}${props.departmentId}/update/`, {
      method: 'PUT',
      body: form,
    })
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
</script>

<style scoped>
.vue-toolbar {
  display: inline-block;
  vertical-align: middle;
}
</style>
