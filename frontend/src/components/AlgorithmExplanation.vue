<script setup lang="ts">
import type { LocalizedCopy } from "../localization";

defineProps<{
  copy: LocalizedCopy;
}>();
</script>

<template>
  <section class="algorithm" aria-labelledby="algorithm-title">
    <div class="algorithm-heading">
      <div class="eyebrow"><span></span> {{ copy.algorithmEyebrow }}</div>
      <h2 id="algorithm-title">{{ copy.algorithmTitle }}</h2>
      <p>{{ copy.algorithmIntro }}</p>
    </div>
    <ol class="algorithm-steps">
      <li v-for="(step, index) in copy.algorithmSteps" :key="step.title">
        <span class="algorithm-number">{{ String(index + 1).padStart(2, "0") }}</span>
        <div>
          <h3>{{ step.title }}</h3>
          <p>{{ step.body }}</p>
        </div>
      </li>
    </ol>
    <p class="algorithm-safeguard">{{ copy.algorithmSafeguard }}</p>
    <a
      class="algorithm-technical-link"
      href="https://github.com/lesniakania/wwjd/blob/main/ALGORITHM.md#reflection-algorithm"
      target="_blank"
      rel="noopener noreferrer"
    >
      {{ copy.algorithmTechnicalDescription }} <span aria-hidden="true">→</span>
    </a>
  </section>
</template>
