'use client'

import { useEffect, useState } from 'react'
import SignalBadge from './SignalBadge'

interface Alert {
  id: number
  asset: string
  alert_type: string
  message: string
  signal: string
  confidence: number
  severity: string
  is_read: boolean
  timestamp: string
}

interface AlertFeedProps {
  apiUrl: string
}

const SEVERITY_STYLES: Record<string, { bar: string; bg: string; dot: string }> = {
  critical: { bar: 'border-l-red-500',   bg: 'bg-red-50',    dot: 'bg-red-500'   },
  warning:  { bar: 'border-l-amber-400', bg: 'bg-amber-50',  dot: 'bg-amber-400' },
  info:     { bar: 'border-l-indigo-400',bg: 'bg-indigo-50', dot: 'bg-indigo-400'},
}

function formatTime(ts: string): string {
  try {
    return new Date(ts).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return ''
  }
}

export default function AlertFeed({ apiUrl }: AlertFeedProps) {
  const [alerts, setAlerts] = useState<Alert[]>([])

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(`${apiUrl}/api/alerts?limit=30`)
        if (res.ok) setAlerts(await res.json())
      } catch {}
    }
    load()
    const interval = setInterval(load, 10000)
    return () => clearInterval(interval)
  }, [apiUrl])

  const styles = (severity: string) =>
    SEVERITY_STYLES[severity] || SEVERITY_STYLES.info

  return (
    <div className="card p-4 h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse inline-block" />
          <h2 className="font-bold text-slate-900 text-sm">Live Alerts</h2>
        </div>
        <span className="text-[10px] font-semibold text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
          {alerts.length} events
        </span>
      </div>

      {/* Feed */}
      <div className="flex-1 overflow-y-auto space-y-1.5 scrollbar-thin">
        {alerts.length === 0 && (
          <div className="text-center text-slate-400 text-sm py-8">
            Monitoring markets…<br />
            <span className="text-xs text-slate-300">Alerts will appear here</span>
          </div>
        )}
        {alerts.map((alert) => {
          const s = styles(alert.severity)
          return (
            <div
              key={alert.id}
              className={`border-l-[3px] pl-3 py-2 rounded-r-lg text-sm ${s.bar} ${s.bg} ${alert.is_read ? 'opacity-50' : ''}`}
            >
              <div className="flex items-center gap-1.5 mb-0.5">
                <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${s.dot}`} />
                <span className="font-bold text-slate-800 text-xs">{alert.asset}</span>
                <SignalBadge signal={alert.signal} size="sm" />
                <span className="ml-auto text-slate-400 text-[10px]">{formatTime(alert.timestamp)}</span>
              </div>
              <p className="text-slate-600 text-xs leading-snug pl-3">{alert.message}</p>
            </div>
          )
        })}
      </div>
    </div>
  )
}
