export interface Source {
  source_id: string
  reference: string
  quotation: string
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

export interface ConversationTurn {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatReply {
  answer: string
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
    throw new Error(language === 'pl' ? 'Nie udało się przygotować refleksji. Spróbuj ponownie.' : 'The reflection could not be prepared. Please try again.')
  }
  return response.json() as Promise<Reflection>
}

export async function continueConversation(
  situation: string,
  question: string,
  history: ConversationTurn[],
  sourceIds: string[],
  language: 'pl' | 'en',
): Promise<ChatReply> {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ situation, question, history, source_ids: sourceIds, language }),
  })

  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: string } | null
    throw new Error(body?.detail || (language === 'pl'
      ? 'Nie udało się odpowiedzieć. Spróbuj ponownie.'
      : 'The question could not be answered. Please try again.'))
  }
  return response.json() as Promise<ChatReply>
}
