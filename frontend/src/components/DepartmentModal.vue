<template>
  <div class="vue-toolbar">
    <button type="button" class="btn btn-primary" @click="open">新增部门</button>
    <a :href="fullPageUrl" class="btn btn-link btn-sm">或使用完整页面</a>

    <ModalShell :show="show" title="新增部门" @close="close">
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
    const data = await submitJson(props.apiUrl, {
      method: 'POST',
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
