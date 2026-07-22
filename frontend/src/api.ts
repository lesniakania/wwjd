export interface Source {
  reference: string
  quotation: string
  literary_type: string
  origin_context: string
  broader_context: string
  original_meaning: string
  situation_application: string
  context_sources: string[]
  context_confidence: string
  context_reviewed: boolean
  translation: string
  context_note: string | null
  relevance: string
  context_reference: string
  context_quotation: string
}

export interface Reflection {
  summary: string
  suggested_actions: string[]
  sources: Source[]
  safety_message: string | null
  limitations: string
  generated_with: string
}

export interface SharedReflection {
  id: string
  situation: string
  language: 'pl' | 'en'
  reflection: Reflection
}

export async function requestReflection(situation: string, language: 'pl' | 'en'): Promise<Reflection> {
  const response = await fetch('/api/reflections', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ situation, language }),
  })

  if (!response.ok) {
    if (response.status === 422) {
      throw new Error(language === 'pl' ? 'Opisz sytuację trochę dokładniej.' : 'Please describe the situation in a little more detail.')
    }
    const body = await response.json().catch(() => null) as { detail?: string } | null
    throw new Error(body?.detail || (language === 'pl' ? 'Nie udało się przygotować refleksji. Spróbuj ponownie.' : 'The reflection could not be prepared. Please try again.'))
  }
  return response.json() as Promise<Reflection>
}


export async function createShare(situation: string, language: 'pl' | 'en', reflection: Reflection): Promise<string> {
  const response = await fetch('/api/shares', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ situation, language, reflection }),
  })
  if (!response.ok) throw new Error(language === 'pl' ? 'Nie udało się utworzyć linku.' : 'The share link could not be created.')
  const body = await response.json() as { id: string }
  return body.id
}

export async function getShare(id: string): Promise<SharedReflection> {
  const response = await fetch(`/api/shares/${encodeURIComponent(id)}`)
  if (!response.ok) throw new Error('Nie znaleziono udostępnionej odpowiedzi. / Shared response not found.')
  return response.json() as Promise<SharedReflection>
}
