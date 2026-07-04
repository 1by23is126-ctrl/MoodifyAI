import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const phases = [
  'Decoding emotional patterns…',
  'Analyzing sentiment depth…',
  'Mapping musical resonance…',
  'Synthesizing audio frequencies…',
  'Aligning atmospheric context…'
];

export default function AnalysisLoader() {
  const [phaseIndex, setPhaseIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setPhaseIndex(prev => Math.min(prev + 1, phases.length - 1));
    }, 720);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-[420px] relative">
      <div className="relative w-32 h-32 mb-12">
        {/* Outer breathing halo */}
        <motion.div
          className="absolute -inset-10 rounded-full"
          style={{
            background: 'radial-gradient(circle, color-mix(in srgb, var(--mood-primary) 32%, transparent), transparent 70%)',
            filter: 'blur(24px)'
          }}
          animate={{ scale: [1, 1.18, 1], opacity: [0.45, 0.8, 0.45] }}
          transition={{ duration: 2.4, repeat: Infinity, ease: 'easeInOut' }}
        />

        {/* Core glow */}
        <div
          className="absolute inset-0 rounded-full"
          style={{
            background: 'radial-gradient(circle, color-mix(in srgb, var(--mood-primary) 42%, transparent) 0%, transparent 70%)',
            filter: 'blur(18px)'
          }}
        />

        {/* Rotating ring 1 — outer */}
        <motion.div
          className="absolute inset-0 rounded-full"
          style={{
            borderStyle: 'solid',
            borderWidth: '2px',
            borderTopColor: 'var(--mood-primary)',
            borderRightColor: 'transparent',
            borderBottomColor: 'var(--mood-secondary)',
            borderLeftColor: 'transparent',
            filter: 'drop-shadow(0 0 6px var(--mood-glow))'
          }}
          animate={{ rotate: 360 }}
          transition={{ duration: 2.4, repeat: Infinity, ease: 'linear' }}
        />

        {/* Rotating ring 2 — inner */}
        <motion.div
          className="absolute inset-4 rounded-full"
          style={{
            borderStyle: 'solid',
            borderWidth: '1px',
            borderTopColor: 'transparent',
            borderRightColor: 'var(--mood-secondary)',
            borderBottomColor: 'transparent',
            borderLeftColor: 'var(--mood-primary)',
            opacity: 0.75
          }}
          animate={{ rotate: -360 }}
          transition={{ duration: 3.6, repeat: Infinity, ease: 'linear' }}
        />

        {/* Pulse ring */}
        <motion.div
          className="absolute inset-8 rounded-full border"
          style={{ borderColor: 'rgba(255,255,255,0.22)' }}
          animate={{ scale: [1, 1.22, 1], opacity: [0.7, 0.12, 0.7] }}
          transition={{ duration: 1.8, repeat: Infinity, ease: 'easeInOut' }}
        />

        {/* Center dot */}
        <div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-white"
          style={{ boxShadow: '0 0 14px #fff, 0 0 30px var(--mood-glow)' }}
        />
      </div>

      <div className="h-7 relative overflow-hidden w-full max-w-sm flex justify-center">
        <AnimatePresence mode="wait">
          <motion.div
            key={phaseIndex}
            initial={{ opacity: 0, y: 12, filter: 'blur(4px)' }}
            animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
            exit={{ opacity: 0, y: -12, filter: 'blur(4px)' }}
            transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
            className="absolute tracking-[0.02em] text-[0.86rem] font-medium text-secondary"
          >
            {phases[phaseIndex]}
          </motion.div>
        </AnimatePresence>
      </div>

      <div className="mt-7 flex items-center gap-1.5">
        {phases.map((_, idx) => (
          <motion.span
            key={idx}
            className="block h-[3px] rounded-full"
            style={{
              backgroundColor: idx <= phaseIndex ? 'var(--mood-primary)' : 'rgba(255,255,255,0.08)',
              boxShadow: idx <= phaseIndex ? '0 0 10px var(--mood-glow)' : 'none'
            }}
            animate={{ width: idx === phaseIndex ? 28 : 12 }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          />
        ))}
      </div>
    </div>
  );
}
