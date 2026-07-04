import React from 'react';
import { AnimatePresence, motion } from 'framer-motion';

export default function StatusBanner({ message, onDismiss }) {
  return (
    <AnimatePresence>
      {message && (
        <motion.div
          initial={{ opacity: 0, y: -12, filter: 'blur(8px)' }}
          animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
          exit={{ opacity: 0, y: -12, filter: 'blur(8px)' }}
          transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
          className="pointer-events-auto fixed inset-x-0 top-5 z-[60] flex justify-center px-4"
          data-testid="status-banner"
        >
          <div className="glass-3 max-w-2xl rounded-2xl px-5 py-3 text-sm text-stellar">
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-3 min-w-0">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 flex-shrink-0" style={{ boxShadow: '0 0 8px rgb(251, 191, 36)' }} />
                <p className="text-[0.86rem] leading-relaxed truncate">{message}</p>
              </div>
              {onDismiss && (
                <button
                  type="button"
                  onClick={onDismiss}
                  className="flex-shrink-0 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-[10px] uppercase tracking-[0.2em] font-semibold text-muted transition hover:bg-white/10 hover:text-stellar"
                  data-testid="status-banner-dismiss"
                >
                  Dismiss
                </button>
              )}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
