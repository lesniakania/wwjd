const measurementId = import.meta.env.VITE_GA_MEASUREMENT_ID?.trim()

declare global {
  interface Window {
    dataLayer: unknown[]
    gtag: (...args: unknown[]) => void
  }
}

let initialized = false

export function enableAnalytics() {
  if (!measurementId || initialized || typeof document === 'undefined') return

  initialized = true
  window.dataLayer = window.dataLayer || []
  window.gtag = function () {
    // Google Tag expects the array-like Arguments object, not a rest-parameter array.
    // eslint-disable-next-line prefer-rest-params
    window.dataLayer.push(arguments)
  }
  window.gtag('js', new Date())
  window.gtag('config', measurementId, {
    anonymize_ip: true,
    allow_google_signals: false,
    allow_ad_personalization_signals: false,
  })

  const script = document.createElement('script')
  script.async = true
  script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(measurementId)}`
  document.head.appendChild(script)
}

export function trackEvent(name: string, parameters: Record<string, string | number | boolean> = {}) {
  if (!initialized) return
  window.gtag('event', name, parameters)
}

export function analyticsIsConfigured() {
  return Boolean(measurementId)
}
