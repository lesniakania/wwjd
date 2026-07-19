<script setup lang="ts">
import { computed, ref } from 'vue'
import { requestReflection, type Reflection } from './api'

const maxLength = 3000
const situation = ref('')
const reflection = ref<Reflection | null>(null)
const loading = ref(false)
const error = ref('')

const tips = [
  'Describe the facts before your interpretation of them.',
  'Include the decision you are trying to make.',
  'Mention who may be helped or harmed by the decision.',
  'Leave out names, addresses, and identifying details.',
]

const canSubmit = computed(() => situation.value.trim().length >= 20 && !loading.value)

async function submit() {
  if (!canSubmit.value) return
  loading.value = true
  error.value = ''
  reflection.value = null
  try {
    reflection.value = await requestReflection(situation.value.trim())
  } catch (caught) {
    error.value = caught instanceof Error ? caught.message : 'Something went wrong.'
  } finally {
    loading.value = false
  }
}

function reset() {
  reflection.value = null
  error.value = ''
  situation.value = ''
}
</script>

<template>
  <div class="page-shell">
    <header class="site-header">
      <a class="wordmark" href="#" aria-label="WWJD home">
        <span class="wordmark-mark">W</span>
        <span>WWJD</span>
      </a>
      <span class="header-note">A Bible-grounded reflection</span>
    </header>

    <main>
      <section v-if="!reflection" class="hero" aria-labelledby="page-title">
        <div class="eyebrow"><span></span> A moment to pause</div>
        <h1 id="page-title">What would<br /><em>Jesus do?</em></h1>
        <p class="intro">
          Describe what you are facing. We’ll look for relevant Scripture and offer a thoughtful,
          practical reflection—grounded in the text, not certainty.
        </p>

        <form class="prompt-card" @submit.prevent="submit">
          <label for="situation">What would Jesus do?</label>
          <textarea
            id="situation"
            v-model="situation"
            :maxlength="maxLength"
            rows="7"
            placeholder="I’m struggling with a decision at work..."
            aria-describedby="prompt-help"
          ></textarea>
          <div class="field-footer">
            <span id="prompt-help">Share the situation, not anyone’s private details.</span>
            <span>{{ situation.length }} / {{ maxLength }}</span>
          </div>
          <button type="submit" :disabled="!canSubmit">
            <span v-if="loading" class="spinner" aria-hidden="true"></span>
            {{ loading ? 'Reflecting…' : 'Find a way forward' }}
            <span v-if="!loading" aria-hidden="true">→</span>
          </button>
        </form>

        <p v-if="error" class="error" role="alert">{{ error }}</p>

        <aside class="tips" aria-labelledby="tips-title">
          <p id="tips-title">A clearer situation leads to a more useful reflection</p>
          <ul>
            <li v-for="tip in tips" :key="tip">{{ tip }}</li>
          </ul>
        </aside>
      </section>

      <section v-else class="result" aria-live="polite">
        <button class="back-button" type="button" @click="reset">← Ask another question</button>
        <div class="result-heading">
          <div class="eyebrow"><span></span> A grounded reflection</div>
          <h1>A way<br /><em>forward.</em></h1>
        </div>

        <div v-if="reflection.safety_message" class="safety" role="alert">
          <strong>Pause and seek immediate support</strong>
          <p>{{ reflection.safety_message }}</p>
        </div>

        <article class="reflection-card">
          <p class="summary">{{ reflection.summary }}</p>
          <h2>Consider these next steps</h2>
          <ol>
            <li v-for="action in reflection.suggested_actions" :key="action">{{ action }}</li>
          </ol>
        </article>

        <section class="sources" aria-labelledby="sources-title">
          <div class="section-heading">
            <p>Read it for yourself</p>
            <h2 id="sources-title">Scripture behind the reflection</h2>
          </div>
          <div class="source-grid">
            <figure v-for="source in reflection.sources" :key="source.reference" class="source-card">
              <blockquote>“{{ source.quotation }}”</blockquote>
              <figcaption>
                <strong>{{ source.reference }}</strong>
                <span>{{ source.translation }}</span>
                <small v-if="source.context_note">{{ source.context_note }}</small>
              </figcaption>
            </figure>
          </div>
        </section>

        <p class="limitations">{{ reflection.limitations }}</p>
      </section>
    </main>

    <footer>
      <span>Scripture quotations from the public-domain World English Bible.</span>
      <span>Your situation is not stored by this application.</span>
    </footer>
  </div>
</template>

