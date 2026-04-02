'use client'
import { useState } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Menu, X, Zap } from 'lucide-react'

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <motion.nav
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md border-b border-border-base"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <span className="text-xl font-bold text-primary-gradient">AIP</span>
          </Link>

          {/* Desktop nav links */}
          <div className="hidden md:flex items-center gap-8">
            {[
              { label: 'Features', href: '#features' },
              { label: 'Markets', href: '#markets' },
              { label: 'About', href: '#about' },
            ].map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className="text-text-muted hover:text-text-base transition-colors duration-150 text-sm font-medium"
              >
                {item.label}
              </Link>
            ))}
          </div>

          {/* Desktop CTAs */}
          <div className="hidden md:flex items-center gap-3">
            <Link
              href="/dashboard"
              className="text-text-muted hover:text-text-base transition-colors text-sm font-medium"
            >
              Dashboard
            </Link>
            <Link
              href="/dashboard"
              className="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-all shadow-primary hover:shadow-md"
            >
              Get Started
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            className="md:hidden text-text-muted hover:text-text-base"
            onClick={() => setIsOpen(!isOpen)}
            aria-label="Toggle menu"
          >
            {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Mobile menu */}
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            className="md:hidden py-4 border-t border-border-base"
          >
            <div className="flex flex-col gap-1">
              {['Features', 'Markets', 'About'].map((item) => (
                <Link
                  key={item}
                  href={`#${item.toLowerCase()}`}
                  className="px-2 py-2 text-text-muted hover:text-text-base hover:bg-bg-base rounded-lg transition-colors text-sm font-medium"
                  onClick={() => setIsOpen(false)}
                >
                  {item}
                </Link>
              ))}
              <Link
                href="/dashboard"
                className="mt-3 bg-primary text-white px-4 py-2 rounded-lg text-sm font-semibold text-center"
                onClick={() => setIsOpen(false)}
              >
                Get Started — Free
              </Link>
            </div>
          </motion.div>
        )}
      </div>
    </motion.nav>
  )
}
