import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import VoiceMic from './VoiceMic';

const placeholders = [
  "I'm feeling completely drained after a long day…",
  "Everything is electric and I want to move…",
  "Just watching the rain hit the window glass…",
  "Focused on deep work, need to block the noise…",
  "Feeling nostalgic about last summer…"
];

export default function MoodInput({ value, onChange, onSubmit }) {
  const [isFocused, setIsFocused] = useState(false);
  const [placeholderIndex, setPlaceholderIndex] = useState(0);

  useEffect(() => {
    if (isFocused || value) return;
    const interval = setInterval(() => {
      setPlaceholderIndex(prev => (prev + 1) % placeholders.length);
    }, 4200);
    return () => clearInterval(interval);
  }, [isFocused, value]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (value.trim()) onSubmit();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const charCount = value.length;
  const isOverLimit = charCount > 280;
  const canSubmit = Boolean(value.trim()) && !isOverLimit;

  return (
    <motion.div
      className="w-full max-w-2xl relative z-20"
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.85, duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
    >
      <form onSubmit={handleSubmit} className="relative">
        <div className={`mood-input-shell ${isFocused ? 'is-focused' : ''}`}>
          <div className="mood-textarea-frame relative">
            <textarea
              value={value}
              onChange={(e) => onChange(e.target.value)}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              onKeyDown={handleKeyDown}
              className="glass-input mood-textarea bg-transparent resize-none"
              data-testid="mood-input-textarea"
            />

            <AnimatePresence mode="wait">
              {!value && !isFocused && (
                <motion.div
                  key={placeholderIndex}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -6 }}
                  transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
                  className="placeholder-contrast mood-placeholder pointer-events-none"
                >
                  {placeholders[placeholderIndex]}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <div className="mood-input-toolbar">
            <div className="mood-input-meta">
              <span
                className={`text-[11px] font-medium tabular-nums transition-colors ${
                  isOverLimit ? 'text-rose-400' : 'text-muted'
                }`}
                aria-live="polite"
              >
                {charCount} <span className="opacity-50">/ 280</span>
              </span>

              <span className="h-3 w-px bg-white/10" aria-hidden />

              <VoiceMic onTranscript={(text) => onChange(text)} />

              <span className="hidden sm:inline text-[10px] tracking-[0.18em] uppercase text-muted/80">
                or press <kbd className="ml-1 px-1.5 py-0.5 rounded border border-white/10 bg-white/[0.04] text-[9px] font-medium text-secondary">↵</kbd>
              </span>
            </div>

            <motion.button
              type="submit"
              disabled={!canSubmit}
              whileHover={canSubmit ? { y: -1 } : {}}
              whileTap={canSubmit ? { y: 0, scale: 0.985 } : {}}
              className="btn-primary mood-submit-button rounded-xl flex items-center gap-2 group"
              data-testid="mood-input-submit"
            >
              <span>Synthesize</span>
              <svg
                className="w-3.5 h-3.5 transition-transform duration-300 group-hover:translate-x-0.5"
                viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"
              >
                <line x1="5" y1="12" x2="19" y2="12"></line>
                <polyline points="12 5 19 12 12 19"></polyline>
              </svg>
            </motion.button>
          </div>
        </div>
      </form>
    </motion.div>
  );
}
