<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { continueConversation, requestReflection, type ConversationTurn, type Reflection, type Source } from './api'

const maxLength = 3000
type Language = 'pl' | 'en'
const language = ref<Language>('pl')
const situation = ref('')
const reflection = ref<Reflection | null>(null)
const loading = ref(false)
const chatLoading = ref(false)
const error = ref('')
const followup = ref('')
interface ChatMessage extends ConversationTurn {
  sources?: Source[]
  safetyMessage?: string | null
}
const conversation = ref<ChatMessage[]>([])

const copy = {
  pl: {
    header: 'Refleksja oparta na Biblii', eyebrow: 'Chwila na zatrzymanie', title1: 'Co zrobiłby', title2: 'Jezus?',
    intro: 'Opisz, z czym się mierzysz. Odszukamy odpowiednie fragmenty Pisma i zaproponujemy przemyślaną, praktyczną refleksję — opartą na tekście, nie na pewności.',
    label: 'Co zrobiłby Jezus?', placeholder: 'Zmagam się z trudną decyzją w pracy…', privacy: 'Opisz sytuację bez prywatnych danych innych osób.',
    submit: 'Znajdź drogę naprzód', loading: 'Szukam odpowiedzi…', tipsTitle: 'Jaśniejszy opis sytuacji pozwala stworzyć bardziej pomocną refleksję',
    tips: ['Najpierw opisz fakty, a potem własną interpretację.', 'Napisz, jaką decyzję próbujesz podjąć.', 'Wspomnij, komu ta decyzja może pomóc lub zaszkodzić.', 'Pomiń imiona, adresy i dane pozwalające zidentyfikować osoby.'],
    fallbackError: 'Coś poszło nie tak.', back: 'Zadaj inne pytanie', resultEyebrow: 'Refleksja oparta na źródłach',
    result1: 'Droga', result2: 'naprzód.', safetyTitle: 'Zatrzymaj się i poszukaj natychmiastowego wsparcia', actions: 'Rozważ te kolejne kroki',
    read: 'Przeczytaj samodzielnie', sources: 'Pismo stojące za refleksją', footerBible: 'Cytaty: Uwspółcześniona Biblia Gdańska, © 2018 Fundacja Wrota Nadziei, CC BY-ND 4.0.',
    selectedVerse: 'Wybrany werset', passageContext: 'Kontekst fragmentu',
    footerPrivacy: 'Ta aplikacja nie zapisuje opisu Twojej sytuacji.',
    chatTitle: 'Porozmawiaj o tych fragmentach', chatIntro: 'Zapytaj o kontekst, znaczenie albo możliwe zastosowanie. Odpowiedź pozostanie oparta na pokazanych źródłach.',
    chatLabel: 'Twoje pytanie', chatPlaceholder: 'Dlaczego ten fragment pasuje do mojej sytuacji?', send: 'Zapytaj', sending: 'Odpowiadam…',
    you: 'Ty', guide: 'Przewodnik', cited: 'Fragmenty wykorzystane w odpowiedzi',
    prompts: ['Wyjaśnij kontekst pierwszego fragmentu', 'Dlaczego te cytaty pasują do tej sytuacji?', 'Czego nie należy z nich wywnioskować?'],
  },
  en: {
    header: 'A Bible-grounded reflection', eyebrow: 'A moment to pause', title1: 'What would', title2: 'Jesus do?',
    intro: 'Describe what you are facing. We’ll look for relevant Scripture and offer a thoughtful, practical reflection—grounded in the text, not certainty.',
    label: 'What would Jesus do?', placeholder: 'I’m struggling with a decision at work...', privacy: 'Share the situation, not anyone’s private details.',
    submit: 'Find a way forward', loading: 'Reflecting…', tipsTitle: 'A clearer situation leads to a more useful reflection',
    tips: ['Describe the facts before your interpretation of them.', 'Include the decision you are trying to make.', 'Mention who may be helped or harmed by the decision.', 'Leave out names, addresses, and identifying details.'],
    fallbackError: 'Something went wrong.', back: 'Ask another question', resultEyebrow: 'A grounded reflection',
    result1: 'A way', result2: 'forward.', safetyTitle: 'Pause and seek immediate support', actions: 'Consider these next steps',
    read: 'Read it for yourself', sources: 'Scripture behind the reflection', footerBible: 'Scripture quotations from the public-domain World English Bible.',
    selectedVerse: 'Selected verse', passageContext: 'Passage context',
    footerPrivacy: 'Your situation is not stored by this application.',
    chatTitle: 'Talk through these passages', chatIntro: 'Ask about context, meaning, or a possible application. The answer will remain grounded in the displayed sources.',
    chatLabel: 'Your question', chatPlaceholder: 'Why does this passage fit my situation?', send: 'Ask', sending: 'Answering…',
    you: 'You', guide: 'Guide', cited: 'Passages used in this answer',
    prompts: ['Explain the context of the first passage', 'Why do these quotations fit this situation?', 'What should I not infer from them?'],
  },
} as const

