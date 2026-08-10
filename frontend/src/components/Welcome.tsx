import { motion } from 'framer-motion'

import { suggestions } from '../suggestions'

export function Welcome({ onPick }: { onPick: (question: string) => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="mx-auto flex max-w-3xl flex-col items-center px-6 py-14 text-center"
    >
      <span className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3.5 py-1.5 text-xs text-slate-400 backdrop-blur">
        <span className="h-1.5 w-1.5 rounded-full bg-mint-400" />
        Grounded in FDA drug labels · RAG + Qwen 2.5
      </span>

      <h1 className="text-balance text-4xl font-semibold tracking-tight text-white sm:text-5xl">
        Understand your medicines
        <span className="bg-gradient-to-r from-mint-300 via-mint-400 to-sky-400 bg-clip-text text-transparent">
          {' '}
          in plain English
        </span>
      </h1>

      <p className="mt-4 max-w-xl text-[15px] leading-7 text-slate-400">
        Ask about uses, side effects, dosage, interactions or foods to avoid. Every answer is
        retrieved from FDA documents first, then explained without the jargon.
      </p>

      <div className="mt-10 grid w-full gap-3 sm:grid-cols-2">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion.question}
            type="button"
            onClick={() => onPick(suggestion.question)}
            className="glass group flex items-center gap-3 rounded-2xl p-4 text-left transition hover:border-mint-500/30 hover:bg-mint-500/[0.07]"
          >
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-white/10 bg-white/5 transition group-hover:border-mint-500/30">
              <suggestion.icon className="h-4 w-4 text-mint-400" />
            </span>
            <span className="min-w-0">
              <span className="block text-[11px] uppercase tracking-[0.12em] text-slate-500">
                {suggestion.label}
              </span>
              <span className="block truncate text-sm text-slate-200">{suggestion.question}</span>
            </span>
          </button>
        ))}
      </div>
    </motion.div>
  )
}
