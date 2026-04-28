<template>
  <main class="container page-shell meetings-page-shell">
    <div class="page-header">
      <div class="page-header__inner">
        <div class="page-header__copy">
          <h2 class="page-header__title">会议管理</h2>
          <span class="page-header__subtitle">支持会议的创建、查询、审批状态查看等操作。</span>
        </div>
        <div class="d-flex gap-2">
          <MeetingsModal api-url="/api/v1/meetings/" :organizers="organizers" :use-spa-api="true" @saved="refreshMeetings" />
        </div>
      </div>
    </div>

    <div class="panel panel-default page-panel">
      <div class="panel-body">
        <div class="form-section-title">查询条件</div>
        <form class="row filter-form" @submit.prevent="searchMeetings">
          <div class="col-sm-6 col-md-3 form-group">
            <label class="form-label" for="meeting-keyword">关键词（主题/发起人）</label>
            <input id="meeting-keyword" v-model.trim="filters.search" type="text" class="form-control" placeholder="请输入关键词">
          </div>
          <div class="col-sm-6 col-md-3 form-group">
            <label class="form-label" for="meeting-date">会议日期（按开始日）</label>
            <input id="meeting-date" v-model="filters.date" type="date" class="form-control">
          </div>
          <div class="col-sm-6 col-md-3 form-group">
            <label class="form-label" for="meeting-status">会议状态</label>
            <select id="meeting-status" v-model="filters.status" class="form-control">
              <option value="">全部</option>
              <option v-for="statusOption in statusOptions" :key="statusOption.value" :value="statusOption.value">
                {{ statusOption.label }}
              </option>
            </select>
          </div>
          <div class="col-sm-6 col-md-3 form-group">
            <label class="form-label">&nbsp;</label>
            <div class="filter-actions">
              <button class="btn btn-primary" type="submit">查询</button>
              <button class="btn btn-default" type="button" @click="resetFilters">重置</button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
    <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>
    <div v-if="loading" class="text-muted">加载中...</div>

    <div v-else class="meetings-content-grid">
      <div class="meetings-list-col panel panel-default page-panel">
        <div class="panel-body">
          <div class="page-card-header">
            <div>
              <span class="form-section-title mb-0">
                会议列表
                <span class="meeting-view-tabs">
                  <a href="#" :class="{ active: viewType !== 'mine' }" @click.prevent="setViewType('all')">所有会议</a>
                  <a href="#" :class="{ active: viewType === 'mine' }" @click.prevent="setViewType('mine')">我的会议</a>
                </span>
              </span>
            </div>
          </div>

          <div class="table-responsive">
            <table class="table align-middle mb-0 meeting-list-table">
              <colgroup>
                <col style="width: 17%;">
                <col style="width: 15%;">
                <col style="width: 12%;">
                <col style="width: 10%;">
                <col style="width: 8%;">
                <col style="width: 11%;">
                <col style="width: 27%;">
              </colgroup>
              <thead>
                <tr>
                  <th class="meeting-col-title">会议主题</th>
                  <th class="meeting-col-time">会议时间</th>
                  <th class="meeting-col-location">地点</th>
                  <th class="meeting-col-organizer">发起人</th>
                  <th class="meeting-col-count">参会人数</th>
                  <th class="meeting-col-status">状态</th>
                  <th class="text-end meeting-col-actions">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="meeting in meetings" :key="meeting.id">
                  <td class="meeting-col-title">{{ meeting.title }}</td>
                  <td class="meeting-col-time">{{ meeting.start_time_display || formatDateTime(meeting.start_time) }}</td>
                  <td class="meeting-col-location">{{ meeting.location || '—' }}</td>
                  <td class="meeting-col-organizer">{{ meeting.organizer_name || '—' }}</td>
                  <td class="meeting-col-count">{{ meeting.attendee_count ?? 0 }}</td>
                  <td class="meeting-col-status">
                    <span class="label badge-status" :class="badgeClass(meeting.status_badge_class)">
                      {{ meeting.status_label }}
                    </span>
                  </td>
                  <td class="text-end meeting-col-actions">
                    <div class="btn-action-group">
                      <template v-if="viewType === 'mine'">
                        <button
                          v-if="canApply(meeting)"
                          type="button"
                          class="btn btn-xs btn-primary"
                          @click="applyMeeting(meeting)"
                        >申请</button>
                        <button v-else type="button" class="btn btn-xs btn-default" disabled title="仅草稿或未通过状态可申请">申请</button>
                        <a :href="meetingDetailUrl(meeting)" class="btn btn-xs btn-default">纪要编辑</a>
                        <button
                          type="button"
                          class="btn btn-xs btn-danger"
                          :disabled="!canApply(meeting)"
                          title="仅草稿或未通过状态可删除"
                          @click="deleteMeeting(meeting)"
                        >删除</button>
                      </template>
                      <template v-else>
                        <MeetingApprovalModal
                          v-if="meeting.status === 'pending'"
                          :api-url="`/api/v1/meetings/${meeting.id}/approve/`"
                          :meeting-title="meeting.title"
                          :status-label="meeting.status_label"
                          :use-spa-api="true"
                          @saved="refreshMeetings"
                        />
                        <button v-else type="button" class="btn btn-xs btn-default" disabled>审批</button>
                        <a :href="meetingDetailUrl(meeting)" class="btn btn-xs btn-default">编辑纪要</a>
                        <button type="button" class="btn btn-xs btn-danger" @click="deleteMeeting(meeting)">删除</button>
                      </template>
                    </div>
                  </td>
                </tr>
                <tr v-if="!meetings.length">
                  <td colspan="7" class="text-center text-muted">
                    <template v-if="viewType === 'mine'">暂无您发起的会议，请点击上方「新建会议」创建。</template>
                    <template v-else>暂无会议记录，请点击上方「新建会议」或到 <a href="/admin/">管理后台</a> 添加。</template>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <nav v-if="total > 0" class="pagination-shell">
            <ul v-if="pageRange.length > 1" class="pagination pagination-sm pull-right mb-0">
              <li :class="{ disabled: !previous }">
                <a v-if="previous" href="#" @click.prevent="changePage(page - 1)">上一页</a>
                <span v-else>上一页</span>
              </li>
              <li v-for="p in pageRange" :key="p" :class="{ active: p === page }">
                <a v-if="p !== page" href="#" @click.prevent="changePage(p)">{{ p }}</a>
                <span v-else>{{ p }}</span>
              </li>
              <li :class="{ disabled: !next }">
                <a v-if="next" href="#" @click.prevent="changePage(page + 1)">下一页</a>
                <span v-else>下一页</span>
              </li>
            </ul>
            <div class="clearfix"></div>
            <div class="pagination-summary">
              显示第 {{ startIndex }} - {{ endIndex }} 条，共 {{ total }} 条记录
            </div>
          </nav>
        </div>
      </div>

      <div class="meetings-stats-col panel panel-default page-panel meeting-stats-panel">
        <div class="panel-body">
          <div class="page-card-header">
            <span class="form-section-title mb-0">会议统计</span>
          </div>

          <template v-if="viewType === 'mine'">
            <div class="meeting-stats-section">
              <div class="meeting-stats-total">{{ meetingStats.mine_total }}</div>
              <div class="meeting-stats-total-label">我的会议</div>
            </div>

            <div class="meeting-stats-section">
              <div class="meeting-stats-section-title">我的会议</div>
              <div class="meeting-stats-list">
                <div class="meeting-stats-item">
                  <span>已申请</span>
                  <strong>{{ meetingStats.mine_applied }}</strong>
                </div>
                <div class="meeting-stats-item">
                  <span>草稿</span>
                  <strong>{{ meetingStats.mine_draft }}</strong>
                </div>
              </div>
            </div>

            <div class="meeting-stats-section">
              <div class="meeting-stats-section-title">已申请会议</div>
              <div class="meeting-stats-list">
                <div class="meeting-stats-item">
                  <span>待审批</span>
                  <strong>{{ meetingStats.applied_pending }}</strong>
                </div>
                <div class="meeting-stats-item">
                  <span>审批未通过</span>
                  <strong>{{ meetingStats.applied_unapproved }}</strong>
                </div>
                <div class="meeting-stats-item">
                  <span>审批通过</span>
                  <strong>{{ meetingStats.applied_approved }}</strong>
                </div>
                <div class="meeting-stats-item">
                  <span>过期</span>
                  <strong>{{ meetingStats.applied_expired }}</strong>
                </div>
              </div>
            </div>
          </template>

          <template v-else>
            <div class="meeting-stats-section">
              <div class="meeting-stats-total">{{ meetingStats.total }}</div>
              <div class="meeting-stats-total-label">会议总数</div>
            </div>

            <div class="meeting-stats-section">
              <div class="meeting-stats-section-title">审批状态</div>
              <div class="meeting-stats-list">
                <div class="meeting-stats-item">
                  <span>待审批</span>
                  <strong>{{ meetingStats.pending }}</strong>
                </div>
                <div class="meeting-stats-item">
                  <span>审批未通过</span>
                  <strong>{{ meetingStats.unapproved }}</strong>
                </div>
                <div class="meeting-stats-item">
                  <span>审批通过</span>
                  <strong>{{ meetingStats.approved }}</strong>
                </div>
                <div class="meeting-stats-item">
                  <span>过期</span>
                  <strong>{{ meetingStats.expired }}</strong>
                </div>
              </div>
            </div>

            <div class="meeting-stats-section">
              <div class="meeting-stats-section-title">已通过会议</div>
              <div class="meeting-stats-list">
                <div class="meeting-stats-item">
                  <span>未开始</span>
                  <strong>{{ meetingStats.approved_pending }}</strong>
                </div>
                <div class="meeting-stats-item">
                  <span>开始</span>
                  <strong>{{ meetingStats.in_progress }}</strong>
                </div>
                <div class="meeting-stats-item">
                  <span>结束</span>
                  <strong>{{ meetingStats.done }}</strong>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import MeetingApprovalModal from '../components/MeetingApprovalModal.vue'