const t = computed(() => copy[language.value])

const canSubmit = computed(() => situation.value.trim().length >= 20 && !loading.value)

async function submit() {
  if (!canSubmit.value) return
  loading.value = true
  error.value = ''
  reflection.value = null
  try {
    reflection.value = await requestReflection(situation.value.trim(), language.value)
    conversation.value = []
  } catch (caught) {
    error.value = caught instanceof Error ? caught.message : t.value.fallbackError
  } finally {
    loading.value = false
  }
}

function setLanguage(next: Language) {
  language.value = next
  reflection.value = null
  conversation.value = []
  error.value = ''
}

watch(language, (value) => document.documentElement.setAttribute('lang', value), { immediate: true })

function reset() {
  reflection.value = null
  error.value = ''
  situation.value = ''
  followup.value = ''
  conversation.value = []
}

async function askFollowup() {
  const question = followup.value.trim()
  if (!reflection.value || question.length < 2 || chatLoading.value) return
  const history = conversation.value.map(({ role, content }) => ({ role, content }))
  conversation.value.push({ role: 'user', content: question })
  followup.value = ''
  chatLoading.value = true
  error.value = ''
  try {
    const reply = await continueConversation(situation.value.trim(), question, history, language.value)
    conversation.value.push({
      role: 'assistant', content: reply.answer, sources: reply.sources, safetyMessage: reply.safety_message,
    })
  } catch (caught) {
    error.value = caught instanceof Error ? caught.message : t.value.fallbackError
  } finally {
    chatLoading.value = false
  }
}

function askPrompt(prompt: string) {
  followup.value = prompt
  void askFollowup()
}
</script>

