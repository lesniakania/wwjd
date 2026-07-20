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
          relevance: 'This passage addresses honesty.',
          context_reference: 'Matthew 5:42–46',
          context_quotation: '[42] Give to him who asks you. [44] Love your enemies.',
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

  it('continues with a source-grounded follow-up conversation', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          summary: 'Choose honesty with compassion.', suggested_actions: ['Check the facts.'],
          sources: [{ reference: 'Proverbs 18:13', quotation: 'He who answers before he hears...', translation: 'WEB', context_note: null, relevance: 'Checking claims.', context_reference: 'Proverbs 18:11–15', context_quotation: 'Context.' }],
          safety_message: null, limitations: 'A reflection, not certainty.', generated_with: 'local-extractive',
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          answer: 'The passage asks you to listen before reaching a conclusion.',
          sources: [{ reference: 'Proverbs 18:13', quotation: 'He who answers before he hears...', translation: 'WEB', context_note: null, relevance: 'Checking claims.', context_reference: 'Proverbs 18:11–15', context_quotation: 'Context.' }],
          safety_message: null, limitations: 'A reflection, not certainty.', generated_with: 'local-extractive',
        }),
      })
    vi.stubGlobal('fetch', fetchMock)
    render(App)
    await fireEvent.click(screen.getByRole('button', { name: 'EN' }))
    await fireEvent.update(screen.getByLabelText('What would Jesus do?'), 'I saw a claim online and want to judge the situation fairly.')
    await fireEvent.click(screen.getByRole('button', { name: /find a way forward/i }))
    await screen.findByText('Choose honesty with compassion.')
    await fireEvent.update(screen.getByLabelText('Your question'), 'What does this passage mean in context?')
    await fireEvent.click(screen.getByRole('button', { name: 'Ask' }))
    expect(await screen.findByText(/listen before reaching a conclusion/i)).toBeTruthy()
    expect(fetchMock).toHaveBeenLastCalledWith('/api/chat', expect.objectContaining({ method: 'POST' }))
  })
})
