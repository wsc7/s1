import { createApp } from 'vue'
import PersonEditModal from './components/PersonEditModal.vue'

// Find all edit modal containers and mount them
document.addEventListener('DOMContentLoaded', () => {
  const editModalElements = document.querySelectorAll('[data-vue-edit-modal]')

  editModalElements.forEach(el => {
    const personId = el.dataset.personId
    const apiUrl = el.dataset.apiUrl || '/api/people/'

    if (personId) {
      createApp(PersonEditModal, {
        personId: parseInt(personId),
        apiUrl,
      }).mount(el)
    }
  })
})