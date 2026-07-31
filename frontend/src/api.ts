export interface Source {
  reference: string
  quotation: string
  literary_type: string
  origin_context: string
  broader_context: string
  original_meaning: string
  situation_application: string
  context_sources: ContextSource[]
  context_confidence: string
  context_reviewed: boolean
  translation: string
  context_note: string | null
  relevance: string
  context_reference: string
  context_quotation: string
}

export interface ContextSource {
  label: string
  url: string
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

interface ApiError {
  detail?: string
}

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? '').trim().replace(/\/$/, '')

function apiUrl(path: string): string {
  return `${apiBaseUrl}${path}`
}

async function responseError(response: Response, fallbackMessage: string): Promise<Error> {
  const body = await response.json().catch(() => null) as ApiError | null
  return new Error(body?.detail || fallbackMessage)
}

async function requestJson<ResponseBody>(
  url: string,
  init: RequestInit | undefined,
  fallbackMessage: string,
): Promise<ResponseBody> {
  const response = init ? await fetch(url, init) : await fetch(url)
  if (!response.ok) {
    throw await responseError(response, fallbackMessage)
  }
  return response.json() as Promise<ResponseBody>
}

export async function requestReflection(situation: string, language: 'pl' | 'en'): Promise<Reflection> {
  const validationMessage = language === 'pl'
    ? 'Opisz sytuację trochę dokładniej.'
    : 'Please describe the situation in a little more detail.'
  const response = await fetch(apiUrl('/api/reflections'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ situation, language }),
  })
  if (response.status === 422) {
    throw new Error(validationMessage)
  }
  if (!response.ok) {
    const fallbackMessage = language === 'pl'
      ? 'Nie udało się przygotować refleksji. Spróbuj ponownie.'
      : 'The reflection could not be prepared. Please try again.'
    throw await responseError(response, fallbackMessage)
  }
  return response.json() as Promise<Reflection>
}


export async function createShare(situation: string, language: 'pl' | 'en', reflection: Reflection): Promise<string> {
  const fallbackMessage = language === 'pl'
    ? 'Nie udało się utworzyć linku.'
    : 'The share link could not be created.'
  const body = await requestJson<{ id: string }>(apiUrl('/api/shares'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ situation, language, reflection }),
  }, fallbackMessage)
  return body.id
}

export async function getShare(id: string): Promise<SharedReflection> {
  return requestJson<SharedReflection>(
    apiUrl(`/api/shares/${encodeURIComponent(id)}`),
    undefined,
    'Nie znaleziono udostępnionej odpowiedzi. / Shared response not found.',
  )
}
