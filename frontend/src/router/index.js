import { createRouter, createWebHistory } from 'vue-router'

import DashboardPage from '../pages/DashboardPage.vue'
import DepartmentsPage from '../pages/DepartmentsPage.vue'
import LoginPage from '../pages/LoginPage.vue'
import MeetingDetailPage from '../pages/MeetingDetailPage.vue'
import MeetingsPage from '../pages/MeetingsPage.vue'
import NotificationsPage from '../pages/NotificationsPage.vue'
import PeoplePage from '../pages/PeoplePage.vue'
import ProfilePage from '../pages/ProfilePage.vue'
import RegisterPage from '../pages/RegisterPage.vue'
import ReminderSettingsPage from '../pages/ReminderSettingsPage.vue'
import { getAccessToken, getSessionTokens } from '../utils/request'

const meetingInfoRedirect = (to) => `/meetings/${to.params.id}/info/`
const meetingAttendeesRedirect = (to) => `/meetings/${to.params.meetingId || to.params.id}/attendees/`
const meetingAttachmentsRedirect = (to) => `/meetings/${to.params.meetingId || to.params.id}/attachments/`
const meetingAgendaRedirect = (to) => `/meetings/${to.params.meetingId || to.params.id}/agenda/`

const routes = [
  { path: '/', component: DashboardPage },
  { path: '/login', component: LoginPage, meta: { public: true } },
  { path: '/register/', component: RegisterPage, meta: { public: true } },
  { path: '/meetings', component: MeetingsPage },
  { path: '/meetings/add/', redirect: '/meetings' },
  { path: '/meetings/:id/delete/', redirect: '/meetings' },
  { path: '/meetings/:id/apply/', redirect: '/meetings' },
  { path: '/meetings/:meetingId/agenda/items/:itemId/delete/', redirect: meetingAgendaRedirect },
  { path: '/meetings/:meetingId/attendees/:attendeeId/remove/', redirect: meetingAttendeesRedirect },
  { path: '/meetings/:meetingId/attachments/:attachmentId/remove/', redirect: meetingAttachmentsRedirect },
  { path: '/meetings/:meetingId/respond/', redirect: '/notifications/' },
  { path: '/meetings/:id', redirect: meetingInfoRedirect },
  { path: '/meetings/:id/', redirect: meetingInfoRedirect },
  { path: '/meetings/:id/edit/', redirect: meetingInfoRedirect },
  { path: '/meetings/:id/info/', component: MeetingDetailPage, meta: { tab: 'info' } },
  { path: '/meetings/:id/attendees/', component: MeetingDetailPage, meta: { tab: 'attendees' } },
  { path: '/meetings/:id/attachments/', component: MeetingDetailPage, meta: { tab: 'attachments' } },
  { path: '/meetings/:id/agenda/', component: MeetingDetailPage, meta: { tab: 'agenda' } },
  { path: '/people', component: PeoplePage },
  { path: '/people/add/', redirect: '/people' },
  { path: '/people/:id/edit/', redirect: '/people' },
  { path: '/people/:id/delete/', redirect: '/people' },
  { path: '/departments', component: DepartmentsPage },
  { path: '/departments/add/', redirect: '/departments' },
  { path: '/departments/:id/edit/', redirect: '/departments' },
  { path: '/departments/:id/delete/', redirect: '/departments' },
  { path: '/profile/', component: ProfilePage },
  { path: '/reminder-settings/', component: ReminderSettingsPage },
  { path: '/notifications/', component: NotificationsPage },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const token = getAccessToken()

  if (to.path === '/login' && token) {
    return '/meetings'
  }

  if (to.meta.public || token) {
    return true
  }

  try {
    await getSessionTokens()
    return true
  } catch {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
})

export default router
