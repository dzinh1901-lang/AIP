'use client'

import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, BarChart, Bar, Cell,
} from 'recharts'
import { useEffect, useState } from 'react'

interface PricePoint {
  id: number
  symbol: string
  price: number
  change_24h: number
  timestamp: string
}

interface AnalyticsPanelProps {
  apiUrl: string
  symbols?: string[]
}

const COLORS: Record<string, string> = {
  BTC: '#f59e0b',
  ETH: '#6366f1',
  GOLD: '#10b981',
  OIL: '#ef4444',
}

function formatTimestamp(ts: string): string {
  try {
    return new Date(ts).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return ts
  }
}

export default function AnalyticsPanel({ apiUrl, symbols = ['BTC', 'ETH', 'GOLD', 'OIL'] }: AnalyticsPanelProps) {
  const [priceHistory, setPriceHistory] = useState<Record<string, PricePoint[]>>({})
  const [activeSymbol, setActiveSymbol] = useState('BTC')

  useEffect(() => {
    const loadHistory = async (symbol: string) => {
      try {
        const res = await fetch(`${apiUrl}/api/history/${symbol}?limit=50`)
        if (res.ok) {
          const data = await res.json()
          setPriceHistory(prev => ({ ...prev, [symbol]: data.reverse() }))
        }
      } catch {}
    }
    symbols.forEach(loadHistory)
    const interval = setInterval(() => symbols.forEach(loadHistory), 30000)
    return () => clearInterval(interval)
  }, [apiUrl, symbols])

  const chartData = (priceHistory[activeSymbol] || []).map(p => ({
    time: formatTimestamp(p.timestamp),
    price: p.price,
    change: p.change_24h,
  }))

  const changeBarData = symbols.map(sym => {
    const latest = priceHistory[sym]?.[priceHistory[sym].length - 1]
    return { symbol: sym, change: latest?.change_24h ?? 0 }
  })

  const accentColor = COLORS[activeSymbol] || '#6366f1'

  return (
    <div className="card p-5">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <span className="w-8 h-8 rounded-lg bg-slate-100 text-slate-600 flex items-center justify-center text-sm border border-slate-200">📊</span>
        <div>
          <h2 className="font-bold text-slate-900 leading-tight">Analytics</h2>
          <p className="text-xs text-slate-400">Price history &amp; 24h performance</p>
        </div>
      </div>

      {/* Symbol selector */}
      <div className="flex gap-2 mb-4">
        {symbols.map(sym => (
          <button
            key={sym}
            onClick={() => setActiveSymbol(sym)}
            style={activeSymbol === sym ? { borderColor: COLORS[sym], color: COLORS[sym], backgroundColor: `${COLORS[sym]}15` } : {}}
            className={`px-3 py-1 text-xs rounded-full border font-semibold transition-all ${
              activeSymbol === sym
                ? 'shadow-sm'
                : 'border-slate-200 text-slate-500 hover:border-slate-300 bg-white'
            }`}
          >
            {sym}
          </button>
        ))}
      </div>

      {/* Price chart */}
      <div className="mb-5">
        <p className="text-xs text-slate-400 font-medium mb-2">Price History — {activeSymbol}</p>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="time" tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis
                tick={{ fill: '#94a3b8', fontSize: 10 }}
                tickFormatter={v => `$${v.toLocaleString()}`}
                width={72}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e2e8f0',
                  borderRadius: 8,
                  boxShadow: '0 4px 12px rgb(0 0 0 / 0.08)',
                  fontSize: 12,
                }}
                labelStyle={{ color: '#0f172a', fontWeight: 600 }}
                formatter={(v: number) => [`$${v.toLocaleString()}`, 'Price']}
              />
              <Line
                type="monotone"
                dataKey="price"
                stroke={accentColor}
                dot={false}
                strokeWidth={2}
                activeDot={{ r: 4, fill: accentColor }}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-40 flex items-center justify-center text-slate-400 text-sm bg-slate-50 rounded-lg border border-dashed border-slate-200">
            Collecting price data…
          </div>
        )}
      </div>

      {/* 24h change bar chart */}
      <div>
        <p className="text-xs text-slate-400 font-medium mb-2">24h Change (%)</p>
        <ResponsiveContainer width="100%" height={100}>
          <BarChart data={changeBarData} barSize={28}>
            <XAxis dataKey="symbol" tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} unit="%" axisLine={false} tickLine={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e2e8f0',
                borderRadius: 8,
                fontSize: 12,
              }}
              formatter={(v: number) => [`${v.toFixed(2)}%`, '24h Change']}
            />
            <Bar dataKey="change" radius={[4, 4, 0, 0]}>
              {changeBarData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.change >= 0 ? '#10b981' : '#ef4444'}
                  fillOpacity={0.85}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
