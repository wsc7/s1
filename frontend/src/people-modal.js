import { createApp } from 'vue'
import PersonModal from './components/PersonModal.vue'

const el = document.getElementById('vue-people-toolbar')
if (el) {
  const apiUrl = el.dataset.apiUrl || '/api/people/create/'
  const fullPageUrl = el.dataset.fullPageUrl || '/people/add/'
  createApp(PersonModal, {
    apiUrl,
    fullPageUrl,
  }).mount(el)
}
