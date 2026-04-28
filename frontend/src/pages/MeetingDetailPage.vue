<template>
  <main class="container my-4 meeting-detail-page">
    <div class="page-header">
      <div class="page-header__inner">
        <div class="page-header__copy">
          <h2 class="page-header__title">会议纪要</h2>
          <span class="page-header__subtitle">{{ meeting.title || '加载中...' }}</span>
        </div>
        <RouterLink class="btn btn-default" to="/meetings">返回会议列表</RouterLink>
      </div>
    </div>

    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
    <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>
    <div v-if="loading" class="text-muted">加载中...</div>

    <template v-else>
      <ul class="nav nav-tabs detail-nav">
        <li :class="{ active: activeTab === 'info' }">
          <RouterLink :to="tabUrl('info')">会议信息</RouterLink>
        </li>
        <li :class="{ active: activeTab === 'attendees' }">
          <RouterLink :to="tabUrl('attendees')">参与人信息</RouterLink>
        </li>
        <li :class="{ active: activeTab === 'attachments' }">
          <RouterLink :to="tabUrl('attachments')">附件信息</RouterLink>
        </li>
        <li :class="{ active: activeTab === 'agenda' }">
          <RouterLink :to="tabUrl('agenda')">会议事项</RouterLink>
        </li>
      </ul>

      <div class="card meeting-meta mt-3">
        <div class="card-body">
          <div class="row">
            <div class="col-md-3"><p><strong>发起人：</strong>{{ meeting.organizer_name || '未指定' }}</p></div>
            <div class="col-md-3"><p><strong>会议时间：</strong>{{ meetingTimeText }}</p></div>
            <div class="col-md-3"><p><strong>参会人数：</strong>{{ meeting.attendee_count || 0 }} 人</p></div>
            <div class="col-md-3"><p><strong>状态：</strong>{{ meeting.status_label || '—' }}</p></div>
          </div>
        </div>
      </div>

      <section v-if="activeTab === 'info'" class="row meeting-info-layout">
        <div class="col-md-8">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">会议信息</h5>
            </div>
            <div class="card-body">
              <form class="form-horizontal" @submit.prevent="saveMeetingInfo">
                <div class="form-group">
                  <label>会议主题 <span class="text-danger">*</span></label>
                  <input v-model="meetingForm.title" type="text" class="form-control" required>
                </div>
                <div class="form-group">
                  <label>发起人</label>
                  <select v-model="meetingForm.organizer" class="form-control">
                    <option value="">— 未指定 —</option>
                    <option v-for="organizer in organizers" :key="organizer.id" :value="String(organizer.id)">{{ organizer.name }}</option>
                  </select>
                </div>
                <div class="row">
                  <div class="col-md-6 form-group">
                    <label>开始时间 <span class="text-danger">*</span></label>
                    <input v-model="meetingForm.start_time" type="datetime-local" class="form-control" required>
                  </div>
                  <div class="col-md-6 form-group">
                    <label>结束时间 <span class="text-danger">*</span></label>
                    <input v-model="meetingForm.end_time" type="datetime-local" class="form-control" required>
                  </div>
                </div>
                <div class="form-group">
                  <label>地点</label>
                  <input v-model="meetingForm.location" type="text" class="form-control">
                </div>
                <div class="form-group">
                  <label>参会人数</label>
                  <input v-model.number="meetingForm.attendee_count" type="number" min="0" class="form-control">
                </div>
                <div class="form-group">
                  <label>状态</label>
                  <select v-model="meetingForm.status" class="form-control">
                    <option value="draft">草稿</option>
                    <option value="pending">待审批</option>
                    <option value="approved_pending">审批通过未开始</option>
                    <option value="rejected">审批未通过</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>说明</label>
                  <textarea v-model="meetingForm.description" rows="4" class="form-control"></textarea>
                </div>
                <button type="submit" class="btn btn-primary" :disabled="submittingInfo">
                  {{ submittingInfo ? '保存中...' : '保存会议信息' }}
                </button>
              </form>
              <div class="meeting-info-actions">
                <button type="button" class="btn btn-danger" @click="deleteMeeting">删除该会议</button>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-4">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">摘要</h5>
            </div>
            <div class="card-body">
              <p><strong>地点：</strong>{{ meeting.location || '未指定' }}</p>
              <p><strong>参会人数：</strong>{{ meeting.attendee_count || 0 }} 人</p>
              <p><strong>附件数量：</strong>{{ meeting.attachment_count || 0 }} 个</p>
              <p><strong>当前状态：</strong>{{ meeting.status_label || '—' }}</p>
            </div>
          </div>
        </div>
      </section>

      <section v-else-if="activeTab === 'attendees'" class="row attendees-layout">
        <div class="col-md-5">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">添加参与人</h5>
            </div>
            <div class="card-body">
              <div class="form-group">
                <input v-model.trim="personSearch" type="text" class="form-control" placeholder="搜索姓名或部门...">
              </div>
              <div class="attendee-select-actions">
                <button type="button" class="btn btn-default btn-sm" @click="selectAllPeople">全选</button>
                <button type="button" class="btn btn-default btn-sm" @click="clearSelectedPeople">全不选</button>
                <button type="button" class="btn btn-default btn-sm" @click="selectVisiblePeople">选择可见</button>
                <button type="button" class="btn btn-default btn-sm" @click="clearVisiblePeople">取消可见</button>
              </div>
              <p class="text-muted small">已选中: {{ selectedPersonIds.length }} / {{ availablePeople.length }} 人</p>
              <div class="person-checkbox-list">
                <div v-for="person in filteredPeople" :key="person.id" class="checkbox">
                  <label>
                    <input v-model="selectedPersonIds" type="checkbox" :value="person.id">
                    {{ person.name }}<span v-if="person.department_name" class="text-muted">（{{ person.department_name }}）</span>
                  </label>
                </div>
                <p v-if="!filteredPeople.length" class="text-muted">暂无可选人员</p>
              </div>
              <div class="checkbox">
                <label><input v-model="isRequired" type="checkbox"> 必须参加</label>
              </div>
              <button type="button" class="btn btn-primary" :disabled="!selectedPersonIds.length" @click="addAttendees">添加参与人</button>
            </div>
          </div>
        </div>

        <div class="col-md-7">
          <div class="card">
            <div class="card-header current-attendees-header">
              <h5 class="mb-0">当前参与人 ({{ attendees.length }})</h5>
              <select v-model="attendeeFilter" class="form-control input-sm attendee-filter">
                <option value="all">全部</option>
                <option value="accepted">已接受</option>
                <option value="declined">已拒绝</option>
                <option value="pending">待回复</option>
                <option value="required">必须参加</option>
                <option value="optional">可选</option>
              </select>
            </div>
            <div class="card-body">
              <div class="attendee-select-actions">
                <button type="button" class="btn btn-default btn-sm" :disabled="!selectedAttendeeIds.length" @click="batchAttendees('mark_required')">设为必须参加</button>
                <button type="button" class="btn btn-default btn-sm" :disabled="!selectedAttendeeIds.length" @click="batchAttendees('mark_optional')">设为可选</button>
                <button type="button" class="btn btn-danger btn-sm" :disabled="!selectedAttendeeIds.length" @click="batchAttendees('batch_remove')">批量移除</button>
              </div>
              <div class="table-responsive">
                <table class="table table-striped">
                  <thead>
                    <tr>
                      <th><input :checked="allVisibleAttendeesSelected" type="checkbox" @change="toggleVisibleAttendees($event)"></th>
                      <th>姓名</th>
                      <th>部门</th>
                      <th>回复状态</th>
                      <th>类型</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="attendee in filteredAttendees" :key="attendee.id">
                      <td><input v-model="selectedAttendeeIds" type="checkbox" :value="attendee.id"></td>
                      <td>{{ attendee.person_name }}</td>
                      <td>{{ attendee.department_name || '—' }}</td>
                      <td>{{ attendee.response_label }}</td>
                      <td>{{ attendee.is_required ? '必须参加' : '可选' }}</td>
                      <td><button type="button" class="btn btn-xs btn-danger" @click="removeAttendee(attendee)">移除</button></td>
                    </tr>
                    <tr v-if="!filteredAttendees.length">
                      <td colspan="6" class="text-center text-muted">暂无参与人</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section v-else-if="activeTab === 'attachments'" class="row attachments-layout">
        <div class="col-md-4">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">上传附件</h5>
            </div>
            <div class="card-body">
              <div class="form-group">
                <input ref="attachmentInput" type="file" class="form-control" @change="attachmentFile = $event.target.files[0] || null">
              </div>
              <button type="button" class="btn btn-primary" :disabled="!attachmentFile" @click="uploadAttachment">上传附件</button>
            </div>
          </div>
        </div>
        <div class="col-md-8">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">当前附件 ({{ attachments.length }})</h5>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="table table-striped">
                  <thead>
                    <tr>
                      <th>文件名</th>
                      <th>上传人</th>
                      <th>上传时间</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="attachment in attachments" :key="attachment.id">
                      <td>{{ attachment.filename }}</td>
                      <td>{{ attachment.uploaded_by_name || '-' }}</td>
                      <td>{{ attachment.created_at_display }}</td>
                      <td>
                        <a class="btn btn-xs btn-default" :href="attachment.file_url">下载</a>
                        <button type="button" class="btn btn-xs btn-danger" @click="deleteAttachment(attachment)">删除</button>
                      </td>
                    </tr>
                    <tr v-if="!attachments.length">
                      <td colspan="4" class="text-center text-muted">暂无附件</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section v-else class="agenda-section">
        <div class="card">
          <div class="card-header agenda-header">
            <h5 class="mb-0">事项列表</h5>
            <button type="button" class="btn btn-primary" @click="openAgendaModal()">添加事项</button>
          </div>
          <div class="card-body">
            <div v-for="item in agendaItems" :key="item.id" class="agenda-item-card">
              <div class="agenda-item-main">
                <div>
                  <h5>{{ item.title }}</h5>
                  <p class="text-muted mb-0">{{ item.start_time_display }} - {{ item.end_time_display }}</p>
                </div>
                <span class="label" :class="agendaBadgeClass(item.status)">{{ item.status_label }}</span>
              </div>
              <div class="agenda-item-actions">
                <button type="button" class="btn btn-xs btn-default" @click="openAgendaModal(item)">编辑</button>
                <button type="button" class="btn btn-xs btn-danger" @click="deleteAgendaItem(item)">删除</button>
              </div>
              <div class="agenda-assignees">
                <div v-for="assignment in item.assignees" :key="assignment.id" class="checkbox">
                  <label>
                    <input :checked="assignment.is_completed" type="checkbox" @change="toggleAssignment(assignment, $event)">
                    {{ assignment.person_name }}
                  </label>
                </div>
                <p v-if="!item.assignees.length" class="text-muted small">暂无事项人员</p>
              </div>
            </div>
            <p v-if="!agendaItems.length" class="text-center text-muted">暂无会议事项</p>
          </div>
        </div>
      </section>
    </template>

    <ModalShell :show="agendaModalVisible" :title="agendaForm.id ? '编辑事项' : '添加事项'" @close="closeAgendaModal">
      <div class="form-group">
        <label>事项 <span class="text-danger">*</span></label>
        <input v-model="agendaForm.title" type="text" class="form-control">
      </div>
      <div class="form-group">
        <label>开始时间</label>
        <input v-model="agendaForm.start_time" type="datetime-local" class="form-control">
      </div>
      <div class="form-group">
        <label>结束时间</label>
        <input v-model="agendaForm.end_time" type="datetime-local" class="form-control">
      </div>
      <div class="form-group">
        <label>状态</label>
        <select v-model="agendaForm.status" class="form-control">
          <option value="not_started">未开始</option>
          <option value="in_progress">进行中</option>
          <option value="finished">已结束</option>
        </select>
      </div>
      <div class="form-group">
        <label>事项人员</label>
        <div class="agenda-checkbox-group">
          <div v-for="person in assigneeOptions" :key="person.id" class="checkbox">
            <label>
              <input v-model="agendaForm.assignee_ids" type="checkbox" :value="person.id">
              {{ person.name }}<span v-if="person.department" class="text-muted">（{{ person.department }}）</span>
            </label>
          </div>
          <p v-if="!assigneeOptions.length" class="text-muted small mb-0">当前会议暂无可选参与人。</p>
        </div>
      </div>
      <template #footer>
        <button type="button" class="btn btn-default" @click="closeAgendaModal">取消</button>
        <button type="button" class="btn btn-primary" @click="saveAgendaItem">保存事项</button>
      </template>
    </ModalShell>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import ModalShell from '../components/ModalShell.vue'
