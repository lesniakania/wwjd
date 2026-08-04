<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { Link2, Share2 } from "@lucide/vue";
import {
  createShare,
  getShare,
  requestReflection,
  type Reflection,
} from "./api";
import {
  analyticsIsConfigured,
  enableAnalytics,
  trackEvent,
} from "./analytics";
import PromptForm from "./components/PromptForm.vue";
import { copyFor, Language, languageFrom } from "./localization";

const language = ref<Language>(Language.Polish);
const situation = ref("");
const reflection = ref<Reflection | null>(null);
const loading = ref(false);
const error = ref("");
const isSharedView = ref(false);
const sharing = ref(false);
const shareStatus = ref("");
const shareUrl = ref("");
type AnalyticsConsent = "accepted" | "rejected" | null;
const analyticsConsent = ref<AnalyticsConsent>(null);
const consentStorageKey = "wwjd-analytics-consent";

const t = computed(() => copyFor(language.value));

async function submit(submittedSituation: string): Promise<void> {
  situation.value = submittedSituation;
  loading.value = true;
  trackEvent("reflection_requested", { language: language.value });
  error.value = "";
  reflection.value = null;
  try {
    reflection.value = await requestReflection(
      submittedSituation,
      language.value,
    );
    trackEvent("reflection_received", {
      language: language.value,
      source_count: reflection.value.sources.length,
    });
  } catch (caught) {
    trackEvent("reflection_error", { language: language.value });
    error.value =
      caught instanceof Error ? caught.message : t.value.fallbackError;
  } finally {
    loading.value = false;
  }
}

function setLanguage(next: Language): void {
  language.value = next;
  reflection.value = null;
  error.value = "";
  trackEvent("language_changed", { language: next });
}

watch(
  language,
  (value) => {
    document.documentElement.setAttribute("lang", value);
    document.title = copyFor(value).appTitle;
  },
  { immediate: true },
);

function reset() {
  if (isSharedView.value) {
    window.location.href = "/";
    return;
  }
  reflection.value = null;
  error.value = "";
  situation.value = "";
}

async function shareReflection() {
  if (!reflection.value || sharing.value) return;
  sharing.value = true;
  shareStatus.value = "";
  try {
    if (!shareUrl.value) {
      const id = await createShare(
        situation.value,
        language.value,
        reflection.value,
      );
      shareUrl.value = `${window.location.origin}/share/${id}`;
    }
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(shareUrl.value);
      shareStatus.value = t.value.shared;
    } else {
      shareStatus.value = t.value.ready;
    }
    trackEvent("reflection_shared", { language: language.value });
  } catch (caught) {
    shareStatus.value =
      caught instanceof Error ? caught.message : t.value.fallbackError;
  } finally {
    sharing.value = false;
  }
}

function setAnalyticsConsent(value: Exclude<AnalyticsConsent, null>) {
  analyticsConsent.value = value;
  localStorage.setItem(consentStorageKey, value);
  if (value === "accepted") enableAnalytics();
}

onMounted(async () => {
  const match = window.location.pathname.match(/^\/share\/([^/]+)\/?$/);
  if (match) {
    loading.value = true;
    try {
      const shared = await getShare(match[1]);
      language.value = languageFrom(shared.language);
      situation.value = shared.situation;
      reflection.value = shared.reflection;
      isSharedView.value = true;
    } catch (caught) {
      error.value =
        caught instanceof Error
          ? caught.message
          : copyFor(Language.Polish).fallbackError;
    } finally {
      loading.value = false;
    }
  }
  if (!analyticsIsConfigured()) return;
  const savedConsent = localStorage.getItem(consentStorageKey);
  if (savedConsent === "accepted" || savedConsent === "rejected") {
    analyticsConsent.value = savedConsent;
    if (savedConsent === "accepted") enableAnalytics();
  }
});
</script>