<template>
  <div class="page-shell">
    <header class="site-header">
      <a class="wordmark" href="#" aria-label="WWJD home">
        <span class="wordmark-mark">W</span>
        <span>WWJD</span>
      </a>
      <div class="header-actions">
        <span class="header-note">{{ t.header }}</span>
        <div class="language-switch" aria-label="Language / Język">
          <button type="button" :class="{ active: language === 'pl' }" :aria-pressed="language === 'pl'" @click="setLanguage('pl')">PL</button>
          <button type="button" :class="{ active: language === 'en' }" :aria-pressed="language === 'en'" @click="setLanguage('en')">EN</button>
        </div>
      </div>
    </header>

    <main>
      <section v-if="!reflection" class="hero" aria-labelledby="page-title">
        <div class="eyebrow"><span></span> {{ t.eyebrow }}</div>
        <h1 id="page-title">{{ t.title1 }}<br /><em>{{ t.title2 }}</em></h1>
        <p class="intro">{{ t.intro }}</p>

        <form class="prompt-card" @submit.prevent="submit">
          <label for="situation">{{ t.label }}</label>
          <textarea
            id="situation"
            v-model="situation"
            :maxlength="maxLength"
            rows="7"
            :placeholder="t.placeholder"
            aria-describedby="prompt-help"
          ></textarea>
          <div class="field-footer">
            <span id="prompt-help">{{ t.privacy }}</span>
            <span>{{ situation.length }} / {{ maxLength }}</span>
          </div>
          <button type="submit" :disabled="!canSubmit">
            <span v-if="loading" class="spinner" aria-hidden="true"></span>
            {{ loading ? t.loading : t.submit }}
            <span v-if="!loading" aria-hidden="true">→</span>
          </button>
        </form>

        <p v-if="error" class="error" role="alert">{{ error }}</p>

        <aside class="tips" aria-labelledby="tips-title">
          <p id="tips-title">{{ t.tipsTitle }}</p>
          <ul>
            <li v-for="tip in t.tips" :key="tip">{{ tip }}</li>
          </ul>
        </aside>
      </section>

      <section v-else class="result" aria-live="polite">
        <button class="back-button" type="button" @click="reset">← {{ t.back }}</button>
        <div class="result-heading">
          <div class="eyebrow"><span></span> {{ t.resultEyebrow }}</div>
          <h1>{{ t.result1 }}<br /><em>{{ t.result2 }}</em></h1>
        </div>

        <div v-if="reflection.safety_message" class="safety" role="alert">
          <strong>{{ t.safetyTitle }}</strong>
          <p>{{ reflection.safety_message }}</p>
        </div>

        <article class="reflection-card">
          <p class="summary">{{ reflection.summary }}</p>
          <h2>{{ t.actions }}</h2>
          <ol>
            <li v-for="action in reflection.suggested_actions" :key="action">{{ action }}</li>
          </ol>
        </article>

        <section class="sources" aria-labelledby="sources-title">
          <div class="section-heading">
            <p>{{ t.read }}</p>
            <h2 id="sources-title">{{ t.sources }}</h2>
          </div>
          <div class="source-grid">
            <figure v-for="source in reflection.sources" :key="source.reference" class="source-card">
              <span class="quote-label">{{ t.selectedVerse }}</span>
              <blockquote class="focus-quote">“{{ source.quotation }}”</blockquote>
              <figcaption>
                <strong>{{ source.reference }}</strong>
                <p class="relevance">{{ source.relevance }}</p>
                <details class="context-block" open>
                  <summary>{{ t.passageContext }} · {{ source.context_reference }}</summary>
                  <p>{{ source.context_quotation }}</p>
                </details>
                <span>{{ source.translation }}</span>
                <small v-if="source.context_note">{{ source.context_note }}</small>
              </figcaption>
            </figure>
          </div>
        </section>

        <section class="conversation" aria-labelledby="chat-title">
          <div class="section-heading">
            <p>{{ t.guide }}</p>
            <h2 id="chat-title">{{ t.chatTitle }}</h2>
            <span>{{ t.chatIntro }}</span>
          </div>

          <div v-if="conversation.length" class="message-list" aria-live="polite">
            <article v-for="(message, index) in conversation" :key="index" class="message" :class="message.role">
              <span class="message-role">{{ message.role === 'user' ? t.you : t.guide }}</span>
              <p>{{ message.content }}</p>
              <div v-if="message.safetyMessage" class="safety" role="alert">{{ message.safetyMessage }}</div>
              <details v-if="message.sources?.length" class="message-sources">
                <summary>{{ t.cited }} ({{ message.sources.length }})</summary>
                <ul>
                  <li v-for="source in message.sources" :key="source.reference">
                    <strong>{{ source.reference }}</strong> — “{{ source.quotation }}”
                  </li>
                </ul>
              </details>
            </article>
          </div>

          <div v-if="!conversation.length" class="prompt-suggestions">
            <button v-for="prompt in t.prompts" :key="prompt" type="button" @click="askPrompt(prompt)">{{ prompt }}</button>
          </div>

          <form class="chat-form" @submit.prevent="askFollowup">
            <label for="followup">{{ t.chatLabel }}</label>
            <div class="chat-input-row">
              <textarea id="followup" v-model="followup" rows="2" maxlength="1000" :placeholder="t.chatPlaceholder"></textarea>
              <button type="submit" :disabled="followup.trim().length < 2 || chatLoading">
                <span v-if="chatLoading" class="spinner" aria-hidden="true"></span>
                {{ chatLoading ? t.sending : t.send }}
              </button>
            </div>
          </form>
          <p v-if="error" class="error" role="alert">{{ error }}</p>
        </section>

        <p class="limitations">{{ reflection.limitations }}</p>
      </section>
    </main>

    <footer>
      <span>{{ t.footerBible }}</span>
      <span>{{ t.footerPrivacy }}</span>
    </footer>
  </div>
</template>