import request from '../utils/request'

const route = useRoute()
const router = useRouter()
const meetingId = computed(() => route.params.id)
const activeTab = computed(() => route.meta.tab || 'info')
const loading = ref(true)
const errorMessage = ref('')
const successMessage = ref('')
const meeting = ref({})
const organizers = ref([])
const submittingInfo = ref(false)
const attendees = ref([])
const availablePeople = ref([])
const selectedPersonIds = ref([])
const selectedAttendeeIds = ref([])
const personSearch = ref('')
const attendeeFilter = ref('all')
const isRequired = ref(true)
const attachments = ref([])
const attachmentFile = ref(null)
const attachmentInput = ref(null)
const agendaItems = ref([])
const assigneeOptions = ref([])
const agendaModalVisible = ref(false)

const meetingForm = reactive({
  title: '',
  organizer: '',
  start_time: '',
  end_time: '',
  location: '',
  attendee_count: 0,
  status: 'draft',
  description: '',
})

const agendaForm = reactive({
  id: null,
  title: '',
  start_time: '',
  end_time: '',
  status: 'not_started',
  assignee_ids: [],
})

const toDatetimeLocal = (value) => (value ? value.slice(0, 16) : '')

const meetingTimeText = computed(() => {
  const start = meeting.value.start_time_display || toDatetimeLocal(meeting.value.start_time).replace('T', ' ')
  const end = meeting.value.end_time_display || toDatetimeLocal(meeting.value.end_time).replace('T', ' ')
  return end ? `${start} - ${end}` : start || '—'
})

