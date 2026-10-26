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
  provenance?: {
    source?: string
    medicine?: string
    section?: string
    matched_records?: number
  }
}

// In production, empty string uses Vercel's edge proxy (/api/* -> Render backend)
// avoiding any browser CORS or third-party domain blocking.
const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')

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
      detail: 'Connecting to medical knowledge pipeline...',
    }
  }
}

export async function askQuestion(
  question: string,
  signal?: AbortSignal,
  retryCount = 0
): Promise<AskResult> {
  try {
    const response = await fetch(`${API_BASE}/api/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
      signal,
    })

    // If Render is in the middle of a cold boot, Vercel edge proxy returns 502/504 timeout.
    // Instead of failing, wait 5 seconds and retry while the container finishes booting!
    if ((response.status === 502 || response.status === 504) && retryCount < 4) {
      console.warn(`Backend is waking up (status ${response.status}). Retrying in 5s (attempt ${retryCount + 1}/4)...`)
      await new Promise((resolve) => setTimeout(resolve, 5000))
      if (signal?.aborted) {
        throw new DOMException('Aborted', 'AbortError')
      }
      return askQuestion(question, signal, retryCount + 1)
    }

    if (!response.ok) {
      throw new Error(await parseError(response))
    }

    return (await response.json()) as AskResult
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw error
    }

    if (error instanceof TypeError && error.message.toLowerCase().includes('fetch')) {
      if (retryCount < 3) {
        await new Promise((resolve) => setTimeout(resolve, 5000))
        if (signal?.aborted) {
          throw new DOMException('Aborted', 'AbortError')
        }
        return askQuestion(question, signal, retryCount + 1)
      }
      throw new Error(
        'The backend server is waking up from sleep mode (Render cold start takes ~40s). Please wait a few seconds and send again!'
      )
    }

    throw error
  }
}
