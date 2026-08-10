import { useEffect, useRef } from 'react'
import { ArrowUp, Square } from 'lucide-react'

interface ComposerProps {
  value: string
  onChange: (value: string) => void
  onSubmit: () => void
  onStop: () => void
  busy: boolean
  disabled: boolean
}

export function Composer({ value, onChange, onSubmit, onStop, busy, disabled }: ComposerProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    const element = textareaRef.current

    if (!element) {
      return
    }

    element.style.height = 'auto'
    element.style.height = `${Math.min(element.scrollHeight, 200)}px`
  }, [value])

  const canSend = value.trim().length > 0 && !busy && !disabled

  return (
    <div className="rounded-3xl border border-white/10 bg-ink-800/70 p-2 shadow-panel backdrop-blur-xl focus-within:border-mint-500/40 focus-within:shadow-glow">
      <div className="flex items-end gap-2">
        <textarea
          ref={textareaRef}
          rows={1}
          value={value}
          disabled={disabled}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
              event.preventDefault()

              if (canSend) {
                onSubmit()
              }
            }
          }}
          placeholder="Ask about a medicine — uses, side effects, food, interactions…"
          className="scroll-slim max-h-[200px] flex-1 resize-none bg-transparent px-4 py-3 text-[15px] text-slate-100 outline-none placeholder:text-slate-500 disabled:cursor-not-allowed"
        />

        {busy ? (
          <button
            type="button"
            onClick={onStop}
            aria-label="Stop generating"
            className="mb-1 mr-1 flex h-10 w-10 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-slate-200 transition hover:bg-white/10"
          >
            <Square className="h-4 w-4 fill-current" />
          </button>
        ) : (
          <button
            type="button"
            onClick={onSubmit}
            disabled={!canSend}
            aria-label="Send question"
            className="mb-1 mr-1 flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-mint-300 to-mint-600 text-ink-950 transition enabled:hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-30"
          >
            <ArrowUp className="h-5 w-5" strokeWidth={2.5} />
          </button>
        )}
      </div>

      <p className="px-4 pb-2 pt-1 text-[11px] text-slate-500">
        Enter to send · Shift + Enter for a new line · Educational information only, not medical advice.
      </p>
    </div>
  )
}
