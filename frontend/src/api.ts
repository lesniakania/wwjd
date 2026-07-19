export interface Source {
  reference: string
  quotation: string
  translation: string
  context_note: string | null
}

export interface Reflection {
  summary: string
  suggested_actions: string[]
  sources: Source[]
  safety_message: string | null
  limitations: string
  generated_with: string
}

export async function requestReflection(situation: string): Promise<Reflection> {
  const response = await fetch('/api/reflections', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ situation }),
  })

  if (!response.ok) {
    if (response.status === 422) {
      throw new Error('Please describe the situation in a little more detail.')
    }
    throw new Error('The reflection could not be prepared. Please try again.')
  }
  return response.json() as Promise<Reflection>
}

