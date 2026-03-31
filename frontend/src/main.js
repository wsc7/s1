import { createApp } from 'vue'
import App from './App.vue'

const el = document.getElementById('vue-meeting-root')
if (el) {
  createApp(App).mount(el)
}
