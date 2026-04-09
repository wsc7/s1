<template>
  <div class="vue-toolbar">
    <button type="button" class="btn btn-primary" @click="open">添加参与人</button>

    <ModalShell :show="show" title="添加参与人" :wide="true" @close="close">
      <div class="form-group">
        <label>搜索姓名、部门或工号</label>
        <div class="input-group">
          <input v-model.trim="searchText" type="text" class="form-control" placeholder="搜索姓名或部门...">
          <span class="input-group-btn">
            <button type="button" class="btn btn-default" @click="clearSearch">清空</button>
          </span>
        </div>
      </div>

      <div style="margin-bottom: 10px;">
        <button type="button" class="btn btn-xs btn-default" @click="selectAll">全选</button>
        <button type="button" class="btn btn-xs btn-default" @click="deselectAll">全不选</button>
        <button type="button" class="btn btn-xs btn-default" @click="selectVisible">选择可见</button>
        <button type="button" class="btn btn-xs btn-default" @click="deselectVisible">取消可见</button>
      </div>

      <div class="attendee-list-box">
        <div v-if="filteredAttendees.length === 0" class="text-muted">暂无匹配人员</div>
        <div v-for="person in filteredAttendees" :key="person.id" class="checkbox attendee-item">
          <label>
            <input :checked="selectedIds.includes(person.id)" type="checkbox" @change="toggleSelection(person.id, $event.target.checked)">
            <span>{{ person.name }}</span>
            <small class="text-muted" v-if="person.department || person.employee_no">
              （{{ [person.department, person.employee_no].filter(Boolean).join(' / ') }}）
            </small>
          </label>
        </div>
      </div>

      <div class="text-muted small" style="margin-top: 8px;">
        已选中: <span>{{ selectedIds.length }}</span> / <span>{{ attendees.length }}</span> 人
      </div>

      <div class="checkbox" style="margin-top: 15px;">
        <label>
          <input v-model="isRequired" type="checkbox">
          必须参加
        </label>
      </div>

      <template #footer>
        <form ref="formRef" method="post" :action="submitUrl" style="display: inline;">
          <input type="hidden" name="csrfmiddlewaretoken" :value="csrfToken">
          <input type="hidden" name="form_type" value="attendees">
          <input v-if="isRequired" type="hidden" name="is_required" value="on">
          <input v-for="id in selectedIds" :key="`selected-${id}`" type="hidden" name="attendees" :value="id">
        </form>
        <button type="button" class="btn btn-default" @click="close">取消</button>
        <button type="button" class="btn btn-primary" :disabled="selectedIds.length === 0" @click="submit">添加参与人</button>
      </template>
    </ModalShell>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import ModalShell from './ModalShell.vue'

const props = defineProps({
  attendees: { type: Array, default: () => [] },
  submitUrl: { type: String, required: true },
  csrfToken: { type: String, default: '' },
})

const show = ref(false)
const searchText = ref('')
const selectedIds = ref([])
const isRequired = ref(true)
const formRef = ref(null)

const filteredAttendees = computed(() => {
  const keyword = searchText.value.trim().toLowerCase()
  if (!keyword) {
    return props.attendees
  }
  return props.attendees.filter((person) => (person.search_text || '').includes(keyword))
})

function open() {
  searchText.value = ''
  selectedIds.value = []
  isRequired.value = true
  show.value = true
}

function close() {
  show.value = false
}

function clearSearch() {
  searchText.value = ''
}

function toggleSelection(id, checked) {
  if (checked) {
    if (!selectedIds.value.includes(id)) {
      selectedIds.value = [...selectedIds.value, id]
    }
    return
  }
  selectedIds.value = selectedIds.value.filter((item) => item !== id)
}

function selectAll() {
  selectedIds.value = props.attendees.map((person) => person.id)
}

function deselectAll() {
  selectedIds.value = []
}

function selectVisible() {
  const merged = new Set(selectedIds.value)
  filteredAttendees.value.forEach((person) => merged.add(person.id))
  selectedIds.value = Array.from(merged)
}

function deselectVisible() {
  const visibleIds = new Set(filteredAttendees.value.map((person) => person.id))
  selectedIds.value = selectedIds.value.filter((id) => !visibleIds.has(id))
}

function submit() {
  if (selectedIds.value.length === 0 || !formRef.value) {
    return
  }
  formRef.value.submit()
}
</script>

<style scoped>
.vue-toolbar {
  display: inline-block;
  vertical-align: middle;
}
.attendee-list-box {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px;
}
</style>
