<template>
  <div class="vue-toolbar">
    <button type="button" class="btn btn-xs btn-default" @click="open">编辑</button>

    <ModalShell :show="show" title="编辑事项" @close="close">
      <p v-if="errorMsg" class="text-danger small">{{ errorMsg }}</p>
      <div class="form-group">
        <label>事项 <span class="text-danger">*</span></label>
        <input v-model="form.title" type="text" class="form-control" required>
      </div>
      <div class="form-group">
        <label>开始时间</label>
        <input v-model="form.start_time" type="datetime-local" class="form-control">
      </div>
      <div class="form-group">
        <label>结束时间</label>
        <input v-model="form.end_time" type="datetime-local" class="form-control">
      </div>
      <div class="form-group">
        <label>状态</label>
        <select v-model="form.status" class="form-control">
          <option value="not_started">未开始</option>
          <option value="in_progress">进行中</option>
          <option value="finished">已结束</option>
        </select>
      </div>
      <div class="form-group">
        <label>事项人员</label>
        <div class="agenda-checkbox-group">
          <div v-if="assigneeOptions.length" v-for="person in assigneeOptions" :key="person.id" class="checkbox">
            <label>
              <input v-model="form.assignees" type="checkbox" :value="person.id">
              {{ person.name }}<span v-if="person.department" class="text-muted">（{{ person.department }}）</span>
            </label>
          </div>
          <p v-else class="text-muted small mb-0">当前会议暂无可选参与人。</p>
        </div>
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
  meetingId: { type: [String, Number], required: true },
  itemId: { type: [String, Number], required: true },
  apiUrl: { type: String, required: true },
})

const show = ref(false)
const submitting = ref(false)
const errorMsg = ref('')
const assigneeOptions = ref([])
const form = reactive({
  title: '',
  start_time: '',
  end_time: '',
  status: 'not_started',
  assignees: [],
})

function open() {
  errorMsg.value = ''
  loadAgendaItemData()
  show.value = true
}

function close() {
  show.value = false
}

async function loadAgendaItemData() {
  try {
    const response = await fetch(`${props.apiUrl}${props.itemId}/`, {
      credentials: 'same-origin',
    })
    if (response.ok) {
      const itemData = await response.json()
      assigneeOptions.value = itemData.assignee_options || []
      Object.assign(form, {
        title: itemData.title || '',
        start_time: itemData.start_time || '',
        end_time: itemData.end_time || '',
        status: itemData.status || 'not_started',
        assignees: (itemData.assignee_ids || []).map(id => Number(id)),
      })
    } else {
      errorMsg.value = '加载事项信息失败，请刷新页面重试。'
    }
  } catch (e) {
    errorMsg.value = '网络错误，请稍后重试。'
  }
}

async function submit() {
  if (!form.title.trim()) {
    errorMsg.value = '请填写事项。'
    return
  }
  submitting.value = true
  errorMsg.value = ''
  try {
    const payload = {
      ...form,
      assignees: form.assignees.map(id => Number(id)),
    }
    const data = await submitJson(`${props.apiUrl}${props.itemId}/update/`, {
      method: 'PUT',
      body: payload,
    })
    if (data.ok) {
      window.location.reload()
      return
    }
    errorMsg.value = formatErrors(data.errors, agendaErrorLabels)
  } catch (e) {
    errorMsg.value = '网络错误，请稍后重试。'
  } finally {
    submitting.value = false
  }
}

const agendaErrorLabels = {
  title: '事项',
  start_time: '开始时间',
  end_time: '结束时间',
  status: '状态',
  assignees: '事项人员',
  _: '错误',
}
</script>

<style scoped>
.vue-toolbar {
  display: inline-block;
  vertical-align: middle;
}
.agenda-checkbox-group {
  max-height: 220px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px 12px;
}
.mb-0 {
  margin-bottom: 0;
}
</style>
