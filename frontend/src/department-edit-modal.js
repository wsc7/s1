import { createApp } from 'vue'
import DepartmentEditModal from './components/DepartmentEditModal.vue'

// Find all edit modal containers and mount them
document.addEventListener('DOMContentLoaded', () => {
  const editModalElements = document.querySelectorAll('[data-vue-department-edit-modal]')

  editModalElements.forEach(el => {
    const departmentId = el.dataset.departmentId
    const apiUrl = el.dataset.apiUrl || '/api/departments/'

    if (departmentId) {
      createApp(DepartmentEditModal, {
        departmentId: parseInt(departmentId),
        apiUrl,
      }).mount(el)
    }
  })
})