import Link from 'next/link'
import { Zap, AtSign, GitBranch, Globe } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="bg-bg-secondary border-t border-accent-blue/10 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          <div>
            <Link href="/" className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-blue to-accent-purple flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold gradient-text">AIP</span>
            </Link>
            <p className="text-gray-500 text-sm leading-relaxed">
              AI-powered market intelligence platform for professional traders and institutions.
            </p>
            <div className="flex gap-3 mt-4">
              {[AtSign, GitBranch, Globe].map((Icon, i) => (
                <a
                  key={i}
                  href="#"
                  className="w-8 h-8 rounded-lg bg-bg-card border border-white/10 flex items-center justify-center text-gray-500 hover:text-accent-blue hover:border-accent-blue/30 transition-colors"
                >
                  <Icon className="w-4 h-4" />
                </a>
              ))}
            </div>
          </div>

          {[
            {
              title: 'Platform',
              links: ['Features', 'Markets', 'Analytics', 'Alerts'],
            },
            {
              title: 'Company',
              links: ['About', 'Blog', 'Careers', 'Press'],
            },
            {
              title: 'Legal',
              links: ['Privacy Policy', 'Terms of Service', 'Cookie Policy', 'Compliance'],
            },
          ].map((col) => (
            <div key={col.title}>
              <h4 className="text-white font-semibold mb-4">{col.title}</h4>
              <ul className="space-y-2">
                {col.links.map((link) => (
                  <li key={link}>
                    <a
                      href="#"
                      className="text-gray-500 hover:text-accent-blue text-sm transition-colors"
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="border-t border-white/10 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-gray-600 text-sm">
            © {new Date().getFullYear()} AIP Technologies. All rights reserved.
          </p>
          <p className="text-gray-700 text-xs">
            Market data for informational purposes only. Not financial advice.
          </p>
        </div>
      </div>
    </footer>
  )
}
