import React from 'react'
import { motion } from 'framer-motion'

const fragments = [
  'Emotional drift detected',
  'Neural harmony stabilizing',
  'Late-night melancholy pattern observed',
  'Cognitive fatigue detected',
  'Resonance synchronization active',
  'Pulse alignment in progress',
  'Atmospheric depth tuning',
  'Memory trace resonating'
]

const positions = [
  { top: '12%', left: '8%', delay: 0 },
  { top: '22%', left: '72%', delay: 1.2 },
  { top: '46%', left: '18%', delay: 0.6 },
  { top: '65%', left: '80%', delay: 1.8 },
  { top: '72%', left: '34%', delay: 0.4 },
  { top: '82%', left: '12%', delay: 2.0 },
  { top: '40%', left: '88%', delay: 1.0 }
]

export default function AmbientEcosystem({ active = false }) {
  return (
    <div className="pointer-events-none absolute inset-0 z-10 overflow-hidden opacity-0 sm:opacity-100">
      {positions.map((pos, index) => (
        <motion.div
          key={`${pos.left}-${pos.top}`}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: active ? 0.12 : 0.05, y: [0, -6, 0] }}
          transition={{ duration: 10 + (index * 0.5), delay: pos.delay, repeat: Infinity, ease: 'easeInOut' }}
          style={{ position: 'absolute', top: pos.top, left: pos.left, maxWidth: '240px' }}
          className="text-[10px] uppercase tracking-[0.35em] leading-tight text-soft-ivory/20 mix-blend-screen"
        >
          {fragments[index % fragments.length]}
        </motion.div>
      ))}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: active ? 0.08 : 0.03 }}
        transition={{ duration: 12, ease: 'easeInOut', repeat: Infinity, repeatType: 'reverse' }}
        className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(255,255,255,0.06),transparent_22%),radial-gradient(circle_at_bottom_right,rgba(255,210,170,0.04),transparent_28%)]"
      />
    </div>
  )
}
