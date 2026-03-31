<template>
  <Teleport to="body">
    <div v-show="show" class="vue-modal-mask" @click.self="$emit('close')">
      <div :class="['vue-modal-panel', { 'vue-modal-panel-wide': wide }]">
        <div class="vue-modal-header">
          <h4 class="vue-modal-title">{{ title }}</h4>
          <button type="button" class="close" aria-label="关闭" @click="$emit('close')">&times;</button>
        </div>
        <div class="vue-modal-body">
          <slot />
        </div>
        <div class="vue-modal-footer">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  show: { type: Boolean, default: false },
  title: { type: String, required: true },
  wide: { type: Boolean, default: false },
})

defineEmits(['close'])
</script>

<style scoped>
.vue-modal-mask {
  position: fixed;
  inset: 0;
  z-index: 1050;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}
.vue-modal-panel {
  background: #fff;
  border-radius: 6px;
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  overflow: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}
.vue-modal-panel-wide {
  max-width: 640px;
}
.vue-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #e5e5e5;
}
.vue-modal-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}
.vue-modal-body {
  padding: 16px;
}
.vue-modal-footer {
  padding: 12px 16px;
  border-top: 1px solid #e5e5e5;
  text-align: right;
}
.vue-modal-footer .btn + .btn {
  margin-left: 8px;
}
</style>
