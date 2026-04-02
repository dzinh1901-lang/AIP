'use client'

import { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function LoginPage() {
  const router = useRouter()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const form = new URLSearchParams()
      form.append('username', username)
      form.append('password', password)
      const res = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: form.toString(),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        setError(data.detail || 'Invalid credentials')
        setLoading(false)
        return
      }
      const { access_token, refresh_token } = await res.json()
      localStorage.setItem('aip_token', access_token)
      localStorage.setItem('aip_refresh_token', refresh_token)
      router.push('/')
    } catch {
      setError('Connection error — is the backend running?')
    }
    setLoading(false)
  }, [username, password, router])

  const handleRegister = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const res = await fetch(`${API_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password, email: email || undefined }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        setError(data.detail || 'Registration failed')
        setLoading(false)
        return
      }
      await handleLogin()
    } catch {
      setError('Connection error — is the backend running?')
    }
    setLoading(false)
  }, [username, password, email, handleLogin])

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (mode === 'login') handleLogin()
    else handleRegister()
  }

  const handleKey = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      if (mode === 'login') handleLogin()
      else handleRegister()
    }
  }

  const inputClass =
    'w-full bg-white border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 transition-all'

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ background: 'var(--color-bg)' }}>
      <div className="w-full max-w-sm">
        {/* Brand */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-indigo-600 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-indigo-200">
            <span className="text-white text-xl font-black">AIP</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Welcome back</h1>
          <p className="text-slate-500 text-sm mt-1">Agentic Market Intelligence Platform</p>
        </div>

        {/* Card */}
        <div className="card p-6">
          {/* Mode tabs */}
          <div className="flex gap-2 mb-6 bg-slate-100 p-1 rounded-xl">
            {(['login', 'register'] as const).map(m => (
              <button
                key={m}
                onClick={() => { setMode(m); setError('') }}
                className={`flex-1 py-2 text-sm rounded-lg font-semibold capitalize transition-all ${
                  mode === m
                    ? 'bg-white text-indigo-700 shadow-sm border border-slate-200'
                    : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                {m}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5">Username</label>
              <input
                type="text"
                value={username}
                onChange={e => setUsername(e.target.value)}
                onKeyDown={handleKey}
                placeholder="your_username"
                autoComplete="username"
                className={inputClass}
              />
            </div>

            {mode === 'register' && (
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1.5">Email <span className="text-slate-400 font-normal">(optional)</span></label>
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  autoComplete="email"
                  className={inputClass}
                />
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5">Password</label>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                onKeyDown={handleKey}
                placeholder="••••••••"
                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                className={inputClass}
              />
            </div>

            {error && (
              <p className="text-xs text-red-700 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading || !username || !password}
              className="w-full py-2.5 rounded-xl bg-indigo-600 text-white font-bold text-sm hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm shadow-indigo-200"
            >
              {loading ? '⟳ Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}
            </button>
          </form>

          <p className="text-xs text-slate-400 text-center mt-5">
            When <code className="text-slate-500 bg-slate-100 px-1 py-0.5 rounded">REQUIRE_AUTH=false</code> (default),<br />
            authentication is optional — the dashboard works without login.
          </p>
        </div>

        <p className="text-center mt-4">
          <a href="/" className="text-xs text-indigo-600 hover:underline font-medium">← Back to dashboard</a>
        </p>
      </div>
    </div>
  )
}