import MeetingsModal from '../components/MeetingsModal.vue'
import request from '../utils/request'

const route = useRoute()
const router = useRouter()
const meetings = ref([])
const organizers = ref([])
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const total = ref(0)
const page = ref(Number(route.query.page) || 1)
const next = ref(null)
const previous = ref(null)
const viewType = ref(route.query.view === 'mine' ? 'mine' : 'all')
const filters = reactive({
  search: route.query.q || '',
  status: route.query.status || '',
  date: route.query.date || '',
})
const statusOptions = ref([
  { value: 'draft', label: '草稿' },
  { value: 'pending', label: '待审批' },
  { value: 'approved_pending', label: '审批通过未开始' },
  { value: 'in_progress', label: '进行中' },
  { value: 'done', label: '已结束' },
  { value: 'expired_cancelled', label: '未审批过期已取消' },
  { value: 'rejected', label: '审批未通过' },
])
const meetingStats = ref({
  total: 0,
  pending: 0,
  unapproved: 0,
  approved: 0,
  expired: 0,
  approved_pending: 0,
  in_progress: 0,
  done: 0,
  mine_total: 0,
  mine_applied: 0,
  mine_draft: 0,
  applied_pending: 0,
  applied_unapproved: 0,
  applied_approved: 0,
  applied_expired: 0,
})