const filteredPeople = computed(() => {
  const keyword = personSearch.value.toLowerCase()
  if (!keyword) {
    return availablePeople.value
  }
  return availablePeople.value.filter((person) => (
    person.name.toLowerCase().includes(keyword)
    || (person.department_name || '').toLowerCase().includes(keyword)
  ))
})

const filteredAttendees = computed(() => attendees.value.filter((attendee) => {
  if (attendeeFilter.value === 'all') return true
  if (attendeeFilter.value === 'required') return attendee.is_required
  if (attendeeFilter.value === 'optional') return !attendee.is_required
  return attendee.response === attendeeFilter.value
}))

const allVisibleAttendeesSelected = computed(() => (
  filteredAttendees.value.length > 0
  && filteredAttendees.value.every((attendee) => selectedAttendeeIds.value.includes(attendee.id))
))

const tabUrl = (tab) => {
  if (tab === 'info') {
    return `/meetings/${meetingId.value}/info/`
  }
  return `/meetings/${meetingId.value}/${tab}/`
}

const setMeetingForm = () => {
  Object.assign(meetingForm, {
    title: meeting.value.title || '',
    organizer: meeting.value.organizer ? String(meeting.value.organizer) : '',
    start_time: toDatetimeLocal(meeting.value.start_time),
    end_time: toDatetimeLocal(meeting.value.end_time),
    location: meeting.value.location || '',
    attendee_count: meeting.value.attendee_count || 0,
    status: meeting.value.status || 'draft',
    description: meeting.value.description || '',
  })
}

