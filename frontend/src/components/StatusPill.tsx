import type { Health } from '../api'

const presentation: Record<Health['status'], { label: string; dot: string; ring: string }> = {
  ready: { label: 'FDA index live', dot: 'bg-mint-400', ring: 'ring-mint-400/30' },
  demo: { label: 'Demo mode', dot: 'bg-amber-400', ring: 'ring-amber-400/30' },
  unavailable: { label: 'Backend offline', dot: 'bg-rose-400', ring: 'ring-rose-400/30' },
  offline: { label: 'Waking up…', dot: 'bg-amber-400', ring: 'ring-amber-400/30 animate-pulse' },
}

export function StatusPill({ health }: { health: Health | null }) {
  const isReady = health?.ready === true
  const state = health ? presentation[health.status] : null

  return (
    <div className="flex items-center gap-2">
      <div
        title={health?.detail ?? undefined}
        className="flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5 text-xs font-medium text-slate-300 backdrop-blur"
      >
        <span
          className={`h-2 w-2 rounded-full ring-4 ${state ? `${state.dot} ${state.ring}` : 'bg-slate-500 ring-slate-500/20'}`}
        />
        {state ? state.label : 'Connecting…'}
      </div>

      {!isReady ? (
        <a
          href="https://mediaudit-ai-gcxb.onrender.com/api/health"
          target="_blank"
          rel="noopener noreferrer"
          title="Click to manually ping and wake up the Render backend"
          className="rounded-full border border-amber-400/30 bg-amber-400/10 px-3 py-1 text-xs font-medium text-amber-300 hover:bg-amber-400/20 transition-colors"
        >
          ⚡ Wake Server
        </a>
      ) : null}
    </div>
  )
}
