<template>
  <div class="page-shell">
    <div class="page-header">
      <h2 class="page-header__title">人员管理</h2>
      <span class="page-header__subtitle">维护人员基本信息、部门信息及角色权限。</span>
    </div>

    <div class="panel panel-default page-panel">
      <div class="panel-body">
        <div class="form-section-title">查询条件</div>
        <form class="row filter-form" @submit.prevent="searchPeople">
          <div class="col-sm-6 col-md-3 form-group">
            <label class="form-label" for="people-keyword">姓名 / 工号</label>
            <input id="people-keyword" v-model.trim="filters.search" type="text" class="form-control" placeholder="请输入姓名或工号">
          </div>
          <div class="col-sm-6 col-md-3 form-group">
            <label class="form-label" for="people-department">所属部门</label>
            <select id="people-department" v-model="filters.department_id" class="form-control">
              <option value="">全部</option>
              <option v-for="department in departments" :key="department.id" :value="String(department.id)">
                {{ department.name }}
              </option>
            </select>
          </div>
          <div class="col-sm-6 col-md-3 form-group">
            <label class="form-label" for="people-role">角色</label>
            <input id="people-role" v-model.trim="filters.role" type="text" class="form-control" placeholder="请输入角色">
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

    <div v-else class="panel panel-default page-panel">
      <div class="panel-body">
        <div class="page-card-header">
          <span class="form-section-title mb-0">人员列表</span>
        </div>

        <div class="table-responsive">
          <table v-if="people.length" class="table table-striped align-middle mb-0">
            <thead>
              <tr>
                <th>姓名</th>
                <th>工号</th>
                <th>部门</th>
                <th>职务</th>
                <th>角色</th>
                <th>联系方式</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="person in people" :key="person.id">
                <td>{{ person.name }}</td>
                <td>{{ person.employee_no || '—' }}</td>
                <td>{{ person.department_name || '—' }}</td>
                <td>{{ person.position || '—' }}</td>
                <td>
                  <span v-if="person.role" class="label label-default badge-role">{{ person.role }}</span>
                  <span v-else>—</span>
                </td>
                <td>{{ person.phone || '—' }}</td>
              </tr>
            </tbody>
          </table>
          <div v-else class="text-center text-muted" style="padding: 24px 12px;">暂无人员记录。</div>
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

const loading = ref(false)
const errorMessage = ref('')
const people = ref([])
const departments = ref([])
const total = ref(0)
const page = ref(1)
const next = ref(null)
const previous = ref(null)
const filters = reactive({
  search: '',
  department_id: '',
  role: '',
})

const buildParams = () => ({
  page: page.value,
  search: filters.search || undefined,
  department_id: filters.department_id || undefined,
  role: filters.role || undefined,
})

const fetchPeople = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const { data } = await request.get('/people/', { params: buildParams() })
    people.value = data.results || []
    total.value = data.count || 0
    next.value = data.next
    previous.value = data.previous
  } catch (error) {
    errorMessage.value = error.message || '人员列表加载失败。'
  } finally {
    loading.value = false
  }
}

const fetchDepartments = async () => {
  try {
    const { data } = await request.get('/departments/', { params: { page: 1 } })
    departments.value = data.results || []
  } catch (error) {
    errorMessage.value = error.message || '部门列表加载失败。'
  }
}

const searchPeople = () => {
  page.value = 1
  fetchPeople()
}

const resetFilters = () => {
  filters.search = ''
  filters.department_id = ''
  filters.role = ''
  page.value = 1
  fetchPeople()
}

const changePage = (targetPage) => {
  if (targetPage < 1) {
    return
  }
  page.value = targetPage
  fetchPeople()
}

onMounted(() => {
  fetchDepartments()
  fetchPeople()
})
</script>