const loadMeeting = async () => {
  const { data } = await request.get(`/meetings/${meetingId.value}/`)
  meeting.value = data
  setMeetingForm()
}

const loadOptions = async () => {
  const { data } = await request.get('/meetings/options/')
  organizers.value = data.organizers || []
}

const loadPeople = async () => {
  const { data } = await request.get('/people/', { params: { page_size: 1000 } })
  const attendeePersonIds = new Set(attendees.value.map((attendee) => attendee.person))
  availablePeople.value = (data.results || []).filter((person) => !attendeePersonIds.has(person.id))
}

const loadAttendees = async () => {
  const { data } = await request.get(`/meetings/${meetingId.value}/attendees/`)
  attendees.value = data.results || []
  selectedAttendeeIds.value = []
  await loadPeople()
}

const loadAttachments = async () => {
  const { data } = await request.get(`/meetings/${meetingId.value}/attachments/`)
  attachments.value = data.results || []
}

const loadAgenda = async () => {
  const { data } = await request.get(`/meetings/${meetingId.value}/agenda-items/`)
  agendaItems.value = data.results || []
  assigneeOptions.value = data.assignee_options || []
}

const loadTabData = async () => {
  if (activeTab.value === 'attendees') {
    await loadAttendees()
  } else if (activeTab.value === 'attachments') {
    await loadAttachments()
  } else if (activeTab.value === 'agenda') {
    await loadAgenda()
  }
}

