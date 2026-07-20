import { cleanup, fireEvent, render, screen } from '@testing-library/vue'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from './App.vue'

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
  vi.unstubAllGlobals()
})

describe('App', () => {
  it('guides the user before submission', () => {
    render(App)
    expect(screen.getByRole('heading', { name: /co zrobiłby jezus/i })).toBeTruthy()
    expect(screen.getByLabelText('Co zrobiłby Jezus?')).toBeTruthy()
    expect(screen.getByText(/najpierw opisz fakty/i)).toBeTruthy()
  })

  it('switches between Polish and English', async () => {
    render(App)
    await fireEvent.click(screen.getByRole('button', { name: 'EN' }))
    expect(screen.getByRole('heading', { name: /what would jesus do/i })).toBeTruthy()
    expect(screen.getByLabelText('What would Jesus do?')).toBeTruthy()
  })

  it('renders a grounded response', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        summary: 'Choose honesty with compassion.',
        suggested_actions: ['Speak truthfully.'],
        sources: [{
          reference: 'Matthew 5:44',
          quotation: 'Love your enemies.',
          translation: 'World English Bible (WEB)',
          context_note: 'From one of the four Gospels',
        }],
        safety_message: null,
        limitations: 'A reflection, not certainty.',
        generated_with: 'local-extractive',
      }),
    }))
    render(App)
    await fireEvent.click(screen.getByRole('button', { name: 'EN' }))
    await fireEvent.update(
      screen.getByLabelText('What would Jesus do?'),
      'My friend hurt me and I am unsure how to respond with kindness.',
    )
    await fireEvent.click(screen.getByRole('button', { name: /find a way forward/i }))
    expect(await screen.findByText('Choose honesty with compassion.')).toBeTruthy()
    expect(screen.getByText('Matthew 5:44')).toBeTruthy()
  })
})
