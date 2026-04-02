'use client'
import { motion } from 'framer-motion'
import LoginForm from '@/components/LoginForm'
import Link from 'next/link'

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-bg-base flex items-center justify-center px-4 relative overflow-hidden">
      {/* Subtle background decoration */}
      <div className="absolute inset-0 pointer-events-none">
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `radial-gradient(circle at 1px 1px, #2F6BFF 1px, transparent 0)`,
            backgroundSize: '28px 28px',
          }}
        />
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-primary/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-gold/5 rounded-full blur-3xl translate-y-1/3 -translate-x-1/3" />
      </div>

      <div className="relative z-10 w-full max-w-md">
        {/* Back link */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="flex justify-center mb-6"
        >
          <Link
            href="/"
            className="flex items-center gap-1.5 text-text-muted hover:text-primary transition-colors text-sm font-medium"
          >
            ← Back to home
          </Link>
        </motion.div>

        <LoginForm />
      </div>
    </div>
  )
}