const pageSize = 10

const pageRange = computed(() => {
  const totalPages = Math.ceil(total.value / pageSize) || 1
  const pages = []
  for (let i = 1; i <= totalPages; i++) {
    pages.push(i)
  }
  return pages
})

const startIndex = computed(() => total.value === 0 ? 0 : (page.value - 1) * pageSize + 1)
const endIndex = computed(() => Math.min(page.value * pageSize, total.value))

const buildParams = () => ({
  page: page.value,
  view: viewType.value,
  q: filters.search || undefined,
  status: filters.status || undefined,
  date: filters.date || undefined,
})

const syncQuery = () => {
  router.replace({
    path: '/meetings',
    query: {
      view: viewType.value,
      q: filters.search || undefined,
      date: filters.date || undefined,
      status: filters.status || undefined,
      page: page.value > 1 ? page.value : undefined,
    },
  })
}

const badgeClass = (statusBadgeClass) => `label-${statusBadgeClass || 'default'}`

const canApply = (meeting) => ['draft', 'rejected'].includes(meeting.status)

const meetingDetailUrl = (meeting) => `/meetings/${meeting.id}/info/`

const formatDateTime = (value) => {
  if (!value) {
    return '—'
  }

  return value.slice(0, 16).replace('T', ' ')
}

const fetchOptions = async () => {
  try {
    const { data } = await request.get('/meetings/options/')
    organizers.value = data.organizers || []
    statusOptions.value = data.statuses || statusOptions.value
  } catch (error) {
    errorMessage.value = error.message || '会议选项加载失败。'
  }
}

const fetchMeetings = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    syncQuery()
    const { data } = await request.get('/meetings/', { params: buildParams() })
    meetings.value = data.results || []
    total.value = data.count || 0
    next.value = data.next
    previous.value = data.previous
  } catch (error) {
    errorMessage.value = error.message || '会议列表加载失败。'
  } finally {
    loading.value = false
  }
}

const fetchMeetingStats = async () => {
  try {
    const { data } = await request.get('/meetings/stats/', { params: { view: viewType.value } })
    meetingStats.value = { ...meetingStats.value, ...data }
  } catch (error) {
    errorMessage.value = error.message || '会议统计加载失败。'
  }
}

const refreshMeetings = () => {
  successMessage.value = '会议信息已更新。'
  fetchOptions()
  fetchMeetingStats()
  fetchMeetings()
}

const searchMeetings = () => {
  successMessage.value = ''
  page.value = 1
  fetchMeetingStats()
  fetchMeetings()
}

