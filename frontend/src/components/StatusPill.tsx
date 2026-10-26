import type { Health } from '../api'

const presentation: Record<Health['status'], { label: string; dot: string; ring: string }> = {
  ready: { label: 'FDA index live', dot: 'bg-mint-400', ring: 'ring-mint-400/30' },
  demo: { label: 'Demo mode', dot: 'bg-amber-400', ring: 'ring-amber-400/30' },
  unavailable: { label: 'Pipeline offline', dot: 'bg-rose-400', ring: 'ring-rose-400/30' },
  offline: { label: 'Waking up…', dot: 'bg-amber-400', ring: 'ring-amber-400/30 animate-pulse' },
}

export function StatusPill({ health }: { health: Health | null }) {
  const state = health ? presentation[health.status] : null

  return (
    <div
      title={health?.detail ?? undefined}
      className="flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5 text-xs font-medium text-slate-300 backdrop-blur"
    >
      <span
        className={`h-2 w-2 rounded-full ring-4 ${state ? `${state.dot} ${state.ring}` : 'bg-slate-500 ring-slate-500/20'}`}
      />
      {state ? state.label : 'Connecting…'}
    </div>
  )
}
