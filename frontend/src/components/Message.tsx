import { motion } from 'framer-motion'
import { AlertTriangle, Sparkles, User } from 'lucide-react'
import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

export type MessageRole = 'user' | 'assistant'

export interface ChatMessage {
  id: string
  role: MessageRole
  content: string
  error?: boolean
  demo?: boolean
}

function Avatar({ role, error }: { role: MessageRole; error?: boolean }) {
  if (role === 'user') {
    return (
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-slate-300">
        <User className="h-4 w-4" />
      </div>
    )
  }

  return (
    <div
      className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl text-ink-950 ${
        error ? 'bg-gradient-to-br from-rose-300 to-rose-500' : 'bg-gradient-to-br from-mint-300 to-mint-600'
      }`}
    >
      {error ? <AlertTriangle className="h-4 w-4" /> : <Sparkles className="h-4 w-4" />}
    </div>
  )
}

export function Message({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user'

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}
    >
      <Avatar role={message.role} error={message.error} />

      <div
        className={`max-w-[46rem] rounded-3xl px-5 py-4 ${
          isUser
            ? 'rounded-tr-lg border border-mint-500/20 bg-mint-500/10 text-slate-100'
            : message.error
              ? 'rounded-tl-lg border border-rose-400/25 bg-rose-500/10'
              : 'glass rounded-tl-lg shadow-panel'
        }`}
      >
        {message.demo ? (
          <span className="mb-2 inline-flex rounded-full border border-amber-400/30 bg-amber-400/10 px-2 py-0.5 text-[11px] font-medium uppercase tracking-wide text-amber-300">
            Demo answer
          </span>
        ) : null}

        {isUser ? (
          <p className="whitespace-pre-wrap text-[15px] leading-7">{message.content}</p>
        ) : (
          <div className="prose-answer">
            <Markdown remarkPlugins={[remarkGfm]}>{message.content}</Markdown>
          </div>
        )}
      </div>
    </motion.div>
  )
}

export function ThinkingMessage() {
  return (
    <div className="flex gap-3">
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-mint-300 to-mint-600 text-ink-950">
        <Sparkles className="h-4 w-4" />
      </div>

      <div className="glass flex items-center gap-3 rounded-3xl rounded-tl-lg px-5 py-4">
        <div className="flex gap-1.5">
          {[0, 1, 2].map((index) => (
            <motion.span
              key={index}
              className="h-2 w-2 rounded-full bg-mint-400"
              animate={{ opacity: [0.25, 1, 0.25], y: [0, -3, 0] }}
              transition={{ duration: 1.1, repeat: Infinity, delay: index * 0.15 }}
            />
          ))}
        </div>
        <span className="text-sm text-slate-400">Searching FDA documents…</span>
      </div>
    </div>
  )
}
