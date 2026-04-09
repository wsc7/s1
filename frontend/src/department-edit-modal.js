import DepartmentEditModal from './components/DepartmentEditModal.vue'
import { mountBySelector } from './modal-utils.js'

mountBySelector('[data-vue-department-edit-modal]', DepartmentEditModal, (el) => {
  const departmentId = el.dataset.departmentId
  if (!departmentId) {
    return null
  }
  return {
    departmentId: parseInt(departmentId, 10),
    apiUrl: el.dataset.apiUrl || '/api/departments/',
  }
})
