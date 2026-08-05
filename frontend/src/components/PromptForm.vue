<script setup lang="ts">
import { computed, ref } from "vue";
import type { LocalizedCopy } from "../localization";

const maximumLength = 3000;
const minimumLength = 20;

const props = defineProps<{
  copy: LocalizedCopy;
  loading: boolean;
  error: string;
}>();

const emit = defineEmits<{
  submit: [situation: string];
}>();

const situation = ref("");
const canSubmit = computed(
  () => situation.value.trim().length >= minimumLength && !props.loading,
);

function submit(): void {
  if (!canSubmit.value) {
    return;
  }
  emit("submit", situation.value.trim());
}

</script>

<template>
  <form class="prompt-card" @submit.prevent="submit">
    <label for="situation">{{ copy.label }}</label>
    <textarea
      id="situation"
      v-model="situation"
      :maxlength="maximumLength"
      rows="7"
      :placeholder="copy.placeholder"
      aria-describedby="prompt-help"
      @keydown.ctrl.enter.prevent="submit"
      @keydown.meta.enter.prevent="submit"
    ></textarea>
    <div class="field-footer">
      <span id="prompt-help">{{ copy.privacy }}</span>
      <span>{{ situation.length }} / {{ maximumLength }}</span>
    </div>
    <button type="submit" :disabled="!canSubmit">
      <span v-if="loading" class="spinner" aria-hidden="true"></span>
      {{ loading ? copy.loading : copy.submit }}
      <span v-if="!loading" aria-hidden="true">→</span>
    </button>
  </form>
  <p v-if="error" class="error" role="alert">{{ error }}</p>
</template>
