import DepartmentModal from './components/DepartmentModal.vue'
import { mountById } from './modal-utils.js'

mountById('vue-departments-toolbar', DepartmentModal, (el) => ({
  apiUrl: el.dataset.apiUrl || '/api/departments/create/',
  fullPageUrl: el.dataset.fullPageUrl || '/departments/add/',
}))
