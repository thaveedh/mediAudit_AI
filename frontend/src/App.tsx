import { useCallback, useEffect, useRef, useState } from 'react'
import { Info } from 'lucide-react'

import { askQuestion, fetchHealth, type Health } from './api'
import { Composer } from './components/Composer'
import { Message, ThinkingMessage, type ChatMessage } from './components/Message'
import { Sidebar } from './components/Sidebar'
import { StatusPill } from './components/StatusPill'
import { Welcome } from './components/Welcome'

function createId() {
  return Math.random().toString(36).slice(2)
}

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [health, setHealth] = useState<Health | null>(null)

  const abortRef = useRef<AbortController | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    let cancelled = false
    let timer: ReturnType<typeof setTimeout> | null = null

    const check = () => {
      const controller = new AbortController()

      fetchHealth(controller.signal)
        .then((res) => {
          if (!cancelled) {
            setHealth(res)
            // If the server is offline or waking up, check again in 4 seconds
            if (!res.ready) {
              timer = setTimeout(check, 4000)
            }
          }
        })
        .catch(() => {
          if (!cancelled) {
            timer = setTimeout(check, 4000)
          }
        })
    }

    check()

    return () => {
      cancelled = true
      if (timer) clearTimeout(timer)
    }
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, busy])

  const send = useCallback(
    async (raw: string) => {
      const question = raw.trim()

      if (!question || busy) {
        return
      }

      const controller = new AbortController()
      abortRef.current = controller

      setInput('')
      setBusy(true)
      setMessages((current) => [...current, { id: createId(), role: 'user', content: question }])

      try {
        const result = await askQuestion(question, controller.signal)

        setMessages((current) => [
          ...current,
          { id: createId(), role: 'assistant', content: result.answer },
        ])
      } catch (error) {
        if (error instanceof DOMException && error.name === 'AbortError') {
          return
        }

        setMessages((current) => [
          ...current,
          {
            id: createId(),
            role: 'assistant',
            error: true,
            content:
              error instanceof Error
                ? error.message
                : 'Something went wrong while contacting the assistant.',
          },
        ])
      } finally {
        abortRef.current = null
        setBusy(false)
      }
    },
    [busy],
  )

  const stop = useCallback(() => {
    abortRef.current?.abort()
    abortRef.current = null
    setBusy(false)
  }, [])

  const reset = useCallback(() => {
    stop()
    setMessages([])
    setInput('')
  }, [stop])

  return (
    <div className="flex h-full">
      <Sidebar
        health={health}
        onPick={(question) => void send(question)}
        onReset={reset}
        hasConversation={messages.length > 0}
      />

      <main className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between gap-4 border-b border-white/[0.06] px-6 py-4 backdrop-blur-xl">
          <div className="min-w-0">
            <h2 className="truncate text-sm font-semibold tracking-tight text-white">
              Prescription Audit &amp; Drug Information
            </h2>
            <p className="truncate text-xs text-slate-500">
              Retrieval-augmented answers from FDA drug labels
            </p>
          </div>

          <StatusPill health={health} />
        </header>

        <div className="scroll-slim flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <Welcome onPick={(question) => void send(question)} />
          ) : (
            <div className="mx-auto flex max-w-4xl flex-col gap-6 px-6 py-8">
              {messages.map((message) => (
                <Message key={message.id} message={message} />
              ))}
              {busy ? <ThinkingMessage /> : null}
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        <div className="border-t border-white/[0.06] bg-ink-950/40 px-6 py-4 backdrop-blur-xl">
          <div className="mx-auto max-w-4xl">
            <Composer
              value={input}
              onChange={setInput}
              onSubmit={() => void send(input)}
              onStop={stop}
              busy={busy}
              disabled={false}
            />

            {health && !health.ready ? (
              <p className="mt-3 flex items-start gap-2 text-xs text-amber-300/80">
                <Info className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                {health.detail ?? 'The assistant pipeline is not ready yet.'}
              </p>
            ) : null}
          </div>
        </div>
      </main>
    </div>
  )
}
