import MeetingsModal from './components/MeetingsModal.vue'
import { mountById, readJsonScript } from './modal-utils.js'

mountById('vue-meetings-toolbar', MeetingsModal, (el) => ({
  organizers: readJsonScript('meetings-organizers-json'),
  apiUrl: el.dataset.apiUrl || '/api/meetings/create/',
  fullPageUrl: el.dataset.fullPageUrl || '/meetings/add/',
}))
