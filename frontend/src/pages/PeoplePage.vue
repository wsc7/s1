<template>
  <div class="page-shell people-page-shell">
    <div class="page-header">
      <div class="page-header__inner">
        <div class="page-header__copy">
          <h2 class="page-header__title">人员管理</h2>
          <span class="page-header__subtitle">维护人员基本信息、部门信息及角色权限。</span>
        </div>
        <div class="d-flex gap-2">
          <PersonModal api-url="/api/v1/people/" :departments="departments" :use-spa-api="true" @saved="refreshPeople" />
          <button type="button" class="btn btn-default" disabled>批量导入</button>
        </div>
      </div>
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
            <select id="people-department" v-model="filters.department" class="form-control">
              <option value="">全部</option>
              <option v-for="department in departments" :key="department.id" :value="department.name">
                {{ department.name }}
              </option>
            </select>
          </div>
          <div class="col-sm-6 col-md-3 form-group">
            <label class="form-label" for="people-role">角色</label>
            <select id="people-role" v-model="filters.role" class="form-control">
              <option value="">全部</option>
              <option v-for="role in roles" :key="role" :value="role">{{ role }}</option>
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

    <div v-else class="people-content-grid">
      <div class="panel panel-default page-panel">
        <div class="panel-body">
          <div class="page-card-header">
            <span class="form-section-title mb-0">人员列表</span>
          </div>

          <div class="table-responsive">
            <table class="table table-striped align-middle mb-0">
              <thead>
                <tr>
                  <th>姓名</th>
                  <th>工号</th>
                  <th>部门</th>
                  <th>职务</th>
                  <th>角色</th>
                  <th>联系方式</th>
                  <th class="text-end">操作</th>
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
                  <td class="text-end action-cell">
                    <PersonEditModal
                      :person-id="person.id"
                      api-url="/api/v1/people/"
                      :departments="departments"
                      :use-spa-api="true"
                      @saved="refreshPeople"
                    />
                    <button type="button" class="btn btn-xs btn-danger" @click="deletePerson(person)">删除</button>
                  </td>
                </tr>
                <tr v-if="!people.length">
                  <td colspan="7" class="text-center text-muted">暂无人员记录，请点击上方「新增人员」添加。</td>
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

      <div class="panel panel-default page-panel people-stats-panel">
        <div class="panel-body">
          <div class="page-card-header">
            <span class="form-section-title mb-0">人员统计</span>
          </div>
          <div class="people-stats-section">
            <div class="people-stats-total">{{ total }}</div>
            <div class="people-stats-total-label">人员总数</div>
          </div>
          <div class="people-stats-section" v-if="departments.length">
            <div class="people-stats-section-title">部门筛选</div>
            <div class="people-stats-list">
              <div class="people-stats-item" v-for="department in departments.slice(0, 5)" :key="department.id">
                <span>{{ department.name }}</span>
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

import PersonEditModal from '../components/PersonEditModal.vue'
import PersonModal from '../components/PersonModal.vue'
import request from '../utils/request'

const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const people = ref([])
const departments = ref([])
const roles = ref([])
const total = ref(0)
const page = ref(1)
const next = ref(null)
const previous = ref(null)
const filters = reactive({
  search: '',
  department: '',
  role: '',
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
  department: filters.department || undefined,
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

const fetchOptions = async () => {
  try {
    const { data } = await request.get('/people/options/')
    departments.value = data.departments || []
    roles.value = data.roles || []
  } catch (error) {
    errorMessage.value = error.message || '人员选项加载失败。'
  }
}

const refreshPeople = () => {
  successMessage.value = '人员信息已更新。'
  fetchOptions()
  fetchPeople()
}

const searchPeople = () => {
  successMessage.value = ''
  page.value = 1
  fetchPeople()
}

const resetFilters = () => {
  filters.search = ''
  filters.department = ''
  filters.role = ''
  successMessage.value = ''
  page.value = 1
  fetchPeople()
}

const changePage = (targetPage) => {
  if (targetPage < 1) {
    return
  }
  successMessage.value = ''
  page.value = targetPage
  fetchPeople()
}

const deletePerson = async (person) => {
  if (!window.confirm('确定删除该人员？')) {
    return
  }

  try {
    await request.delete(`/people/${person.id}/`)
    successMessage.value = '人员已删除。'
    fetchPeople()
  } catch (error) {
    errorMessage.value = error.message || '删除人员失败。'
  }
}

onMounted(() => {
  fetchOptions()
  fetchPeople()
})
</script>

<style scoped>
.people-page-shell {
  position: relative;
  width: 100%;
  max-width: 1320px;
  box-sizing: border-box;
  margin: 0 auto;
  padding-right: 360px;
}

.people-content-grid {
  display: block;
}

.people-stats-panel {
  position: fixed;
  top: 220px;
  right: 80px;
  width: 320px;
}

.people-stats-section + .people-stats-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eef2f6;
}

.people-stats-total {
  color: #2f6fed;
  font-size: 36px;
  font-weight: 700;
  line-height: 1;
}

.people-stats-total-label {
  margin-top: 8px;
  color: #667085;
  font-size: 13px;
}

.people-stats-section-title {
  margin-bottom: 12px;
  color: #344054;
  font-size: 13px;
  font-weight: 600;
}

.people-stats-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.people-stats-item {
  padding: 10px 12px;
  border-radius: 10px;
  background: #f8fafc;
  color: #344054;
}

.action-cell .btn + .btn,
.action-cell .vue-toolbar + .btn {
  margin-left: 6px;
}

@media (max-width: 1199px) {
  .people-page-shell {
    width: auto;
    max-width: none;
    padding-right: 0;
  }

  .people-stats-panel {
    position: static;
    width: auto;
    margin-top: 16px;
  }
}
</style>
