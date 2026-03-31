const path = require('path')
const { defineConfig } = require('vite')
const vue = require('@vitejs/plugin-vue')

module.exports = defineConfig({
  plugins: [vue()],
  root: path.resolve(__dirname, 'frontend'),
  build: {
    outDir: path.resolve(__dirname, 'app1/static/vue'),
    emptyOutDir: true,
    cssCodeSplit: false,
    codeSplitting: false,
    rollupOptions: {
      input: {
        meetingApp: path.resolve(__dirname, 'frontend/src/main.js'),
        meetingsModal: path.resolve(__dirname, 'frontend/src/meetings-modal.js'),
        meetingAttendeesModal: path.resolve(__dirname, 'frontend/src/meeting-attendees-modal.js'),
        peopleModal: path.resolve(__dirname, 'frontend/src/people-modal.js'),
        peopleEditModal: path.resolve(__dirname, 'frontend/src/people-edit-modal.js'),
        departmentModal: path.resolve(__dirname, 'frontend/src/department-modal.js'),
        departmentEditModal: path.resolve(__dirname, 'frontend/src/department-edit-modal.js'),
      },
      output: {
        format: 'es',
        entryFileNames: (chunkInfo) => {
          const map = {
            meetingApp: 'meeting-app.js',
            meetingsModal: 'meetings-modal.js',
            meetingAttendeesModal: 'meeting-attendees-modal.js',
            peopleModal: 'people-modal.js',
            peopleEditModal: 'people-edit-modal.js',
            departmentModal: 'department-modal.js',
            departmentEditModal: 'department-edit-modal.js',
          }
          return map[chunkInfo.name] || '[name].js'
        },
        assetFileNames: (assetInfo) => {
          const n = assetInfo.names && assetInfo.names[0]
          if (n && n.endsWith('.css')) {
            return 'chunk-[name].css'
          }
          return '[name].[ext]'
        },
      },
    },
  },
})
