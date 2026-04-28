<template>
  <div class="vue-toolbar">
    <button type="button" class="btn btn-xs btn-default" @click="open">编辑</button>

    <ModalShell :show="show" title="编辑人员" @close="close">
      <p v-if="errorMsg" class="text-danger small">{{ errorMsg }}</p>
      <div class="form-group">
        <label>姓名 <span class="text-danger">*</span></label>
        <input v-model="form.name" type="text" class="form-control" required>
      </div>
      <div class="form-group">
        <label>工号</label>
        <input v-model="form.employee_no" type="text" class="form-control">
      </div>
      <div class="form-group">
        <label>部门</label>
        <select v-model="form.department" class="form-control">
          <option value="">— 请选择部门 —</option>
          <option v-for="dept in departmentOptions" :key="dept.id" :value="dept.id">{{ dept.name }}</option>
        </select>
      </div>
      <div class="form-group">
        <label>职务</label>
        <input v-model="form.position" type="text" class="form-control">
      </div>
      <div class="form-group">
        <label>角色</label>
        <input v-model="form.role" type="text" class="form-control">
      </div>
      <div class="form-group">
        <label>联系方式</label>
        <input v-model="form.phone" type="text" class="form-control">
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
import { computed, reactive, ref } from 'vue'
import ModalShell from './ModalShell.vue'
import { formatErrors, submitJson, toSpaApiUrl } from '../modal-utils.js'
import request from '../utils/request'

const props = defineProps({
  personId: { type: [String, Number], required: true },
  apiUrl: { type: String, required: true },
  departments: { type: Array, default: () => [] },
  useSpaApi: { type: Boolean, default: false },
})

const emit = defineEmits(['saved'])

const show = ref(false)
const submitting = ref(false)
const errorMsg = ref('')
const form = reactive({
  name: '',
  employee_no: '',
  department: '',
  position: '',
  role: '',
  phone: '',
})

const loadedDepartments = ref([])
const departmentOptions = computed(() => props.departments.length ? props.departments : loadedDepartments.value)

async function fetchDepartments() {
  if (props.departments.length) {
    return
  }
  try {
    const response = await fetch('/api/departments/', {
      credentials: 'same-origin'
    })
    if (response.ok) {
      const data = await response.json()
      loadedDepartments.value = data.departments || []
    }
  } catch (e) {
    console.error('Failed to fetch departments:', e)
  }
}

function open() {
  errorMsg.value = ''
  fetchDepartments()
  loadPersonData()
  show.value = true
}

function close() {
  show.value = false
}

async function loadPersonData() {
  try {
    if (props.useSpaApi) {
      const { data: personData } = await request.get(`${toSpaApiUrl(props.apiUrl)}${props.personId}/`)
      Object.assign(form, {
        name: personData.name || '',
        employee_no: personData.employee_no || '',
        department: personData.department || '',
        position: personData.position || '',
        role: personData.role || '',
        phone: personData.phone || '',
      })
      return
    }

    const response = await fetch(`/api/people/${props.personId}/`, {
      credentials: 'same-origin',
    })
    if (response.ok) {
      const personData = await response.json()
      Object.assign(form, {
        name: personData.name || '',
        employee_no: personData.employee_no || '',
        department: personData.department_id || '',
        position: personData.position || '',
        role: personData.role || '',
        phone: personData.phone || '',
      })
    } else {
      errorMsg.value = '加载人员信息失败，请刷新页面重试。'
    }
  } catch (e) {
    errorMsg.value = '网络错误，请稍后重试。'
  }
}

async function submit() {
  if (!form.name.trim()) {
    errorMsg.value = '请填写姓名。'
    return
  }
  submitting.value = true
  errorMsg.value = ''
  try {
    if (props.useSpaApi) {
      await request.patch(`${toSpaApiUrl(props.apiUrl)}${props.personId}/`, form)
      emit('saved')
      close()
      return
    }

    const data = await submitJson(`${props.apiUrl}${props.personId}/update/`, {
      method: 'PUT',
      body: form,
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
  display: inline;
}
</style>
