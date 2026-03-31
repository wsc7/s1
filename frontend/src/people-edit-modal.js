import PersonEditModal from './components/PersonEditModal.vue'
import { mountBySelector } from './modal-utils.js'

mountBySelector('[data-vue-edit-modal]', PersonEditModal, (el) => {
  const personId = el.dataset.personId
  if (!personId) {
    return null
  }
  return {
    personId: parseInt(personId, 10),
    apiUrl: el.dataset.apiUrl || '/api/people/',
  }
})
