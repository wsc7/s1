import { createApp } from 'vue'
import DepartmentModal from './components/DepartmentModal.vue'

document.addEventListener('DOMContentLoaded', () => {
  const el = document.getElementById('vue-departments-toolbar')
  if (el) {
    const apiUrl = el.dataset.apiUrl || '/api/departments/create/'
    const fullPageUrl = el.dataset.fullPageUrl || '/departments/add/'
    createApp(DepartmentModal, {
      apiUrl,
      fullPageUrl,
    }).mount(el)
  }
})