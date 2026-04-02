'use client'

import { useEffect, useState, useCallback, useRef } from 'react'

// ── Types ─────────────────────────────────────────────────────────────────────

interface AgentStatus {
  agent: string
  status: string
  last_run?: string
  notes?: string
}

interface ActivityEntry {
  id: number
  agent_name: string
  action_type: string
  summary?: string
  timestamp: string
}

interface ChatMessage {
  role: 'user' | 'assistant'
  message: string
  timestamp?: string
}

// ── Constants ────────────────────────────────────────────────────────────────

const AGENT_META: Record<string, { emoji: string; title: string; accent: string; bg: string; border: string }> = {
  orchestrator:        { emoji: '🎯', title: 'Orchestrator (COO)',       accent: 'text-violet-700', bg: 'bg-violet-50',  border: 'border-violet-200' },
  marketing:           { emoji: '📣', title: 'Marketing Director',       accent: 'text-pink-700',   bg: 'bg-pink-50',    border: 'border-pink-200' },
  market_intelligence: { emoji: '🔍', title: 'Chief Analyst',            accent: 'text-blue-700',   bg: 'bg-blue-50',    border: 'border-blue-200' },
  customer_success:    { emoji: '💬', title: 'Customer Success',         accent: 'text-emerald-700',bg: 'bg-emerald-50', border: 'border-emerald-200' },
  analytics:           { emoji: '📊', title: 'Analytics (Data Analyst)', accent: 'text-amber-700',  bg: 'bg-amber-50',   border: 'border-amber-200' },
}

// ── Sub-components ────────────────────────────────────────────────────────────

function AgentStatusCard({ agent }: { agent: AgentStatus }) {
  const meta = AGENT_META[agent.agent] ?? { emoji: '🤖', title: agent.agent, accent: 'text-slate-600', bg: 'bg-slate-50', border: 'border-slate-200' }
  const isActive = agent.status === 'active'

  return (
    <div className={`rounded-xl border p-4 flex flex-col gap-1.5 ${meta.bg} ${meta.border}`}>
      <div className="flex items-center gap-2">
        <span className="text-lg">{meta.emoji}</span>
        <span className={`font-bold text-sm ${meta.accent}`}>{meta.title}</span>
        <span className="ml-auto flex items-center gap-1">
          <span className={`w-2 h-2 rounded-full ${isActive ? 'bg-emerald-500 animate-pulse' : 'bg-slate-300'}`} />
          <span className="text-xs text-slate-500 capitalize">{agent.status}</span>
        </span>
      </div>
      {agent.notes && <p className="text-xs text-slate-500">{agent.notes}</p>}
    </div>
  )
}

