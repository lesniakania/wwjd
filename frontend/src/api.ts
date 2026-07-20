export interface Source {
  reference: string
  quotation: string
  explanation: string
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
