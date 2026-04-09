import PersonModal from './components/PersonModal.vue'
import { mountById } from './modal-utils.js'

mountById('vue-people-toolbar', PersonModal, (el) => ({
  apiUrl: el.dataset.apiUrl || '/api/people/create/',
  fullPageUrl: el.dataset.fullPageUrl || '/people/add/',
}))
