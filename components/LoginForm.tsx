'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Eye, EyeOff, Zap, Mail, Lock } from 'lucide-react'
import Link from 'next/link'

export default function LoginForm() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    await new Promise((resolve) => setTimeout(resolve, 800))
    router.push('/dashboard')
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 16, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.4 }}
      className="light-card rounded-2xl p-8 w-full"
    >
      {/* Logo + heading */}
      <div className="flex flex-col items-center mb-8">
        <div className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center mb-4">
          <Zap className="w-6 h-6 text-white" />
        </div>
        <h1 className="text-2xl font-bold text-text-base">Sign in to AIP</h1>
        <p className="text-text-muted text-sm mt-1">Your market intelligence awaits</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Email */}
        <div>
          <label className="text-sm font-medium text-text-base mb-1.5 block">Email</label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              className="w-full bg-bg-base border border-border-base rounded-lg pl-10 pr-4 py-2.5 text-text-base placeholder-text-muted/50 focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10 transition-all text-sm"
            />
          </div>
        </div>

        {/* Password */}
        <div>
          <label className="text-sm font-medium text-text-base mb-1.5 block">Password</label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
            <input
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              className="w-full bg-bg-base border border-border-base rounded-lg pl-10 pr-12 py-2.5 text-text-base placeholder-text-muted/50 focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10 transition-all text-sm"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-base transition-colors"
            >
              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          <div className="flex justify-end mt-1.5">
            <Link href="#" className="text-xs text-primary hover:underline font-medium">
              Forgot password?
            </Link>
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-primary hover:bg-primary/90 py-2.5 rounded-lg text-white font-semibold transition-all disabled:opacity-60 disabled:cursor-not-allowed shadow-primary"
        >
          {isLoading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Signing in…
            </span>
          ) : (
            'Sign In'
          )}
        </button>
      </form>

      <p className="text-center text-text-muted text-sm mt-6">
        Don&apos;t have an account?{' '}
        <Link href="#" className="text-primary hover:underline font-medium">
          Sign up
        </Link>
      </p>

      <div className="mt-4 pt-4 border-t border-border-base text-center">
        <Link
          href="/dashboard"
          className="text-xs text-text-muted hover:text-primary transition-colors"
        >
          Skip login — Browse dashboard freely →
        </Link>
      </div>
    </motion.div>
  )
}
