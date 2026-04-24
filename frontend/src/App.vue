<template>
  <div>
    <nav v-if="showNav" class="navbar navbar-default navbar-static-top app-navbar">
      <div class="container">
        <div class="navbar-header">
          <RouterLink class="navbar-brand" to="/meetings">会议与人员管理系统</RouterLink>
        </div>
        <ul class="nav navbar-nav">
          <li><RouterLink to="/meetings">会议</RouterLink></li>
          <li><RouterLink to="/people">人员</RouterLink></li>
          <li><RouterLink to="/departments">部门</RouterLink></li>
        </ul>
        <ul class="nav navbar-nav navbar-right">
          <li><a href="#" @click.prevent="handleLogout">退出登录</a></li>
        </ul>
      </div>
    </nav>

    <main class="container app-main" :class="showNav ? 'app-main--with-nav' : 'app-main--login'">
      <div v-if="globalError" class="alert alert-danger">{{ globalError }}</div>
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'

import request, { clearTokens, getAccessToken } from './utils/request'

const route = useRoute()
const router = useRouter()
const globalError = ref('')
const showNav = computed(() => route.path !== '/login')

const loadCurrentUser = async () => {
  if (!getAccessToken()) {
    return
  }

  try {
    await request.get('/auth/me/')
    globalError.value = ''
  } catch (error) {
    globalError.value = error.message || '获取当前用户信息失败。'
  }
}

const handleLogout = () => {
  clearTokens()
  router.push('/login')
}

onMounted(() => {
  loadCurrentUser()
})
</script>

<style>
body {
  background: #f5f7fb;
  color: #101828;
}

.app-navbar {
  margin-bottom: 0;
  border-left: 0;
  border-right: 0;
  border-top: 0;
  border-bottom: 1px solid #e4e7ec;
  background: #fff;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
}

.app-navbar .navbar-brand {
  color: #101828 !important;
  font-weight: 700;
}

.app-navbar .navbar-nav > li > a {
  color: #344054;
}

.app-navbar .navbar-nav > li > a.router-link-active {
  color: #2f6fed;
  font-weight: 600;
}

.app-main {
  padding-bottom: 28px;
}

.app-main--with-nav {
  padding-top: 24px;
}

.app-main--login {
  padding-top: 40px;
}

.page-shell {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-panel {
  border-radius: 12px;
  border: 1px solid rgba(15, 23, 42, 0.06);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
  background: #fff;
}

.page-panel .panel-body {
  padding: 18px 20px;
}

.form-section-title {
  margin-bottom: 14px;
  color: #667085;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.page-header {
  margin: 0;
  padding: 0;
  border: 0;
}

.page-header__title {
  margin: 0;
  color: #101828;
  font-size: 24px;
  font-weight: 700;
  line-height: 1.25;
}

.page-header__subtitle {
  display: block;
  margin-top: 6px;
  color: #667085;
  font-size: 12px;
  line-height: 1.5;
}

.page-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.filter-form .form-group,
.filter-form [class*='col-'] {
  margin-bottom: 0;
}

.form-label {
  display: inline-block;
  margin-bottom: 6px;
  color: #344054;
  font-size: 12px;
  font-weight: 600;
}

.filter-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  min-height: 34px;
}

.table-responsive {
  border: 0;
  margin-bottom: 0;
}

.table {
  margin-bottom: 0;
}

.table > thead > tr > th {
  border-bottom: 1px solid #e4e7ec;
  color: #667085;
  font-size: 12px;
  font-weight: 700;
  padding: 10px 12px;
  vertical-align: middle;
  background: #f8fafc;
}

.table > tbody > tr > td {
  padding: 10px 12px;
  vertical-align: middle;
  border-top: 1px solid #eef2f6;
  color: #101828;
}

.table tbody tr:hover {
  background: rgba(47, 111, 237, 0.03);
}

.pagination-shell {
  margin-top: 16px;
}

.pagination-summary {
  color: #667085;
  font-size: 12px;
  line-height: 34px;
}

.badge-status,
.badge-role {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 8px;
}

@media (max-width: 767px) {
  .app-main--with-nav {
    padding-top: 16px;
  }

  .page-panel .panel-body {
    padding: 16px;
  }
}
</style>
