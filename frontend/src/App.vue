<template>
  <div class="app-root">
    <template v-if="showNav">
      <div class="main-wrapper">
        <div class="navbar-bg"></div>

        <nav class="navbar main-navbar">
          <ul class="navbar-nav navbar-right">
            <li class="dropdown">
              <a href="#" class="nav-link dropdown-toggle nav-link-lg nav-link-user" style="background:transparent !important;">
                <div class="d-sm-none d-lg-inline-block" style="display:inline-block;">Hi, {{ currentUsername }}</div>
              </a>
            </li>
            <li><a href="/profile/" class="nav-link">个人中心</a></li>
            <li><a href="/reminder-settings/" class="nav-link">提醒设置</a></li>
            <li><a href="#" class="nav-link" @click.prevent="handleLogout">退出</a></li>
          </ul>
        </nav>

        <div class="main-sidebar sidebar-style-2">
          <aside id="sidebar-wrapper">
            <div class="sidebar-brand">
              <RouterLink to="/">会议管理系统</RouterLink>
            </div>
            <ul class="sidebar-menu">
              <li :class="{ active: route.path === '/' }">
                <RouterLink class="nav-link" to="/"><i class="fab fa-fort-awesome"></i> <span>首页</span></RouterLink>
              </li>
              <li class="menu-header">系统模块</li>
              <li :class="{ active: route.path.startsWith('/meetings') }">
                <RouterLink class="nav-link" to="/meetings"><i class="fas fa-calendar-alt"></i> <span>会议管理</span></RouterLink>
              </li>
              <li :class="{ active: route.path.startsWith('/people') }">
                <RouterLink class="nav-link" to="/people"><i class="fas fa-users"></i> <span>人员管理</span></RouterLink>
              </li>
              <li :class="{ active: route.path.startsWith('/departments') }">
                <RouterLink class="nav-link" to="/departments"><i class="fas fa-sitemap"></i> <span>部门管理</span></RouterLink>
              </li>
              <li class="menu-header">工具</li>
              <li>
                <a class="nav-link" href="/notifications/"><i class="fas fa-bell"></i> <span>通知中心</span></a>
              </li>
              <li>
                <a class="nav-link" href="/profile/"><i class="fas fa-user-cog"></i> <span>个人中心</span></a>
              </li>
              <li>
                <a class="nav-link" href="/reminder-settings/"><i class="fas fa-cog"></i> <span>提醒设置</span></a>
              </li>
            </ul>
          </aside>
        </div>

        <div class="main-content nx-dashboard">
          <div class="nx-blob nx-blob--1"></div>
          <div class="nx-blob nx-blob--2"></div>
          <div v-if="globalError" class="alert alert-danger">{{ globalError }}</div>
          <RouterView />
        </div>

        <footer class="main-footer">
          <div class="footer-left"></div>
        </footer>
      </div>
    </template>

    <main v-else class="container app-main app-main--login">
      <div v-if="globalError" class="alert alert-danger">{{ globalError }}</div>
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { computed, watch, ref } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'

import request, { clearTokens, getAccessToken } from './utils/request'

const route = useRoute()
const globalError = ref('')
const currentUsername = ref('用户')
const showNav = computed(() => !route.meta.public)

const loadCurrentUser = async () => {
  if (!getAccessToken()) {
    return
  }

  try {
    const { data } = await request.get('/auth/me/')
    currentUsername.value = data.username || data.name || '用户'
    globalError.value = ''
  } catch (error) {
    globalError.value = error.message || '获取当前用户信息失败。'
  }
}

const handleLogout = () => {
  clearTokens()
  window.location.href = '/logout/'
}

watch(
  () => route.path,
  () => {
    if (showNav.value) {
      loadCurrentUser()
    } else {
      currentUsername.value = '用户'
      globalError.value = ''
    }
  },
  { immediate: true }
)
</script>

<style>
body {
  font-size: 13px;
  line-height: 1.5;
}

.main-wrapper {
  display: block;
}

.main-content.nx-dashboard {
  padding-right: 20px;
  padding-bottom: 28px;
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

.page-header__inner {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 2px;
}

.page-header__copy {
  min-width: 0;
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

@media (max-width: 991px) {
  .main-content.nx-dashboard {
    padding-right: 15px;
  }

  .page-header__inner,
  .page-card-header {
    flex-direction: column;
    align-items: stretch;
  }

  .text-end,
  .text-right,
  .pagination-summary {
    text-align: left;
  }
}

@media (max-width: 767px) {
  .page-panel .panel-body {
    padding: 16px;
  }
}
</style>
