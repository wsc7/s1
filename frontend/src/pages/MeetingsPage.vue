<template>
  <div class="page-shell">
    <div class="page-header">
      <h2 class="page-header__title">会议管理</h2>
      <span class="page-header__subtitle">支持会议的创建、查询、审批状态查看等操作。</span>
    </div>

    <div class="panel panel-default page-panel">
      <div class="panel-body">
        <div class="form-section-title">查询条件</div>
        <form class="row filter-form" @submit.prevent="searchMeetings">
          <div class="col-sm-6 col-md-3 form-group">
            <label class="form-label" for="meeting-keyword">关键词（主题/地点/描述）</label>
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
    <div v-if="loading" class="text-muted">加载中...</div>

    <div v-else class="meetings-content-grid">
      <div class="panel panel-default page-panel">
        <div class="panel-body">
          <div class="page-card-header">
            <span class="form-section-title mb-0">会议列表</span>
          </div>

          <div class="table-responsive">
            <table v-if="meetings.length" class="table table-striped align-middle mb-0">
              <thead>
                <tr>
                  <th>会议主题</th>
                  <th>会议时间</th>
                  <th>地点</th>
                  <th>发起人</th>
                  <th>参会人数</th>
                  <th>状态</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="meeting in meetings" :key="meeting.id">
                  <td>{{ meeting.title }}</td>
                  <td>{{ formatDateTime(meeting.start_time) }}</td>
                  <td>{{ meeting.location || '—' }}</td>
                  <td>{{ meeting.organizer_name || '—' }}</td>
                  <td>{{ meeting.attendee_count ?? '—' }}</td>
                  <td>
                    <span class="label badge-status" :class="badgeClass(meeting.status_badge_class)">
                      {{ meeting.status_label }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-else class="text-center text-muted" style="padding: 24px 12px;">暂无会议记录。</div>
          </div>

          <div class="clearfix pagination-shell">
            <div class="pull-left pagination-summary">共 {{ total }} 条，当前第 {{ page }} 页</div>
            <div class="pull-right">
              <button class="btn btn-default" :disabled="!previous" @click="changePage(page - 1)">上一页</button>
              <button class="btn btn-default" style="margin-left: 8px;" :disabled="!next" @click="changePage(page + 1)">下一页</button>
            </div>
          </div>
        </div>
      </div>

      <div class="panel panel-default page-panel meeting-stats-panel">
        <div class="panel-body">
          <div class="page-card-header">
            <span class="form-section-title mb-0">会议统计</span>
          </div>

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
                <span>未审批</span>
                <strong>{{ meetingStats.unapproved }}</strong>
              </div>
              <div class="meeting-stats-item">
                <span>审批通过</span>
                <strong>{{ meetingStats.approved }}</strong>
              </div>
            </div>
          </div>

          <div class="meeting-stats-section">
            <div class="meeting-stats-section-title">审批通过后状态</div>
            <div class="meeting-stats-list">
              <div class="meeting-stats-item">
                <span>未开始</span>
                <strong>{{ meetingStats.approvedPending }}</strong>
              </div>
              <div class="meeting-stats-item">
                <span>开始</span>
                <strong>{{ meetingStats.inProgress }}</strong>
              </div>
              <div class="meeting-stats-item">
                <span>结束</span>
                <strong>{{ meetingStats.done }}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

import request from '../utils/request'

const meetings = ref([])
const allMeetings = ref([])
const loading = ref(false)
const errorMessage = ref('')
const total = ref(0)
const page = ref(1)
const next = ref(null)
const previous = ref(null)
const filters = reactive({
  search: '',
  status: '',
  date: '',
})
const statusOptions = [
  { value: 'draft', label: '草稿' },
  { value: 'pending', label: '待审批' },
  { value: 'approved_pending', label: '审批通过未开始' },
  { value: 'in_progress', label: '进行中' },
  { value: 'done', label: '已结束' },
  { value: 'expired_cancelled', label: '未审批过期已取消' },
  { value: 'rejected', label: '审批未通过' },
]

const meetingStats = computed(() => {
  const stats = {
    total: allMeetings.value.length,
    pending: 0,
    unapproved: 0,
    approved: 0,
    approvedPending: 0,
    inProgress: 0,
    done: 0,
  }

  allMeetings.value.forEach((meeting) => {
    if (meeting.status === 'pending') {
      stats.pending += 1
      stats.unapproved += 1
    }

    if (meeting.status === 'expired_cancelled') {
      stats.unapproved += 1
    }

    if (['approved_pending', 'in_progress', 'done'].includes(meeting.status)) {
      stats.approved += 1
    }

    if (meeting.status === 'approved_pending') {
      stats.approvedPending += 1
    }

    if (meeting.status === 'in_progress') {
      stats.inProgress += 1
    }

    if (meeting.status === 'done') {
      stats.done += 1
    }
  })

  return stats
})

const buildParams = () => ({
  page: page.value,
  search: filters.search || undefined,
  status: filters.status || undefined,
  date: filters.date || undefined,
})

const badgeClass = (statusBadgeClass) => `label-${statusBadgeClass || 'default'}`

const formatDateTime = (value) => {
  if (!value) {
    return '—'
  }

  return value.slice(0, 16).replace('T', MA ')
}

const fetchMeetings = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
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
    const { data } = await request.get('/meetings/', { params: { page_size: 1000 } })
    allMeetings.value = data.results || []
  } catch (error) {
    errorMessage.value = error.message || '会议统计加载失败。'
  }
}

const searchMeetings = () => {
  page.value = 1
  fetchMeetings()
}

const resetFilters = () => {
  filters.search = ''
  filters.status = ''
  filters.date = ''
  page.value = 1
  fetchMeetings()
}

const changePage = (targetPage) => {
  if (targetPage < 1) {
    return
  }
  page.value = targetPage
  fetchMeetings()
}

onMounted(() => {
  fetchMeetingStats()
  fetchMeetings()
})
</script>

<style scoped>
.meetings-content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 16px;
  align-items: start;
}

.meeting-stats-panel {
  position: sticky;
  top: 24px;
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

@media (max-width: 991px) {
  .meetings-content-grid {
    grid-template-columns: 1fr;
  }

  .meeting-stats-panel {
    position: static;
  }
}
</style>
