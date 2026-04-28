<template>
  <div class="page-shell departments-page-shell">
    <div class="page-header">
      <div class="page-header__inner">
        <div class="page-header__copy">
          <h2 class="page-header__title">部门管理</h2>
          <span class="page-header__subtitle">维护部门基本信息。</span>
        </div>
        <div class="d-flex gap-2">
          <DepartmentModal api-url="/api/v1/departments/" :use-spa-api="true" @saved="refreshDepartments" />
        </div>
      </div>
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
    <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>
    <div v-if="loading" class="text-muted">加载中...</div>

    <div v-else class="departments-content-grid">
      <div class="panel panel-default page-panel">
        <div class="panel-body">
          <div class="page-card-header">
            <span class="form-section-title mb-0">部门列表</span>
          </div>

          <div class="table-responsive">
            <table class="table table-striped align-middle mb-0">
              <thead>
                <tr>
                  <th>部门名称</th>
                  <th>描述</th>
                  <th>创建时间</th>
                  <th>更新时间</th>
                  <th class="text-end">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="department in departments" :key="department.id">
                  <td>{{ department.name }}</td>
                  <td>{{ truncateDescription(department.description) }}</td>
                  <td>{{ department.created_at_display || formatDateTime(department.created_at) }}</td>
                  <td>{{ department.updated_at_display || formatDateTime(department.updated_at) }}</td>
                  <td class="text-end action-cell">
                    <DepartmentEditModal
                      :department-id="department.id"
                      api-url="/api/v1/departments/"
                      :use-spa-api="true"
                      @saved="refreshDepartments"
                    />
                    <button type="button" class="btn btn-xs btn-danger" @click="deleteDepartment(department)">删除</button>
                  </td>
                </tr>
                <tr v-if="!departments.length">
                  <td colspan="5" class="text-center text-muted">暂无部门记录，请点击上方「新增部门」添加。</td>
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

      <div class="panel panel-default page-panel department-stats-panel">
        <div class="panel-body">
          <div class="page-card-header">
            <span class="form-section-title mb-0">部门统计</span>
          </div>
          <div class="department-stats-section">
            <div class="department-stats-total">{{ total }}</div>
            <div class="department-stats-total-label">部门总数</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

import DepartmentEditModal from '../components/DepartmentEditModal.vue'
import DepartmentModal from '../components/DepartmentModal.vue'
import request from '../utils/request'

const departments = ref([])
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const total = ref(0)
const page = ref(1)
const next = ref(null)
const previous = ref(null)
const filters = reactive({
  search: '',
})

const pageSize = 10
const pageRange = computed(() => {
  const totalPages = Math.ceil(total.value / pageSize) || 1
  const pages = []
  for (let i = 1; i <= totalPages; i++) pages.push(i)
  return pages
})
const startIndex = computed(() => total.value === 0 ? 0 : (page.value - 1) * pageSize + 1)
const endIndex = computed(() => Math.min(page.value * pageSize, total.value))

const buildParams = () => ({
  page: page.value,
  q: filters.search || undefined,
})

const formatDateTime = (value) => {
  if (!value) {
    return '—'
  }

  return value.slice(0, 16).replace('T', ' ')
}

const truncateDescription = (value) => {
  if (!value) {
    return '—'
  }
  return value.length > 50 ? `${value.slice(0, 49)}…` : value
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

const refreshDepartments = () => {
  successMessage.value = '部门信息已更新。'
  fetchDepartments()
}

const searchDepartments = () => {
  successMessage.value = ''
  page.value = 1
  fetchDepartments()
}

const resetFilters = () => {
  filters.search = ''
  successMessage.value = ''
  page.value = 1
  fetchDepartments()
}

const changePage = (targetPage) => {
  if (targetPage < 1) {
    return
  }
  successMessage.value = ''
  page.value = targetPage
  fetchDepartments()
}

const deleteDepartment = async (department) => {
  if (!window.confirm('确定删除该部门？如果该部门下有人员，将无法删除。')) {
    return
  }

  try {
    await request.delete(`/departments/${department.id}/`)
    successMessage.value = '部门已删除。'
    fetchDepartments()
  } catch (error) {
    errorMessage.value = error.message || '删除部门失败。'
  }
}

onMounted(() => {
  fetchDepartments()
})
</script>

<style scoped>
.departments-page-shell {
  position: relative;
  width: 100%;
  max-width: 1320px;
  box-sizing: border-box;
  margin: 0 auto;
  padding-right: 360px;
}

.departments-content-grid {
  display: block;
}

.department-stats-panel {
  position: fixed;
  top: 220px;
  right: 80px;
  width: 320px;
}

.department-stats-section + .department-stats-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eef2f6;
}

.department-stats-total {
  color: #2f6fed;
  font-size: 36px;
  font-weight: 700;
  line-height: 1;
}

.department-stats-total-label {
  margin-top: 8px;
  color: #667085;
  font-size: 13px;
}

.action-cell .btn + .btn,
.action-cell .vue-toolbar + .btn {
  margin-left: 6px;
}

@media (max-width: 1199px) {
  .departments-page-shell {
    width: auto;
    max-width: none;
    padding-right: 0;
  }

  .department-stats-panel {
    position: static;
    width: auto;
    margin-top: 16px;
  }
}
</style>