const loadPage = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    await Promise.all([loadMeeting(), loadOptions()])
    await loadTabData()
  } catch (error) {
    errorMessage.value = error.message || '会议详情加载失败。'
  } finally {
    loading.value = false
  }
}

const saveMeetingInfo = async () => {
  submittingInfo.value = true
  errorMessage.value = ''
  try {
    const { data } = await request.patch(`/meetings/${meetingId.value}/`, {
      ...meetingForm,
      organizer: meetingForm.organizer || null,
      attendee_count: meetingForm.attendee_count || 0,
    })
    meeting.value = data
    setMeetingForm()
    successMessage.value = '会议信息已保存。'
  } catch (error) {
    errorMessage.value = error.message || '保存会议信息失败。'
  } finally {
    submittingInfo.value = false
  }
}

const deleteMeeting = async () => {
  if (!window.confirm('确定删除该会议？此操作不可恢复。')) {
    return
  }
  try {
    await request.delete(`/meetings/${meetingId.value}/`)
    router.push('/meetings')
  } catch (error) {
    errorMessage.value = error.message || '删除会议失败。'
  }
}

const selectAllPeople = () => {
  selectedPersonIds.value = availablePeople.value.map((person) => person.id)
}

const clearSelectedPeople = () => {
  selectedPersonIds.value = []
}

const selectVisiblePeople = () => {
  selectedPersonIds.value = Array.from(new Set([
    ...selectedPersonIds.value,
    ...filteredPeople.value.map((person) => person.id),
  ]))
}

const clearVisiblePeople = () => {
  const visibleIds = new Set(filteredPeople.value.map((person) => person.id))
  selectedPersonIds.value = selectedPersonIds.value.filter((id) => !visibleIds.has(id))
}

const addAttendees = async () => {
  try {
    await request.post(`/meetings/${meetingId.value}/attendees/`, {
      attendees: selectedPersonIds.value,
      is_required: isRequired.value,
    })
    selectedPersonIds.value = []
    successMessage.value = '参与人已添加。'
    await Promise.all([loadMeeting(), loadAttendees()])
  } catch (error) {
    errorMessage.value = error.message || '添加参与人失败。'
  }
}

const toggleVisibleAttendees = (event) => {
  const visibleIds = filteredAttendees.value.map((attendee) => attendee.id)
  if (event.target.checked) {
    selectedAttendeeIds.value = Array.from(new Set([...selectedAttendeeIds.value, ...visibleIds]))
    return
  }
  const visibleSet = new Set(visibleIds)
  selectedAttendeeIds.value = selectedAttendeeIds.value.filter((id) => !visibleSet.has(id))
}

const batchAttendees = async (action) => {
  if (action === 'batch_remove' && !window.confirm('确定要批量移除选中的参与人吗？')) {
    return
  }
  try {
    await request.post(`/meetings/${meetingId.value}/attendees/batch/`, {
      action,
      attendee_ids: selectedAttendeeIds.value,
    })
    successMessage.value = '参与人信息已更新。'
    await Promise.all([loadMeeting(), loadAttendees()])
  } catch (error) {
    errorMessage.value = error.message || '批量操作失败。'
  }
}

const removeAttendee = async (attendee) => {
  if (!window.confirm('确定要移除此参与人吗？')) {
    return
  }
  try {
    await request.delete(`/meetings/${meetingId.value}/attendees/${attendee.id}/`)
    successMessage.value = '参与人已移除。'
    await Promise.all([loadMeeting(), loadAttendees()])
  } catch (error) {
    errorMessage.value = error.message || '移除参与人失败。'
  }
}

