<template>
  <div class="approval-trigger-wrap">
    <button type="button" class="btn btn-xs btn-primary" @click="open">审批</button>

    <ModalShell :show="show" title="会议审批" @close="close">
      <p v-if="errorMsg" class="text-danger small">{{ errorMsg }}</p>
      <div class="form-group">
        <label>会议主题</label>
        <input :value="meetingTitle" type="text" class="form-control" readonly>
      </div>
      <div class="form-group">
        <label>当前状态</label>
        <input :value="statusLabel" type="text" class="form-control" readonly>
      </div>
      <div class="form-group">
        <label>审批意见</label>
        <textarea v-model="form.opinion" class="form-control" rows="4" placeholder="请输入审批意见"></textarea>
      </div>

      <template #footer>
        <button type="button" class="btn btn-default" :disabled="submitting" @click="close">取消</button>
        <button type="button" class="btn btn-danger" :disabled="submitting" @click="submit('reject')">未通过</button>
        <button type="button" class="btn btn-primary" :disabled="submitting" @click="submit('approve')">通过</button>
      </template>
    </ModalShell>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import ModalShell from './ModalShell.vue'
import { formatErrors, submitJson, toSpaApiUrl } from '../modal-utils.js'
import request from '../utils/request'

const props = defineProps({
  apiUrl: { type: String, required: true },
  meetingTitle: { type: String, required: true },
  statusLabel: { type: String, default: '待审批' },
  useSpaApi: { type: Boolean, default: false },
})

const emit = defineEmits(['saved'])

const show = ref(false)
const submitting = ref(false)
const errorMsg = ref('')
const form = reactive({
  opinion: '',
})

function open() {
  errorMsg.value = ''
  form.opinion = ''
  show.value = true
}

function close() {
  if (submitting.value) {
    return
  }
  show.value = false
}

async function submit(action) {
  submitting.value = true
  errorMsg.value = ''
  try {
    if (props.useSpaApi) {
      await request.post(toSpaApiUrl(props.apiUrl), {
        action,
        opinion: form.opinion,
      })
      emit('saved')
      close()
      return
    }

    const data = await submitJson(props.apiUrl, {
      method: 'POST',
      body: {
        action,
        opinion: form.opinion,
      },
    })
    if (data.ok) {
      window.location.reload()
      return
    }
    errorMsg.value = formatErrors(data.errors, {
      action: '操作',
      opinion: '意见',
      _: '审批',
    })
  } catch (e) {
    errorMsg.value = e.message || '网络错误，请稍后重试。'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.approval-trigger-wrap {
  display: inline-block;
  vertical-align: middle;
}
</style>
