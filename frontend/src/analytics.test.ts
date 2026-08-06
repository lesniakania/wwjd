import { afterEach, describe, expect, it, vi } from 'vitest'

afterEach(() => {
  document.head.querySelectorAll('script[src*="googletagmanager.com/gtag/js"]').forEach((script) => {
    script.remove()
  })
  delete window.dataLayer
  delete window.gtag
  vi.resetModules()
  vi.unstubAllEnvs()
})

describe('analytics', () => {
  it('queues gtag commands using the arguments object expected by Google', async () => {
    vi.stubEnv('VITE_GA_MEASUREMENT_ID', 'G-TEST123')
    const { enableAnalytics } = await import('./analytics')

    enableAnalytics()

    expect(window.dataLayer).toHaveLength(2)
    expect(Array.isArray(window.dataLayer[0])).toBe(false)
    expect(Array.from(window.dataLayer[0] as ArrayLike<unknown>)[0]).toBe('js')
    expect(Array.isArray(window.dataLayer[1])).toBe(false)
    expect(Array.from(window.dataLayer[1] as ArrayLike<unknown>)).toEqual([
      'config',
      'G-TEST123',
      {
        anonymize_ip: true,
        allow_google_signals: false,
        allow_ad_personalization_signals: false,
      },
    ])
  })
})
