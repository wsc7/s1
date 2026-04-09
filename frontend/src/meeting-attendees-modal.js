import MeetingAttendeesModal from './components/MeetingAttendeesModal.vue'
import { getCsrfToken } from './csrf.js'
import { mountById, readJsonScript } from './modal-utils.js'

mountById('vue-meeting-attendees-modal', MeetingAttendeesModal, (el) => ({
  attendees: readJsonScript('meeting-attendee-options-json'),
  submitUrl: el.dataset.submitUrl || window.location.pathname,
  csrfToken: getCsrfToken() || '',
}))
