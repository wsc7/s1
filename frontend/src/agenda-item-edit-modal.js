import AgendaItemEditModal from './components/AgendaItemEditModal.vue'
import { mountBySelector } from './modal-utils.js'

mountBySelector('[data-vue-agenda-edit-modal]', AgendaItemEditModal, (el) => {
  const meetingId = el.dataset.meetingId
  const itemId = el.dataset.itemId
  if (!meetingId || !itemId) {
    return null
  }
  return {
    meetingId: parseInt(meetingId, 10),
    itemId: parseInt(itemId, 10),
    apiUrl: el.dataset.apiUrl || `/api/meetings/${meetingId}/agenda-items/`,
  }
})
