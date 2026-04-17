import MeetingApprovalModal from './components/MeetingApprovalModal.vue'
import { mountBySelector } from './modal-utils.js'

mountBySelector('[data-meeting-approval]', MeetingApprovalModal, (el) => ({
  apiUrl: el.dataset.apiUrl,
  meetingTitle: el.dataset.meetingTitle || '',
  statusLabel: el.dataset.statusLabel || '待审批',
}))
