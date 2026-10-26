export type HealthStatus = 'ready' | 'demo' | 'unavailable' | 'offline'

export interface Health {
  status: HealthStatus
  ready: boolean
  demo: boolean
  detail: string | null
}

export interface AskResult {
  question: string
  answer: string
}

// Fallback to live Render backend if VITE_API_BASE_URL is not set
const API_BASE =
  (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '') ||
  'https://mediaudit-ai-gcxb.onrender.com'

async function parseError(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown }

    if (typeof body.detail === 'string') {
      return body.detail
    }
  } catch {
    // fall through to the generic message
  }

  return `Request failed with status ${response.status}.`
}

export async function fetchHealth(signal?: AbortSignal): Promise<Health> {
  try {
    const response = await fetch(`${API_BASE}/api/health`, { signal })

    if (!response.ok) {
      return {
        status: 'unavailable',
        ready: false,
        demo: false,
        detail: await parseError(response),
      }
    }

    return (await response.json()) as Health
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw error
    }

    return {
      status: 'offline',
      ready: false,
      demo: false,
      detail: 'Backend service is waking up on Render. This usually takes 20-30 seconds on cold start.',
    }
  }
}

export async function askQuestion(question: string, signal?: AbortSignal): Promise<AskResult> {
  try {
    const response = await fetch(`${API_BASE}/api/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
      signal,
    })

    if (!response.ok) {
      throw new Error(await parseError(response))
    }

    return (await response.json()) as AskResult
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw error
    }

    if (error instanceof TypeError && error.message.toLowerCase().includes('fetch')) {
      throw new Error(
        'Backend server is waking up from sleep. Please wait ~15-20 seconds and click send again!'
      )
    }

    throw error
  }
}
