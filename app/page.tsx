import Navbar from '@/components/Navbar'
import Hero from '@/components/Hero'
import MarketTicker from '@/components/MarketTicker'
import Features from '@/components/Features'
import Stats from '@/components/Stats'
import ConsensusPreview from '@/components/ConsensusPreview'
import Footer from '@/components/Footer'

export default function Home() {
  return (
    <main className="min-h-screen bg-bg-base">
      <Navbar />
      <Hero />
      <MarketTicker />
      <Features />
      <ConsensusPreview />
      <Stats />
      <Footer />
    </main>
  )
}
