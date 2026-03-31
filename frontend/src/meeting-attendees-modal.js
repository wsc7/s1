import { createApp } from 'vue'
import MeetingAttendeesModal from './components/MeetingAttendeesModal.vue'
import { getCsrfToken } from './csrf.js'

const el = document.getElementById('vue-meeting-attendees-modal')
if (el) {
  let attendees = []
  const jsonEl = document.getElementById('meeting-attendee-options-json')
  if (jsonEl && jsonEl.textContent) {
    try {
      attendees = JSON.parse(jsonEl.textContent.trim())
    } catch {
      attendees = []
    }
  }

  createApp(MeetingAttendeesModal, {
    attendees,
    submitUrl: el.dataset.submitUrl || window.location.pathname,
    csrfToken: getCsrfToken() || '',
  }).mount(el)
}