const resetFilters = () => {
  filters.search = ''
  filters.status = ''
  filters.date = ''
  successMessage.value = ''
  page.value = 1
  fetchMeetingStats()
  fetchMeetings()
}

const setViewType = (targetViewType) => {
  if (viewType.value === targetViewType) {
    return
  }
  viewType.value = targetViewType
  successMessage.value = ''
  page.value = 1
  fetchMeetingStats()
  fetchMeetings()
}

const changePage = (targetPage) => {
  if (targetPage < 1) {
    return
  }
  successMessage.value = ''
  page.value = targetPage
  fetchMeetings()
}

const applyMeeting = async (meeting) => {
  if (!window.confirm('确定提交申请？')) {
    return
  }

  try {
    await request.post(`/meetings/${meeting.id}/apply/`)
    successMessage.value = `会议「${meeting.title}」已提交申请，等待审批。`
    fetchMeetingStats()
    fetchMeetings()
  } catch (error) {
    errorMessage.value = error.message || '提交会议申请失败。'
  }
}

const deleteMeeting = async (meeting) => {
  if (!canApply(meeting) && viewType.value === 'mine') {
    return
  }
  if (!window.confirm('确定删除该会议？')) {
    return
  }

  try {
    await request.delete(`/meetings/${meeting.id}/`)
    successMessage.value = '会议已删除。'
    fetchMeetingStats()
    fetchMeetings()
  } catch (error) {
    errorMessage.value = error.message || '删除会议失败。'
  }
}

onMounted(() => {
  fetchOptions()
  fetchMeetingStats()
  fetchMeetings()
})
</script>

<style scoped>
.meetings-page-shell {
  position: relative;
  width: 100%;
  max-width: 1320px;
  box-sizing: border-box;
  margin: 0 auto;
  padding-right: 360px;
}

.meetings-content-grid {
  display: block;
}

.meetings-list-col {
  display: block;
}

.meetings-stats-col {
  display: block;
}

.meeting-view-tabs {
  display: inline-flex;
  border: 1px solid #d0d5dd;
  border-radius: 6px;
  overflow: hidden;
  margin-left: 12px;
  vertical-align: middle;
}

.meeting-view-tabs a {
  padding: 3px 14px;
  font-size: 0.82rem;
  color: #344054;
  text-decoration: none;
  background: #fff;
  border-right: 1px solid #d0d5dd;
  line-height: 1.8;
  transition: background 0.15s;
}

.meeting-view-tabs a:last-child {
  border-right: none;
}

.meeting-view-tabs a.active {
  background: #f0f4ff;
  color: #2c5fe6;
  font-weight: 600;
}

.meeting-view-tabs a:hover:not(.active) {
  background: #f5f6fa;
}

.meeting-list-table {
  width: 100%;
  table-layout: fixed;
}

.meeting-list-table .meeting-col-title,
.meeting-list-table .meeting-col-location {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meeting-list-table .meeting-col-count {
  text-align: center;
}

.meeting-list-table .meeting-col-status,
.meeting-list-table .meeting-col-time,
.meeting-list-table .meeting-col-organizer,
.meeting-list-table .meeting-col-count {
  white-space: nowrap;
}

.meeting-list-table .meeting-col-actions {
  white-space: nowrap;
}

.btn-action-group {
  display: inline-flex;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
  flex-wrap: wrap;
}

.meeting-stats-panel {
  position: fixed;
  top: 220px;
  right: 80px;
  width: 320px;
}

.meeting-stats-section + .meeting-stats-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eef2f6;
}

.meeting-stats-total {
  color: #2f6fed;
  font-size: 36px;
  font-weight: 700;
  line-height: 1;
}

.meeting-stats-total-label {
  margin-top: 8px;
  color: #667085;
  font-size: 13px;
}

.meeting-stats-section-title {
  margin-bottom: 12px;
  color: #344054;
  font-size: 13px;
  font-weight: 600;
}

.meeting-stats-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.meeting-stats-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 10px;
  background: #f8fafc;
  color: #344054;
}

.meeting-stats-item strong {
  color: #101828;
  font-size: 18px;
}

@media (max-width: 1399px) {
  .meeting-list-table {
    min-width: 1080px;
    table-layout: auto;
  }

  .meeting-list-table .meeting-col-title,
  .meeting-list-table .meeting-col-location {
    white-space: normal;
  }
}

@media (max-width: 1199px) {
  .meetings-page-shell {
    width: auto;
    max-width: none;
    padding-right: 0;
  }

  .meeting-stats-panel {
    position: static;
    width: auto;
    margin-top: 16px;
  }
}
</style>
