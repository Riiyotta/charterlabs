import SmoothScroll from './components/motion/SmoothScroll.jsx'
import Handoff from './components/motion/Handoff.jsx'
import Header from './components/Header.jsx'
import Hero from './components/Hero.jsx'
import Intro from './components/Intro.jsx'
import Logo from './components/Logo.jsx'
import Send from './components/Send.jsx'
import DarkTransition from './components/DarkTransition.jsx'
import Overview from './components/Overview.jsx'
import Earn from './components/Earn.jsx'
import Payroll from './components/Payroll.jsx'
import Security from './components/Security.jsx'
import Faq from './components/Faq.jsx'
import Footer from './components/Footer.jsx'

// DOM order per CLONE_SPEC §0.8
export default function App() {
  return (
    <>
      <SmoothScroll />
      <Header />
      <main className="relative z-6 bg-surface tablet:min-h-svh">
        <div>
          <Handoff tone="light">
            <Hero />
          </Handoff>
          <Intro />
          <Handoff tone="light">
            <Logo />
          </Handoff>
          {/* §2.4 Send */}
          <Send />
          {/* §2.5 Dark transition */}
          <DarkTransition />
          {/* §2.6 Overview */}
          <Overview />
          {/* §2.7 Earn */}
          <Earn />
          {/* §2.8 Payroll */}
          <Payroll />
          {/* §2.9 Security */}
          <Handoff tone="inverse">
            <Security />
          </Handoff>
          {/* §2.10 FAQ */}
          <Faq />
        </div>
      </main>
      <Footer />
    </>
  )
}
