<template>
  <main class="container profile-page" style="margin-top: 2rem;">
    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
    <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>

    <div class="page-header">
      <div class="page-header__inner">
        <div class="page-header__copy">
          <h2 class="page-header__title">个人中心</h2>
          <span class="page-header__subtitle">查看和管理您的个人信息、账户设置和提醒偏好</span>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-muted">加载中...</div>
    <div v-else class="row">
      <div class="col-md-4">
        <div class="card">
          <div class="card-body">
            <h4 class="card-title">个人信息概览</h4>
            <hr>
            <div class="form-section-title">基本信息</div>
            <table class="table table-borderless">
              <tbody>
                <tr><th width="35%">用户名</th><td>{{ user.username }}</td></tr>
                <tr><th>邮箱</th><td>{{ user.email || '未设置' }}</td></tr>
                <tr><th>注册时间</th><td>{{ user.date_joined_display }}</td></tr>
                <tr><th>最后登录</th><td>{{ user.last_login_display || '从未登录' }}</td></tr>
              </tbody>
            </table>

            <div class="form-section-title">人员信息</div>
            <table class="table table-borderless">
              <tbody>
                <tr><th width="35%">姓名</th><td>{{ person.name || '未设置' }}</td></tr>
                <tr><th>工号</th><td>{{ person.employee_no || '未设置' }}</td></tr>
                <tr><th>部门</th><td>{{ person.department_name || '未指定' }}</td></tr>
                <tr><th>职务</th><td>{{ person.position || '未设置' }}</td></tr>
                <tr><th>角色</th><td>{{ person.role || '未设置' }}</td></tr>
                <tr><th>联系方式</th><td>{{ person.phone || '未设置' }}</td></tr>
              </tbody>
            </table>

            <div class="form-section-title">提醒设置</div>
            <table class="table table-borderless">
              <tbody>
                <tr>
                  <th width="35%">邮件通知</th>
                  <td><span :class="reminderSettings.email_notifications ? 'text-success' : 'text-muted'">{{ reminderSettings.email_notifications ? '启用' : '禁用' }}</span></td>
                </tr>
                <tr>
                  <th>应用内通知</th>
                  <td><span :class="reminderSettings.in_app_notifications ? 'text-success' : 'text-muted'">{{ reminderSettings.in_app_notifications ? '启用' : '禁用' }}</span></td>
                </tr>
                <tr>
                  <th>短信通知</th>
                  <td><span :class="reminderSettings.sms_notifications ? 'text-success' : 'text-muted'">{{ reminderSettings.sms_notifications ? '启用' : '禁用' }}</span></td>
                </tr>
                <tr>
                  <th>免打扰时段</th>
                  <td>
                    <template v-if="reminderSettings.quiet_hours_start && reminderSettings.quiet_hours_end">
                      {{ reminderSettings.quiet_hours_start }} - {{ reminderSettings.quiet_hours_end }}
                    </template>
                    <span v-else class="text-muted">未设置</span>
                  </td>
                </tr>
              </tbody>
            </table>

            <div class="mt-3">
              <RouterLink to="/reminder-settings/" class="btn btn-default btn-block">管理提醒设置</RouterLink>
              <RouterLink to="/notifications/" class="btn btn-default btn-block">查看通知中心</RouterLink>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-8">
        <div class="card profile-card">
          <div class="card-body">
            <h4 class="card-title">编辑个人信息</h4>
            <p class="text-muted">更新您的姓名、部门、职务等个人信息</p>
            <form @submit.prevent="savePerson">
              <div class="row">
                <div class="col-md-6">
                  <div class="form-group">
                    <label>姓名 <span class="text-danger">*</span></label>
                    <input v-model="personForm.name" type="text" class="form-control" required>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="form-group">
                    <label>工号</label>
                    <input v-model="personForm.employee_no" type="text" class="form-control">
                  </div>
                </div>
              </div>

              <div class="form-group">
                <label>部门</label>
                <select v-model="personForm.department" class="form-control">
                  <option value="">— 请选择部门 —</option>
                  <option v-for="department in departments" :key="department.id" :value="String(department.id)">{{ department.name }}</option>
                </select>
              </div>

              <div class="row">
                <div class="col-md-6">
                  <div class="form-group">
                    <label>职务</label>
                    <input v-model="personForm.position" type="text" class="form-control">
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="form-group">
                    <label>角色</label>
                    <input v-model="personForm.role" type="text" class="form-control">
                  </div>
                </div>
              </div>

              <div class="form-group">
                <label>联系方式</label>
                <input v-model="personForm.phone" type="text" class="form-control">
              </div>

              <div class="text-right">
                <button type="submit" class="btn btn-primary">保存个人信息</button>
              </div>
            </form>
          </div>
        </div>

        <div class="card profile-card">
          <div class="card-body">
            <h4 class="card-title">编辑账户信息</h4>
            <p class="text-muted">更新您的邮箱地址</p>
            <form @submit.prevent="saveUser">
              <div class="form-group">
                <label>邮箱地址</label>
                <input v-model="userForm.email" type="email" class="form-control">
                <p class="help-block">用于接收系统通知和密码重置</p>
              </div>
              <div class="text-right">
                <button type="submit" class="btn btn-primary">保存账户信息</button>
              </div>
            </form>
          </div>
        </div>

        <div class="card profile-card">
          <div class="card-body">
            <h4 class="card-title">修改密码</h4>
            <p class="text-muted">修改您的登录密码，需要验证当前密码</p>
            <form @submit.prevent="savePassword">
              <div class="form-group">
                <label>当前密码</label>
                <input v-model="passwordForm.old_password" type="password" class="form-control">
              </div>
              <div class="row">
                <div class="col-md-6">
                  <div class="form-group">
                    <label>新密码</label>
                    <input v-model="passwordForm.new_password1" type="password" class="form-control">
                    <p class="help-block">密码至少需要8个字符，不能全是数字</p>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="form-group">
                    <label>确认新密码</label>
                    <input v-model="passwordForm.new_password2" type="password" class="form-control">
                  </div>
                </div>
              </div>
              <div class="text-right">
                <button type="submit" class="btn btn-primary">修改密码</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'

