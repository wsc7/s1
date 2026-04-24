<template>
  <div class="page-shell">
    <div class="page-header">
      <h2 class="page-header__title">部门管理</h2>
      <span class="page-header__subtitle">维护部门基本信息。</span>
    </div>

    <div class="panel panel-default page-panel">
      <div class="panel-body">
        <div class="form-section-title">查询条件</div>
        <form class="row filter-form" @submit.prevent="searchDepartments">
          <div class="col-sm-6 form-group">
            <label class="form-label" for="department-keyword">部门名称 / 描述</label>
            <input id="department-keyword" v-model.trim="filters.search" type="text" class="form-control" placeholder="请输入部门名称或描述">
          </div>
          <div class="col-sm-6 form-group">
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

    <div v-else class="panel panel-default page-panel">
      <div class="panel-body">
        <div class="page-card-header">
          <span class="form-section-title mb-0">部门列表</span>
        </div>

        <div class="table-responsive">
          <table v-if="departments.length" class="table table-striped align-middle mb-0">
            <thead>
              <tr>
                <th>部门名称</th>
                <th>描述</th>
                <th>创建时间</th>
                <th>更新时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="department in departments" :key="department.id">
                <td>{{ department.name }}</td>
                <td>{{ department.description || '—' }}</td>
                <td>{{ formatDateTime(department.created_at) }}</td>
                <td>{{ formatDateTime(department.updated_at) }}</td>
              </tr>
            </tbody>
          </table>
          <div v-else class="text-center text-muted" style="padding: 24px 12px;">暂无部门记录。</div>
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
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'

import request from '../utils/request'

const departments = ref([])
const loading = ref(false)
const errorMessage = ref('')
const total = ref(0)
const page = ref(1)
const next = ref(null)
const previous = ref(null)
const filters = reactive({
  search: '',
})

const buildParams = () => ({
  page: page.value,
  search: filters.search || undefined,
})

const formatDateTime = (value) => {
  if (!value) {
    return '—'
  }

  return value.slice(0, 16).replace('T', ' ')
}

const fetchDepartments = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const { data } = await request.get('/departments/', { params: buildParams() })
    departments.value = data.results || []
    total.value = data.count || 0
    next.value = data.next
    previous.value = data.previous
  } catch (error) {
    errorMessage.value = error.message || '部门列表加载失败。'
  } finally {
    loading.value = false
  }
}

const searchDepartments = () => {
  page.value = 1
  fetchDepartments()
}

const resetFilters = () => {
  filters.search = ''
  page.value = 1
  fetchDepartments()
}

const changePage = (targetPage) => {
  if (targetPage < 1) {
    return
  }
  page.value = targetPage
  fetchDepartments()
}

onMounted(() => {
  fetchDepartments()
})
</script>
