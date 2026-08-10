import { Database, FileText, Plus, ShieldCheck, Sparkles } from 'lucide-react'

import type { Health } from '../api'
import { suggestions } from '../suggestions'

interface SidebarProps {
  health: Health | null
  onPick: (question: string) => void
  onReset: () => void
  hasConversation: boolean
}

const pipeline = [
  { icon: FileText, label: 'FDA documents', detail: 'Parsed drug labels' },
  { icon: Database, label: 'ChromaDB', detail: 'Vector retrieval' },
  { icon: Sparkles, label: 'Qwen 2.5 3B', detail: 'Plain-English answer' },
]

export function Sidebar({ health, onPick, onReset, hasConversation }: SidebarProps) {
  return (
    <aside className="hidden w-[19rem] shrink-0 flex-col gap-5 border-r border-white/[0.06] bg-ink-900/60 p-5 backdrop-blur-xl lg:flex">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-mint-300 to-mint-600 shadow-glow">
          <ShieldCheck className="h-5 w-5 text-ink-950" />
        </div>
        <div>
          <p className="text-sm font-semibold tracking-tight text-white">MediAudit AI</p>
          <p className="text-xs text-slate-500">Prescription intelligence</p>
        </div>
      </div>

      <button
        type="button"
        onClick={onReset}
        disabled={!hasConversation}
        className="flex items-center justify-center gap-2 rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-2.5 text-sm font-medium text-slate-200 transition enabled:hover:border-mint-500/40 enabled:hover:bg-mint-500/10 disabled:opacity-40"
      >
        <Plus className="h-4 w-4" />
        New conversation
      </button>

      <div>
        <p className="px-1 pb-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-slate-500">
          Ask about
        </p>
        <div className="flex flex-col gap-1.5">
          {suggestions.map((suggestion) => (
            <button
              key={suggestion.question}
              type="button"
              onClick={() => onPick(suggestion.question)}
              className="group flex items-start gap-3 rounded-2xl border border-transparent px-3 py-2.5 text-left transition hover:border-white/10 hover:bg-white/[0.05]"
            >
              <suggestion.icon className="mt-0.5 h-4 w-4 shrink-0 text-slate-500 transition group-hover:text-mint-400" />
              <span className="min-w-0">
                <span className="block text-sm font-medium text-slate-200">{suggestion.label}</span>
                <span className="block truncate text-xs text-slate-500">{suggestion.question}</span>
              </span>
            </button>
          ))}
        </div>
      </div>

      <div className="mt-auto space-y-3">
        <p className="px-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-slate-500">
          Pipeline
        </p>
        <div className="glass rounded-2xl p-3">
          {pipeline.map((step, index) => (
            <div key={step.label} className="flex items-center gap-3 py-1.5">
              <step.icon className="h-4 w-4 text-mint-400" />
              <div className="min-w-0 flex-1">
                <p className="text-xs font-medium text-slate-200">{step.label}</p>
                <p className="truncate text-[11px] text-slate-500">{step.detail}</p>
              </div>
              <span className="text-[11px] text-slate-600">{index + 1}</span>
            </div>
          ))}
        </div>

        {health?.detail ? (
          <p className="rounded-2xl border border-white/[0.06] bg-white/[0.02] p-3 text-[11px] leading-relaxed text-slate-500">
            {health.detail}
          </p>
        ) : null}
      </div>
    </aside>
  )
}
