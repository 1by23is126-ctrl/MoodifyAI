import React, { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';

export default function EcosystemWidgets({ moodData, phase, setPhase }) {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 30000);
    return () => clearInterval(timer);
  }, []);

  const timeStr = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const dateStr = time.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' });

  if (phase === 'analyzing') return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.5 }}
        className="fixed inset-0 pointer-events-none z-30"
      >
        {/* Top Header: Logo, Navigation, Time */}
        <div className="top-header-shell">
          <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="top-header-brand"
          >
            <div className="relative w-9 h-9 shrink-0 rounded-full border border-white/10 bg-white/[0.03] flex items-center justify-center backdrop-blur-xl overflow-hidden">
              <div
                className="w-3 h-3 rounded-full animate-pulse"
                style={{
                  backgroundColor: 'var(--mood-primary)',
                  boxShadow: '0 0 14px var(--mood-glow), 0 0 28px var(--mood-glow)'
                }}
              />
              <div
                className="absolute inset-0 rounded-full"
                style={{
                  background: 'radial-gradient(circle at 30% 30%, rgba(255,255,255,0.12), transparent 50%)'
                }}
              />
            </div>
            <div className="flex min-w-0 flex-col leading-tight">
              <span className="font-display font-semibold tracking-[-0.01em] text-stellar text-[0.96rem]">
                Moodify<span className="text-muted font-medium">AI</span>
              </span>
              <span className="text-[9px] tracking-[0.22em] uppercase text-muted/70 font-medium">
                emotional engine
              </span>
            </div>
          </motion.div>

          <nav className="top-header-nav" aria-label="Primary">
            <button
              type="button"
              onClick={() => setPhase('idle')}
              className="btn-secondary px-4 py-2 rounded-full text-[0.78rem] font-semibold"
            >
              Home
            </button>
            <button
              type="button"
              onClick={() => setPhase('analytics')}
              className="btn-secondary px-4 py-2 rounded-full text-[0.78rem] font-semibold"
            >
              Dashboard
            </button>
            <button
              type="button"
              onClick={() => setPhase('history')}
              className="btn-secondary px-4 py-2 rounded-full text-[0.78rem] font-semibold"
            >
              History
            </button>
            <button
              type="button"
              onClick={() => setPhase('journal')}
              className="btn-secondary px-4 py-2 rounded-full text-[0.78rem] font-semibold"
            >
              Journal
            </button>
          </nav>

          <motion.div
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="top-header-clock flex flex-col items-end gap-1"
          >
            <div className="text-sm font-medium tracking-[0.06em] text-stellar tabular-nums">{timeStr}</div>
            <div className="text-[10px] text-muted uppercase tracking-[0.22em] font-medium">{dateStr}</div>

            {moodData && phase === 'results' && (
              <motion.div
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="mt-3 px-3 py-1.5 rounded-full bg-white/[0.04] backdrop-blur-xl border border-white/10 flex items-center gap-2"
              >
                <span
                  className="w-1 h-1 rounded-full"
                  style={{
                    backgroundColor: 'var(--mood-secondary)',
                    boxShadow: '0 0 6px var(--mood-secondary)'
                  }}
                />
                <span className="text-[9px] uppercase tracking-[0.24em] text-muted font-semibold">
                  env &middot; {moodData.profile?.weather || 'stable'}
                </span>
              </motion.div>
            )}
          </motion.div>
        </div>

        {/* Bottom Right: Analytics Toggle */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.45, duration: 0.6 }}
          className="absolute bottom-6 right-6 pointer-events-auto"
        >
          <button
            onClick={() => setPhase(phase === 'analytics' ? (moodData ? 'results' : 'idle') : 'analytics')}
            className="btn-icon w-11 h-11"
            title={phase === 'analytics' ? 'Close analytics' : 'View analytics'}
            aria-label={phase === 'analytics' ? 'Close analytics' : 'View analytics'}
            data-testid="analytics-toggle"
          >
            {phase === 'analytics' ? (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            ) : (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 3v18h18" />
                <path d="M7 14l4-4 4 4 6-6" />
              </svg>
            )}
          </button>
        </motion.div>

        {/* Bottom Left: System Status */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.65 }}
          transition={{ delay: 0.5, duration: 0.8 }}
          className="absolute bottom-6 left-6 flex items-center gap-2"
        >
          <span className="relative flex h-1.5 w-1.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-60" />
            <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-400 shadow-[0_0_8px_rgb(74,222,128)]" />
          </span>
          <span className="text-[9px] font-mono tracking-[0.28em] uppercase text-muted">
            engine &middot; active
          </span>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