import request from '../utils/request'

const loading = ref(true)
const errorMessage = ref('')
const successMessage = ref('')
const user = ref({})
const person = ref({})
const reminderSettings = ref({})
const departments = ref([])

const personForm = reactive({
  name: '',
  employee_no: '',
  department: '',
  position: '',
  role: '',
  phone: '',
})

const userForm = reactive({
  email: '',
})

const passwordForm = reactive({
  old_password: '',
  new_password1: '',
  new_password2: '',
})

const setForms = () => {
  Object.assign(personForm, {
    name: person.value.name || '',
    employee_no: person.value.employee_no || '',
    department: person.value.department ? String(person.value.department) : '',
    position: person.value.position || '',
    role: person.value.role || '',
    phone: person.value.phone || '',
  })
  userForm.email = user.value.email || ''
}

const loadProfile = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const { data } = await request.get('/profile/')
    user.value = data.user || {}
    person.value = data.person || {}
    reminderSettings.value = data.reminder_settings || {}
    departments.value = data.departments || []
    setForms()
  } catch (error) {
    errorMessage.value = error.message || '个人中心加载失败。'
  } finally {
    loading.value = false
  }
}

const savePerson = async () => {
  errorMessage.value = ''
  try {
    const { data } = await request.patch('/profile/', {
      section: 'person',
      ...personForm,
      department: personForm.department || null,
    })
    person.value = data.person || person.value
    setForms()
    successMessage.value = data.detail || '个人信息已更新'
  } catch (error) {
    errorMessage.value = error.message || '请修正个人信息表单中的错误'
  }
}

const saveUser = async () => {
  errorMessage.value = ''
  try {
    const { data } = await request.patch('/profile/', {
      section: 'user',
      email: userForm.email,
    })
    user.value = data.user || user.value
    setForms()
    successMessage.value = data.detail || '账户信息已更新'
  } catch (error) {
    errorMessage.value = error.message || '请修正账户信息表单中的错误'
  }
}

const savePassword = async () => {
  errorMessage.value = ''
  try {
    const { data } = await request.post('/profile/password/', passwordForm)
    Object.assign(passwordForm, { old_password: '', new_password1: '', new_password2: '' })
    successMessage.value = data.detail || '密码已成功修改'
  } catch (error) {
    errorMessage.value = error.message || '请修正密码修改表单中的错误'
  }
}

onMounted(loadProfile)
</script>

<style scoped>
.profile-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card {
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fff;
}

.card-body {
  padding: 15px;
}

.profile-card {
  margin-bottom: 1.5rem;
}

.table-borderless > tbody > tr > th,
.table-borderless > tbody > tr > td {
  border-top: 0;
}

.mt-3 {
  margin-top: 1rem;
}
</style>