function SupportChat({ apiUrl }: { apiUrl: string }) {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = useCallback(async () => {
    const msg = input.trim()
    if (!msg || loading) return
    setInput('')
    setLoading(true)
    setMessages(prev => [...prev, { role: 'user', message: msg }])

    const streamUrl = `${apiUrl}/api/agents/support/chat/stream`
    try {
      const res = await fetch(streamUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(typeof window !== 'undefined' && localStorage.getItem('aip_token')
            ? { Authorization: `Bearer ${localStorage.getItem('aip_token')}` }
            : {}),
        },
        body: JSON.stringify({ session_id: sessionId, message: msg }),
      })

      if (!res.ok || !res.body) throw new Error('stream unavailable')

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let assistantMsg = ''
      let streamingIdx = -1

      setMessages(prev => {
        streamingIdx = prev.length
        return [...prev, { role: 'assistant', message: '' }]
      })

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const evt = JSON.parse(line.slice(6))
            if (evt.type === 'session' && evt.session_id) {
              setSessionId(evt.session_id)
            } else if (evt.type === 'token' && evt.content) {
              assistantMsg += evt.content
              const captured = assistantMsg
              setMessages(prev => {
                const updated = [...prev]
                if (streamingIdx >= 0 && updated[streamingIdx]) {
                  updated[streamingIdx] = { role: 'assistant', message: captured }
                }
                return updated
              })
            }
          } catch {}
        }
      }
    } catch {
      try {
        const res = await fetch(`${apiUrl}/api/agents/support/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(typeof window !== 'undefined' && localStorage.getItem('aip_token')
              ? { Authorization: `Bearer ${localStorage.getItem('aip_token')}` }
              : {}),
          },
          body: JSON.stringify({ session_id: sessionId, message: msg }),
        })
        if (res.ok) {
          const data = await res.json()
          setSessionId(data.session_id)
          setMessages(prev => [...prev, { role: 'assistant', message: data.reply }])
        }
      } catch {}
    }
    setLoading(false)
  }, [input, loading, sessionId, apiUrl])

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto space-y-2.5 mb-3 pr-1 max-h-64 scrollbar-thin">
        {messages.length === 0 && (
          <p className="text-xs text-slate-400 italic">Ask anything about AIP — features, signals, getting started…</p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`rounded-2xl px-3.5 py-2 text-sm max-w-[85%] ${
              m.role === 'user'
                ? 'bg-indigo-600 text-white rounded-br-sm'
                : 'bg-slate-100 text-slate-800 rounded-bl-sm border border-slate-200'
            }`}>
              {m.message}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="rounded-2xl rounded-bl-sm px-3.5 py-2 text-sm bg-slate-100 border border-slate-200 text-slate-400">
              <span className="animate-pulse">Thinking…</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="flex gap-2">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask a question…"
          className="flex-1 bg-white border border-slate-200 rounded-xl px-3.5 py-2 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 transition-all"
        />
        <button
          onClick={send}
          disabled={loading || !input.trim()}
          className="px-3.5 py-2 rounded-xl bg-indigo-600 text-white text-sm hover:bg-indigo-700 transition-colors disabled:opacity-40 font-bold"
        >
          ↑
        </button>
      </div>
    </div>
  )
}

function AgentQueryPanel({
  title,
  endpoint,
  method = 'GET',
  placeholder,
  buttonLabel,
  apiUrl,
  fieldName,
}: {
  title: string
  endpoint: string
  method?: string
  placeholder?: string
  buttonLabel: string
  apiUrl: string
  fieldName?: string
}) {
  const [result, setResult] = useState<string | null>(null)
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const run = useCallback(async () => {
    setLoading(true)
    setResult(null)
    try {
      const url = method === 'GET' ? `${apiUrl}${endpoint}` : `${apiUrl}${endpoint}`
      const opts: RequestInit = { method }
      if (method === 'POST' && fieldName) {
        opts.headers = { 'Content-Type': 'application/json' }
        opts.body = JSON.stringify({ [fieldName]: input })
      }
      const res = await fetch(url, opts)
      if (res.ok) {
        const data = await res.json()
        const text =
          data.reply ?? data.insight ?? data.analysis ?? data.content ?? data.guide ??
          (typeof data === 'string' ? data : JSON.stringify(data, null, 2))
        setResult(text)
      } else {
        setResult(`Error ${res.status}`)
      }
    } catch (e: any) {
      setResult(`Error: ${e.message}`)
    }
    setLoading(false)
  }, [apiUrl, endpoint, method, fieldName, input])

  return (
    <div>
      <p className="text-xs font-bold text-slate-600 mb-2 uppercase tracking-wide">{title}</p>
      {fieldName && (
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder={placeholder}
          className="w-full bg-white border border-slate-200 rounded-xl px-3.5 py-2 text-sm text-slate-900 placeholder-slate-400 mb-2 focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 transition-all"
        />
      )}
      <button
        onClick={run}
        disabled={loading || (!!fieldName && !input.trim())}
        className="px-4 py-1.5 text-xs rounded-xl bg-indigo-600 text-white font-semibold hover:bg-indigo-700 transition-colors disabled:opacity-40 mb-3"
      >
        {loading ? '⟳ Loading…' : buttonLabel}
      </button>
      {result && (
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 text-xs text-slate-700 whitespace-pre-wrap max-h-48 overflow-y-auto scrollbar-thin leading-relaxed">
          {result}
        </div>
      )}
    </div>
  )
}

// ── Main component ────────────────────────────────────────────────────────────

export default function AgentsPanel({ apiUrl }: { apiUrl: string }) {
  const [statuses, setStatuses] = useState<AgentStatus[]>([])
  const [activity, setActivity] = useState<ActivityEntry[]>([])
  const [activeTab, setActiveTab] = useState<'overview' | 'orchestrator' | 'marketing' | 'intel' | 'support' | 'analytics'>('overview')

  const loadStatus = useCallback(async () => {
    try {
      const res = await fetch(`${apiUrl}/api/agents/status`)
      if (res.ok) setStatuses(await res.json())
    } catch {}
  }, [apiUrl])

  const loadActivity = useCallback(async () => {
    try {
      const res = await fetch(`${apiUrl}/api/agents/activity?limit=20`)
      if (res.ok) setActivity(await res.json())
    } catch {}
  }, [apiUrl])

  useEffect(() => {
    loadStatus()
    loadActivity()
    const interval = setInterval(() => { loadStatus(); loadActivity() }, 30000)
    return () => clearInterval(interval)
  }, [loadStatus, loadActivity])

  const tabs = [
    { id: 'overview',     label: '🗂 Overview' },
    { id: 'orchestrator', label: '🎯 COO' },
    { id: 'marketing',    label: '📣 Marketing' },
    { id: 'intel',        label: '🔍 Analyst' },
    { id: 'support',      label: '💬 Support' },
    { id: 'analytics',    label: '📊 Analytics' },
  ] as const

  return (
    <div className="card p-5">
      {/* Panel header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-600 flex items-center justify-center text-sm border border-indigo-200">🤖</span>
          <div>
            <h2 className="font-bold text-slate-900 leading-tight">AI Agent Team</h2>
            <p className="text-xs text-slate-400">5 specialist agents</p>
          </div>
        </div>
        <span className="text-xs font-semibold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-full border border-slate-200">
          {statuses.filter(s => s.status === 'active').length}/{statuses.length || 5} active
        </span>
      </div>

      {/* Tab bar */}
      <div className="flex gap-1 mb-4 overflow-x-auto pb-1">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-3 py-1.5 text-xs rounded-lg border whitespace-nowrap font-medium transition-all ${
              activeTab === tab.id
                ? 'border-indigo-300 bg-indigo-50 text-indigo-700 shadow-sm'
                : 'border-slate-200 text-slate-500 hover:border-slate-300 hover:text-slate-700 bg-white'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Overview */}
      {activeTab === 'overview' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
            {statuses.map(s => (
              <AgentStatusCard key={s.agent} agent={s} />
            ))}
          </div>
          <div>
            <p className="section-label mb-2">Recent Activity</p>
            <div className="space-y-0 max-h-48 overflow-y-auto scrollbar-thin rounded-lg border border-slate-100 divide-y divide-slate-100">
              {activity.length === 0 && (
                <p className="text-xs text-slate-400 italic p-3">No activity yet — agents run on schedule.</p>
              )}
              {activity.map(a => (
                <div key={a.id} className="flex items-start gap-2 text-xs text-slate-500 py-2 px-3">
                  <span>{AGENT_META[a.agent_name]?.emoji ?? '🤖'}</span>
                  <span className="font-semibold text-slate-700 capitalize">{a.agent_name.replace('_', ' ')}</span>
                  <span className="text-slate-300">·</span>
                  <span>{a.action_type}</span>
                  {a.summary && <span className="text-slate-400 truncate flex-1">{a.summary}</span>}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Orchestrator */}
      {activeTab === 'orchestrator' && (
        <div className="space-y-5">
          <AgentQueryPanel
            title="Daily Admin Briefing"
            endpoint="/api/agents/orchestrator/briefing/generate"
            method="POST"
            buttonLabel="Generate Briefing"
            apiUrl={apiUrl}
          />
          <AgentQueryPanel
            title="Ask the COO"
            endpoint="/api/agents/orchestrator/query"
            method="POST"
            placeholder="e.g. What's the platform's current risk level?"
            buttonLabel="Ask"
            apiUrl={apiUrl}
            fieldName="query"
          />
        </div>
      )}

      {/* Marketing */}
      {activeTab === 'marketing' && (
        <div className="space-y-5">
          <AgentQueryPanel
            title="Generate Content (Teaser + Lead Nurture)"
            endpoint="/api/agents/marketing/generate"
            method="POST"
            buttonLabel="Generate Content"
            apiUrl={apiUrl}
          />
          <AgentQueryPanel
            title="Lead Insight"
            endpoint="/api/agents/marketing/lead-insight"
            method="POST"
            placeholder="e.g. Crypto day trader, saw our ad on LinkedIn"
            buttonLabel="Generate Insight"
            apiUrl={apiUrl}
            fieldName="lead_context"
          />
        </div>
      )}

      {/* Market Intelligence */}
      {activeTab === 'intel' && (
        <div className="space-y-5">
          <AgentQueryPanel
            title="Generate Narrative Report"
            endpoint="/api/agents/market-intel/narrative/generate"
            method="POST"
            buttonLabel="Generate Narrative"
            apiUrl={apiUrl}
          />
          <AgentQueryPanel
            title="Asset Deep-Dive"
            endpoint="/api/agents/market-intel/deep-dive"
            method="POST"
            placeholder="e.g. BTC, Gold, ETH"
            buttonLabel="Deep Dive"
            apiUrl={apiUrl}
            fieldName="symbol"
          />
        </div>
      )}

      {/* Customer Success */}
      {activeTab === 'support' && (
        <div className="h-80">
          <SupportChat apiUrl={apiUrl} />
        </div>
      )}

      {/* Analytics */}
      {activeTab === 'analytics' && (
        <div className="space-y-5">
          <AgentQueryPanel
            title="Generate KPI Report"
            endpoint="/api/agents/analytics/kpi/generate"
            method="POST"
            buttonLabel="Generate KPI Report"
            apiUrl={apiUrl}
          />
          <AgentQueryPanel
            title="Latest KPI Report"
            endpoint="/api/agents/analytics/kpi"
            method="GET"
            buttonLabel="Load KPI Report"
            apiUrl={apiUrl}
          />
        </div>
      )}
    </div>
  )
}