const uploadAttachment = async () => {
  if (!attachmentFile.value) {
    return
  }
  const payload = new FormData()
  payload.append('file', attachmentFile.value)
  try {
    await request.post(`/meetings/${meetingId.value}/attachments/`, payload)
    attachmentFile.value = null
    if (attachmentInput.value) {
      attachmentInput.value.value = ''
    }
    successMessage.value = '附件已上传。'
    await Promise.all([loadMeeting(), loadAttachments()])
  } catch (error) {
    errorMessage.value = error.message || '上传附件失败。'
  }
}

const deleteAttachment = async (attachment) => {
  if (!window.confirm('确定删除该附件吗？')) {
    return
  }
  try {
    await request.delete(`/meetings/${meetingId.value}/attachments/${attachment.id}/`)
    successMessage.value = '附件已删除。'
    await Promise.all([loadMeeting(), loadAttachments()])
  } catch (error) {
    errorMessage.value = error.message || '删除附件失败。'
  }
}

const agendaBadgeClass = (status) => ({
  not_started: 'label-default',
  in_progress: 'label-info',
  finished: 'label-success',
}[status] || 'label-default')

const openAgendaModal = (item = null) => {
  Object.assign(agendaForm, {
    id: item?.id || null,
    title: item?.title || '',
    start_time: toDatetimeLocal(item?.start_time),
    end_time: toDatetimeLocal(item?.end_time),
    status: item?.status || 'not_started',
    assignee_ids: item ? item.assignees.map((assignment) => assignment.person) : [],
  })
  agendaModalVisible.value = true
}

const closeAgendaModal = () => {
  agendaModalVisible.value = false
}

const saveAgendaItem = async () => {
  if (!agendaForm.title.trim()) {
    errorMessage.value = '请填写事项。'
    return
  }
  try {
    const payload = {
      title: agendaForm.title,
      start_time: agendaForm.start_time,
      end_time: agendaForm.end_time,
      status: agendaForm.status,
      assignee_ids: agendaForm.assignee_ids,
    }
    if (agendaForm.id) {
      await request.patch(`/meetings/${meetingId.value}/agenda-items/${agendaForm.id}/`, payload)
    } else {
      await request.post(`/meetings/${meetingId.value}/agenda-items/`, payload)
    }
    agendaModalVisible.value = false
    successMessage.value = '会议事项已保存。'
    await loadAgenda()
  } catch (error) {
    errorMessage.value = error.message || '保存会议事项失败。'
  }
}

const deleteAgendaItem = async (item) => {
  if (!window.confirm('确定删除该事项吗？')) {
    return
  }
  try {
    await request.delete(`/meetings/${meetingId.value}/agenda-items/${item.id}/`)
    successMessage.value = '会议事项已删除。'
    await loadAgenda()
  } catch (error) {
    errorMessage.value = error.message || '删除会议事项失败。'
  }
}

const toggleAssignment = async (assignment, event) => {
  try {
    await request.patch(`/meetings/${meetingId.value}/agenda-assignments/${assignment.id}/`, {
      is_completed: event.target.checked,
    })
    assignment.is_completed = event.target.checked
  } catch (error) {
    errorMessage.value = error.message || '更新完成状态失败。'
    event.target.checked = assignment.is_completed
  }
}

watch(
  () => route.fullPath,
  async () => {
    successMessage.value = ''
    await loadPage()
  }
)

onMounted(loadPage)
</script>

<style scoped>
.meeting-detail-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-nav {
  margin-top: 4px;
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

.mt-3 {
  margin-top: 1rem;
}

.mb-0 {
  margin-bottom: 0;
}

.meeting-meta p {
  margin-bottom: 0;
}

.meeting-info-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.attendee-select-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}

.person-checkbox-list,
.agenda-checkbox-group {
  max-height: 280px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px 12px;
  margin-bottom: 12px;
}

.current-attendees-header,
.agenda-header,
.agenda-item-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.attendee-filter {
  width: 130px;
}

.agenda-item-card {
  padding: 14px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  margin-bottom: 12px;
}

.agenda-item-actions {
  margin-top: 10px;
}

.agenda-assignees {
  margin-top: 10px;
}

.agenda-assignees .checkbox {
  display: inline-block;
  margin-right: 14px;
}

@media (max-width: 767px) {
  .current-attendees-header,
  .agenda-header,
  .agenda-item-main {
    align-items: stretch;
    flex-direction: column;
  }

  .attendee-filter {
    width: 100%;
  }
}
</style>
