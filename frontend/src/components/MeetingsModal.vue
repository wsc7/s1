<template>
  <div class="vue-toolbar">
    <button type="button" class="btn btn-primary" @click="open">新建会议</button>

    <ModalShell :show="show" title="新建会议" :wide="true" @close="close">
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
        <label>说明</label>
        <textarea v-model="form.description" class="form-control" rows="3"></textarea>
      </div>

      <a :href="fullPageUrl" class="btn btn-link">或使用完整页面</a>
      <template #footer>
        <button type="button" class="btn btn-default" @click="close">取消</button>
        <button type="button" class="btn btn-default" :disabled="!!submitting" @click="submit('draft')">
          {{ submitting === 'draft' ? '保存中…' : '保存' }}
        </button>
        <button type="button" class="btn btn-primary" :disabled="!!submitting" @click="submit('pending')">
          {{ submitting === 'pending' ? '申请中…' : '申请' }}
        </button>
      </template>
    </ModalShell>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import ModalShell from './ModalShell.vue'
import { formatErrors, submitJson, toSpaApiUrl } from '../modal-utils.js'
import request from '../utils/request'

const props = defineProps({
  apiUrl: { type: String, required: true },
  fullPageUrl: { type: String, default: '/meetings/add/' },
  organizers: { type: Array, default: () => [] },
  useSpaApi: { type: Boolean, default: false },
})

const emit = defineEmits(['saved'])

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
    description: '',
  })
  show.value = true
}

function close() {
  if (submitting.value) {
    return
  }
  show.value = false
}

function buildPayload(status) {
  return {
    title: form.title,
    location: form.location,
    attendee_count: form.attendee_count || 0,
    status,
    description: form.description,
    start_time: form.start_time,
    end_time: form.end_time,
    organizer: form.organizer || null,
  }
}

async function submit(status) {
  if (!form.title.trim() || !form.start_time || !form.end_time) {
    errorMsg.value = '请填写主题、开始时间与结束时间。'
    return
  }
  submitting.value = status
  errorMsg.value = ''
  try {
    if (props.useSpaApi) {
      await request.post(toSpaApiUrl(props.apiUrl), buildPayload(status))
      emit('saved')
      show.value = false
      return
    }

    const data = await submitJson(props.apiUrl, {
      method: 'POST',
      body: buildPayload(status),
    })
    if (data.ok) {
      window.location.reload()
      return
    }
    errorMsg.value = formatErrors(data.errors)
  } catch (e) {
    errorMsg.value = e.message || '网络错误，请稍后重试。'
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
