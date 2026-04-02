'use client'
import { useState } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Menu, X, Zap } from 'lucide-react'

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <motion.nav
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6 }}
      className="fixed top-0 left-0 right-0 z-50 glass-card border-b border-accent-blue/10"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-blue to-accent-purple flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold gradient-text">AIP</span>
          </Link>

          <div className="hidden md:flex items-center gap-8">
            {['Features', 'Markets', 'About'].map((item) => (
              <Link
                key={item}
                href={`#${item.toLowerCase()}`}
                className="text-gray-400 hover:text-accent-blue transition-colors duration-200 text-sm font-medium"
              >
                {item}
              </Link>
            ))}
          </div>

          <div className="hidden md:flex items-center gap-4">
            <Link href="/login" className="text-gray-400 hover:text-white transition-colors text-sm">
              Sign In
            </Link>
            <Link
              href="/login"
              className="bg-gradient-to-r from-accent-blue to-accent-purple px-4 py-2 rounded-lg text-white text-sm font-medium hover:opacity-90 transition-opacity animate-glow"
            >
              Get Started
            </Link>
          </div>

          <button
            className="md:hidden text-gray-400 hover:text-white"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="md:hidden py-4 border-t border-white/10"
          >
            {['Features', 'Markets', 'About'].map((item) => (
              <Link
                key={item}
                href={`#${item.toLowerCase()}`}
                className="block py-2 text-gray-400 hover:text-accent-blue transition-colors"
                onClick={() => setIsOpen(false)}
              >
                {item}
              </Link>
            ))}
            <Link
              href="/login"
              className="block mt-4 bg-gradient-to-r from-accent-blue to-accent-purple px-4 py-2 rounded-lg text-white text-sm font-medium text-center"
              onClick={() => setIsOpen(false)}
            >
              Get Started
            </Link>
          </motion.div>
        )}
      </div>
    </motion.nav>
  )
}
