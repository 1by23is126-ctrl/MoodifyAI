import React from 'react';
import { motion } from 'framer-motion';

export default function HeroSection() {
  return (
    <div className="hero-contrast flex flex-col items-center text-center z-20 w-full mt-6">
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15, duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        className="hero-eyebrow mb-7 inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full"
      >
        <span className="relative flex h-1.5 w-1.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-70" style={{ backgroundColor: 'var(--mood-primary)' }} />
          <span className="relative inline-flex rounded-full h-1.5 w-1.5 shadow-[0_0_10px_var(--mood-glow)]" style={{ backgroundColor: 'var(--mood-primary)' }} />
        </span>
        <span className="readable-kicker text-[10px] font-semibold tracking-[0.22em] uppercase">
          AI Emotional Intelligence · v1.0
        </span>
      </motion.div>

      <motion.h1
        className="hero-title text-[clamp(2.6rem,6.6vw,4.6rem)] mb-5"
        initial={{ opacity: 0, y: 16, filter: 'blur(8px)' }}
        animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
        transition={{ delay: 0.3, duration: 0.95, ease: [0.16, 1, 0.3, 1] }}
      >
        Soundtrack your{' '}
        <span className="hero-title-accent editorial-italic">inner</span>{' '}
        <span className="hero-title-accent">world.</span>
      </motion.h1>

      <motion.p
        className="hero-copy text-base md:text-[1.06rem] max-w-[34rem] mx-auto"
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.55, duration: 0.85 }}
      >
        Type a feeling. Our neural engine maps your sentiment to a cinematic soundscape,
        tuned to the texture of this exact moment.
      </motion.p>
    </div>
  );
}
