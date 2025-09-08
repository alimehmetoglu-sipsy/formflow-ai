import Hero from './components/Hero'
import Features from './components/Features'
import Templates from './components/Templates'
import Pricing from './components/Pricing'
import Testimonials from './components/Testimonials'
import FAQ from './components/FAQ'
import Footer from './components/Footer'

export default function LandingPage() {
  return (
    <main className="overflow-x-hidden">
      <Hero />
      <Features />
      <Templates />
      <Pricing />
      <Testimonials />
      <FAQ />
      <Footer />
    </main>
  )
}