<template>
  <div class="page-shell">
    <header class="site-header">
      <a class="wordmark" href="#" :aria-label="t.homeLabel">
        <span class="wordmark-mark">J</span>
        <span>{{ t.appTitle }}</span>
      </a>
      <div class="header-actions">
        <span class="header-note">{{ t.header }}</span>
        <div
          v-if="!isSharedView"
          class="language-switch"
          aria-label="Language / Język"
        >
          <button
            type="button"
            :class="{ active: language === Language.Polish }"
            :aria-pressed="language === Language.Polish"
            @click="setLanguage(Language.Polish)"
          >
            PL
          </button>
          <button
            type="button"
            :class="{ active: language === Language.English }"
            :aria-pressed="language === Language.English"
            @click="setLanguage(Language.English)"
          >
            EN
          </button>
        </div>
      </div>
    </header>

    <main>
      <template v-if="!reflection">
      <section class="hero" aria-labelledby="page-title">
        <div class="eyebrow"><span></span> {{ t.eyebrow }}</div>
        <h1 id="page-title">
          {{ t.title1 }}<br /><em>{{ t.title2 }}</em>
        </h1>
        <p class="intro">{{ t.intro }}</p>

        <PromptForm
          :key="language"
          :copy="t"
          :loading="loading"
          :error="error"
          @submit="submit"
        />

        <aside class="tips" aria-labelledby="tips-title">
          <p id="tips-title">{{ t.tipsTitle }}</p>
          <ul>
            <li v-for="tip in t.tips" :key="tip">{{ tip }}</li>
          </ul>
        </aside>
      </section>

      <section class="algorithm" aria-labelledby="algorithm-title">
        <div class="algorithm-heading">
          <div class="eyebrow"><span></span> {{ t.algorithmEyebrow }}</div>
          <h2 id="algorithm-title">{{ t.algorithmTitle }}</h2>
          <p>{{ t.algorithmIntro }}</p>
        </div>
        <ol class="algorithm-steps">
          <li v-for="(step, index) in t.algorithmSteps" :key="step.title">
            <span class="algorithm-number">{{ String(index + 1).padStart(2, "0") }}</span>
            <div>
              <h3>{{ step.title }}</h3>
              <p>{{ step.body }}</p>
            </div>
          </li>
        </ol>
        <p class="algorithm-safeguard">{{ t.algorithmSafeguard }}</p>
      </section>
      </template>

      <section v-else class="result" aria-live="polite">
        <button class="back-button" type="button" @click="reset">
          ← {{ t.back }}
        </button>

        <div class="result-tools">
          <span v-if="isSharedView" class="shared-badge">{{
            t.sharedBadge
          }}</span>
          <template v-else>
            <div class="share-controls">
              <button
                class="share-button"
                type="button"
                :disabled="sharing"
                @click="shareReflection"
              >
                {{ sharing ? t.sharing : t.share }}
                <Share2 v-if="!sharing" class="share-icon" aria-hidden="true" />
              </button>
              <span class="share-privacy">{{ t.sharePrivacy }}</span>
              <a v-if="shareUrl" class="share-link" :href="shareUrl">
                <Link2 class="share-link-icon" aria-hidden="true" />
                <span class="share-link-url">{{ shareUrl }}</span>
                <span v-if="shareStatus" class="share-link-status" role="status">{{
                  shareStatus
                }}</span>
              </a>
              <span v-else-if="shareStatus" class="share-status" role="status">{{
                shareStatus
              }}</span>
            </div>
          </template>
        </div>

        <section
          class="shared-question"
          aria-labelledby="shared-question-title"
        >
          <span id="shared-question-title">{{
            isSharedView ? t.sharedQuestion : t.question
          }}</span>
          <p>{{ situation }}</p>
        </section>

        <div v-if="reflection.safety_message" class="safety" role="alert">
          <strong>{{ t.safetyTitle }}</strong>
          <p>{{ reflection.safety_message }}</p>
        </div>

        <section class="sources" aria-labelledby="sources-title">
          <div class="section-heading">
            <p>{{ t.read }}</p>
            <h2 id="sources-title">{{ t.sources }}</h2>
          </div>
          <div class="source-grid">
            <figure
              v-for="source in reflection.sources"
              :key="source.reference"
              class="source-card"
            >
              <span class="quote-label">{{ t.selectedVerse }}</span>
              <blockquote class="focus-quote">
                “{{ source.quotation }}”
              </blockquote>
              <figcaption>
                <strong>{{ source.reference }}</strong>
                <span class="context-kind">{{ source.literary_type }}</span>
                <span class="explanation-label">{{ t.contextOrigin }}</span>
                <p class="explanation">{{ source.origin_context }}</p>
                <span class="explanation-label">{{ t.broaderContext }}</span>
                <p class="explanation">{{ source.broader_context }}</p>
                <span class="explanation-label">{{ t.originalMeaning }}</span>
                <p class="explanation">{{ source.original_meaning }}</p>
                <span class="explanation-label">{{ t.application }}</span>
                <p class="explanation application">
                  {{ source.situation_application }}
                </p>
                <details class="context-block">
                  <summary>
                    {{ t.passageContext }} · {{ source.context_reference }}
                  </summary>
                  <p>{{ source.context_quotation }}</p>
                </details>
                <details
                  v-if="source.context_sources.length"
                  class="context-sources"
                >
                  <summary>{{ t.contextSources }}</summary>
                  <ul>
                    <li v-for="item in source.context_sources" :key="item.url">
                      <a :href="item.url" target="_blank" rel="noopener noreferrer">
                        {{ item.label }}
                      </a>
                    </li>
                  </ul>
                </details>
                <span>{{ source.translation }}</span>
                <small v-if="source.context_note">{{
                  source.context_note
                }}</small>
              </figcaption>
            </figure>
          </div>
        </section>

        <p class="limitations">{{ reflection.limitations }}</p>
      </section>
    </main>

    <footer>
      <span>{{ t.footerBible }}</span>
      <span>{{ t.footerPrivacy }}</span>
    </footer>

    <aside
      v-if="analyticsIsConfigured() && analyticsConsent === null"
      class="analytics-consent"
      aria-label="Google Analytics"
    >
      <p>{{ t.analyticsText }}</p>
      <div>
        <button
          type="button"
          class="consent-accept"
          @click="setAnalyticsConsent('accepted')"
        >
          {{ t.analyticsAccept }}
        </button>
        <button type="button" @click="setAnalyticsConsent('rejected')">
          {{ t.analyticsReject }}
        </button>
      </div>
    </aside>
  </div>
</template>
