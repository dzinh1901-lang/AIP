'use client'

import SignalBadge from './SignalBadge'

interface KeySignal {
  asset: string
  signal: string
  confidence: number
}

interface Brief {
  id?: number
  content: string
  key_signals?: KeySignal[]
  risks?: string[]
  date?: string
  timestamp?: string
}

interface BriefPanelProps {
  brief: Brief | null
  loading?: boolean
}

export default function BriefPanel({ brief, loading }: BriefPanelProps) {
  return (
    <div className="rounded-xl border border-slate-700 bg-[#0f172a] p-5 text-slate-200">
      {/* Panel header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <span className="w-8 h-8 rounded-lg bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 flex items-center justify-center text-sm">
            📰
          </span>
          <div>
            <h2 className="font-bold text-slate-100 leading-tight text-sm">Daily Intelligence Brief</h2>
            <p className="text-[10px] text-slate-500">AI-synthesized market narrative</p>
          </div>
        </div>
        {brief?.date && (
          <span className="text-[10px] font-semibold text-slate-500 bg-slate-800 border border-slate-700 px-2.5 py-1 rounded-full">
            {brief.date}
          </span>
        )}
      </div>

      {loading ? (
        <div className="text-center text-slate-500 text-sm py-8">
          <div className="animate-spin w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full mx-auto mb-3" />
          Generating intelligence brief…
        </div>
      ) : brief ? (
        <div className="space-y-4">
          <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">
            {brief.content}
          </p>

          {brief.key_signals && brief.key_signals.length > 0 && (
            <div className="border-t border-slate-800 pt-4">
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2.5">Key Signals</p>
              <div className="flex flex-wrap gap-2">
                {brief.key_signals.map((s, i) => (
                  <div key={i} className="flex items-center gap-1.5 bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1.5">
                    <span className="text-xs font-bold text-slate-200">{s.asset}</span>
                    <SignalBadge signal={s.signal} size="sm" />
                    <span className="text-[10px] text-slate-500">{(s.confidence * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {brief.risks && brief.risks.length > 0 && (
            <div className="border-t border-slate-800 pt-4">
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2.5">⚠️ Risk Factors</p>
              <ul className="space-y-1.5">
                {brief.risks.map((risk, i) => (
                  <li key={i} className="text-xs text-amber-400/90 flex items-start gap-2">
                    <span className="mt-0.5 text-amber-500">•</span>
                    <span>{risk}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center text-slate-500 text-sm py-8">
          No brief available yet.<br />
          <span className="text-xs text-slate-600">Generates daily or on demand.</span>
        </div>
      )}
    </div>
  )
}
