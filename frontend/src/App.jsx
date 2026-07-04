import React, { Suspense, lazy, useCallback, useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useEmotionalEngine } from './hooks/useEmotionalEngine';

import MoodBackground from './components/MoodBackground';
import Particles from './components/Particles';
import CustomCursor from './components/CustomCursor';
import AiOrb from './components/AiOrb';
import EcosystemWidgets from './components/EcosystemWidgets';
import ErrorBoundary from './components/ErrorBoundary';
import StatusBanner from './components/StatusBanner';

import HeroSection from './components/HeroSection';
import MoodInput from './components/MoodInput';
import AnalysisLoader from './components/AnalysisLoader';

const CinematicReveal = lazy(() => import('./components/CinematicReveal'));
const AnalyticsDashboard = lazy(() => import('./components/AnalyticsDashboard'));
const HistoryPanel = lazy(() => import('./components/HistoryPanel'));
const JournalPanel = lazy(() => import('./components/JournalPanel'));

function FallbackPanel({ label }) {
  return (
    <div className="glass-card mx-auto max-w-5xl rounded-3xl px-8 py-10 text-center">
      <div className="inline-flex items-center gap-3 text-secondary text-sm">
        <span className="w-1.5 h-1.5 rounded-full bg-[var(--mood-primary)] animate-pulse" style={{ boxShadow: '0 0 10px var(--mood-glow)' }} />
        {label}
      </div>
    </div>
  );
}

function AppContent() {
  const {
    phase,
    setPhase,
    rawInput,
    setRawInput,
    currentMood,
    moodData,
    themeColors,
    errorMessage,
    clearError,
    processInput,
    reset,
    returnToInput
  } = useEmotionalEngine();

  const activeView = phase;
  const isResultsVisible = phase === 'results' || phase === 'analytics';
  const isWorkspaceVisible = ['idle', 'analyzing', 'results', 'analytics', 'history', 'journal'].includes(phase);

  const handleReturnHome = useCallback(() => {
    returnToInput();
  }, [returnToInput]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isResultsVisible) handleReturnHome();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleReturnHome, isResultsVisible]);

  return (
    <div className="relative min-h-screen overflow-hidden selection:bg-[var(--mood-primary)]/30">
      <StatusBanner message={errorMessage} onDismiss={clearError} />
      <CustomCursor />
      <MoodBackground mood={currentMood} />
      <Particles mood={currentMood} phase={phase} />

      {/* Ambient glow centered on orb */}
      <div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[78vw] h-[78vw] max-w-[760px] max-h-[760px] ambient-glow transition-opacity duration-1000"
        style={{ opacity: phase === 'analyzing' ? 0.6 : phase === 'idle' ? 0.32 : 0.18 }}
      />

      <EcosystemWidgets moodData={moodData} phase={phase} setPhase={setPhase} />

      <AnimatePresence>
        {isResultsVisible && (
          <motion.button
            key="cinematic-back"
            type="button"
            onClick={handleReturnHome}
            className="cinematic-back-button"
            aria-label="Return to mood input"
            title="Return to mood input"
            initial={{ opacity: 0, y: -8, filter: 'blur(8px)' }}
            animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
            exit={{ opacity: 0, y: -8, filter: 'blur(8px)' }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
            data-testid="return-button"
          >
            <span className="cinematic-back-button__icon" aria-hidden="true">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M19 12H5" />
                <path d="M12 19l-7-7 7-7" />
              </svg>
            </span>
            <span className="cinematic-back-button__label">Return</span>
          </motion.button>
        )}
      </AnimatePresence>

      <main className="relative z-10 container mx-auto px-6 h-screen flex flex-col items-center justify-center pointer-events-none">

        {!isResultsVisible && phase !== 'analyzing' && (
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none" style={{ zIndex: 1 }}>
            <AiOrb phase={phase} mood={currentMood} colors={themeColors} />
          </div>
        )}

        <AnimatePresence mode="wait">
          {phase === 'idle' && (
            <motion.div
              key="idle"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10, filter: 'blur(6px)' }}
              transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
              className="w-full max-w-3xl flex flex-col items-center gap-10 pointer-events-auto"
            >
              <HeroSection />
              <MoodInput
                value={rawInput}
                onChange={setRawInput}
                onSubmit={() => processInput(rawInput)}
              />
            </motion.div>
          )}

          {phase === 'analyzing' && (
            <motion.div
              key="analyzing"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.06, filter: 'blur(12px)' }}
              transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
              className="w-full pointer-events-auto"
            >
              <AnalysisLoader />
            </motion.div>
          )}

          {activeView === 'results' && moodData && (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 24, filter: 'blur(12px)' }}
              animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
              exit={{ opacity: 0, y: 28, filter: 'blur(16px)' }}
              transition={{ duration: 0.75, ease: [0.16, 1, 0.3, 1] }}
              className="w-full h-full pt-28 pb-12 overflow-y-auto pointer-events-auto hide-scrollbar"
            >
              <Suspense fallback={<FallbackPanel label="Preparing your cinematic experience…" />}>
                <CinematicReveal moodData={moodData} onReset={reset} />
              </Suspense>
            </motion.div>
          )}

          {activeView === 'analytics' && (
            <motion.div
              key="analytics"
              initial={{ opacity: 0, y: 18, filter: 'blur(10px)' }}
              animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
              exit={{ opacity: 0, y: 22, filter: 'blur(14px)' }}
              transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
              className="w-full h-full pt-28 pb-12 overflow-y-auto pointer-events-auto hide-scrollbar"
            >
              <Suspense fallback={<FallbackPanel label="Loading analytics…" />}>
                <AnalyticsDashboard onBack={() => setPhase(moodData ? 'results' : 'idle')} />
              </Suspense>
            </motion.div>
          )}

          {phase === 'history' && (
            <motion.div
              key="history"
              initial={{ opacity: 0, y: 18, filter: 'blur(10px)' }}
              animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
              exit={{ opacity: 0, y: 22, filter: 'blur(14px)' }}
              transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
              className="w-full h-full pt-28 pb-12 overflow-y-auto pointer-events-auto hide-scrollbar"
            >
              <Suspense fallback={<FallbackPanel label="Loading history…" />}>
                <HistoryPanel onBack={() => setPhase('idle')} />
              </Suspense>
            </motion.div>
          )}

          {phase === 'journal' && (
            <motion.div
              key="journal"
              initial={{ opacity: 0, y: 18, filter: 'blur(10px)' }}
              animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
              exit={{ opacity: 0, y: 22, filter: 'blur(14px)' }}
              transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
              className="w-full h-full pt-28 pb-12 overflow-y-auto pointer-events-auto hide-scrollbar"
            >
              <Suspense fallback={<FallbackPanel label="Loading journal…" />}>
                <JournalPanel onBack={() => setPhase('idle')} />
              </Suspense>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <AppContent />
    </ErrorBoundary>
  );
}
