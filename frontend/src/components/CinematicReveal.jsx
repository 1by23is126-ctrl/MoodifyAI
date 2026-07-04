import React, { useMemo, useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import TrackCard from './TrackCard';
import MoodSpectrum from './MoodSpectrum';
import JournalComposer from './JournalComposer';

const LANGUAGE_LABELS = {
  english: 'English',
  hindi: 'Hindi',
  kannada: 'Kannada',
  tamil: 'Tamil',
  telugu: 'Telugu'
};

const normalizeLanguageKey = (language) => String(language || '').trim().toLowerCase();

const normalizeLanguageLabel = (language) => {
  const key = normalizeLanguageKey(language);
  return LANGUAGE_LABELS[key] || String(language || '').trim();
};

export default function CinematicReveal({ moodData, onReset }) {
  const { mood, nuancedLabel, intensity, scores, tracks, explanation, title, secondary, hiddenUndertone, confidence, dimensions } = moodData;

  const recommendationsByLanguage = useMemo(() => {
    const rbl = moodData.recommendationsByLanguage || moodData.recommendations_by_language;

    if (rbl && Object.keys(rbl).length > 0) {
      return Object.entries(rbl).reduce((grouped, [language, languageTracks]) => {
        if (!Array.isArray(languageTracks)) return grouped;

        const normalizedLanguage = normalizeLanguageLabel(language);
        if (!normalizedLanguage) return grouped;

        grouped[normalizedLanguage] = languageTracks
          .map((track) => ({
            ...track,
            language: normalizeLanguageLabel(track?.language || normalizedLanguage)
          }))
          .filter((track) => normalizeLanguageKey(track.language) === normalizeLanguageKey(normalizedLanguage));

        return grouped;
      }, {});
    }

    return { English: tracks || [] };
  }, [moodData.recommendationsByLanguage, moodData.recommendations_by_language, tracks]);

  const languages = useMemo(() =>
    Object.keys(recommendationsByLanguage).filter(
      (lang) => Array.isArray(recommendationsByLanguage[lang]) && recommendationsByLanguage[lang].length > 0
    ),
    [recommendationsByLanguage]
  );

  const [activeLanguage, setActiveLanguage] = useState(() => languages[0] || 'English');

  useEffect(() => {
    const hasActiveLanguage = languages.some(
      (language) => normalizeLanguageKey(language) === normalizeLanguageKey(activeLanguage)
    );

    if (languages.length > 0 && !hasActiveLanguage) {
      setActiveLanguage(languages[0]);
    }
  }, [languages, activeLanguage]);

  const activeTracks = useMemo(() => {
    const matchedLanguage = Object.keys(recommendationsByLanguage).find(
      (language) => normalizeLanguageKey(language) === normalizeLanguageKey(activeLanguage)
    );
    const filteredSongs = matchedLanguage ? recommendationsByLanguage[matchedLanguage] : [];
    return filteredSongs || [];
  }, [recommendationsByLanguage, activeLanguage]);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.07, delayChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 18, filter: 'blur(8px)' },
    visible: { opacity: 1, y: 0, filter: 'blur(0px)', transition: { duration: 0.65, ease: [0.16, 1, 0.3, 1] } }
  };

  const pills = [
    { label: 'Intensity', value: intensity },
    { label: 'Nuance', value: nuancedLabel },
    secondary && { label: 'Undercurrent', value: secondary },
    hiddenUndertone && { label: 'Hidden', value: hiddenUndertone },
    confidence && { label: 'Confidence', value: `${Math.round(confidence * 100)}%` }
  ].filter(Boolean);

  return (
    <div className="w-full max-w-[1500px] mx-auto flex flex-col gap-10 pb-24 relative px-4" style={{ zIndex: 20 }}>
      <motion.div
        initial="hidden"
        animate="visible"
        variants={containerVariants}
        className="grid grid-cols-1 lg:grid-cols-[minmax(380px,460px)_1fr] gap-7"
      >
        {/* Left Column: Mood Summary */}
        <div className="flex flex-col gap-5">
          <motion.div variants={itemVariants} className="mood-result-hero p-8 md:p-9 relative">
            <span className="mood-result-hero__monogram" aria-hidden>{mood?.charAt(0) || 'M'}</span>

            <div className="relative z-10">
              <div className="flex items-center gap-2 mb-4">
                <span className="w-1 h-1 rounded-full" style={{ background: 'var(--mood-primary)', boxShadow: '0 0 8px var(--mood-glow)' }} />
                <span className="readable-kicker text-[10px] tracking-[0.24em] uppercase font-semibold text-muted">
                  Primary state detected
                </span>
              </div>

              <h2 className="text-[clamp(2rem,3.6vw,2.85rem)] font-display font-semibold leading-[1.02] tracking-[-0.025em] mb-6 text-stellar">
                {title?.split('|').map((part, idx, arr) => (
                  <React.Fragment key={idx}>
                    {idx === 1 ? <span className="editorial-italic font-normal text-secondary"> {part.trim()}</span> : part.trim()}
                    {idx < arr.length - 1 && idx === 0 && <span className="mx-2 text-muted/40">·</span>}
                  </React.Fragment>
                )) || 'Soundscape composed'}
              </h2>

              <div className="flex gap-1.5 mb-7 flex-wrap">
                {pills.map((pill) => (
                  <span key={pill.label} className="mood-pill">
                    <span className="mood-pill__label">{pill.label}</span>
                    <span className="opacity-90">{pill.value}</span>
                  </span>
                ))}
              </div>

              <p className="hero-copy leading-[1.7] text-[0.97rem] text-secondary/95 max-w-prose">
                {explanation}
              </p>
            </div>
          </motion.div>

          <motion.div variants={itemVariants}>
            <MoodSpectrum scores={scores} dimensions={dimensions} primary={nuancedLabel} secondary={secondary} confidence={confidence} />
          </motion.div>

          <motion.div variants={itemVariants}>
            <JournalComposer moodData={moodData} />
          </motion.div>

          <motion.div variants={itemVariants} className="flex gap-3 items-stretch">
            <button
              onClick={onReset}
              className="btn-icon w-12 h-12 flex-shrink-0"
              title="New Analysis"
              aria-label="New analysis"
              data-testid="new-analysis-btn"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
                <path d="M3 3v5h5"/>
              </svg>
            </button>
            <div className="flex-1 glass-2 rounded-2xl flex items-center px-5 text-[0.78rem] tracking-[0.04em]">
              <span className="text-muted">Source ·</span>
              <span className="ml-2 text-secondary">curated multilingual mood library</span>
            </div>
          </motion.div>
        </div>

        {/* Right Column: Track Cards */}
        <div style={{ position: 'relative', zIndex: 30 }}>
          <motion.div className="flex items-end justify-between gap-4 mb-5 px-1" variants={itemVariants}>
            <div>
              <span className="readable-kicker text-[10px] tracking-[0.24em] uppercase font-semibold text-muted">
                Curated for you
              </span>
              <h3 className="text-[1.45rem] md:text-[1.6rem] font-display font-semibold tracking-[-0.02em] text-stellar mt-1">
                Recommended <span className="editorial-italic font-normal">soundscape</span>
              </h3>
            </div>
            <span className="text-[11px] tracking-[0.18em] uppercase text-muted font-semibold whitespace-nowrap pb-1">
              {activeTracks.length} <span className="opacity-50 font-medium">tracks</span>
            </span>
          </motion.div>

          {languages.length > 1 && (
            <motion.div
              className="language-tabs mb-6"
              variants={itemVariants}
              role="tablist"
              aria-label="Recommendation language"
              data-testid="language-tabs"
            >
              {languages.map((language) => (
                <button
                  key={language}
                  type="button"
                  role="tab"
                  aria-selected={normalizeLanguageKey(activeLanguage) === normalizeLanguageKey(language)}
                  className={`language-tab ${normalizeLanguageKey(activeLanguage) === normalizeLanguageKey(language) ? 'is-active' : ''}`}
                  onClick={() => setActiveLanguage(language)}
                  data-testid={`language-tab-${language.toLowerCase()}`}
                >
                  {language}
                </button>
              ))}
            </motion.div>
          )}

          <motion.div
            key={activeLanguage}
            className="recommendations-grid overflow-y-auto pr-1 space-y-3"
            style={{
              display: 'block',
              maxHeight: '520px',
              overflowY: 'auto',
              scrollbarWidth: 'thin',
              scrollbarColor: 'rgba(148,163,184,0.45) transparent'
            }}
            initial="hidden"
            animate="visible"
            variants={{
              hidden: {},
              visible: { transition: { staggerChildren: 0.04 } }
            }}
          >
            {activeTracks.length === 0 ? (
              <div className="recommendations-empty text-center py-16">
                <p className="text-muted text-sm">No tracks found for this mood in {activeLanguage}.</p>
              </div>
            ) : (
              activeTracks.map((song, idx) => (
                <motion.div
                  key={`${activeLanguage}-${song?.title || song?.name || idx}-${idx}`}
                  variants={{
                    hidden: { opacity: 0, y: 12, filter: 'blur(6px)' },
                    visible: { opacity: 1, y: 0, filter: 'blur(0px)', transition: { duration: 0.45, ease: [0.16, 1, 0.3, 1] } }
                  }}
                >
                  <TrackCard track={song} index={idx} />
                </motion.div>
              ))
            )}
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}
