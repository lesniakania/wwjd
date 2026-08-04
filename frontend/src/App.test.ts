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
    expect(screen.getByRole('link', { name: /Co na to Jezus.*strona główna/ })).toBeTruthy()
    expect(screen.getByRole('heading', { name: /co na to jezus/i })).toBeTruthy()
    expect(screen.getByLabelText('Co na to Jezus?')).toBeTruthy()
    expect(document.title).toBe('Co na to Jezus?')
    expect(screen.getByText(/najpierw opisz fakty/i)).toBeTruthy()
    expect(screen.getByRole('heading', { name: /jak powstaje refleksja/i })).toBeTruthy()
    expect(screen.getByText(/21 obszarów etycznych/i)).toBeTruthy()
    expect(screen.getByText(/model językowy nie wybiera dowolnych cytatów/i)).toBeTruthy()
  })

  it('switches between Polish and English', async () => {
    render(App)
    await fireEvent.click(screen.getByRole('button', { name: 'EN' }))
    expect(screen.getByRole('link', { name: /What would Jesus do.*home/ })).toBeTruthy()
    expect(screen.getByRole('heading', { name: /what would jesus do/i })).toBeTruthy()
    expect(screen.getByLabelText('What would Jesus do?')).toBeTruthy()
    expect(document.title).toBe('What would Jesus do?')
    expect(screen.getByRole('heading', { name: /how the reflection is created/i })).toBeTruthy()
    expect(screen.getByText(/21 ethical themes/i)).toBeTruthy()
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
          literary_type: 'Teaching of Jesus',
          origin_context: 'Jesus is teaching his disciples and the crowd.',
          broader_context: 'This forms part of the Sermon on the Mount.',
          original_meaning: 'Jesus calls his listeners to answer hostility with active goodwill.',
          situation_application: 'This challenges retaliation in the described situation.',
          context_sources: [{
            label: 'Matthew 5:1–7:29',
            url: 'https://bible.usccb.org/bible/matthew/5',
          }],
          context_confidence: 'high',
          context_reviewed: true,
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
    await fireEvent.click(screen.getByRole('button', { name: /^see$/i }))
    expect(await screen.findByRole('heading', { name: /Bible passages and their context/i })).toBeTruthy()
    expect(screen.queryByText('Choose honesty with compassion.')).toBeNull()
    expect(screen.getByText('Matthew 5:44')).toBeTruthy()
    expect(screen.getByText(/Jesus calls his listeners/i)).toBeTruthy()
    expect(screen.getByText(/read the complete unit/i)).toBeTruthy()
    expect(screen.getByText(/human-reviewed context based on these sources/i)).toBeTruthy()
    const sourceLink = screen.getByRole('link', { name: 'Matthew 5:1–7:29' })
    expect(sourceLink.getAttribute('href')).toBe('https://bible.usccb.org/bible/matthew/5')
  })

  it('creates and copies a share link for the exact response', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined)
    Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText } })
    const reflection = {
      summary: 'Choose honesty.', suggested_actions: ['Speak truthfully.'], safety_message: null,
      limitations: 'A reflection.', generated_with: 'local-extractive',
      sources: [{
        reference: 'Matthew 5:44', quotation: 'Love your enemies.', literary_type: 'Teaching',
        origin_context: 'A sermon.', broader_context: 'The wider sermon.', original_meaning: 'Active goodwill.',
        situation_application: 'Do not retaliate.', context_sources: [], context_confidence: 'high',
        context_reviewed: true, translation: 'WEB', context_note: null, relevance: 'Relevant.',
        context_reference: 'Matthew 5:43–45', context_quotation: 'Love your enemies.',
      }],
    }
    vi.stubGlobal('fetch', vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => reflection })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ id: 'safe-share-id' }) }))
    render(App)
    await fireEvent.update(screen.getByLabelText('Co na to Jezus?'), 'Przyjaciel mnie zranił i nie wiem, jak odpowiedzieć z miłością.')
    await fireEvent.click(screen.getByRole('button', { name: /^zobacz$/i }))
    await screen.findByText('Matthew 5:44')
    await fireEvent.click(screen.getByRole('button', { name: /^udostępnij/i }))
    expect(await screen.findByText('Link skopiowany')).toBeTruthy()
    expect(writeText).toHaveBeenCalledWith(`${window.location.origin}/share/safe-share-id`)
  })
})
