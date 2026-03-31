import { createApp } from 'vue'
import MeetingsModal from './components/MeetingsModal.vue'

const el = document.getElementById('vue-meetings-toolbar')
if (el) {
  let organizers = []
  const jsonEl = document.getElementById('meetings-organizers-json')
  if (jsonEl && jsonEl.textContent) {
    try {
      organizers = JSON.parse(jsonEl.textContent.trim())
    } catch {
      organizers = []
    }
  }
  const apiUrl = el.dataset.apiUrl || '/api/meetings/create/'
  const fullPageUrl = el.dataset.fullPageUrl || '/meetings/add/'
  createApp(MeetingsModal, {
    organizers,
    apiUrl,
    fullPageUrl,
  }).mount(el)
}
