import { createRouter, createWebHistory } from 'vue-router'

import DepartmentsPage from '../pages/DepartmentsPage.vue'
import LoginPage from '../pages/LoginPage.vue'
import MeetingsPage from '../pages/MeetingsPage.vue'
import PeoplePage from '../pages/PeoplePage.vue'
import { getAccessToken } from '../utils/request'

const routes = [
  { path: '/', redirect: '/meetings' },
  { path: '/login', component: LoginPage, meta: { public: true } },
  { path: '/meetings', component: MeetingsPage },
  { path: '/people', component: PeoplePage },
  { path: '/departments', component: DepartmentsPage },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = getAccessToken()

  if (!to.meta.public && !token) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  if (to.path === '/login' && token) {
    return '/meetings'
  }

  return true
})

export default router
